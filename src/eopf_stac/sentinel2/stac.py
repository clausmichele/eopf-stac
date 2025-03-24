import logging
import os
from itertools import chain

import antimeridian
import pystac
from pystac.extensions.eo import EOExtension
from pystac.extensions.grid import GridExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.sat import OrbitState, SatExtension
from pystac.extensions.scientific import ItemScientificExtension
from pystac.extensions.timestamps import TimestampsExtension
from pystac.extensions.view import ViewExtension
from pystac.utils import now_in_utc, str_to_datetime
from stactools.sentinel2.constants import (
    SENTINEL_CONSTELLATION,
    SENTINEL_INSTRUMENTS,
)
from stactools.sentinel2.mgrs import MgrsExtension

from eopf_stac.constants import (
    EOPF_PROVIDER,
    LICENSE_PROVIDER,
    SENTINEL_LICENSE,
    SENTINEL_PROVIDER,
)
from eopf_stac.sentinel2.assets import (
    get_aot_wvp_assets,
    get_band_assets,
    get_dataset_assets,
    get_extra_assets,
    get_scl_assets,
    get_tci_assets,
)
from eopf_stac.sentinel2.constants import (
    DATASET_PATHS_TO_ASSET,
    L1C_BAND_ASSETS_TO_PATH,
    L1C_TCI_ASSETS_TO_PATH,
    L2A_AOT_WVP_ASSETS_TO_PATH,
    L2A_BAND_ASSETS_TO_PATH,
    L2A_SCL_ASSETS_TO_PATH,
    L2A_TCI_ASSETS_TO_PATH,
    MGRS_PATTERN,
)

logger = logging.getLogger(__name__)


def arrange_bbox(bbox):
    longitudes = [bbox[0], bbox[2]]
    latitudes = [bbox[1], bbox[3]]

    corrected_bbox = [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]
    return corrected_bbox


