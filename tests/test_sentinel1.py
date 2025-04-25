from eopf_stac.sentinel1.stac import create_item
from tests.utils import check_common_metadata, check_metadata_asset, check_product_asset, get_metadata, get_product_type


def test_create_item_ocn_iw():
    file = "tests/data-files/S01SIWOCN_20250321T063156_0024_a052_T356.json"
    url = "s3://eopf-data/S01SIWOCN_20250321T063156_0024_a052_T356.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S01SIWOCN"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate()  # fails for sar extension

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S1A_IW_OCN__2SDV_20250321T063156_20250321T063221_058399_0738CE_2479"
    assert item.common_metadata.mission == "Sentinel-1"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["sar"]
    assert len(item.stac_extensions) == 6

    # -- Assets
    assert len(item.assets) == 5

    check_product_asset(item, url)
    check_metadata_asset(item, url)


def test_create_item_grd_iw():
    file = "tests/data-files/S01SIWGRH_20250319T002519_0024_a019_T651.json"
    url = "s3://eopf-data/S01SIWGRH_20250319T002519_0024_a019_T651.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S01SIWGRH"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate()  # fails for sar extension

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S1A_IW_GRDH_1SDV_20250319T002519_20250319T002544_058366_07377B_ABA5"
    assert item.common_metadata.mission == "Sentinel-1"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["sar"]
    assert len(item.stac_extensions) == 6

    # -- Assets
    assert len(item.assets) == 8

    check_product_asset(item, url)
    check_metadata_asset(item, url)


def test_create_item_slc_iw():
    file = "tests/data-files/S01SIWSLC_20250130T161959_0027_a029_T298.json"
    url = "s3://eopf-data/S01SIWSLC_20250130T161959_0027_a029_T298.zarr"

    metadata = get_metadata(file)
    product_type = get_product_type(metadata)
    assert product_type == "S01SIWSLC"

    item = create_item(metadata=metadata, product_type=product_type, asset_href_prefix=url)
    # item.validate()  # fails for sar extension

    # -- Common metadata
    check_common_metadata(item)
    assert item.id == "S1A_IW_SLC__1SDV_20250130T161959_20250130T162026_057676_071BB7_3B7C"
    assert item.common_metadata.mission == "Sentinel-1"
    assert len(item.common_metadata.providers) == 3
    assert item.common_metadata.instruments == ["sar"]
    assert len(item.stac_extensions) == 6

    # -- Assets
    assert len(item.assets) == 2

    check_product_asset(item, url)
    check_metadata_asset(item, url)
