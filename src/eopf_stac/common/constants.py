from copy import deepcopy
from typing import Final

import pystac
from pystac.collection import ItemAssetDefinition
from pystac.link import Link
from pystac.provider import ProviderRole

from eopf_stac.common.eopf_xarray import EopfXarrayBackendConfig, OpMode

SUPPORTED_PRODUCT_TYPES_S1 = [
    "S01SIWGRH",
    "S01SSMGRH",
    "S01SEWGRH",
    "S01SIWSLC",
    "S01SWVSLC",
    "S01SSMSLC",
    "S01SEWSLC",
    "S01SIWOCN",
    "S01SEWOCN",
    "S01SSMOCN",
    "S01SWVOCN",
]
SUPPORTED_PRODUCT_TYPES_S2 = ["S02MSIL1C", "S02MSIL2A"]

SUPPORTED_S3_OLCI_L1_PRODUCT_TYPES = ["S03OLCEFR", "S03OLCERR"]
SUPPORTED_S3_OLCI_L2_PRODUCT_TYPES = ["S03OLCLFR"]
SUPPORTED_PRODUCT_TYPES_S3 = SUPPORTED_S3_OLCI_L1_PRODUCT_TYPES + SUPPORTED_S3_OLCI_L2_PRODUCT_TYPES

# Other Sentinen-3 product types to support
# SRAL
# SLSTR
# SYN

PRODUCT_TYPE_TO_COLLECTION: Final[dict] = {
    "S01SIWGRH": "sentinel-1-l1-grd",
    "S01SSMGRH": "sentinel-1-l1-grd",
    "S01SEWGRH": "sentinel-1-l1-grd",
    "S01SIWSLC": "sentinel-1-l1-slc",
    "S01SWVSLC": "sentinel-1-l1-slc",
    "S01SSMSLC": "sentinel-1-l1-slc",
    "S01SEWSLC": "sentinel-1-l1-slc",
    "S01SIWOCN": "sentinel-1-l2-ocn",
    "S01SEWOCN": "sentinel-1-l2-ocn",
    "S01SSMOCN": "sentinel-1-l2-ocn",
    "S01SWVOCN": "sentinel-1-l2-ocn",
    "S02MSIL1C": "sentinel-2-l1c",
    "S02MSIL2A": "sentinel-2-l2a",
    "S03OLCEFR": "sentinel-3-olci-l1-efr",
    "S03OLCERR": "sentinel-3-olci-l1-err",
    "S03OLCLFR": "sentinel-3-olci-l2-lfr",
}

MEDIA_TYPE_ZARR = "application/vnd+zarr"
MEDIA_TYPE_JSON = "application/json"

ROLE_DATA = "data"
ROLE_METADATA = "metadata"
ROLE_VISUAL = "visual"
ROLE_DATASET = "dataset"

SENTINEL_LICENSE: Final[Link] = Link(
    rel="license",
    title="Legal notice on the use of Copernicus Sentinel Data and Service Information",
    target="https://sentinel.esa.int/documents/247904/690755/Sentinel_Data_Legal_Notice",
    media_type="application/pdf",
)

LICENSE_PROVIDER: Final[pystac.Provider] = pystac.Provider(
    name="European Commission",
    roles=[ProviderRole.LICENSOR],
    url="https://commission.europa.eu/",
)

SENTINEL_PROVIDER: Final[pystac.Provider] = pystac.Provider(
    name="ESA",
    roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR],
    url="https://sentinel.esa.int/web/sentinel/missions",
)

EOPF_PROVIDER: Final[pystac.Provider] = pystac.Provider(
    name="EOPF Sentinel Zarr Samples Service",
    url="https://zarr.eopf.copernicus.eu/",
    roles=[ProviderRole.HOST, ProviderRole.PROCESSOR],
)

THUMBNAIL_ASSET: pystac.Asset = pystac.Asset(
    href="",
    title="",
    media_type="image/png",
    roles=["thumbnail"],
)

PRODUCT_METADATA_PATH: Final[str] = ".zmetadata"
PRODUCT_METADATA_ASSET_KEY: Final[str] = "product_metadata"

PRODUCT_ASSET_KEY: Final[str] = "product"
PRODUCT_ASSET_EXTRA_FIELDS: Final[dict] = {
    "xarray:open_datatree_kwargs": EopfXarrayBackendConfig(mode=OpMode.NATIVE).to_dict()
}

DATASET_ASSET_EXTRA_FIELDS: Final[dict] = {
    "xarray:open_dataset_kwargs": EopfXarrayBackendConfig(mode=OpMode.NATIVE).to_dict()
}


def get_item_asset_metadata() -> ItemAssetDefinition:
    return ItemAssetDefinition.create(
        title="Consolidated Metadata",
        description="Consolidated metadata of the EOPF product",
        media_type=MEDIA_TYPE_JSON,
        roles=[ROLE_METADATA],
    )


def get_item_asset_product():
    return ItemAssetDefinition.create(
        title="EOPF Product",
        description="The full Zarr hierarchy of the EOPF product",
        media_type=MEDIA_TYPE_ZARR,
        roles=[ROLE_DATA, ROLE_METADATA],
        extra_fields=deepcopy(PRODUCT_ASSET_EXTRA_FIELDS),
    )


PRODUCT_EXTENSION_SCHEMA_URI = "https://stac-extensions.github.io/product/v0.1.0/schema.json"
PROCESSING_EXTENSION_SCHEMA_URI = "https://stac-extensions.github.io/processing/v1.2.0/schema.json"
EOPF_EXTENSION_SCHEMA_URI = "https://cs-si.github.io/eopf-stac-extension/v1.2.0/schema.json"
