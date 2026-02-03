import pytest

from eopf_stac.main import validate_env


class TestEnvValidation:
    def test_stac_api_url(self):
        # if dry run, STAC_API_URL not required
        try:
            validate_env("", True, output_file=None, env={})
        except Exception as e:
            pytest.fail(f"Unexpected error {e}")

        # if not dry run and not output_file, STAC_API_URL is required
        with pytest.raises(ValueError):
            validate_env("", False, output_file=None, env={})

    def test_s3_url(self):
        # if s3 url provided, the credentials are required
        url = "s3://test"
        env = {"STAC_API_URL": ""}
        # env = {"STAC_API_URL": "", "S3_ENDPOINT_URL": "", "AWS_ACCESS_KEY_ID": "", "AWS_SECRET_ACCESS_KEY": ""}
        with pytest.raises(ValueError):
            validate_env(url, False, output_file=None, env=env)
