import pytest

from tests.utils import (
    check_common_metadata,
    check_metadata_asset,
    check_product_asset,
    create_stac_item_s1,
    create_test_product_spec,
)

S01SIWSLC = {
    "path": "data/converted/cpm-2.6.0/S01SIWSLC_20250130T161959_0027_A029_T406.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1A_IW_SLC__1SDV_20250130T161959_20250130T162026_057676_071BB7_3B7C",
    "baseline_version": "003.90",
}
S01SEWSLC = {
    "path": "data/converted/cpm-2.6.0/S01SEWSLC_20250410T172242_0011_C088__792.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1C_EW_SLC__1SDV_20250410T172242_20250410T172254_001834_0036A8_4DDC",
    "baseline_version": "003.91",
}
S01SSMSLC = {
    "path": "data/converted/cpm-2.6.0/S01SSMSLC_20250412T183632_0008_A030__883.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1A_SM_SLC__1SDV_20250412T183632_20250412T183641_058727_074621_04EE",
    "baseline_version": "003.91",
}
S01SWVSLC = {
    "path": "data/converted/cpm-2.6.0/S01SWVSLC_20250414T005618_0105_C136__583.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1C_WV_SLC__1SSV_20250414T005618_20250414T005803_001882_0039A3_AE9F",
    "baseline_version": None,
}
S01SSMGRH = {
    "path": "data/converted/cpm-2.6.0/S01SSMGRH_20250408T213530_0024_A149__445.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1A_SM_GRDH_1SDH_20250408T213530_20250408T213554_058671_0743C6_742E",
    "baseline_version": "003.91",
}
S01SEWGRH = {
    "path": "data/converted/cpm-2.6.0/S01SEWGRH_20250411T115021_0059_C099_T310.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1C_EW_GRDH_1SDH_20250411T115021_20250411T115121_001845_003744_2081",
    "baseline_version": "003.91",
}
S01SIWGRH = {
    "path": "data/converted/cpm-2.6.0/S01SIWGRH_20250319T002519_0024_A019__966.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1A_IW_GRDH_1SDV_20250319T002519_20250319T002544_058366_07377B_ABA5",
    "baseline_version": "003.91",
}
S01SIWOCN = {
    "path": "data/converted/cpm-2.6.0/S01SIWOCN_20250321T063156_0024_A052_T570.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1A_IW_OCN__2SDV_20250321T063156_20250321T063221_058399_0738CE_2479",
    "baseline_version": "003.91",
}
S01SEWOCN = {
    "path": "data/converted/cpm-2.6.0/S01SEWOCN_20250404T180906_0020_C001__332.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1C_EW_OCN__2SDH_20250404T180906_20250404T180927_001747_003100_31EF",
    "baseline_version": "003.91",
}
S01SSMOCN = {
    "path": "data/converted/cpm-2.6.0/S01SSMOCN_20250408T073117_0019_A140__166.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1A_SM_OCN__2SDV_20250408T073117_20250408T073136_058662_074370_9E64",
    "baseline_version": "003.91",
}
S01SWVOCN = {
    "path": "data/converted/cpm-2.6.0/S01SWVOCN_20250411T110757_0222_C098__159.zarr",
    "cpm": "2.6.0",
    "source_uri": "S1C_WV_OCN__2SSV_20250411T110757_20250411T111139_001844_00373F_489D",
    "baseline_version": "003.91",
}


@pytest.fixture(
    scope="module",
    params=[
        S01SIWSLC,
        S01SEWSLC,
        S01SSMSLC,
        S01SWVSLC,
        S01SSMGRH,
        S01SIWGRH,
        S01SEWGRH,
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
    assert len(stac_item.stac_extensions) == 6

    # -- Check processing extension
    # assert stac_item.properties.get("processing:version") == product_spec.get("baseline_version")
    assert stac_item.properties.get("processing:software").get("EOPF-CPM") is not None

    # -- Check assets
    check_product_asset(stac_item, product_spec.get("url"))
    check_metadata_asset(stac_item, product_spec.get("url"))
