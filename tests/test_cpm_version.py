from eopf_stac.common.stac import get_cpm_version


def test_cpmversion():
    path1 = "data/converted/cpm-2.5.9/S02MSIL2A_20250109T100401_0000_A122_T808.zarr"
    path2 = "https://objects.eodc.eu/e05ab01a9d56408d82ac32d69a5aae2a:202507-s02msil2a/23/products/cpm_v256/S2A_MSIL2A_20250723T033201_N0511_R018_T48QUF_20250723T082115.zarr"
    m1 = get_cpm_version(path1)
    m2 = get_cpm_version(path2)
    m3 = get_cpm_version("path/without/cpm/version")

    assert m1 == "2.5.9"
    assert m2 == "2.5.6"
    assert m3 is None
