import re
from copy import deepcopy
from re import Pattern
from typing import Final

from eopf_stac.constants import DATASET_ASSET_EXTRA_FIELDS

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

OTHER_ASSET_EXTRA_FIELDS: dict[str:dict] = {
    "alternate": {"xarray": deepcopy(DATASET_ASSET_EXTRA_FIELDS)},
}

BAND_ASSET_EXTRA_FIELDS: dict[str:dict] = {
    "alternate": {
        "xarray": {
            "xarray:open_dataset_kwargs": {
                "engine": "eopf-zarr",
                "mode": "analysis",
                "chunks": {},
                "bands": None,
                "spatial_res": None,
            },
        }
    },
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
