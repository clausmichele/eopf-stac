import logging
import os
import re
from itertools import chain

import pystac
import zarr
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.scientific import ItemScientificExtension
from pystac.extensions.view import ViewExtension
from stactools.sentinel2.constants import (
    SENTINEL_CONSTELLATION,
    SENTINEL_INSTRUMENTS,
)

from eopf_stac.common.constants import (
    EOPF_PROVIDER,
    LICENSE_PROVIDER,
    SENTINEL_LICENSE,
    SENTINEL_PROVIDER,
)
from eopf_stac.common.stac import (
    create_cdse_link,
    fill_eo_properties,
    fill_eopf_properties,
    fill_mgrs_grid_properties,
    fill_processing_properties,
    fill_product_properties,
    fill_sat_properties,
    fill_timestamp_properties,
    fill_version_properties,
    fix_geometry,
    get_datetimes,
    get_identifier_from_href,
    rearrange_bbox,
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
)

logger = logging.getLogger(__name__)


def create_item(
    metadata: dict,
    product_type: str,
    asset_href_prefix: str,
    cpm_version: str = None,
    cdse_scene_id: str | None = None,
    cdse_scene_href: str | None = None,
    collection_id: str | None = None,
) -> pystac.Item:
    stac_discovery = metadata[".zattrs"]["stac_discovery"]
    other_metadata = metadata[".zattrs"]["other_metadata"]
    properties = stac_discovery["properties"]

    # -- datetimes
    datetimes = get_datetimes(properties)
    datetime = datetimes[0]
    start_datetime = datetimes[1]
    end_datetime = datetimes[2]

    bbox = rearrange_bbox(stac_discovery.get("bbox"))

    identifier = get_identifier_from_href(asset_href_prefix)

    item = pystac.Item(
        id=identifier,
        bbox=bbox,
        geometry=stac_discovery.get("geometry"),
        properties={},
        datetime=datetime,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )

    # -- Geometry (fix antimeridian, unclosed ring, etc)
    fix_geometry(item)

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

    if properties.get("platform"):
        item.common_metadata.platform = properties.get("platform")
    if properties.get("mission"):
        item.common_metadata.mission = properties.get("mission")

    # -- Extensions

    # Timestamps
    fill_timestamp_properties(item, properties)

    # Electro-Optical Extension
    fill_eo_properties(item, properties)

    # Satellite Extension
    fill_sat_properties(item, properties)

    # Projection Extension
    proj_code = properties.get("proj:code")  # Since CPM 2.6.4 this field is available
    if proj_code is None:
        proj_code = properties.get("proj:epsg")  # CPM version 2.5.6
        if proj_code is not None:
            proj_code = f"EPSG:{proj_code}"
        if proj_code is None:
            proj_code = other_metadata.get("horizontal_CRS_code")  # 2.5.6 < CPM version < 2.6.4

    proj_bbox = properties.get("proj:bbox")  # in CPM 2.5.6 and 2.6.4 this field is available
    if proj_bbox is None:
        proj_bbox = calculate_proj_bbox(url=asset_href_prefix)  # 2.5.6 < CPM version < 2.6.4

    if any([proj_code, proj_bbox]):
        projection = ProjectionExtension.ext(item, add_if_missing=True)
        if proj_bbox is not None:
            projection.bbox = proj_bbox
        if proj_code is not None:
            projection.code = proj_code

    # MGRS and Grid Extension
    # First try to extract mgrs fields from identifier
    mgrs_grid = fill_mgrs_grid_properties(item=item, identifier=identifier)
    if not mgrs_grid:
        if cdse_scene_id is not None:
            # Retry with csde scene id
            mgrs_grid = fill_mgrs_grid_properties(item=item, identifier=cdse_scene_id)
    if not mgrs_grid:
        logger.warning("Unable to populate MGRS and Grid Extensions fields from product identifier")

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
    baseline_version = get_baseline_processing_version(identifier)
    if baseline_version is None:
        if cdse_scene_id is not None:
            # Retry with csde scene id
            baseline_version = get_baseline_processing_version(cdse_scene_id)
    fill_processing_properties(item, properties, cpm_version, baseline_version)

    # Product Extension
    fill_product_properties(item, product_type, properties)

    # Scientific Extension
    if properties.get("sci:doi"):
        sci = ItemScientificExtension.ext(item, add_if_missing=True)
        sci.doi = properties.get("sci:doi")

    # EOPF Extension
    fill_eopf_properties(item, properties)

    # Version Extension
    fill_version_properties(item)

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
    extra_assets = get_extra_assets(asset_href=asset_href_prefix, item=item, collection_id=collection_id)

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
    if cdse_scene_href is not None:
        item.links.append(create_cdse_link(cdse_scene_href))

    return item


def calculate_proj_bbox(url: str, res: int = 10) -> list | None:
    logger.info(f"Calculating bounding box in data crs coordinates for resolution {res} ...")
    try:
        path_geom_x_coords = "conditions/geometry/x"
        path_geom_y_coords = "conditions/geometry/y"
        geom_x_coords = zarr.open_array(os.path.join(url, path_geom_x_coords))
        geom_y_coords = zarr.open_array(os.path.join(url, path_geom_y_coords))
        ulx = float(geom_x_coords[0])
        uly = float(geom_y_coords[0])

        if res == 10:
            ncols = 10980
            nrows = 10980
        elif res == 20:
            ncols = 5490
            nrows = 5490
        else:
            ncols = 1830
            nrows = 1830

        #  [xmin, ymin, xmax, ymax]
        proj_bbox = [
            ulx,
            uly - res * ncols,
            ulx + res * nrows,
            uly,
        ]
        return proj_bbox
    except Exception as e:
        logger.error(f"Unable to read coordinates from Zarr data: {str(e)}")
        return None


def get_baseline_processing_version(identifier: str) -> str | None:
    # S2B_MSIL1C_20240428T102559_N0510_R108_T32UPC_20240428T123125
    # S2A_MSIL2A_20250109T100401_N0511_R122_T34UCE_20250109T122750
    proc_version = None
    if identifier is not None:
        proc_version_pattern = re.compile(r"_N(\d{2})(\d{2})")
        proc_version_match = proc_version_pattern.search(identifier)
        if proc_version_match and len(proc_version_groups := proc_version_match.groups()) == 2:
            proc_version = f"{proc_version_groups[0]}.{proc_version_groups[1]}"

    return proc_version
