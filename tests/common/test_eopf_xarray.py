import pytest

from eopf_stac.common.eopf_xarray import EopfXarrayBackendConfig, OpMode


class TestEopfXarrayConfig:
    def test_native_mode_defaults(self):
        config = EopfXarrayBackendConfig(mode=OpMode.NATIVE).to_dict()

        assert isinstance(config, dict)
        assert config["engine"] == "eopf-zarr"
        assert config["op_mode"] == "native"
        assert config["chunks"] == {}
        with pytest.raises(KeyError):
            _ = config["bands"]
            _ = config["spatial_res"]

    def test_analysis_mode_defaults(self):
        config = EopfXarrayBackendConfig(mode=OpMode.ANALYSIS).to_dict()
        assert isinstance(config, dict)
        assert config["engine"] == "eopf-zarr"
        assert config["op_mode"] == "analysis"
        assert config["chunks"] == {}
        assert config["bands"] is None
        assert config["spatial_res"] is None

    def test_analysis_mode(self):
        config = EopfXarrayBackendConfig(mode=OpMode.ANALYSIS, bands=["b01", "b02"], spatial_res=10).to_dict()
        assert isinstance(config, dict)
        assert config["engine"] == "eopf-zarr"
        assert config["op_mode"] == "analysis"
        assert config["chunks"] == {}
        assert config["bands"] == ["b01", "b02"]
        assert config["spatial_res"] == 10

    def test_analysis_mode_edges(self):
        config = EopfXarrayBackendConfig(mode=OpMode.ANALYSIS, bands=[], spatial_res=0).to_dict()
        assert isinstance(config, dict)
        assert config["engine"] == "eopf-zarr"
        assert config["op_mode"] == "analysis"
        assert config["chunks"] == {}
        assert config["bands"] is None
        assert config["spatial_res"] is None

    def test_chunks(self):
        assert EopfXarrayBackendConfig(mode=OpMode.ANALYSIS, chunks="auto").to_dict()["chunks"] == "auto"
        assert EopfXarrayBackendConfig(mode=OpMode.ANALYSIS, chunks=None).to_dict()["chunks"] is None
        assert EopfXarrayBackendConfig(mode=OpMode.ANALYSIS, chunks=-1).to_dict()["chunks"] == -1
        assert EopfXarrayBackendConfig(mode=OpMode.ANALYSIS, chunks={}).to_dict()["chunks"] == {}
        assert EopfXarrayBackendConfig(mode=OpMode.ANALYSIS).to_dict()["chunks"] == {}
