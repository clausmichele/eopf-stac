import json
import logging
import os
from urllib.parse import urlparse

import fsspec
import pystac
import requests
import s3fs
from pystac.utils import now_in_utc

from eopf_stac.common.constants import (
    PRODUCT_METADATA_PATH,
    PRODUCT_TYPE_TO_COLLECTION,
    SUPPORTED_PRODUCT_TYPES_S1,
    SUPPORTED_PRODUCT_TYPES_S2,
    SUPPORTED_PRODUCT_TYPES_S3,
)
from eopf_stac.common.stac import validate_metadata
from eopf_stac.sentinel1.stac import create_item as create_item_s1
from eopf_stac.sentinel2.stac import create_item as create_item_s2
from eopf_stac.sentinel3.stac import create_item as create_item_s3

logger = logging.getLogger(__name__)


def read_metadata(eopf_href: str) -> dict:
    path = os.path.join(eopf_href, PRODUCT_METADATA_PATH)
    fs = fsspec.filesystem("file")

    if eopf_href.startswith("s3://"):
        fs = s3fs.S3FileSystem(anon=False, endpoint_url=os.environ["S3_ENDPOINT_URL"])
    elif eopf_href.startswith("http"):
        o = urlparse(eopf_href)
        endpoint_url = f"{o.scheme}://{o.netloc}"
        path = os.path.join(o.path, PRODUCT_METADATA_PATH)
        fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint_url})

        # unregister handler to make boto3 work with CEPH
        handlers = fs.s3.meta.events._emitter._handlers
        handlers_to_unregister = handlers.prefix_search("before-parameter-build.s3")
        handler_to_unregister = handlers_to_unregister[0]
        fs.s3.meta.events._emitter.unregister("before-parameter-build.s3", handler_to_unregister)

    # -- open product metadata
    f = fs.open(path, "rb")
    zmetadata = json.load(f)

    return validate_metadata(zmetadata)


def create_item(metadata: dict, eopf_href: str) -> pystac.Item:
    product_type = metadata[".zattrs"]["stac_discovery"].get("properties", {}).get("product:type")
    # workaround eopf-cpm 2.4.x
    if product_type is None:
        product_type = metadata[".zattrs"]["stac_discovery"].get("properties", {}).get("eopf:type")

    if product_type is None:
        raise ValueError("No product type in stac_discovery metadata")

    logger.info(f"Product type is {product_type}")

    item = None
    if product_type in SUPPORTED_PRODUCT_TYPES_S1:
        item = create_item_s1(metadata=metadata, product_type=product_type, asset_href_prefix=eopf_href)
    elif product_type in SUPPORTED_PRODUCT_TYPES_S2:
        item = create_item_s2(metadata=metadata, product_type=product_type, asset_href_prefix=eopf_href)
    elif product_type in SUPPORTED_PRODUCT_TYPES_S3:
        item = create_item_s3(metadata=metadata, product_type=product_type, asset_href_prefix=eopf_href)
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
