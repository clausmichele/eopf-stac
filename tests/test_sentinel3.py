from eopf_stac.sentinel3.constants import OLCI_L2_ASSETS_KEY_TO_PATH
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
        if key == "product":
            assert asset.href == url
            assert asset.extra_fields["xarray:open_datatree_kwargs"]["engine"] == "eopf-zarr"
            assert asset.extra_fields["xarray:open_datatree_kwargs"]["op_mode"] == "native"
        else:
            assert asset.href == url + "/" + path

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
