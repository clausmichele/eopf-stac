import json
import os

import fsspec
import pystac
from pystac.utils import datetime_to_str

from eopf_stac.common.constants import PRODUCT_ASSET_KEY, PRODUCT_METADATA_ASSET_KEY, PRODUCT_METADATA_PATH
from eopf_stac.common.stac import get_identifier, validate_metadata


def get_metadata(file: str) -> dict:
    cwd = os.path.abspath(os.getcwd())
    with open(os.path.join(cwd, file), mode="r", encoding="utf-8") as f:
        zmetadata = json.load(f)
        metadata = validate_metadata(zmetadata)

    assert metadata[".zattrs"]["stac_discovery"] is not None
    assert metadata[".zattrs"]["stac_discovery"]["properties"] is not None
    assert metadata[".zattrs"]["other_metadata"] is not None

    return metadata


def get_eopf_product_info(path: str):
    metadata_file = f"{path}/.zmetadata"

    fs = fsspec.filesystem("file")
    f = fs.open(metadata_file, "rb")
    zmetadata = json.load(f)
    metadata = validate_metadata(zmetadata)
    stac_discovery = metadata[".zattrs"]["stac_discovery"]
    stac_item_id = get_identifier(stac_discovery)

    eopf_id = os.path.splitext(os.path.basename(path))[0]
    eopf_product = {
        "stac_item_id": stac_item_id,
        "stac_item_file_path": os.path.join("tests", f"{eopf_id}.json"),
        "eopf_id": eopf_id,
        "metadata_file": metadata_file,
        "url": f"s3://eopf-data/{eopf_id}.zarr",
    }
    return eopf_product


def save_item_as_file_for_debugging(item, stac_item_file_path):
    with open(stac_item_file_path, mode="w", encoding="utf-8") as file:
        file.write(json.dumps(item.to_dict(), indent=2))


def get_product_type(metadata: dict) -> str:
    return metadata[".zattrs"]["stac_discovery"]["properties"]["product:type"]


def check_common_metadata(item: pystac.Item):
    assert item.datetime is not None
    assert item.geometry is not None
    assert item.bbox is not None
    assert item.common_metadata.platform is not None
    assert item.common_metadata.start_datetime is not None
    assert item.common_metadata.end_datetime is not None
    assert item.common_metadata.created is not None
    assert item.common_metadata.updated is not None
    assert item.common_metadata.created == item.common_metadata.updated
    assert item.properties["published"] == datetime_to_str(item.common_metadata.created)


def check_license_link(item: pystac.Item):
    found_license = False
    for link in item.links:
        if link.rel == "license":
            found_license = True
            assert link.target == "https://sentinel.esa.int/documents/247904/690755/Sentinel_Data_Legal_Notice"
    assert found_license


def check_product_asset(item: pystac.Item, url: str):
    product_asset = item.assets[PRODUCT_ASSET_KEY]
    assert product_asset.href == url
    assert product_asset.extra_fields["xarray:open_datatree_kwargs"]["engine"] == "eopf-zarr"
    assert product_asset.extra_fields["xarray:open_datatree_kwargs"]["op_mode"] == "native"


def check_metadata_asset(item: pystac.Item, url: str):
    product_metadata = item.assets[PRODUCT_METADATA_ASSET_KEY]
    assert product_metadata.href == f"{url}/{PRODUCT_METADATA_PATH}"
