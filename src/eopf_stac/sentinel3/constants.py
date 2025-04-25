import os
from copy import deepcopy

import pystac
from pystac import Extent, Provider, SpatialExtent, TemporalExtent
from pystac.extensions.sat import OrbitState
from pystac.item_assets import ItemAssetDefinition
from pystac.utils import str_to_datetime
from stactools.sentinel3.constants import SENTINEL_OLCI_BANDS

from eopf_stac.common.constants import (
    DATASET_ASSET_EXTRA_FIELDS,
    EOPF_PROVIDER,
    LICENSE_PROVIDER,
    PRODUCT_ASSET_KEY,
    PRODUCT_METADATA_ASSET_KEY,
    PRODUCT_METADATA_PATH,
    ROLE_DATA,
    ROLE_DATASET,
    SENTINEL_PROVIDER,
    get_item_asset_metadata,
    get_item_asset_product,
)

SENTINEL3_METADATA = {
    "extent": Extent(
        SpatialExtent([-180.0, -90.0, 180.0, 90.0]),
        TemporalExtent([[str_to_datetime("2016-02-16T00:00:00Z"), None]]),
    ),
    "keywords": ["Copernicus", "Sentinel", "EU", "ESA", "Satellite", "Global", "Earth"],
    "providers": [
        LICENSE_PROVIDER,
        Provider(
            name=SENTINEL_PROVIDER.name,
            roles=SENTINEL_PROVIDER.roles,
            url=os.path.join(SENTINEL_PROVIDER.url, "sentinel-3"),
        ),
        EOPF_PROVIDER,
    ],
    "constellation": "sentinel-3",
    "platforms": ["sentinel-3a", "sentinel-3b"],
    "sat": {
        "orbit_state": [OrbitState.ASCENDING, OrbitState.DESCENDING],
        "platform_international_designator": ["2016-011A", "2018-039A"],
    },
}


def get_olci_band_item_assets() -> dict[str:ItemAssetDefinition]:
    item_assets = {}
    for band_key, band in SENTINEL_OLCI_BANDS.items():
        item_asset = ItemAssetDefinition.create(
            title=f"TOA radiance for OLCI acquisition band {band_key}",
            media_type=pystac.MediaType.ZARR,
            description=None,
            roles=[ROLE_DATA],
            extra_fields={"bands": [band.to_dict()]},
        )
        item_assets[f"{band_key}_radianceData"] = item_asset

    return item_assets


