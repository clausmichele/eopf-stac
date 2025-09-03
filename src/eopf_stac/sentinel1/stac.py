import logging
import os

import geojson
import pystac
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.view import ViewExtension
from pystac.utils import datetime_to_str

from eopf_stac.common.constants import (
    EOPF_PROVIDER,
    LICENSE_PROVIDER,
    SENTINEL_LICENSE,
    SENTINEL_PROVIDER,
)
from eopf_stac.common.stac import (
    fill_eopf_properties,
    fill_processing_properties,
    fill_product_properties,
    fill_sat_properties,
    fill_timestamp_properties,
    get_datetimes,
    get_identifier,
    get_source_identifier,
    rearrange_bbox,
)
from eopf_stac.sentinel1.assets import create_grd_assets, create_ocn_assets, create_slc_assets
from eopf_stac.sentinel1.constants import (
    S1_GRD_PRODUCT_TYPES,
    S1_OCN_PRODUCT_TYPES,
    S1_PRODUCT_TYPE_MAPPING,
    S1_SLC_PRODUCT_TYPES,
)

logger = logging.getLogger(__name__)


def create_item(
    metadata: dict, product_type: str, asset_href_prefix: str, cpm_version: str = None, source_href: str | None = None
) -> pystac.Item:
    stac_discovery = metadata[".zattrs"]["stac_discovery"]
    other_metadata = metadata[".zattrs"]["other_metadata"]
    properties = stac_discovery["properties"]

    # -- source identifier
    source_identifier = get_source_identifier(source_href)
    logger.debug(source_identifier)

    # -- datetimes
    datetimes = get_datetimes(properties)
    datetime = datetimes[0]
    start_datetime = datetimes[1]
    end_datetime = datetimes[2]

    item = pystac.Item(
        id=get_identifier(stac_discovery),
        bbox=rearrange_bbox(stac_discovery.get("bbox")),
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

    platform = properties.get("platform")
    if platform:
        item.common_metadata.platform = platform
    if properties.get("mission"):
        item.common_metadata.mission = properties.get("mission")

    # -- Extensions

    # Timestamps
    fill_timestamp_properties(item, properties)

    # Satellite Extension
    fill_sat_properties(item, properties)

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
    baseline_version = None
    if properties.get("processing:software") is not None:
        baseline_version = properties.get("processing:software").get("Sentinel-1 IPF")
    fill_processing_properties(item, properties, cpm_version, baseline_version)

    # Product Extension
    fill_product_properties(item, product_type, properties)

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
        item.stac_extensions.append("https://stac-extensions.github.io/sar/v1.3.0/schema.json")
        # sar = SarExtension.ext(item, add_if_missing=True)
        if polarizations:
            item.properties["sar:polarizations"] = polarizations
        if frequency_band:
            item.properties["sar:frequency_band"] = frequency_band
        if center_frequency:
            item.properties["sar:center_frequency"] = center_frequency
        else:
            item.properties["sar:center_frequency"] = 5.405
        if resolution_range:
            item.properties["sar:resolution_range"] = resolution_range
        if resolution_azimuth:
            item.properties["sar:resolution_azimuth"] = resolution_azimuth
        if pixel_spacing_range:
            item.properties["sar:pixel_spacing_range"] = pixel_spacing_range
        if observation_direction:
            item.properties["sar:observation_direction"] = observation_direction
        if pixel_spacing_azimuth:
            item.properties["sar:pixel_spacing_azimuth"] = pixel_spacing_azimuth
        if sar_product_type:
            item.properties["sar:product_type"] = sar_product_type
        if sar_instrument_mode:
            item.properties["sar:instrument_mode"] = sar_instrument_mode

    # EOPF Extension
    fill_eopf_properties(item, properties)

    logger.debug("Getting product components...")
    product_components = get_product_components(metadata=metadata, product_type=product_type)

    # Reconstruct original identifier of SAFE product
    # CPM workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/70
    component_name = None
    for _, name in product_components.items():
        component_name = name
        break  # we need only one component_name
    item.id = construct_identifier_s1(
        product_type=product_type,
        polarization=polarizations_value,
        startTime=datetime_to_str(start_datetime),
        endTime=datetime_to_str(end_datetime),
        platform=platform,
        orbit=properties.get("sat:absolute_orbit"),
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
            asset_href_prefix=asset_href_prefix,
            components=product_components,
            instrument_mode=properties.get("eopf:instrument_mode"),
        )
    else:
        raise ValueError(f"Unsupported Sentinel-1 product type '{product_type}'")

    for key, asset in assets.items():
        assert key not in item.assets
        item.add_asset(key, asset)

    # -- Links

    item.links.append(SENTINEL_LICENSE)

    # CPM workaround for https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/708
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
