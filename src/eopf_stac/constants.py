from typing import Final

import pystac
from pystac.link import Link
from pystac.provider import ProviderRole

SUPPORTED_PRODUCT_TYPES_S1 = []
SUPPORTED_PRODUCT_TYPES_S2 = ["S02MSIL1C", "S02MSIL2A"]
SUPPORTED_PRODUCT_TYPES_S3 = []

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
    name="EOPF Sample Service",
    roles=[ProviderRole.PRODUCER, ProviderRole.HOST],
    url="https://eodc.eu/",
)

PRODUCT_METADATA_ASSET_KEY: Final[str] = "product_metadata"
PRODUCT_METADATA_PATH: Final[str] = ".zmetadata"
PRODUCT_ASSET_KEY: Final[str] = "product"

PRODUCT_TYPE_TO_COLLECTION: Final[dict] = {"S02MSIL1C": "sentinel-2-l1c", "S02MSIL2A": "sentinel-2-l2a"}
