import logging
import os

import geojson
import pystac
from pystac.extensions.sar import FrequencyBand, Polarization, SarExtension
from pystac.extensions.sat import OrbitState, SatExtension
from pystac.extensions.timestamps import TimestampsExtension
from pystac.extensions.view import ViewExtension
from pystac.utils import now_in_utc, str_to_datetime

from eopf_stac.constants import (
    EOPF_PROVIDER,
    LICENSE_PROVIDER,
    SENTINEL_LICENSE,
    SENTINEL_PROVIDER,
)
from eopf_stac.sentinel1.assets import create_grd_assets, create_ocn_assets, create_slc_assets
from eopf_stac.sentinel1.constants import (
    S1_GRD_PRODUCT_TYPES,
    S1_OCN_PRODUCT_TYPES,
    S1_PRODUCT_TYPE_MAPPING,
    S1_SLC_PRODUCT_TYPES,
)

logger = logging.getLogger(__name__)


def arrange_bbox(bbox):
    longitudes = [bbox[0], bbox[2]]
    latitudes = [bbox[1], bbox[3]]

    corrected_bbox = [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]
    return corrected_bbox


def create_item(metadata: dict, asset_href_prefix: str) -> pystac.Item:
    logger.info(f"create_item_s1: {asset_href_prefix}")

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

    item.common_metadata.mission = "Sentinel-1"
    item.common_metadata.providers = [
        LICENSE_PROVIDER,
        pystac.Provider(
            name=SENTINEL_PROVIDER.name,
            roles=SENTINEL_PROVIDER.roles,
            url=os.path.join(SENTINEL_PROVIDER.url, item.common_metadata.mission.lower()),
        ),
        EOPF_PROVIDER,
    ]

    item.common_metadata.constellation = "sentinel-1"
    item.common_metadata.instruments = ["sar"]

    created_datetime = properties.get("created")
    if created_datetime is None:
        created_datetime = now_in_utc()
    else:
        created_datetime = str_to_datetime(created_datetime)
    item.common_metadata.created = created_datetime
    item.common_metadata.updated = created_datetime

    platform = properties.get("platform")
    if platform:
        item.common_metadata.platform = platform
    if properties.get("mission"):
        item.common_metadata.mission = properties.get("mission")

    # -- Extensions

    # Timestamps
    ts_ext = TimestampsExtension.ext(item, add_if_missing=True)
    ts_ext.apply(published=created_datetime)

    # Satellite Extension
    orbit_state = properties.get("sat:orbit_state")
    relative_orbit = properties.get("sat:relative_orbit")
    absolute_orbit = properties.get("sat:absolute_orbit")
    anx_datetime = properties.get("sat:anx_datetime")
    platform_international_designator = properties.get("sat:platform_international_designator")  # "2014-016A"
    if any([orbit_state, relative_orbit, absolute_orbit, platform_international_designator, anx_datetime]):
        sat = SatExtension.ext(item, add_if_missing=True)
        if orbit_state:
            sat.orbit_state = OrbitState(orbit_state.lower())
        if relative_orbit:
            sat.relative_orbit = relative_orbit
        if absolute_orbit:
            sat.absolute_orbit = absolute_orbit
        if platform_international_designator:
            sat.platform_international_designator = platform_international_designator
        if anx_datetime:
            sat.anx_datetime = str_to_datetime(anx_datetime)

    # View Extension
    azimuth = other_metadata.get("view:azimuth")
    incidence_angle = other_metadata.get("view:incidence_angle")
    off_nadir = properties.get("view:off_nadir")
    if any([azimuth, incidence_angle, off_nadir]):
        view = ViewExtension.ext(item, add_if_missing=True)
        if azimuth:
            view.azimuth = azimuth
        if incidence_angle:
            view.incidence_angle = incidence_angle
        if off_nadir:
            view.off_nadir = off_nadir

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
            # Workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/706
            if product_timeliness != "MISSING":
                item.properties["product:timeliness"] = product_timeliness
                item.properties["product:timeliness_category"] = product_timeliness_category

    # SAR Extension
    polarizations = None
    polarizations_value = properties.get("sar:polarizations")
    if polarizations_value:
        polarizations = []
        for p in polarizations_value:
            polarizations.append(Polarization(p))
    frequency_band = FrequencyBand.C
    instrument_mode = properties.get("sar:instrument_mode")
    center_frequency = properties.get("sar:center_frequency")
    resolution_range = properties.get("sar:resolution_range")
    resolution_azimuth = properties.get("sar:resolution_azimuth")
    pixel_spacing_range = properties.get("sar:pixel_spacing_range")
    observation_direction = properties.get("sar:observation_direction")
    pixel_spacing_azimuth = properties.get("sar:pixel_spacing_azimuth")
    sar_product_type = properties.get("sar:product_type")
    sar_instrument_mode = properties.get("eopf:instrument_mode")
    logger.debug(sar_instrument_mode)
    # looks_equivalent_number
    if any(
        [
            polarizations,
            frequency_band,
            instrument_mode,
            center_frequency,
            resolution_range,
            resolution_azimuth,
            pixel_spacing_range,
            observation_direction,
            pixel_spacing_azimuth,
            sar_product_type,
            sar_instrument_mode,
        ]
    ):
        sar = SarExtension.ext(item, add_if_missing=True)
        if polarizations:
            sar.polarizations = polarizations
        if frequency_band:
            sar.frequency_band = frequency_band
        if instrument_mode:
            sar.instrument_mode = instrument_mode
        if center_frequency:
            sar.center_frequency = center_frequency
        else:
            sar.center_frequency = 5.405
        if resolution_range:
            sar.resolution_range = resolution_range
        if resolution_azimuth:
            sar.resolution_azimuth = resolution_azimuth
        if pixel_spacing_range:
            sar.pixel_spacing_range = pixel_spacing_range
        if observation_direction:
            sar.observation_direction = observation_direction
        if pixel_spacing_azimuth:
            sar.pixel_spacing_azimuth = pixel_spacing_azimuth
        if sar_product_type:
            sar.product_type = sar_product_type
        if sar_instrument_mode:
            sar.instrument_mode = sar_instrument_mode

    # EOPF Extension
    eopf_datatake_id = properties.get("eopf:datatake_id")
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

    logger.debug("Getting product components...")
    product_components = get_product_components(metadata=metadata, product_type=product_type)

    # Reconstruct original identifier of SAFE product
    # workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/70
    component_name = None
    for _, name in product_components.items():
        component_name = name
        break  # we need only one component_name

    item.id = construct_identifier_s1(
        product_type=product_type,
        polarization=polarizations_value,
        startTime=start_datetime_str,
        endTime=end_datetime_str,
        platform=platform,
        orbit=absolute_orbit,
        component=component_name,
    )

    # -- Assets
    assets = {}
    logger.debug("Creating assets...")
    if product_type in S1_GRD_PRODUCT_TYPES:
        assets = create_grd_assets(asset_href_prefix=asset_href_prefix, components=product_components)
    elif product_type in S1_SLC_PRODUCT_TYPES:
        assets = create_slc_assets(asset_href_prefix=asset_href_prefix, components=product_components)
    elif product_type in S1_OCN_PRODUCT_TYPES:
        assets = create_ocn_assets(
            asset_href_prefix=asset_href_prefix, components=product_components, instrument_mode=eopf_instrument_mode
        )
    else:
        raise ValueError(f"Unsupported Sentinel-1 product type '{product_type}'")

    for key, asset in assets.items():
        assert key not in item.assets
        item.add_asset(key, asset)

    # -- Links

    item.links.append(SENTINEL_LICENSE)

    # Workaround for
    fix_geometry(item=item)

    return item