def create_item(metadata: dict, asset_href_prefix: str) -> pystac.Item:
    stac_discovery = metadata[".zattrs"]["stac_discovery"]
    other_metadata = metadata[".zattrs"]["other_metadata"]
    properties = stac_discovery["properties"]

    # -- datetimes

    datetime = None
    start_datetime = None
    end_datetime = None
    datetime_str = properties.get("datetime")
    if datetime_str is not None:
        # workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/643
        if datetime_str == "null":
            datetime = None
        else:
            datetime = str_to_datetime(datetime_str)

    if datetime is None:
        # start_datetime and end_datetime must be supplied
        start_datetime_str = properties.get("start_datetime")
        if start_datetime_str is not None:
            start_datetime = str_to_datetime(start_datetime_str)
            datetime = start_datetime
        end_datetime_str = properties.get("end_datetime")
        if end_datetime_str is not None:
            end_datetime = str_to_datetime(end_datetime_str)

    item_id = stac_discovery.get("id")
    # workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/690
    if item_id.lower().endswith(".safe"):
        item_id = os.path.splitext(item_id)[0]

    bbox = arrange_bbox(stac_discovery.get("bbox"))

    item = pystac.Item(
        id=item_id,
        bbox=bbox,
        geometry=stac_discovery.get("geometry"),
        properties={},
        datetime=datetime,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )

    # -- Common metadata

    mission = properties.get("mission")
    if mission is not None:
        item.common_metadata.mission = mission
    else:
        item.common_metadata.mission = SENTINEL_CONSTELLATION.capitalize()

    item.common_metadata.providers = [
        LICENSE_PROVIDER,
        pystac.Provider(
            name=SENTINEL_PROVIDER.name,
            roles=SENTINEL_PROVIDER.roles,
            url=os.path.join(SENTINEL_PROVIDER.url, item.common_metadata.mission.lower()),
        ),
        EOPF_PROVIDER,
    ]

    item.common_metadata.constellation = SENTINEL_CONSTELLATION
    item.common_metadata.instruments = SENTINEL_INSTRUMENTS
    item.common_metadata.gsd = 10

    created_datetime = properties.get("created")
    if created_datetime is None:
        created_datetime = now_in_utc()
    else:
        created_datetime = str_to_datetime(created_datetime)
    item.common_metadata.created = created_datetime
    item.common_metadata.updated = created_datetime

    if properties.get("platform"):
        item.common_metadata.platform = properties.get("platform")
    if properties.get("mission"):
        item.common_metadata.mission = properties.get("mission")
    # TODO published?

    # -- Extensions

    # Timestamps
    ts_ext = TimestampsExtension.ext(item, add_if_missing=True)
    ts_ext.apply(published=created_datetime)

    # Electro-Optical Extension
    eo = EOExtension.ext(item, add_if_missing=True)
    eo.cloud_cover = properties.get("eo:cloud_cover")
    eo.snow_cover = properties.get("eo:snow_cover")

    # Satellite Extension
    orbit_state = properties.get("sat:orbit_state")
    relative_orbit = properties.get("sat:relative_orbit")
    absolute_orbit = properties.get("sat:absolute_orbit")
    platform_international_designator = properties.get("sat:platform_international_designator")
    if any([orbit_state, relative_orbit, absolute_orbit, platform_international_designator]):
        sat = SatExtension.ext(item, add_if_missing=True)
        if orbit_state:
            sat.orbit_state = OrbitState(orbit_state.lower())
        if relative_orbit:
            sat.relative_orbit = relative_orbit
        if absolute_orbit:
            sat.absolute_orbit = absolute_orbit
        if platform_international_designator:
            sat.platform_international_designator = platform_international_designator

    # Projection Extension
    code = other_metadata.get("horizontal_CRS_code")
    centroid = antimeridian.centroid(item.geometry)
    if any([code, centroid]):
        projection = ProjectionExtension.ext(item, add_if_missing=True)
        projection.bbox = bbox
        if code:
            projection.code = code
        if centroid:
            projection.centroid = {"lat": round(centroid.y, 5), "lon": round(centroid.x, 5)}

    # MGRS and Grid Extension
    mgrs_match = MGRS_PATTERN.search(stac_discovery.get("id"))
    if mgrs_match and len(mgrs_groups := mgrs_match.groups()) == 3:
        mgrs = MgrsExtension.ext(item, add_if_missing=True)
        mgrs.utm_zone = int(mgrs_groups[0])
        mgrs.latitude_band = mgrs_groups[1]
        mgrs.grid_square = mgrs_groups[2]
        grid = GridExtension.ext(item, add_if_missing=True)
        grid.code = f"MGRS-{mgrs.utm_zone}{mgrs.latitude_band}{mgrs.grid_square}"
    else:
        logger.warning(f"Error populating MGRS and Grid Extensions fields from ID: {stac_discovery.get('id')}")

    # View Extension
    sun_azimuth = other_metadata.get("mean_sun_azimuth_angle_in_deg_for_all_bands_all_detectors")
    sun_elevation = other_metadata.get("mean_sun_zenith_angle_in_deg_for_all_bands_all_detectors")
    if any([sun_azimuth, sun_elevation]):
        view = ViewExtension.ext(item, add_if_missing=True)
        if sun_azimuth:
            view.sun_azimuth = sun_azimuth
        if sun_elevation:
            view.sun_elevation = sun_elevation
        # TODO view.azimuth view.incidence_angle

    # Processing Extension
    proc_facility = properties.get("processing:facility")
    proc_level = properties.get("processing:level")
    proc_lineage = properties.get("processing:lineage")
    proc_software = properties.get("processing:software")
    proc_datetime = properties.get("processing:datetime")
    proc_version = properties.get("processing:version")
    if any([proc_facility, proc_level, proc_lineage, proc_software, proc_datetime, proc_version]):
        item.stac_extensions.append("https://stac-extensions.github.io/processing/v1.2.0/schema.json")
        if proc_facility:
            item.properties["processing:facility"] = proc_facility
        if proc_level:
            item.properties["processing:level"] = proc_level
        if proc_lineage:
            item.properties["processing:lineage"] = proc_lineage
        if proc_software:
            item.properties["processing:software"] = proc_software
        if proc_datetime:
            item.properties["processing:datetime"] = proc_datetime
        if proc_version:
            item.properties["processing:version"] = proc_version

    # Product Extension
    product_timeliness = properties.get("product:timeliness")
    product_timeliness_category = properties.get("product:timeliness_category")
    product_type = properties.get("product:type")
    product_acquisition_type = properties.get("product:acquisition_type")
    if any([product_type, product_acquisition_type, all([product_timeliness, product_timeliness_category])]):
        item.stac_extensions.append("https://stac-extensions.github.io/product/v0.1.0/schema.json")
        if product_type:
            item.properties["product:type"] = product_type
        if product_acquisition_type:
            item.properties["product:acquisition_type"] = product_acquisition_type
        if all([product_timeliness, product_timeliness_category]):
            item.properties["product:timeliness"] = product_timeliness
            item.properties["product:timeliness_category"] = product_timeliness_category

    # Scientific Extension
    if properties.get("sci:doi"):
        sci = ItemScientificExtension.ext(item, add_if_missing=True)
        sci.doi = properties.get("sci:doi")

    # EOPF Extension
    # workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/689
    # https://github.com/CS-SI/eopf-stac-extension
    eopf_datatake_id = properties.get("eopf:data_take_id")
    eopf_instrument_mode = properties.get("eopf:instrument_mode")
    eopf_origin_datetime = None
    eopf_datastrip_id = None
    eopf_instrument_configuration_id = None
    if any(
        [
            eopf_datatake_id,
            eopf_instrument_mode,
            eopf_origin_datetime,
            eopf_datastrip_id,
            eopf_instrument_configuration_id,
        ]
    ):
        item.stac_extensions.append("https://cs-si.github.io/eopf-stac-extension/v1.2.0/schema.json")
        if eopf_datatake_id:
            item.properties["eopf:datatake_id"] = eopf_datatake_id
        if eopf_instrument_mode:
            item.properties["eopf:instrument_mode"] = eopf_instrument_mode
        if eopf_origin_datetime:
            item.properties["eopf:origin_datetime"] = eopf_origin_datetime
        if eopf_datastrip_id:
            item.properties["eopf:datastrip_id"] = eopf_datastrip_id
        if eopf_instrument_configuration_id:
            item.properties["eopf:instrument_configuration_id"] = eopf_instrument_configuration_id

    # -- Assets

    logger.debug("Creating assets ...")

    if product_type == "S02MSIL1C":
        band_assets = get_band_assets(L1C_BAND_ASSETS_TO_PATH, asset_href_prefix, metadata, item)
        aot_wvp_assets = {}
        scl_assets = {}
        tci_assets = get_tci_assets(L1C_TCI_ASSETS_TO_PATH, asset_href_prefix, metadata, item)
    elif product_type == "S02MSIL2A":
        band_assets = get_band_assets(L2A_BAND_ASSETS_TO_PATH, asset_href_prefix, metadata, item)
        aot_wvp_assets = get_aot_wvp_assets(L2A_AOT_WVP_ASSETS_TO_PATH, asset_href_prefix, metadata, item)
        scl_assets = get_scl_assets(L2A_SCL_ASSETS_TO_PATH, asset_href_prefix, metadata, item)
        tci_assets = get_tci_assets(L2A_TCI_ASSETS_TO_PATH, asset_href_prefix, metadata, item)
    else:
        raise ValueError(f"Invalid Sentinel-2 product type '{product_type}'")

    dataset_assets = get_dataset_assets(DATASET_PATHS_TO_ASSET, asset_href_prefix, metadata, item)
    extra_assets = get_extra_assets(asset_href_prefix, item)

    for key, asset in chain(
        band_assets.items(),
        aot_wvp_assets.items(),
        scl_assets.items(),
        tci_assets.items(),
        dataset_assets.items(),
        extra_assets.items(),
    ):
        assert key not in item.assets
        item.add_asset(key, asset)

    # -- Links

    item.links.append(SENTINEL_LICENSE)

    return item
