import os

import pytest

from eopf_stac.sentinel2.stac import calculate_proj_bbox


def test_calculate_boox():
    # /localhome/wink_ma/workspace/eopf/eopf-stac/data/converted/cpm-2.6.4/S02MSIL1C_20240428T102559_0000_B108_T8EC.zarr
    # /localhome/wink_ma/workspace/eopf/eopf-stac/data/converted/cpm-2.6.2/S02MSIL1C_20240428T102559_0000_B108_T452.zarr
    # /localhome/wink_ma/workspace/eopf/eopf-stac/data/converted/cpm-2.6.2/S02MSIL2A_20250109T100401_0000_A122_TC06.zarr
    # /localhome/wink_ma/workspace/eopf/eopf-stac/data/converted/cpm-2.6.4/S02MSIL2A_20250109T100401_0000_A122_TB26.zarr
    url = os.environ.get("EOPF_DATA_PATH")
    if url is None:
        pytest.fail(reason="Environment variable EOPF_DATA_PATH is not set")

    bbox = calculate_proj_bbox(url, res=10)
    assert bbox is not None