OLCI_L1_ASSETS: dict[str, ItemAssetDefinition] = {
    "radianceData": ItemAssetDefinition.create(
        title="TOA radiance for OLCI acquisition bands 01 to 21",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={
            **deepcopy(DATASET_ASSET_EXTRA_FIELDS),
            "bands": list(map(lambda b: b.to_dict(), SENTINEL_OLCI_BANDS.values())),
        },
    ),
    **get_olci_band_item_assets(),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

OLCI_L1_ASSETS_KEY_TO_PATH: dict[str:str] = {
    "radianceData": "measurements",
    "Oa01_radianceData": "measurements/oa01_radiance",
    "Oa02_radianceData": "measurements/oa02_radiance",
    "Oa03_radianceData": "measurements/oa03_radiance",
    "Oa04_radianceData": "measurements/oa04_radiance",
    "Oa05_radianceData": "measurements/oa05_radiance",
    "Oa06_radianceData": "measurements/oa06_radiance",
    "Oa07_radianceData": "measurements/oa07_radiance",
    "Oa08_radianceData": "measurements/oa08_radiance",
    "Oa09_radianceData": "measurements/oa09_radiance",
    "Oa10_radianceData": "measurements/oa10_radiance",
    "Oa11_radianceData": "measurements/oa11_radiance",
    "Oa12_radianceData": "measurements/oa12_radiance",
    "Oa13_radianceData": "measurements/oa13_radiance",
    "Oa14_radianceData": "measurements/oa14_radiance",
    "Oa15_radianceData": "measurements/oa15_radiance",
    "Oa16_radianceData": "measurements/oa16_radiance",
    "Oa17_radianceData": "measurements/oa17_radiance",
    "Oa18_radianceData": "measurements/oa18_radiance",
    "Oa19_radianceData": "measurements/oa19_radiance",
    "Oa20_radianceData": "measurements/oa20_radiance",
    "Oa21_radianceData": "measurements/oa21_radiance",
    PRODUCT_ASSET_KEY: "",
    PRODUCT_METADATA_ASSET_KEY: PRODUCT_METADATA_PATH,
}


def get_olci_bands(band_keys: list[str] | None = None) -> list[dict]:
    bands = []
    if band_keys is None:
        for _, band in SENTINEL_OLCI_BANDS.items():
            bands.append(band.to_dict())
    else:
        for key in band_keys:
            bands.append(SENTINEL_OLCI_BANDS[key].to_dict())
    return bands


OLCI_L2_ASSETS: dict[str, ItemAssetDefinition] = {
    "lagp": ItemAssetDefinition.create(
        title="Land and atmospheric geophysical products",
        media_type=pystac.MediaType.ZARR,
        description=(
            "Dataset containing variables for the \n"
            "- Green Instantaneous Fraction of Absorbed Photosynthetically Active Radiation (GI-FAPAR) \n"
            "- Terrestrial Chlorophyll Index (OTCI) \n"
            "- Integrated Water Vapour (IWV) \n"
            "- GIFAPAR by-products red and NIR rectified reflectances (RC681, RC865)"
        ),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={
            **deepcopy(DATASET_ASSET_EXTRA_FIELDS),
            "bands": get_olci_bands(["Oa03", "Oa10", "Oa17", "Oa18", "Oa19"]),
        },
    ),
    "gifapar": ItemAssetDefinition.create(
        title="Green Instantaneous FAPAR (GIFAPAR)",
        media_type=pystac.MediaType.ZARR,
        description="Fraction of Absorbed Photosynthetically Active Radiation (FAPAR) in the plant canopy",
        roles=[ROLE_DATA],
        extra_fields={"bands": get_olci_bands(["Oa03", "Oa10", "Oa17"])},
    ),
    "otci": ItemAssetDefinition.create(
        title="OLCI Terrestrial Chlorophyll Index",
        media_type=pystac.MediaType.ZARR,
        description=(
            "Estimates of the Chlorophyll content in terrestrial vegetation, aims at monitoring "
            "vegetation condition and health"
        ),
        roles=[ROLE_DATA],
        extra_fields=None,
    ),
    "iwv": ItemAssetDefinition.create(
        title="Integrated Water Vapour Column",
        media_type=pystac.MediaType.ZARR,
        description=("Total amount of water vapour integrated over an atmosphere column"),
        roles=[ROLE_DATA],
        extra_fields={"bands": get_olci_bands(["Oa18", "Oa19"])},
    ),
    "rc681": ItemAssetDefinition.create(
        title="Green Instantaneous FAPAR (GIFAPAR) - Rectified Reflectance - red channel",
        media_type=pystac.MediaType.ZARR,
        description=(
            "By-products of the GI-FAPAR, the so-called red rectified reflectance is a "
            "virtual reflectance largely decontaminated from atmospheric and angular effects, "
            "and good proxy to Top of Canopy reflectances."
        ),
        roles=[ROLE_DATA],
        extra_fields={"bands": get_olci_bands(["Oa10"])},
    ),
    "rc865": ItemAssetDefinition.create(
        title="Green Instantaneous FAPAR (GIFAPAR) - Rectified Reflectance - NIR channel",
        media_type=pystac.MediaType.ZARR,
        description=(
            "By-products of the GI-FAPAR, the so-called NIR rectified reflectance is a "
            "virtual reflectance largely decontaminated from atmospheric and angular effects, "
            "and good proxy to Top of Canopy reflectances."
        ),
        roles=[ROLE_DATA],
        extra_fields={"bands": get_olci_bands(["Oa17"])},
    ),
    "lqsf": ItemAssetDefinition.create(
        title="Land Quality and Science Flags",
        media_type=pystac.MediaType.ZARR,
        description=(
            "The quality and science flags provide information about validity, suspicious quality, "
            "cosmetic filling, environment and input quality."
        ),
        roles=[ROLE_DATA],
        extra_fields=None,
    ),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

OLCI_L2_ASSETS_KEY_TO_PATH: dict[str:str] = {
    "lagp": "measurements",
    "gifapar": "measurements/gifapar",
    "otci": "measurements/otci",
    "iwv": "measurements/iwv",
    "rc681": "measurements/rc681",
    "rc865": "measurements/rc865",
    "lqsf": "quality/lqsf",
    PRODUCT_ASSET_KEY: "",
    PRODUCT_METADATA_ASSET_KEY: PRODUCT_METADATA_PATH,
}

# -- Collection metadata

S3_OLCI_L1_EFR = {
    "id": "sentinel-3-olci-l1-efr",
    "title": "Sentinel-3 OLCI Level-1 EFR",
    "description": (
        "The Sentinel-3 OLCI L1 EFR product provides TOA radiances at full resolution "
        "for each pixel in the instrument grid, each view and each OLCI channel, plus annotation "
        "data associated to OLCI pixels."
    ),
    "product_type": "S03OLCEFR",
    "processing_level": "L1",
    "instrument": "olci",
    "gsd": 300,
    "item_assets": {**OLCI_L1_ASSETS},
}

S3_OLCI_L1_ERR = {
    "id": "sentinel-3-olci-l1-err",
    "title": "Sentinel-3 OLCI Level-1 ERR",
    "description": (
        "The Sentinel-3 OLCI L1 ERR product provides TOA radiances at reduced resolution "
        "for each pixel in the instrument grid, each view and each OLCI channel, plus annotation "
        "data associated to OLCI pixels."
    ),
    "product_type": "S03OLCERR",
    "processing_level": "L1",
    "instrument": "olci",
    "gsd": 1200,
    "item_assets": {**OLCI_L1_ASSETS},
}

S3_OLCI_L2_LFR = {
    "id": "sentinel-3-olci-l2-lfr",
    "title": "Sentinel-3 OLCI Level-2 LFR",
    "description": (
        "The Sentinel-3 OLCI L2 LFR product provides land and atmospheric geophysical parameters computed for full resolution."
    ),
    "product_type": "S03OLCLFR",
    "processing_level": "L2",
    "instrument": "olci",
    "gsd": 300,
    "item_assets": {**OLCI_L2_ASSETS},
}


# S03SLSRBT / SL_1_RBT
S3_SLSTR_L1_RBT = {}

# S03SLSLST / SL_2_LST
S3_SLSTR_L2_LST = {}

# TBD: SRAL, SYN

# Conversion not supported by CPM; no mapping

S3_OLCI_L2_LRR = {
    "id": "sentinel-3-olci-l2-lrr",
    "title": "Sentinel-3 OLCI Level-2 LRR",
    "description": (
        "The Sentinel-3 OLCI L2 LRR product provides land and atmospheric geophysical parameters computed for reduced resolution."
    ),
    "product_type": "S03OLCLRR",
    "processing_level": "L2",
    "instrument": "olci",
    "gsd": 1200,
    "item_assets": {**OLCI_L2_ASSETS},
}

S3_OLCI_L2_WFR = {
    "id": "sentinel-3-olci-l2-wfr",
    "title": "Sentinel-3 OLCI Level-2 WFR",
    "description": (
        "The Sentinel-3 OCLI Level-2 LFR product provides water and atmospheric geophysical parameters computed for full resolution."
    ),
    "product_type": "S03OLCWFR",
    "processing_level": "L2",
    "instrument": "olci",
    "gsd": 300,
    "item_assets": {
        PRODUCT_ASSET_KEY: get_item_asset_product(),
        PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
    },
}