def fix_geometry(item: pystac.Item):
    coordinates = geojson.Polygon.clean_coordinates(coords=item.geometry["coordinates"], precision=15)
    first_coord = coordinates[0][0]

    # Append first coordinate to polygon
    coordinates[0].append(first_coord)

    # Validate new coordinates
    polygon = geojson.Polygon(coordinates=coordinates, validate=True)

    # Upate item geomatry
    item.geometry = polygon


def get_product_components(metadata: dict, product_type: str) -> dict[str:str]:
    components = {}
    stac_discovery_links = metadata[".zattrs"]["stac_discovery"]["links"]
    if stac_discovery_links:
        for component_name in stac_discovery_links:
            if isinstance(component_name, str):
                if product_type in S1_GRD_PRODUCT_TYPES:
                    key = component_name.split("_")[6]
                    components[key] = component_name
                elif product_type in S1_SLC_PRODUCT_TYPES:
                    parts = component_name.split("_")
                    if len(parts) > 7:
                        key = f"{parts[6]}_{parts[7]}_{parts[8]}"
                    else:
                        key = parts[6]
                    components[key] = component_name
                elif product_type in S1_OCN_PRODUCT_TYPES:
                    key = component_name
                    for sub_component in (
                        metadata.get(f"{component_name.lower()}/.zattrs", {}).get("stac_discovery", {}).get("links", {})
                    ):
                        if isinstance(sub_component, str):
                            components[component_name] = sub_component
    else:
        raise ValueError("Links section in metadata is missing")

    return components


