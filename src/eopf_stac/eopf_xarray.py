from typing import Any

from pystac.utils import StringEnum
from xarray.core.types import T_Chunks


class OpMode(StringEnum):
    """Enumerates the allows values of the eopf-zarr xarray backend "op_mode" field."""

    NATIVE = "native"
    ANALYSIS = "analysis"


class EopfXarrayBackendConfig:
    _config: dict[str, Any]

    def __init__(
        self, mode: OpMode, chunks: T_Chunks = {}, bands: list[str] | None = None, spatial_res: int | None = None
    ) -> None:
        self._config = {}
        self._config["engine"] = "eopf-zarr"
        self._config["op_mode"] = str(mode)
        self._config["chunks"] = chunks

        if bands is not None and len(bands) > 0:
            self._config["bands"] = bands
        else:
            if mode == OpMode.ANALYSIS:
                self._config["bands"] = None

        if spatial_res is not None and spatial_res > 0:
            self._config["spatial_res"] = spatial_res
        else:
            if mode == OpMode.ANALYSIS:
                self._config["spatial_res"] = None

    def to_dict(self) -> dict[str, Any]:
        return self._config
