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
    CDSE_STAC_API_URL,
    PRODUCT_METADATA_PATH,
    PRODUCT_TYPE_TO_COLLECTION,
    SUPPORTED_PRODUCT_TYPES_S1,
    SUPPORTED_PRODUCT_TYPES_S2,
    SUPPORTED_PRODUCT_TYPES_S3,
)
from eopf_stac.common.stac import get_cpm_version, validate_metadata
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


def create_item(metadata: dict, eopf_href: str, source_uri: str | None) -> pystac.Item:
    # Determine product type
    product_type = metadata[".zattrs"]["stac_discovery"].get("properties", {}).get("product:type")
    # workaround eopf-cpm 2.4.x
    if product_type is None:
        product_type = metadata[".zattrs"]["stac_discovery"].get("properties", {}).get("eopf:type")
    if product_type is None:
        raise ValueError("No product type in stac_discovery metadata")
    logger.info(f"Product type is {product_type}")

    # Extract CPM version from eopf_href
    cpm_version = get_cpm_version(eopf_href)
    logger.info(f"CPM version is {cpm_version}")

    # CDSE scene id and href
    logger.info(f"Source URI is {source_uri}")
    cdse_scene_id = None
    if source_uri is not None and len(source_uri) > 0:
        cdse_scene_id = get_source_identifier(source_uri)
        logger.info(f"CDSE scene ID is {cdse_scene_id}")
    else:
        logger.warning("No reference to source product provided. Some STAC properties might not be available!")

    cdse_scene_href = None
    if cdse_scene_id is not None:
        cdse_scene_href = get_source_stac_item_url(cdse_scene_id)
        logger.info(f"CDSE STAC item URL of source scene is {cdse_scene_href}")

    if cdse_scene_href is None:
        logger.warning("No link to the original scene at CSDE will be added to the STAC item!")

    item = None
    if product_type in SUPPORTED_PRODUCT_TYPES_S1:
        item = create_item_s1(
            metadata=metadata,
            product_type=product_type,
            asset_href_prefix=eopf_href,
            cpm_version=cpm_version,
            cdse_scene_id=cdse_scene_id,
            cdse_scene_href=cdse_scene_href,
        )
    elif product_type in SUPPORTED_PRODUCT_TYPES_S2:
        item = create_item_s2(
            metadata=metadata,
            product_type=product_type,
            asset_href_prefix=eopf_href,
            cpm_version=cpm_version,
            cdse_scene_id=cdse_scene_id,
            cdse_scene_href=cdse_scene_href,
        )
    elif product_type in SUPPORTED_PRODUCT_TYPES_S3:
        item = create_item_s3(
            metadata=metadata,
            product_type=product_type,
            asset_href_prefix=eopf_href,
            cpm_version=cpm_version,
            cdse_scene_id=cdse_scene_id,
            cdse_scene_href=cdse_scene_href,
        )
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


def get_source_identifier(source_uri: str | None) -> str:
    source_identifier = None
    if source_uri is not None:
        if source_uri.endswith("/"):
            source_uri = source_uri[:-1]
        source_identifier = source_uri.split("/")[-1]
        if source_identifier.lower().endswith(".safe") or source_identifier.lower().endswith(".sen3"):
            source_identifier = os.path.splitext(source_identifier)[0]
    return source_identifier


def get_source_stac_item_url(source_scene_id: str) -> str | None:
    source_stac_item_url = None
    try:
        source_stac_item_url = get_cdse_stac_item_url(source_scene_id)
    except Exception as e:
        logger.warning(str(e))

    return source_stac_item_url


def get_cdse_stac_item_url(scene_id: str) -> str:
    # https://stac.dataspace.copernicus.eu/v1/search?ids=
    # https://stac.dataspace.copernicus.eu/v1/search?ids=S2B_MSIL1C_20240428T102559_N0510_R108_T32UPC_20240428T123125
    params = {"ids": scene_id}
    repsonse = requests.get(url=f"{CDSE_STAC_API_URL}/search", params=params)
    repsonse.raise_for_status()

    item_url = None
    item_collection_dict = repsonse.json()
    if len(item_collection_dict["features"]) > 0:
        item_dict = item_collection_dict["features"][0]
        for link in item_dict["links"]:
            rel = link.get("rel")
            if rel is not None and rel == "self":
                href = link.get("href")
                if href is not None and len(href) > 0:
                    item_url = href

    if item_url is None:
        raise ValueError(f"Failed to find STAC item for scene id {scene_id} at CDSE")

    return item_url
