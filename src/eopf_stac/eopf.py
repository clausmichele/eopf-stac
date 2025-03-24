import json
import logging
import os

import fsspec
import pystac
import requests
import s3fs
from constants import (
    PRODUCT_METADATA_PATH,
    PRODUCT_TYPE_TO_COLLECTION,
    SUPPORTED_PRODUCT_TYPES_S1,
    SUPPORTED_PRODUCT_TYPES_S2,
    SUPPORTED_PRODUCT_TYPES_S3,
)
from pystac.utils import now_in_utc
from sentinel1.stac import create_item as create_item_s1
from sentinel2.stac import create_item as create_item_s2

logger = logging.getLogger(__name__)


def validate_metadata(metadata: dict) -> dict:
    stac_discovery = metadata.get("metadata", {}).get(".zattrs", {}).get("stac_discovery")
    if stac_discovery is None:
        raise ValueError("JSON object 'stac_discovery' not found in .zmetadata file")

    other_metadata = metadata.get("metadata", {}).get(".zattrs", {}).get("other_metadata")
    if other_metadata is None:
        raise ValueError("JSON object 'other_metadata' not found in .zmetadata file")

    return metadata["metadata"]


def metadata_from_href(eopf_href: str) -> dict:
    fs = fsspec.filesystem("file")
    if eopf_href.startswith("s3://"):
        fs = s3fs.S3FileSystem(anon=False, endpoint_url=os.environ["S3_ENDPOINT_URL"])

    # -- open product metadata
    f = fs.open(os.path.join(eopf_href, PRODUCT_METADATA_PATH), "rb")
    zmetadata = json.load(f)

    return validate_metadata(zmetadata)


def create_item(eopf_href: str) -> pystac.Item:
    logger.info(f"Creating STAC item for {eopf_href} ...")

    logger.debug("Opening .zmetadata ...")
    metadata = metadata_from_href(eopf_href)

    product_type = metadata[".zattrs"]["stac_discovery"].get("properties", {}).get("product:type")
    # workaround eopf-cpm 2.4.x
    if product_type is None:
        product_type = metadata[".zattrs"]["stac_discovery"].get("properties", {}).get("eopf:type")

    if product_type is None:
        raise ValueError("No product type in stac_discovery metadata")

    logger.info(f"Product type is {product_type}")

    item = None

    if product_type in SUPPORTED_PRODUCT_TYPES_S1:
        item = create_item_s1(metadata=metadata, asset_href_prefix=eopf_href)
    elif product_type in SUPPORTED_PRODUCT_TYPES_S2:
        item = create_item_s2(metadata=metadata, asset_href_prefix=eopf_href)
    elif product_type in SUPPORTED_PRODUCT_TYPES_S3:
        pass
    else:
        raise ValueError(f"The product type '{product_type}' is not supported")

    logger.info("Sucessfully created STAC item")
    return item


def register_item(item: pystac.Item, stac_api_url: str) -> pystac.Item:
    logger.info(f"Inserting STAC item into catalog {stac_api_url} ...")

    product_type = item.properties["product:type"]
    collection = PRODUCT_TYPE_TO_COLLECTION.get(product_type)
    if collection is None:
        raise ValueError(f"No collection defined for product type '{product_type}'")
    else:
        item.collection_id = collection

    item.remove_links("self")
    session = requests.Session()
    if "STAC_INGEST_USER" in os.environ and "STAC_INGEST_PASS" in os.environ:
        session.auth = (os.environ["STAC_INGEST_USER"], os.environ["STAC_INGEST_PASS"])
    api_action = "inserted"
    r = session.post(f"{stac_api_url}/collections/{item.collection_id}/items", json=item.to_dict())
    if r.status_code == 409:
        # STAC item already exists -> update
        item.common_metadata.updated = now_in_utc()
        api_action = "updated"
        r = session.put(
            f"{stac_api_url}/collections/{item.collection_id}/items/{item.id}",
            json=item.to_dict(),
        )
    r.raise_for_status()

    logger.info(f"Successfully {api_action} STAC item {item.id} in collection {item.collection_id}")

    return item