def list_equals(actual, expected):
    if len(actual) != len(expected):
        return False

    return all([a == b for a, b in zip(actual, expected)])


def construct_identifier_s1(product_type, polarization, startTime, endTime, platform, orbit, component):
    logger.debug("Re-creating S1 identifier from metadata...")

    mission = "S1"

    product_type_out = S1_PRODUCT_TYPE_MAPPING.get(product_type)
    if product_type_out is None:
        raise ValueError(f"Unexpected product type: {product_type}")

    datatake = None
    crc = None
    if component is not None and len(component) > 0:
        parts = component.split("_")
        if len(parts) >= 7:
            crc = parts[4]
            datatake = parts[5]
            if polarization is None:
                polarization = parts[6]
        else:
            raise ValueError(f"Unexpected format of component name: {component}")
    else:
        raise ValueError("Name of component cannot be empty")

    if polarization is None:
        raise ValueError("Polarization cannot be empty")

    polarization_out = ""
    if product_type in S1_OCN_PRODUCT_TYPES:
        if product_type == "S01SWVOCN":
            polarization_out = "SV" if polarization == "VV" else "SH"
        else:
            polarization_out = "DV" if polarization == "VV" else "DH"
    else:
        if list_equals(polarization, ["VV", "VH"]):
            polarization_out = "DV"
        elif list_equals(polarization, ["HH", "HV"]):
            polarization_out = "DH"
        elif list_equals(polarization, ["VV"]):
            polarization_out = "SV"
        elif list_equals(polarization, ["HH"]):
            polarization_out = "SH"

    if len(polarization_out) == 0:
        raise ValueError(f"Unexpectd polarization value: {polarization}")

    startTime_out = startTime[:19].replace("-", "").replace(":", "")
    endTime_out = endTime[:19].replace("-", "").replace(":", "")

    platform_out = ""
    if platform.lower() == "sentinel-1a":
        platform_out = "A"
    elif platform.lower() == "sentinel-1b":
        platform_out = "B"
    elif platform.lower() == "sentinel-1c":
        platform_out = "C"
    else:
        raise ValueError("Platform cannot be empty")

    orbit_out = str(orbit)
    if len(orbit_out) < 6:
        orbit_out = orbit_out.rjust(6, "0")

    return f"{mission}{platform_out}_{product_type_out}{polarization_out}_{startTime_out}_{endTime_out}_{orbit_out}_{datatake}_{crc}"
