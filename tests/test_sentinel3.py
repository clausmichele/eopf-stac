import pytest

from eopf_stac.common.constants import (
    SUPPORTED_S3_OLCI_L1_PRODUCT_TYPES,
    SUPPORTED_S3_OLCI_L2_PRODUCT_TYPES,
    SUPPORTED_S3_SLSTR_L1_PRODUCT_TYPES,
    SUPPORTED_S3_SLSTR_L2_FRP_PRODUCT_TYPE,
    SUPPORTED_S3_SLSTR_L2_LST_PRODUCT_TYPE,
)
from eopf_stac.sentinel3.constants import OLCI_L2_ASSETS_KEY_TO_PATH, SLSTR_L1_ASSETS_KEY_TO_PATH
from tests.utils import (
    check_common_metadata,
    check_license_link,
    check_metadata_asset,
    check_product_asset,
    create_stac_item_s3,
    create_test_product_spec,
)

S03OLCEFR = {
    "path": "data/converted/cpm-2.5.9/S03OLCEFR_20250416T063751_0180_B248_T673.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3B_OL_1_EFR____20250416T063752_20250416T064052_20250416T083131_0179_105_248_3240_ESA_O_NR_004",
    "baseline_version": "03.50",
}
S03OLCERR = {
    "path": "data/converted/cpm-2.5.9/S03OLCERR_20250424T055918_2658_B362_S338.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3B_OL_1_ERR____20250424T055919_20250424T064337_20250425T063838_2658_105_362______ESA_O_NT_004",
    "baseline_version": "03.50",
}
S03OLCLFR = {
    "path": "data/converted/cpm-2.5.9/S03OLCLFR_20250416T063751_0180_B248_T845.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3B_OL_2_LFR____20250416T063752_20250416T064052_20250416T083835_0179_105_248_3240_ESA_O_NR_003",
    "baseline_version": "03.50",
}
S03OLCLRR = {
    "path": "data/converted/cpm-2.5.9/S03OLCLRR_20250424T023721_2657_B360_T875.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3B_OL_2_LRR____20250424T023722_20250424T032139_20250424T052327_2657_105_360______ESA_O_NR_003",
    "baseline_version": "03.50",
}
S03SLSFRP = {
    "path": "data/converted/cpm-2.5.9/S03SLSFRP_20250512T184151_0180_A384_S368.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3A_SL_2_FRP____20250512T184152_20250512T184452_20250514T064410_0180_125_384_0360_PS1_O_NT_004",
    "baseline_version": "03.50",
}
S03SLSLST = {
    "path": "data/converted/cpm-2.5.9/S03SLSLST_20250428T075538_0180_B035_T508.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3B_SL_2_LST____20250428T075539_20250428T075839_20250428T123039_0179_106_035_2520_ESA_O_NR_004",
    "baseline_version": "03.50",
}
S03SLSRBT = {
    "path": "data/converted/cpm-2.5.9/S03SLSRBT_20250428T081931_0180_A178_T503.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "S3A_SL_1_RBT____20250428T081931_20250428T082231_20250428T104108_0179_125_178_1620_PS1_O_NR_004",
    "baseline_version": "03.50",
}
S03SYNAOD = {
    "path": "data/converted/cpm-2.5.9/S03SYNAOD_20250428T095601_2659_A179_S845.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "",
    "baseline_version": "03.50",
}
S03SYNSDR = {
    "path": "data/converted/cpm-2.5.9/S03SYNSDR_20250427T103841_0180_A165__415.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "",
    "baseline_version": "03.50",
}
S03SYNV10 = {
    "path": "data/converted/cpm-2.5.9/S03SYNV10_20250411T000000_9999_A000__855.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "",
    "baseline_version": "03.50",
}
S03SYNVG1 = {
    "path": "data/converted/cpm-2.5.9/S03SYNVG1_20250427T000000_9999_A000_S847.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "",
    "baseline_version": "03.50",
}
S03SYNVGP = {
    "path": "data/converted/cpm-2.5.9/S03SYNVGP_20250428T081502_2659_A178_S225.zarr",
    "cpm": "2.5.9",
    "stac_item_id": "",
    "baseline_version": "03.50",
}


