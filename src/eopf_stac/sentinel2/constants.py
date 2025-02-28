import re
from re import Pattern
from typing import Final

ROLE_DATA = "data"
ROLE_METADATA = "metadata"
ROLE_REFLECTANCE = "reflectance"
ROLE_VISUAL = "visual"
ROLE_DATASET = "dataset"

MEDIA_TYPE_ZARR = "application/vnd+zarr"
MEDIA_TYPE_JSON = "application/json"

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

L2A_BAND_PATHS_TO_ASSET: Final[dict[str, str]] = {
    "measurements/reflectance/r10m/b02": "B02_10m",
    "measurements/reflectance/r10m/b03": "B03_10m",
    "measurements/reflectance/r10m/b04": "B04_10m",
    "measurements/reflectance/r10m/b08": "B08_10m",
    "measurements/reflectance/r20m/b01": "B01_20m",
    "measurements/reflectance/r20m/b02": "B02_20m",
    "measurements/reflectance/r20m/b03": "B03_20m",
    "measurements/reflectance/r20m/b04": "B04_20m",
    "measurements/reflectance/r20m/b05": "B05_20m",
    "measurements/reflectance/r20m/b06": "B06_20m",
    "measurements/reflectance/r20m/b07": "B07_20m",
    "measurements/reflectance/r20m/b8a": "B8A_20m",
    "measurements/reflectance/r20m/b11": "B11_20m",
    "measurements/reflectance/r20m/b12": "B12_20m",
    "measurements/reflectance/r60m/b01": "B01_60m",
    "measurements/reflectance/r60m/b02": "B02_60m",
    "measurements/reflectance/r60m/b03": "B03_60m",
    "measurements/reflectance/r60m/b04": "B04_60m",
    "measurements/reflectance/r60m/b05": "B05_60m",
    "measurements/reflectance/r60m/b06": "B06_60m",
    "measurements/reflectance/r60m/b07": "B07_60m",
    "measurements/reflectance/r60m/b8a": "B8A_60m",
    "measurements/reflectance/r60m/b09": "B09_60m",
    "measurements/reflectance/r60m/b11": "B11_60m",
    "measurements/reflectance/r60m/b12": "B12_60m",
}

L2A_AOT_WVP_PATHS_TO_ASSET: Final[dict[str, str]] = {
    "quality/atmosphere/r10m/aot": "AOT_10m",
    "quality/atmosphere/r20m/aot": "AOT_20m",
    "quality/atmosphere/r60m/aot": "AOT_60m",
    "quality/atmosphere/r10m/wvp": "WVP_10m",
    "quality/atmosphere/r20m/wvp": "WVP_20m",
    "quality/atmosphere/r60m/wvp": "WVP_60m",
}

L2A_SCL_PATHS_TO_ASSET: Final[dict[str, str]] = {
    "conditions/mask/l2a_classification/r20m/scl": "SCL_20m",
    "conditions/mask/l2a_classification/r60m/scl": "SCL_60m",
}

L2A_TCI_PATHS_TO_ASSET: Final[dict[str, str]] = {
    "quality/l2a_quicklook/r10m/tci": "TCI_10m",
    "quality/l2a_quicklook/r20m/tci": "TCI_20m",
    "quality/l2a_quicklook/r60m/tci": "TCI_60m",
}

DATASET_PATHS_TO_ASSET: Final[dict[str, str]] = {
    "measurements/reflectance/r10m": "SR_10m",
    "measurements/reflectance/r20m": "SR_20m",
    "measurements/reflectance/r60m": "SR_60m",
}

L1C_BANDS_PATH_TO_ASSET: Final[dict[str, str]] = {
    "measurements/reflectance/r60m/b01": "B01_60m",
    "measurements/reflectance/r10m/b02": "B02_10m",
    "measurements/reflectance/r10m/b03": "B03_10m",
    "measurements/reflectance/r10m/b04": "B04_10m",
    "measurements/reflectance/r20m/b05": "B05_20m",
    "measurements/reflectance/r20m/b06": "B06_20m",
    "measurements/reflectance/r20m/b07": "B07_20m",
    "measurements/reflectance/r10m/b08": "B08_10m",
    "measurements/reflectance/r60m/b09": "B09_60m",
    "measurements/reflectance/r60m/b10": "B10_60m",
    "measurements/reflectance/r20m/b11": "B11_20m",
    "measurements/reflectance/r20m/b12": "B12_20m",
    "measurements/reflectance/r20m/b8a": "B8A_20m",
}

L1C_TCI_PATHS_TO_ASSET: Final[dict[str, str]] = {"quality/l1c_quicklook/r10m/tci": "TCI_10m"}
