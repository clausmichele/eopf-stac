import pytest

from tests.utils import (
    check_common_metadata,
    check_metadata_asset,
    check_product_asset,
    check_zipped_product_asset,
    create_stac_item_s1,
    create_test_product_spec,
)

S01SIWGRD = {
    "path": "data/converted/cpm-2.6.2/S01SIWGRD_20250319T002519_0024_A019__205.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1A_IW_GRDH_1SDV_20250319T002519_20250319T002544_058366_07377B_ABA5",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-grd",
}
S01SSMGRD = {
    "path": "data/converted/cpm-2.6.2/S01SSMGRD_20250408T213530_0024_A149__704.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1A_SM_GRDH_1SDH_20250408T213530_20250408T213554_058671_0743C6_742E",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-grd",
}
S01SEWGRD = {
    "path": "data/converted/cpm-2.6.2/S01SEWGRD_20250411T115021_0059_C099_T530.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1C_EW_GRDH_1SDH_20250411T115021_20250411T115121_001845_003744_2081",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-grd",
}
S01SWVSLC = {
    "path": "data/converted/cpm-2.6.2/S01SWVSLC_20250414T005618_0105_C136__800.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1C_WV_SLC__1SSV_20250414T005618_20250414T005803_001882_0039A3_AE9F",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-slc",
}
S01SEWSLC = {
    "path": "data/converted/cpm-2.6.2/S01SEWSLC_20250410T172242_0011_C088__493.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1C_EW_SLC__1SDV_20250410T172242_20250410T172254_001834_0036A8_4DDC",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-slc",
}
S01SSMSLC = {
    "path": "data/converted/cpm-2.6.2/S01SSMSLC_20250412T183632_0008_A030__F0D.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1A_SM_SLC__1SDV_20250412T183632_20250412T183641_058727_074621_04EE",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-slc",
}
S01SIWSLC = {
    "path": "data/converted/cpm-2.6.2/S01SIWSLC_20250130T161959_0027_A029_T031.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1A_IW_SLC__1SDV_20250130T161959_20250130T162026_057676_071BB7_3B7C",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l1-slc",
}
S01SIWOCN = {
    "path": "data/converted/cpm-2.6.2/S01SIWOCN_20250321T063156_0024_A052_T5BC.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1A_IW_OCN__2SDV_20250321T063156_20250321T063221_058399_0738CE_2479",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l2-ocn",
}
S01SEWOCN = {
    "path": "data/converted/cpm-2.6.2/S01SEWOCN_20250404T180906_0020_C001__99B.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1C_EW_OCN__2SDH_20250404T180906_20250404T180927_001747_003100_31EF",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l2-ocn",
}
S01SSMOCN = {
    "path": "data/converted/cpm-2.6.2/S01SSMOCN_20250408T073117_0019_A140__2D6.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1A_SM_OCN__2SDV_20250408T073117_20250408T073136_058662_074370_9E64",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l2-ocn",
}
S01SWVOCN = {
    "path": "data/converted/cpm-2.6.2/S01SWVOCN_20250411T110757_0222_C098__E65.zarr",
    "cpm": "2.6.2",
    "source_uri": "S1C_WV_OCN__2SSV_20250411T110757_20250411T111139_001844_00373F_489D",
    "baseline_version": "003.91",
    "collection": "sentinel-1-l2-ocn",
}


@pytest.fixture(
    scope="module",
    params=[
        S01SIWSLC,
        S01SEWSLC,
        S01SSMSLC,
        S01SWVSLC,
        S01SSMGRD,
        S01SIWGRD,
        S01SEWGRD,
        S01SIWOCN,
        S01SEWOCN,
        S01SSMOCN,
        S01SWVOCN,
    ],
)
def product_spec(request):
    return create_test_product_spec(request.param)


@pytest.fixture
def stac_item(product_spec):
    return create_stac_item_s1(product_spec)


def test_stac_item(stac_item, product_spec):
    # print(json.dumps(stac_item.to_dict(), indent=2))
    stac_item.validate()

    # -- Common metadata
    check_common_metadata(stac_item)
    assert stac_item.common_metadata.mission == "Sentinel-1"
    assert len(stac_item.common_metadata.providers) == 3
    assert stac_item.common_metadata.instruments == ["sar"]
    assert len(stac_item.stac_extensions) == 7

    # -- Check processing extension
    # assert stac_item.properties.get("processing:version") == product_spec.get("baseline_version")
    assert stac_item.properties.get("processing:software").get("EOPF-CPM") is not None

    # -- Check assets
    check_product_asset(stac_item, product_spec.get("url"))
    check_metadata_asset(stac_item, product_spec.get("url"))
    check_zipped_product_asset(stac_item)
