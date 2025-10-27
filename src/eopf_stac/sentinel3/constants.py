import os
from copy import deepcopy

import pystac
from pystac import Extent, Provider, SpatialExtent, TemporalExtent
from pystac.extensions.sat import OrbitState
from pystac.item_assets import ItemAssetDefinition
from pystac.utils import str_to_datetime

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

SENTINEL3_OLCI_BANDS_DICT = {
    "Oa01": {"name": "Oa01", "eo:center_wavelength": 400, "eo:full_width_half_max": 15},
    "Oa02": {"name": "Oa02", "eo:center_wavelength": 412.5, "eo:full_width_half_max": 10},
    "Oa03": {"name": "Oa03", "eo:common_name": "coastal", "eo:center_wavelength": 442.5, "eo:full_width_half_max": 10},
    "Oa04": {"name": "Oa04", "eo:common_name": "blue", "eo:center_wavelength": 490, "eo:full_width_half_max": 10},
    "Oa05": {"name": "Oa05", "eo:common_name": "green05", "eo:center_wavelength": 510, "eo:full_width_half_max": 10},
    "Oa06": {"name": "Oa06", "eo:common_name": "green", "eo:center_wavelength": 560, "eo:full_width_half_max": 10},
    "Oa07": {"name": "Oa07", "eo:common_name": "yellow", "eo:center_wavelength": 620, "eo:full_width_half_max": 10},
    "Oa08": {"name": "Oa08", "eo:center_wavelength": 665, "eo:full_width_half_max": 10},
    "Oa09": {"name": "Oa09", "eo:common_name": "red", "eo:center_wavelength": 673.75, "eo:full_width_half_max": 7.5},
    "Oa10": {"name": "Oa10", "eo:center_wavelength": 681.25, "eo:full_width_half_max": 7.5},
    "Oa11": {
        "name": "Oa11",
        "eo:common_name": "rededge071",
        "eo:center_wavelength": 708.75,
        "eo:full_width_half_max": 10,
    },
    "Oa12": {
        "name": "Oa12",
        "eo:common_name": "rededge075",
        "eo:center_wavelength": 753.75,
        "eo:full_width_half_max": 7.5,
    },
    "Oa13": {"name": "Oa13", "eo:center_wavelength": 761.25, "eo:full_width_half_max": 2.5},
    "Oa14": {"name": "Oa14", "eo:center_wavelength": 764.375, "eo:full_width_half_max": 3.75},
    "Oa15": {"name": "Oa15", "eo:center_wavelength": 767.5, "eo:full_width_half_max": 2.5},
    "Oa16": {
        "name": "Oa16",
        "eo:common_name": "rededge078",
        "eo:center_wavelength": 778.75,
        "eo:full_width_half_max": 15,
    },
    "Oa17": {"name": "Oa17", "eo:common_name": "nir08", "eo:center_wavelength": 865, "eo:full_width_half_max": 20},
    "Oa18": {"name": "Oa18", "eo:center_wavelength": 885, "eo:full_width_half_max": 10},
    "Oa19": {"name": "Oa19", "eo:center_wavelength": 900, "eo:full_width_half_max": 10},
    "Oa20": {"name": "Oa20", "eo:common_name": "nir09", "eo:center_wavelength": 940, "eo:full_width_half_max": 20},
    "Oa21": {"name": "Oa21", "eo:center_wavelength": 1020, "eo:full_width_half_max": 40},
}

