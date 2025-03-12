from typing import Final

import pystac
from pystac.collection import ItemAssetDefinition
from pystac.link import Link
from pystac.provider import ProviderRole

SUPPORTED_PRODUCT_TYPES_S1 = []
SUPPORTED_PRODUCT_TYPES_S2 = ["S02MSIL1C", "S02MSIL2A"]
SUPPORTED_PRODUCT_TYPES_S3 = []

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


PRODUCT_METADATA_PATH: Final[str] = ".zmetadata"
PRODUCT_METADATA_ASSET_KEY: Final[str] = "product_metadata"
PRODUCT_ASSET_KEY: Final[str] = "product"

PRODUCT_TYPE_TO_COLLECTION: Final[dict] = {"S02MSIL1C": "sentinel-2-l1c", "S02MSIL2A": "sentinel-2-l2a"}


def get_item_asset_metadata() -> ItemAssetDefinition:
    return ItemAssetDefinition.create(
        title="Consolidated Metadata",
        description="Consolidated metadata of the EOPF product",
        media_type=MEDIA_TYPE_JSON,
        roles=[ROLE_METADATA],
    )


def get_item_asset_product():
    xarray_open_kwargs = {
        "xarray:open_kwargs": {"consolidated": True, "chunks": {}, "engine": "eopf-zarr", "mode": "sensor"}
    }
    return ItemAssetDefinition.create(
        title="EOPF Product",
        description="The full Zarr hierarchy of the EOPF product",
        media_type=MEDIA_TYPE_ZARR,
        roles=[ROLE_DATA, ROLE_METADATA],
        extra_fields=xarray_open_kwargs,
    )
