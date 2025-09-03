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
from tests.utils import (
    check_common_metadata,
    check_license_link,
    check_metadata_asset,
    check_product_asset,
    create_stac_item_s2,
    create_test_product_spec,
)

# Specify the test products
S02MSIL1C = {
    "path": "data/converted/cpm-2.6.0/S02MSIL1C_20240428T102559_0000_B108_T781.zarr",
    "cpm": "2.6.0",
    "source_uri": "S2B_MSIL1C_20240428T102559_N0510_R108_T32UPC_20240428T123125",
    "baseline_version": "05.10",
}
S02MSIL2A = {
    "path": "data/converted/cpm-2.6.0/S02MSIL2A_20250109T100401_0000_A122_T323.zarr",
    "cpm": "2.6.0",
    "source_uri": "S2A_MSIL2A_20250109T100401_N0511_R122_T34UCE_20250109T122750",
    "baseline_version": "05.11",
}


@pytest.fixture(scope="module", params=[S02MSIL1C, S02MSIL2A])
def product_spec(request):
    return create_test_product_spec(request.param)


@pytest.fixture
def stac_item(product_spec):
    return create_stac_item_s2(product_spec)


def test_stac_item(stac_item, product_spec):
    # print(json.dumps(stac_item.to_dict(), indent=2))

    # -- Check common metadata
    check_common_metadata(stac_item)
    # assert stac_item.id == product_spec.get("stac_item_id")
    assert stac_item.common_metadata.mission == "Sentinel-2"
    assert len(stac_item.common_metadata.providers) == 3
    assert stac_item.common_metadata.instruments == ["msi"]
    assert stac_item.common_metadata.gsd == 10
    assert len(stac_item.stac_extensions) == 12

    # -- Check processing extension
    assert stac_item.properties.get("processing:version") == product_spec.get("baseline_version")
    assert stac_item.properties.get("processing:software").get("EOPF-CPM") is not None

    # -- Check eopf extension
    assert stac_item.properties.get("eopf:instrument_mode") is not None
    assert stac_item.properties.get("eopf:datatake_id") is not None

    # -- Check assets
    check_product_asset(stac_item, product_spec.get("url"))
    check_metadata_asset(stac_item, product_spec.get("url"))
    for key, asset in stac_item.assets.items():
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
    check_license_link(stac_item)

    # -- Product type specific checks
    if stac_item.properties.get("product:type") == "S02MSIL1C":
        check_l1c(item=stac_item, expected=product_spec)
    elif stac_item.properties.get("product:type") == "S02MSIL2A":
        check_l2a(item=stac_item, expected=product_spec)
    else:
        assert True


def check_l1c(item, expected):
    # -- Check eo extension
    # TODO https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/785
    assert item.properties.get("eo:cloud_cover") is not None
    assert item.properties.get("eo:snow_cover") is None

    # -- Check product extension
    assert item.properties.get("product:type") == "S02MSIL1C"

    # -- Check Assets
    assert len(item.assets) == 19
    asset_defs = [
        L1C_BAND_ASSETS_TO_PATH,
        L1C_TCI_ASSETS_TO_PATH,
    ]
    for asset_def in asset_defs:
        for key, path in asset_def.items():
            asset = item.assets[key]
            assert asset.href == expected.get("url") + "/" + path
            assert "data" in asset.roles


def check_l2a(item, expected):
    # -- Check eo extension
    # TODO https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/785
    assert item.properties.get("eo:cloud_cover") is None
    assert item.properties.get("eo:snow_cover") is not None

    # -- Check product extension
    assert item.properties.get("product:type") == "S02MSIL2A"

    # -- Assets
    assert len(item.assets) == 21
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
            assert asset.href == expected.get("url") + "/" + path
            assert "data" in asset.roles
