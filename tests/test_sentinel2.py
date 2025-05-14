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
    get_metadata,
    get_product_type,
)


def test_create_item_l1c():
    file = "tests/data-files/S02MSIL1C_20240428T102559_0000_B108_T853.json"
    url = "s3://eopf-data/S02MSIL1C_20240428T102559_0000_B108_T853.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S02MSIL1C"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate()  # fails for raster extension

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S2B_MSIL1C_20240428T102559_N0510_R108_T32UPC_20240428T123125"
    assert item.common_metadata.mission == "Sentinel-2"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["msi"]
    assert item.common_metadata.gsd == 10
    assert len(item.stac_extensions) == 12

    # -- Assets
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


def test_create_item_l2a():
    file = "tests/data-files/S02MSIL2A_20250109T100401_0000_A122_T461.json"
    url = "s3://eopf-data/S02MSIL2A_20250109T100401_0000_A122_T461.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S02MSIL2A"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate() # fails for raster extension

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

            # TODO Update test: with CPM 2.5.8 these fields should not be None!
            if key.startswith("AOT") or key.startswith("WVP"):
                assert asset.extra_fields.get("raster:scale") is None
                assert asset.extra_fields.get("raster:offset") is None

            if key.startswith("SR_"):
                assert asset.extra_fields["xarray:open_dataset_kwargs"]["engine"] == "eopf-zarr"
                assert asset.extra_fields["xarray:open_dataset_kwargs"]["op_mode"] == "native"
                assert "dataset" in asset.roles
                assert "reflectance" in asset.roles

    # -- Links
    check_license_link(item)