@pytest.fixture(
    scope="module",
    params=[
        S03OLCEFR,
        S03OLCERR,
        S03OLCLFR,
        S03OLCLRR,
        S03SLSFRP,
        S03SLSLST,
        S03SLSRBT,
        # S03SYNAOD,
        # S03SYNSDR,
        # S03SYNV10,
        # S03SYNVG1,
        # S03SYNVGP,
    ],
)
def product_spec(request):
    return create_test_product_spec(request.param)


@pytest.fixture
def stac_item(product_spec):
    return create_stac_item_s3(product_spec)


def test_stac_item(stac_item, product_spec):
    # print(json.dumps(stac_item.to_dict(), indent=2))
    stac_item.validate()

    # -- Check common metadata
    check_common_metadata(stac_item)
    assert stac_item.id == product_spec.get("stac_item_id")
    assert stac_item.common_metadata.mission == "Sentinel-3"
    assert len(stac_item.common_metadata.providers) == 3
    assert len(stac_item.stac_extensions) == 5

    # -- Check processing extension
    assert stac_item.properties.get("processing:version") == product_spec.get("baseline_version")
    assert stac_item.properties.get("processing:software").get("EOPF-CPM") is not None

    # -- Check eopf extension
    # TODO cpm issue
    assert stac_item.properties.get("eopf:instrument_mode") is None

    # -- Check assets
    check_product_asset(stac_item, product_spec.get("url"))
    check_metadata_asset(stac_item, product_spec.get("url"))

    # -- Check links
    check_license_link(stac_item)

    # -- Product type specific checks
    if stac_item.properties.get("product:type") in SUPPORTED_S3_OLCI_L1_PRODUCT_TYPES:
        check_olci_l1(item=stac_item)
    elif stac_item.properties.get("product:type") in SUPPORTED_S3_OLCI_L2_PRODUCT_TYPES:
        check_olci_l2(item=stac_item)
    elif stac_item.properties.get("product:type") in SUPPORTED_S3_SLSTR_L1_PRODUCT_TYPES:
        check_slstr_l1(item=stac_item)
    elif stac_item.properties.get("product:type") == SUPPORTED_S3_SLSTR_L2_LST_PRODUCT_TYPE:
        check_slstr_l2_lst(item=stac_item)
    elif stac_item.properties.get("product:type") == SUPPORTED_S3_SLSTR_L2_FRP_PRODUCT_TYPE:
        check_slstr_l2_frp(item=stac_item)
    else:
        assert True


def check_olci_l2(item):
    assert item.common_metadata.instruments == ["olci"]

    # -- Assets
    assert len(item.assets) == 9

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


def check_olci_l1(item):
    assert item.common_metadata.instruments == ["olci"]

    # -- Assets
    assert len(item.assets) == 24

    radiance = item.assets["radianceData"]
    assert "dataset" in radiance.roles
    # assert radiance.href == f"{url}/measurements"
    assert radiance.extra_fields["xarray:open_dataset_kwargs"]["engine"] == "eopf-zarr"
    assert radiance.extra_fields["xarray:open_dataset_kwargs"]["op_mode"] == "native"
    assert len(radiance.extra_fields["bands"]) == 21

    oa01 = item.assets["Oa01_radianceData"]
    # assert oa01.href == f"{url}/measurements/oa01_radiance"
    assert len(oa01.extra_fields["bands"]) == 1


def check_slstr_l1(item):
    assert item.common_metadata.instruments == ["slstr"]

    # -- Assets
    assert len(item.assets) == 10

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


def check_slstr_l2_lst(item):
    assert item.common_metadata.instruments == ["slstr"]
    assert item.common_metadata.gsd == 300

    # -- Assets
    assert len(item.assets) == 3

    asset = item.assets["lst"]
    assert len(asset.extra_fields["bands"]) == 3
    assert asset.extra_fields["gsd"] == 1000
    assert "dataset" in asset.roles


def check_slstr_l2_frp(item):
    assert item.common_metadata.instruments == ["slstr"]
    assert stac_item.common_metadata.gsd == 300

    # -- Assets
    assert len(item.assets) == 3
