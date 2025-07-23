import os

import pytest

from eopf_stac.sentinel2.constants import (
    DATASET_PATHS_TO_ASSET,
    L1C_BAND_ASSETS_TO_PATH,
    L1C_TCI_ASSETS_TO_PATH,
    L2A_AOT_WVP_ASSETS_TO_PATH,
    L2A_BAND_ASSETS_TO_PATH,
    L2A_SCL_ASSETS_TO_PATH,
    L2A_TCI_ASSETS_TO_PATH,
)
from eopf_stac.sentinel2.stac import create_item
from tests.utils import (
    check_common_metadata,
    check_license_link,
    check_metadata_asset,
    check_product_asset,
    get_eopf_product_info,
    get_metadata,
    get_product_type,
    save_item_as_file_for_debugging,
)


@pytest.fixture
def test_product_l1c():
    path = "data/converted/cpm-2.5.9/S02MSIL1C_20240428T102559_0000_B108_T659.zarr"
    return get_eopf_product_info(path)


@pytest.fixture
def test_product_l2a():
    path = "data/converted/cpm-2.5.9/S02MSIL2A_20250109T100401_0000_A122_T808.zarr"
    return get_eopf_product_info(path)


def test_create_item_l1c(test_product_l1c):
    test_product = test_product_l1c
    url = test_product.get("url")
    metadata = get_metadata(test_product.get("metadata_file"))

    # -- Check product type
    product_type = get_product_type(metadata)
    assert product_type == "S02MSIL1C"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate()  # fails for raster extension

    # temporally save item for debugging
    save_item_as_file_for_debugging(item, test_product.get("stac_item_file_path"))

    # -- Check common metadata
    check_common_metadata(item)
    assert item.id == test_product.get("stac_item_id")
    assert item.common_metadata.mission == "Sentinel-2"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["msi"]
    assert item.common_metadata.gsd == 10
    assert len(item.stac_extensions) == 12

    # -- Check Assets
    assert len(item.assets) == 19

    check_product_asset(item, url)
    check_metadata_asset(item, url)

    asset_defs = [
        L1C_BAND_ASSETS_TO_PATH,
        L1C_TCI_ASSETS_TO_PATH,
    ]
    for asset_def in asset_defs:
        for key, path in asset_def.items():
            asset = item.assets[key]
            assert asset.href == url + "/" + path
            assert "data" in asset.roles

            if key.startswith("SR_"):
                assert asset.extra_fields["xarray:open_dataset_kwargs"]["engine"] == "eopf-zarr"
                assert asset.extra_fields["xarray:open_dataset_kwargs"]["op_mode"] == "native"
                assert "dataset" in asset.roles
                assert "reflectance" in asset.roles

    # -- Links
    check_license_link(item)

    # Remove debugging file when test succeeded
    os.remove(test_product.get("stac_item_file_path"))


def test_create_item_l2a(test_product_l2a):
    test_product = test_product_l2a
    url = test_product.get("url")
    metadata = get_metadata(test_product.get("metadata_file"))

    product_type = get_product_type(metadata)
    assert product_type == "S02MSIL2A"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate() # fails for raster extension

    # temporally save item for debugging
    save_item_as_file_for_debugging(item, test_product.get("stac_item_file_path"))

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S2A_MSIL2A_20250109T100401_N0511_R122_T34UCE_20250109T122750"
    assert item.common_metadata.mission == "Sentinel-2"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["msi"]
    assert item.common_metadata.gsd == 10
    assert len(item.stac_extensions) == 12

    # -- Assets
    assert len(item.assets) == 21

    check_product_asset(item, url)
    check_metadata_asset(item, url)

    asset_defs = [
        L2A_BAND_ASSETS_TO_PATH,
        L2A_AOT_WVP_ASSETS_TO_PATH,
        L2A_SCL_ASSETS_TO_PATH,
        L2A_TCI_ASSETS_TO_PATH,
        DATASET_PATHS_TO_ASSET,
    ]
    for asset_def in asset_defs:
        for key, path in asset_def.items():
            asset = item.assets[key]
            assert asset.href == url + "/" + path
            assert "data" in asset.roles

            if key.startswith("B"):
                assert asset.extra_fields.get("raster:scale") is not None
                assert asset.extra_fields.get("raster:offset") is not None

            if key.startswith("AOT") or key.startswith("WVP"):
                assert asset.extra_fields.get("raster:scale") is not None
                assert asset.extra_fields.get("raster:offset") is not None

            if key.startswith("SR_"):
                assert asset.extra_fields["xarray:open_dataset_kwargs"]["engine"] == "eopf-zarr"
                assert asset.extra_fields["xarray:open_dataset_kwargs"]["op_mode"] == "native"
                assert "dataset" in asset.roles
                assert "reflectance" in asset.roles

    # -- Links
    check_license_link(item)

    # Remove debugging file when test succeeded
    os.remove(test_product.get("stac_item_file_path"))
