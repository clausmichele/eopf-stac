import os

from eopf_stac.sentinel2.stac import calculate_proj_bbox


def test_calculate_boox():
    url = os.environ.get("EOPF_DATA_PATH")
    if url is not None:
        # pytest.fail(reason="Environment variable EOPF_DATA_PATH is not set")
        bbox = calculate_proj_bbox(url, res=10)
        assert bbox is not None
