# eopf-stac

Python tool to create STAC metadata for an EOPF product.

When started, it does the following:
- Opens the EOPF product from a given URL and validates it.
- Creates a STAC item with assets. The assets `href` is based on the given URL.
- Adds the STAC item to a STAC catalog. If an item with the same id already exists, it will be updated.

## Usage

The EOPF product must be referenced by an URL which must be provided as a command-line argument. Only `http(s)://`, `s3://` and `file://` URLs are supported. For debugging, a combination of the `--dry-run` and `--debug` option can be used to see the created STAC item in the logs without inserting it into a catalog.

```bash
$ python src/eopf_stac/main.py --help
usage: eopf-stac.py [-h] [--dry-run] [--debug] URL

positional arguments:
  URL         Local file path or HTTP/S3 URL to the EOPF product.

options:
  -h, --help  show this help message and exit
  --dry-run   Create STAC item only. Do not insert it into the catalog
  --debug     Enable verbose output
```

## Settings 

Additional settings need to be provided through the following environment variables:

| Variable | Description | Default |
| -------- | ----------- | ------- |
| AWS_ACCESS_KEY_ID | If an s3 URL is provided, the access key for the object storage where the EOPF product is stored. | None |
| AWS_SECRET_ACCESS_KEY | If an s3 URL is provided, the secret for the access key. | None |
| S3_ENDPOINT_URL | If an s3 URL is provided, the endpoint URL of the object storage  | None |
| STAC_API_URL | The URL of the STAC catalog to register the created STAC item  | None |
| STAC_INGEST_USER | The username to access the transaction endpoints of the STAC API with HTTP Basic Auth | None |
| STAC_INGEST_PASS | The password to access the transaction endpoints of the STAC API with HTTP Basic Auth | None |

## Docker
The tool can also be exectued with Docker. Images are available at the [Github container registry](https://github.com/EOPF-Sample-Service/eopf-stac/pkgs/container/eopf-stac/versions). It can be run as follows:

```bash
$ docker run \
    --env AWS_ACCESS_KEY_ID=value \
    --env AWS_SECRET_ACCESS_KEY=value \
    --env S3_ENDPOINT_URL=value \
    --env STAC_API_URL=value \
    --env STAC_INGEST_USER=value \
    --env STAC_INGEST_PASS=value \
    ghcr.io/eopf-sample-service/eopf-stac:0.10.0 s3://path/to/eopf.zarr
```