SENTINEL3_SLSTR_BANDS_DICT = {
    "S01": {"name": "S1", "eo:common_name": "green", "eo:center_wavelength": 554.27, "eo:full_width_half_max": 19.26},
    "S02": {"name": "S2", "eo:common_name": "red", "eo:center_wavelength": 659.47, "eo:full_width_half_max": 19.25},
    "S03": {"name": "S3", "eo:common_name": "nir08", "eo:center_wavelength": 868, "eo:full_width_half_max": 20.6},
    "S04": {"name": "S4", "eo:common_name": "cirrus", "eo:center_wavelength": 1374.8, "eo:full_width_half_max": 20.8},
    "S05": {"name": "S5", "eo:common_name": "swir16", "eo:center_wavelength": 1613.4, "eo:full_width_half_max": 60.68},
    "S06": {"name": "S6", "eo:common_name": "swir22", "eo:center_wavelength": 2255.7, "eo:full_width_half_max": 50.15},
    "S07": {"name": "S7", "eo:center_wavelength": 3742, "eo:full_width_half_max": 398},
    "S08": {"name": "S8", "eo:center_wavelength": 10854, "eo:full_width_half_max": 776},
    "S09": {"name": "S9", "eo:center_wavelength": 12022.5, "eo:full_width_half_max": 905},
    "S10": {"name": "F1", "eo:center_wavelength": 3742, "eo:full_width_half_max": 398},
    "S11": {"name": "F2", "eo:center_wavelength": 10854, "eo:full_width_half_max": 776},
}

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
    for band_key, band in SENTINEL3_OLCI_BANDS_DICT.items():
        item_asset = ItemAssetDefinition.create(
            title=f"TOA radiance for OLCI acquisition band {band_key}",
            media_type=pystac.MediaType.ZARR,
            description=None,
            roles=[ROLE_DATA],
            extra_fields={"bands": [band]},
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
            "bands": list(SENTINEL3_OLCI_BANDS_DICT.values()),
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
        for _, band in SENTINEL3_OLCI_BANDS_DICT.items():
            bands.append(band)
    else:
        for key in band_keys:
            bands.append(SENTINEL3_OLCI_BANDS_DICT[key])
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


def get_slstr_bands(band_keys: list[str] | None = None) -> list[dict]:
    bands = []
    if band_keys is None:
        for _, band in SENTINEL3_SLSTR_BANDS_DICT.items():
            bands.append(band)
    else:
        for key in band_keys:
            bands.append(SENTINEL3_SLSTR_BANDS_DICT[key])

    return bands


SLSTR_L1_ASSETS: dict[str, ItemAssetDefinition] = {
    "radiance_an": ItemAssetDefinition.create(
        title="TOA radiance - stripe A, nadir view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA radiances for the 500m grid, stripe A, nadir view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S01", "S02", "S03", "S04", "S05", "S06"]), "gsd": 500},
    ),
    "radiance_ao": ItemAssetDefinition.create(
        title="TOA radiance - stripe A, oblique view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA radiances for the 500m grid, stripe A, oblique view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S01", "S02", "S03", "S04", "S05", "S06"]), "gsd": 500},
    ),
    "radiance_bn": ItemAssetDefinition.create(
        title="TOA radiance - stripe B, nadir view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA radiances for the 500m grid, stripe B, nadir view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S04", "S05", "S06"]), "gsd": 500},
    ),
    "radiance_bo": ItemAssetDefinition.create(
        title="TOA radiance - stripe B, oblique view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA radiances for the 500m grid, stripe B, oblique view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S04", "S05", "S06"]), "gsd": 500},
    ),
    "BT_in": ItemAssetDefinition.create(
        title="TOA brightness temperature - TIR, nadir view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA brightness temperature for channels S7-S9 and F2 in the 1km grid, nadir view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S07", "S08", "S09", "S11"]), "gsd": 1000},
    ),
    "BT_io": ItemAssetDefinition.create(
        title="TOA brightness temperature - TIR, oblique view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA brightness temperature for channels S7-S9 and F2, 1km grid, oblique view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S07", "S08", "S09", "S11"]), "gsd": 1000},
    ),
    "BT_fn": ItemAssetDefinition.create(
        title="TOA brightness temperature - F1, nadir view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA brightness temperature for the F1 channel, 1km grid, nadir view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S10"]), "gsd": 1000},
    ),
    "BT_fo": ItemAssetDefinition.create(
        title="TOA brightness temperature - F1, oblique view",
        media_type=pystac.MediaType.ZARR,
        description=("Dataset of the TOA brightness temperature for the F1 channel, 1km grid, oblique view"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S10"]), "gsd": 1000},
    ),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SLSTR_L1_ASSETS_KEY_TO_PATH: dict[str:str] = {
    "radiance_an": "measurements/anadir",
    "radiance_ao": "measurements/aoblique",
    "radiance_bn": "measurements/bnadir",
    "radiance_bo": "measurements/boblique",
    "BT_in": "measurements/inadir",
    "BT_io": "measurements/ioblique",
    "BT_fn": "measurements/fnadir",
    "BT_fo": "measurements/foblique",
    PRODUCT_ASSET_KEY: "",
    PRODUCT_METADATA_ASSET_KEY: PRODUCT_METADATA_PATH,
}

SLSTR_L2_LST_ASSETS: dict[str, ItemAssetDefinition] = {
    "lst": ItemAssetDefinition.create(
        title="Land Surface Temperature (LST)",
        media_type=pystac.MediaType.ZARR,
        description=("Gridded Land Surface Temperature generated on the wide 1 km measurement grid"),
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S07", "S08", "S09"]), "gsd": 1000},
    ),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SLSTR_L2_LST_ASSETS_KEY_TO_PATH: dict[str:str] = {
    "lst": "measurements",
    PRODUCT_ASSET_KEY: "",
    PRODUCT_METADATA_ASSET_KEY: PRODUCT_METADATA_PATH,
}

SLSTR_L2_FRP_ASSETS: dict[str, ItemAssetDefinition] = {
    "FRP_an": ItemAssetDefinition.create(
        title="FRP_an measurements",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S05", "S06", "S07", "S10"])},
    ),
    "FRP_bn": ItemAssetDefinition.create(
        title="FRP_bn measurements",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S05", "S06", "S07", "S10"])},
    ),
    "FRP_in": ItemAssetDefinition.create(
        title="FRP_in measurements",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields={"bands": get_slstr_bands(["S05", "S06", "S07", "S10"])},
    ),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SLSTR_L2_FRP_ASSETS_KEY_TO_PATH: dict[str:str] = {
    "FRP_an": "measurements/anadir",
    "FRP_bn": "measurements/bnadir",
    "FRP_in": "measurements/inadir",
    PRODUCT_ASSET_KEY: "",
    PRODUCT_METADATA_ASSET_KEY: PRODUCT_METADATA_PATH,
}

SYN_L2_AOD_ASSETS: dict[str, ItemAssetDefinition] = {
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SYN_L2_VGP_ASSETS: dict[str, ItemAssetDefinition] = {
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SYN_L2_VG1_ASSETS: dict[str, ItemAssetDefinition] = {
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SYN_L2_V10_ASSETS: dict[str, ItemAssetDefinition] = {
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

SYN_L2_SYN_ASSETS: dict[str, ItemAssetDefinition] = {
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
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
    "instruments": ["olci"],
    "gsd": [300],
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
    "instruments": ["olci"],
    "gsd": [1200],
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
    "instruments": ["olci"],
    "gsd": [300],
    "item_assets": {**OLCI_L2_ASSETS},
}

S3_OLCI_L2_LRR = {
    "id": "sentinel-3-olci-l2-lrr",
    "title": "Sentinel-3 OLCI Level-2 LRR",
    "description": (
        "The Sentinel-3 OLCI L2 LRR product provides land and atmospheric geophysical parameters computed for reduced resolution."
    ),
    "product_type": "S03OLCLRR",
    "processing_level": "L2",
    "instruments": ["olci"],
    "gsd": [1200],
    "item_assets": {**OLCI_L2_ASSETS},
}

S3_SLSTR_L1_RBT = {
    "id": "sentinel-3-slstr-l1-rbt",
    "title": "Sentinel-3 SLSTR Level-1 RBT",
    "description": (
        "The Sentinel-3 SLSTR Level-1B RBT product provides radiances and brightness temperatures for each pixel "
        "in a regular image grid for each view and SLSTR channel. In addition, it also contains annotations data "
        "associated with each image pixels."
    ),
    "product_type": "S03SLSRBT",
    "processing_level": "L1",
    "instruments": ["slstr"],
    "gsd": [500, 1000],
    "item_assets": {**SLSTR_L1_ASSETS},
}

S3_SLSTR_L2_LST = {
    "id": "sentinel-3-slstr-l2-lst",
    "title": "Sentinel-3 SLSTR Level-2 LST",
    "description": "The Sentinel-3 SLSTR Level-2 LST product provides land surface temperature.",
    "product_type": "S03SLSLST",
    "processing_level": "L2",
    "instruments": ["slstr"],
    "gsd": [500, 1000],
    "item_assets": {**SLSTR_L2_LST_ASSETS},
}

S3_SLSTR_L2_FRP = {
    "id": "sentinel-3-slstr-l2-frp",
    "title": "Sentinel-3 SLSTR Level-2 FRP",
    "description": (
        "The Sentinel-3 SLSTR Level-2 FRP product provides global (over land and water) fire radiative power."
    ),
    "product_type": "S03SLSFRP",
    "processing_level": "L2",
    "instruments": ["slstr"],
    "gsd": [500, 1000],
    "item_assets": {**SLSTR_L2_FRP_ASSETS},
}

S3_SYN_L2_AOD = {
    "id": "sentinel-3-syn-l2-aod",
    "title": "Sentinel-3 SYN Level-2 AOD",
    "description": (
        "The Sentinel-3 Level-2 AOD product is a global product over land and sea providing aerosol "
        "optical thickness, surface reflectance and several aerosol characteristics on a wider resolution (4.5 km)."
    ),
    "product_type": "S03SYNAOD",
    "processing_level": "L2",
    "instruments": ["olci", "slstr"],
    "gsd": [4500],
    "item_assets": {**SYN_L2_AOD_ASSETS},
}

S3_SYN_L2_VGP = {
    "id": "sentinel-3-syn-l2-vgp",
    "title": "Sentinel-3 SYN Level-2 VGP",
    "description": (
        "The Sentinel-3 Level-2 SYN VGP is a 1 km VEGETATION-Like product (~VGT-P) providing TOA reflectance."
    ),
    "product_type": "S03SYNAOD",
    "processing_level": "L2",
    "instruments": ["olci", "slstr"],
    "gsd": [1000],
    "item_assets": {**SYN_L2_VGP_ASSETS},
}

S3_SYN_L2_VG1 = {
    "id": "sentinel-3-syn-l2-vg1",
    "title": "Sentinel-3 SYN Level-2 VG1",
    "description": (
        "The Sentinel-3 Level-2 SYN VG1 is a 1 km VEGETATION-Like product (~VGT-S1) "
        "providing maximum NDVI value composite received during 1 day."
    ),
    "product_type": "S03SYNVG1",
    "processing_level": "L2",
    "instruments": ["olci", "slstr"],
    "gsd": [1000],
    "item_assets": {**SYN_L2_VG1_ASSETS},
}

S3_SYN_L2_V10 = {
    "id": "sentinel-3-syn-l2-v10",
    "title": "Sentinel-3 SYN Level-2 V10",
    "description": (
        "The Sentinel-3 Level-2 SYN V10 is a 1 km VEGETATION-Like product (~VGT-S1) "
        "providing maximum NDVI value composite received during 10 days."
    ),
    "product_type": "S03SYNV10",
    "processing_level": "L2",
    "instruments": ["olci", "slstr"],
    "gsd": [1000],
    "item_assets": {**SYN_L2_V10_ASSETS},
}

S3_SYN_L2_SYN = {
    "id": "sentinel-3-syn-l2",
    "title": "Sentinel-3 SYN Level-2",
    "description": (
        "The Sentinel-3 Level-2 SYN products provide the surface reflectance and aerosol parameters over Land."
    ),
    "product_type": "S03SYNSDR",
    "processing_level": "L2",
    "instruments": ["olci", "slstr"],
    "gsd": [300],
    "item_assets": {**SYN_L2_SYN_ASSETS},
}

# TBD: SRAL

# Conversion not supported by CPM; no mapping

S3_OLCI_L2_WFR = {
    "id": "sentinel-3-olci-l2-wfr",
    "title": "Sentinel-3 OLCI Level-2 WFR",
    "description": (
        "The Sentinel-3 OCLI Level-2 LFR product provides water and atmospheric geophysical parameters computed for full resolution."
    ),
    "product_type": "S03OLCWFR",
    "processing_level": "L2",
    "instruments": ["olci"],
    "gsd": 300,
    "item_assets": {
        PRODUCT_ASSET_KEY: get_item_asset_product(),
        PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
    },
}
