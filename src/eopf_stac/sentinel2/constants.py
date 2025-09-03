import datetime
import os
import re
from copy import deepcopy
from re import Pattern
from typing import Final

from pystac import ItemAssetDefinition, MediaType, Provider
from pystac.collection import (
    Extent,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.sat import OrbitState
from stactools.sentinel2.constants import (
    SENTINEL_BANDS,
)

from eopf_stac.common.constants import (
    DATASET_ASSET_EXTRA_FIELDS,
    EOPF_PROVIDER,
    LICENSE_PROVIDER,
    PRODUCT_ASSET_KEY,
    PRODUCT_METADATA_ASSET_KEY,
    ROLE_DATA,
    ROLE_DATASET,
    SENTINEL_PROVIDER,
    get_item_asset_metadata,
    get_item_asset_product,
)

ROLE_REFLECTANCE = "reflectance"


MGRS_PATTERN: Final[Pattern[str]] = re.compile(
    r"_T(\d{1,2})([CDEFGHJKLMNPQRSTUVWX])([ABCDEFGHJKLMNPQRSTUVWXYZ][ABCDEFGHJKLMNPQRSTUV])"
)

ASSET_TO_DESCRIPTION: Final[dict[str, str]] = {
    "AOT": "Aerosol optical thickness (AOT)",
    "WVP": "Water vapour (WVP)",
    "TCI": "True color image",
    "B02": "Blue (band 2)",
    "B03": "Green (band 3)",
    "B04": "Red (band 4)",
    "B08": "NIR 1 (band 8)",
    "B01": "Coastal aerosol (band 1)",
    "B05": "Red edge 1 (band 5)",
    "B06": "Red edge 2 (band 6)",
    "B07": "Red edge 3 (band 7)",
    "B10": "Cirrus (band 10)",
    "B11": "SWIR 1 (band 11)",
    "B12": "SWIR 2 (band 12)",
    "B8A": "NIR 2 (band 8A)",
    "B09": "NIR 3 (band 9)",
    "SCL": "Scene classification map (SCL)",
    "SR": "Surface Reflectance",
}

L2A_BAND_ASSETS_TO_PATH: Final[dict[str, str]] = {
    "B02_10m": "measurements/reflectance/r10m/b02",
    "B03_10m": "measurements/reflectance/r10m/b03",
    "B04_10m": "measurements/reflectance/r10m/b04",
    "B08_10m": "measurements/reflectance/r10m/b08",
    "B01_20m": "measurements/reflectance/r20m/b01",
    # "B02_20m": "measurements/reflectance/r20m/b02",
    # "B03_20m": "measurements/reflectance/r20m/b03",
    # "B04_20m": "measurements/reflectance/r20m/b04",
    "B05_20m": "measurements/reflectance/r20m/b05",
    "B06_20m": "measurements/reflectance/r20m/b06",
    "B07_20m": "measurements/reflectance/r20m/b07",
    "B8A_20m": "measurements/reflectance/r20m/b8a",
    "B11_20m": "measurements/reflectance/r20m/b11",
    "B12_20m": "measurements/reflectance/r20m/b12",
    # "B01_60m": "measurements/reflectance/r60m/b01",
    # "B02_60m": "measurements/reflectance/r60m/b02",
    # "B03_60m": "measurements/reflectance/r60m/b03",
    # "B04_60m": "measurements/reflectance/r60m/b04",
    # "B05_60m": "measurements/reflectance/r60m/b05",
    # "B06_60m": "measurements/reflectance/r60m/b06",
    # "B07_60m": "measurements/reflectance/r60m/b07",
    # "B8A_60m": "measurements/reflectance/r60m/b8a",
    "B09_60m": "measurements/reflectance/r60m/b09",
    # "B11_60m": "measurements/reflectance/r60m/b11",
    # "B12_60m": "measurements/reflectance/r60m/b12",
}

L2A_AOT_WVP_ASSETS_TO_PATH: Final[dict[str, str]] = {
    "AOT_10m": "quality/atmosphere/r10m/aot",
    # "AOT_20m": "quality/atmosphere/r20m/aot",
    # "AOT_60m": "quality/atmosphere/r60m/aot",
    "WVP_10m": "quality/atmosphere/r10m/wvp",
    # "WVP_20m": "quality/atmosphere/r20m/wvp",
    # "WVP_60m": "quality/atmosphere/r60m/wvp",
}

L2A_SCL_ASSETS_TO_PATH: Final[dict[str, str]] = {
    "SCL_20m": "conditions/mask/l2a_classification/r20m/scl",
    # "SCL_60m": "conditions/mask/l2a_classification/r60m/scl",
}

L2A_TCI_ASSETS_TO_PATH: Final[dict[str, str]] = {
    "TCI_10m": "quality/l2a_quicklook/r10m/tci",
    # "TCI_20m": "quality/l2a_quicklook/r20m/tci",
    # "TCI_60m": "quality/l2a_quicklook/r60m/tci",
}

DATASET_PATHS_TO_ASSET: Final[dict[str, str]] = {
    "SR_10m": "measurements/reflectance/r10m",
    "SR_20m": "measurements/reflectance/r20m",
    "SR_60m": "measurements/reflectance/r60m",
}

L1C_BAND_ASSETS_TO_PATH: Final[dict[str, str]] = {
    "B01_60m": "measurements/reflectance/r60m/b01",
    "B02_10m": "measurements/reflectance/r10m/b02",
    "B03_10m": "measurements/reflectance/r10m/b03",
    "B04_10m": "measurements/reflectance/r10m/b04",
    "B05_20m": "measurements/reflectance/r20m/b05",
    "B06_20m": "measurements/reflectance/r20m/b06",
    "B07_20m": "measurements/reflectance/r20m/b07",
    "B08_10m": "measurements/reflectance/r10m/b08",
    "B09_60m": "measurements/reflectance/r60m/b09",
    "B10_60m": "measurements/reflectance/r60m/b10",
    "B11_20m": "measurements/reflectance/r20m/b11",
    "B12_20m": "measurements/reflectance/r20m/b12",
    "B8A_20m": "measurements/reflectance/r20m/b8a",
}

L1C_TCI_ASSETS_TO_PATH: Final[dict[str, str]] = {"TCI_10m": "quality/l1c_quicklook/r10m/tci"}


def get_msi_band_item_assets() -> dict[str:ItemAssetDefinition]:
    item_assets = {}
    for band_key, band in SENTINEL_BANDS.items():
        item_asset = ItemAssetDefinition.create(
            title=f"TOA radiance for OLCI acquisition band {band_key}",
            media_type=MediaType.ZARR,
            description=None,
            roles=[ROLE_DATA],
            extra_fields={"bands": [band.to_dict()]},
        )
        item_assets[f"{band_key}_radianceData"] = item_asset

    return item_assets


S2_MSI_L1C_ASSETS: dict[str, ItemAssetDefinition] = {
    "SR_10m": ItemAssetDefinition.create(
        title="Surface Reflectance - 10m",
        media_type=MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={
            **deepcopy(DATASET_ASSET_EXTRA_FIELDS),
            "gsd": 10,
            "bands": list(
                map(
                    lambda b: b.to_dict(),
                    [SENTINEL_BANDS["blue"], SENTINEL_BANDS["green"], SENTINEL_BANDS["red"], SENTINEL_BANDS["nir"]],
                )
            ),
        },
    ),
    **get_msi_band_item_assets(),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

# -- Collections


SENTINEL2_METADATA = {
    "extent": Extent(
        SpatialExtent([-180.0, -90.0, 180.0, 90.0]),
        TemporalExtent([datetime.datetime(2024, 4, 1, 0, 0, 0), None]),
    ),
    "keywords": ["Copernicus", "Sentinel", "EU", "ESA", "Satellite", "Global", "Earth", "Reflectance"],
    "providers": [
        LICENSE_PROVIDER,
        Provider(
            name=SENTINEL_PROVIDER.name,
            roles=SENTINEL_PROVIDER.roles,
            url=os.path.join(SENTINEL_PROVIDER.url, "sentinel-2"),
        ),
        EOPF_PROVIDER,
    ],
    "constellation": "sentinel-2",
    "platforms": ["Sentinel-2A", "Sentinel-2B", "Sentinel-2C"],
    "sat": {
        "orbit_state": [OrbitState.ASCENDING, OrbitState.DESCENDING],
        "platform_international_designator": ["2015-028A", "2017-013A", "2024-157A"],
    },
}

#    summaries.add("sci:doi", ["10.5270/S2_-znk9xsj"])
#    summaries.add("bands", bands)

S2_MSI_L1C = {
    "id": "sentinel-2-l1c",
    "title": "Sentinel-2 Level-1C",
    "description": (
        "The Sentinel-2 Level-1C product is composed of 110x110 km2 tiles (ortho-images in UTM/WGS84 projection). "
        "Earth is subdivided on a predefined set of tiles, defined in UTM/WGS84 projection and using a 100 km step. "
        "However, each tile has a surface of 110x110 km² in order to provide large overlap with the neighbouring. "
        "The Level-1C product results from using a Digital Elevation Model (DEM) to project the image in cartographic "
        "geometry. Per-pixel radiometric measurements are provided in Top Of Atmosphere (TOA) reflectances along with "
        "the parameters to transform them into radiances."
    ),
    "product_type": "S02MSIL1C",
    "processing_level": "L1",
    "instruments": ["msi"],
    "gsd": [10, 20, 60],
    "item_assets": {**S2_MSI_L1C_ASSETS},
}
