from eopf_stac.sentinel3.constants import OLCI_L2_ASSETS_KEY_TO_PATH, SLSTR_L1_ASSETS_KEY_TO_PATH
from eopf_stac.sentinel3.stac import create_item
from tests.utils import (
    check_common_metadata,
    check_license_link,
    check_metadata_asset,
    check_product_asset,
    get_metadata,
    get_product_type,
)


def test_create_item_olci_l2():
    file = "tests/data-files/S03OLCLFR_20250416T063751_0180_B248_T691_.json"
    url = "s3://eopf-data/S03OLCLFR_20250416T063751_0180_B248_T691_.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S03OLCLFR"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    item.validate()

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S3B_OL_2_LFR____20250416T063752_20250416T064052_20250416T083835_0179_105_248_3240_ESA_O_NR_003"
    assert item.common_metadata.mission == "Sentinel-3"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["olci"]
    assert item.common_metadata.gsd == 300
    assert len(item.stac_extensions) == 5

    # -- Assets
    assert len(item.assets) == 9

    check_product_asset(item, url)
    check_metadata_asset(item, url)

    for key, path in OLCI_L2_ASSETS_KEY_TO_PATH.items():
        asset = item.assets[key]

        if key == "lagp":
            assert len(asset.extra_fields["bands"]) == 5
        elif key == "iwv":
            assert len(asset.extra_fields["bands"]) == 2
        elif key == "gifapar":
            assert len(asset.extra_fields["bands"]) == 3
        elif key == "rc865":
            assert len(asset.extra_fields["bands"]) == 1
        elif key == "rc681":
            assert len(asset.extra_fields["bands"]) == 1
        else:
            assert asset.extra_fields.get("bands") is None

    # -- Links
    check_license_link(item)


def test_create_item_olci_l1():
    file = "tests/data-files/S03OLCEFR_20250416T063751_0180_B248_T893_.json"
    url = "s3://eopf-data/S03OLCEFR_20250416T063751_0180_B248_T893_.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S03OLCEFR"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    item.validate()

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S3B_OL_1_EFR____20250416T063752_20250416T064052_20250416T083131_0179_105_248_3240_ESA_O_NR_004"
    assert item.common_metadata.mission == "Sentinel-3"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["olci"]
    assert item.common_metadata.gsd == 300
    assert len(item.stac_extensions) == 5

    # -- Assets
    assert len(item.assets) == 24

    check_product_asset(item, url)
    check_metadata_asset(item, url)

    radiance = item.assets["radianceData"]
    assert radiance.href == f"{url}/measurements"
    assert radiance.extra_fields["xarray:open_dataset_kwargs"]["engine"] == "eopf-zarr"
    assert radiance.extra_fields["xarray:open_dataset_kwargs"]["op_mode"] == "native"
    assert len(radiance.extra_fields["bands"]) == 21

    oa01 = item.assets["Oa01_radianceData"]
    assert oa01.href == f"{url}/measurements/oa01_radiance"
    assert len(oa01.extra_fields["bands"]) == 1

    # -- Links
    check_license_link(item)


def test_create_item_slstr_l1():
    file = "tests/data-files/S03SLSRBT_20250428T081931_0180_A178_T725.json"
    url = "s3://eopf-data/S03SLSRBT_20250428T081931_0180_A178_T725.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S03SLSRBT"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    item.validate()

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S3A_SL_1_RBT____20250428T081931_20250428T082231_20250428T104108_0179_125_178_1620_PS1_O_NR_004"
    assert item.common_metadata.mission == "Sentinel-3"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["slstr"]
    assert len(item.stac_extensions) == 5

    # -- Assets
    assert len(item.assets) == 10

    check_product_asset(item, url)
    check_metadata_asset(item, url)

    for key, path in SLSTR_L1_ASSETS_KEY_TO_PATH.items():
        asset = item.assets[key]

        if key in ["radiance_an", "radiance_ao"]:
            assert len(asset.extra_fields["bands"]) == 6
            assert asset.extra_fields["gsd"] == 500
        elif key in ["radiance_bn", "radiance_bo"]:
            assert len(asset.extra_fields["bands"]) == 3
            assert asset.extra_fields["gsd"] == 500
        elif key in ["BT_in", "BT_io"]:
            assert len(asset.extra_fields["bands"]) == 4
            assert asset.extra_fields["gsd"] == 1000
        elif key in ["BT_fn", "BT_fo"]:
            assert len(asset.extra_fields["bands"]) == 1
            assert asset.extra_fields["gsd"] == 1000
        else:
            assert asset.extra_fields.get("bands") is None

    # -- Links
    check_license_link(item)


def test_create_item_slstr_l2_lst():
    file = "tests/data-files/S03SLSLST_20250428T075538_0180_B035_T196.json"
    url = "s3://eopf-data/S03SLSLST_20250428T075538_0180_B035_T196.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S03SLSLST"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    item.validate()

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S3B_SL_2_LST____20250428T075539_20250428T075839_20250428T123039_0179_106_035_2520_ESA_O_NR_004"
    assert item.common_metadata.mission == "Sentinel-3"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["slstr"]
    assert len(item.stac_extensions) == 5

    # -- Assets
    assert len(item.assets) == 3

    check_product_asset(item, url)
    check_metadata_asset(item, url)

    asset = item.assets["lst"]
    assert len(asset.extra_fields["bands"]) == 3
    assert asset.extra_fields["gsd"] == 1000

    # -- Links
    check_license_link(item)
