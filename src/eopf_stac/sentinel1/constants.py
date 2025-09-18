from copy import deepcopy
from typing import Final

import pystac
from pystac.item_assets import ItemAssetDefinition

from eopf_stac.common.constants import (
    DATASET_ASSET_EXTRA_FIELDS,
    PRODUCT_ASSET_EXTRA_FIELDS,
    PRODUCT_ASSET_KEY,
    PRODUCT_METADATA_ASSET_KEY,
    ROLE_DATA,
    ROLE_DATASET,
    ROLE_METADATA,
    get_item_asset_metadata,
    get_item_asset_product,
)

# TODO change asset key to lower
S1_OCN_ASSETS: dict[str, ItemAssetDefinition] = {
    "OSW": ItemAssetDefinition.create(
        title="Ocean Swell spectra",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "OWI": ItemAssetDefinition.create(
        title="Ocean Wind field",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "RVL": ItemAssetDefinition.create(
        title="Surface Radial Velocity",
        media_type=pystac.MediaType.ZARR,
        description=None,
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

S1_SLC_ASSETS: dict[str, ItemAssetDefinition] = {
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

S1_GRD_ASSETS: dict[str, ItemAssetDefinition] = {
    "vh": ItemAssetDefinition.create(
        title="VH Data",
        media_type=pystac.MediaType.ZARR,
        description="VH polarization backscattering coefficient, 16-bit DN.",
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "hh": ItemAssetDefinition.create(
        title="HH Data",
        media_type=pystac.MediaType.ZARR,
        description="HH polarization backscattering coefficient, 16-bit DN.",
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "hv": ItemAssetDefinition.create(
        title="HV Data",
        media_type=pystac.MediaType.ZARR,
        description="HV polarization backscattering coefficient, 16-bit DN.",
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "vv": ItemAssetDefinition.create(
        title="VV Data",
        media_type=pystac.MediaType.ZARR,
        description="VV polarization backscattering coefficient, 16-bit DN.",
        roles=[ROLE_DATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "calibration-hh": ItemAssetDefinition.create(
        title="HH Calibration",
        media_type=pystac.MediaType.ZARR,
        description=(
            "Calibration metadata including calibration information and the beta nought, "
            "sigma nought, gamma and digital number look-up tables that can be used for "
            "absolute product calibration."
        ),
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "calibration-hv": ItemAssetDefinition.create(
        title="HV Calibration",
        media_type=pystac.MediaType.ZARR,
        description=(
            "Calibration metadata including calibration information and the beta nought, "
            "sigma nought, gamma and digital number look-up tables that can be used for "
            "absolute product calibration."
        ),
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "calibration-vh": ItemAssetDefinition.create(
        title="VH Calibration",
        media_type=pystac.MediaType.ZARR,
        description=(
            "Calibration metadata including calibration information and the beta nought, "
            "sigma nought, gamma and digital number look-up tables that can be used for "
            "absolute product calibration."
        ),
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "calibration-vv": ItemAssetDefinition.create(
        title="VV Calibration",
        media_type=pystac.MediaType.ZARR,
        description=(
            "Calibration metadata including calibration information and the beta nought, "
            "sigma nought, gamma and digital number look-up tables that can be used for "
            "absolute product calibration."
        ),
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "noise-hh": ItemAssetDefinition.create(
        title="HH Noise",
        media_type=pystac.MediaType.ZARR,
        description="Estimated thermal noise look-up tables",
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "noise-hv": ItemAssetDefinition.create(
        title="HV Noise",
        media_type=pystac.MediaType.ZARR,
        description="Estimated thermal noise look-up tables",
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "noise-vh": ItemAssetDefinition.create(
        title="VH Noise",
        media_type=pystac.MediaType.ZARR,
        description="Estimated thermal noise look-up tables",
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(DATASET_ASSET_EXTRA_FIELDS),
    ),
    "noise-vv": ItemAssetDefinition.create(
        title="VV Noise",
        description="Estimated thermal noise look-up tables",
        media_type=pystac.MediaType.ZARR,
        roles=[ROLE_METADATA, ROLE_DATASET],
        extra_fields=deepcopy(PRODUCT_ASSET_EXTRA_FIELDS),
    ),
    PRODUCT_ASSET_KEY: get_item_asset_product(),
    PRODUCT_METADATA_ASSET_KEY: get_item_asset_metadata(),
}

S1_ASSET_KEY_TO_PATH: Final[dict[str, str]] = {
    "vh": "measurements",
    "hh": "measurements",
    "hv": "measurements",
    "vv": "measurements",
    "calibration-hh": "quality/calibration",
    "calibration-hv": "quality/calibration",
    "calibration-vh": "quality/calibration",
    "calibration-vv": "quality/calibration",
    "noise-hh": "quality/noise",
    "noise-hv": "quality/noise",
    "noise-vh": "quality/noise",
    "noise-vv": "quality/noise",
    "OSW": "measurements",
    "OWI": "measurements",
    "RVL": "measurements",
}

S1_ASSET_KEYS_FOR_POLARIZATION: Final[dict[str, list[str]]] = {
    "VV": ["vv", "calibration-vv", "noise-vv"],
    "VH": ["vh", "calibration-vh", "noise-vh"],
    "HH": ["hh", "calibration-hh", "noise-hh"],
    "HV": ["hv", "calibration-hv", "noise-hv"],
}

S1_PRODUCT_TYPE_MAPPING: Final[dict[str, str]] = {
    "S01SIWGRH": "IW_GRDH_1S",
    "S01SIWGRD": "IW_GRDH_1S",
    "S01SSMGRH": "SM_GRDH_1S",
    "S01SSMGRD": "SM_GRDH_1S",
    "S01SEWGRH": "EW_GRDH_1S",
    "S01SEWGRD": "EW_GRDH_1S",
    "S01SIWSLC": "IW_SLC__1S",
    "S01SIVSLC": "IW_SLC__1S",  # CPM workaround
    "S01SWVSLC": "WV_SLC__1S",
    "S01SSMSLC": "SM_SLC__1S",
    "S01SEWSLC": "EW_SLC__1S",
    "S01SIWOCN": "IW_OCN__2S",
    "S01SEWOCN": "EW_OCN__2S",
    "S01SSMOCN": "SM_OCN__2S",
    "S01SWVOCN": "WV_OCN__2S",
}

S1_GRD_PRODUCT_TYPES: Final[list[str]] = ["S01SIWGRH", "S01SSMGRH", "S01SEWGRH", "S01SIWGRD", "S01SSMGRD", "S01SEWGRD"]
S1_SLC_PRODUCT_TYPES: Final[list[str]] = ["S01SIWSLC", "S01SWVSLC", "S01SEWSLC", "S01SSMSLC", "S01SIVSLC"]
S1_OCN_PRODUCT_TYPES: Final[list[str]] = ["S01SIWOCN", "S01SEWOCN", "S01SSMOCN", "S01SWVOCN"]
