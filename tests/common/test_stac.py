import datetime

import pytest
from dateutil.tz import tzutc

from eopf_stac.common.stac import (
    get_datetimes,
    get_identifier_from_href,
    rearrange_bbox,
    validate_metadata,
)


class TestSTAC:
    def test_get_identifier_from_href(self):
        tests = [
            "S1A_S2_GRDH_1SDH_20250408T213530_20250408T213554_058671_0743C6_742E.SAFE",
            "S3A_OL_2_WFR____20250416T102344_20250416T102644_20250416T121904_0179_125_008_2340_MAR_O_NR_003.SEN3/",
            "S02MSIL2A_20250109T100401_0000_A122_T323.zarr",
            "s3://eopf-data/cpm_v261/S01SSMGRD_20250408T213530_0024_A149__8D6.zarr",
            "/path/to/data/converted/cpm-2.6.1/S03SLSFRP_20250512T184151_0180_A384_SBFC.zarr",
            "https://objects.eodc.eu/e05ab01a9d56408d82ac32d69a5aae2a:202507-s02msil2a/23/products/cpm_v256/S2A_MSIL2A_20250723T033201_N0511_R018_T48QUF_20250723T082115.zarr",
        ]

        for href in tests:
            identifier = get_identifier_from_href(href)
            assert identifier is not None
            assert len(identifier) > 0
            assert not identifier.endswith("/")
            assert not identifier.endswith(".zarr")
            assert not identifier.endswith(".SAFE")
            assert not identifier.endswith(".SEN3")

    def test_validate_metadata(self):
        zattrs = {".zattrs": {"stac_discovery": {}, "other_metadata": {}}}
        metadata = {"metadata": zattrs}
        assert zattrs == validate_metadata(metadata=metadata)

        with pytest.raises(ValueError):
            validate_metadata(metadata={})

        with pytest.raises(ValueError):
            validate_metadata(metadata={".zattrs": {}})

        with pytest.raises(ValueError):
            validate_metadata(metadata={".zattrs": {"stac_discovery": None}})

        with pytest.raises(ValueError):
            validate_metadata(metadata={".zattrs": {"stac_discovery": {}, "other_metadata": {}}})

    def test_rearrange_bbox(self):
        bbox = [51.794, -23.9554, 37.0764, -10.63]
        assert [37.0764, -23.9554, 51.794, -10.63] == rearrange_bbox(bbox)

    def test_get_datetimes(self):
        properties = {"datetime": "null"}
        assert (None, None, None) == get_datetimes(properties)

        properties = {"datetime": "2025-04-16T06:37:51.892834Z"}
        expected = datetime.datetime(2025, 4, 16, 6, 37, 51, 892834, tzinfo=tzutc())
        assert (expected, None, None) == get_datetimes(properties)

        properties = {"datetime": "null", "start_datetime": "2025-04-16T06:37:51.892834Z"}
        expected = datetime.datetime(2025, 4, 16, 6, 37, 51, 892834, tzinfo=tzutc())
        assert (expected, expected, None) == get_datetimes(properties)

        properties = {
            "datetime": "null",
            "start_datetime": "2025-04-16T06:37:51.892834Z",
            "end_datetime": "2025-04-16T06:40:51.892834Z",
        }
        expected_start = datetime.datetime(2025, 4, 16, 6, 37, 51, 892834, tzinfo=tzutc())
        expected_end = datetime.datetime(2025, 4, 16, 6, 40, 51, 892834, tzinfo=tzutc())
        assert (expected_start, expected_start, expected_end) == get_datetimes(properties)
