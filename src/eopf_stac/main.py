import argparse
import json
import logging
import os
from sys import exit
from typing import Optional

from eopf_stac.io import create_item, read_metadata, register_item

logger = logging.getLogger(__name__)

ENV_STAC_API_URL: str = "STAC_API_URL"
ENV_STAC_INGEST_USER: str = "STAC_INGEST_USER"
ENV_STAC_INGEST_PASS: str = "STAC_INGEST_PASS"
ENV_S3_ENDPOINT_URL: str = "S3_ENDPOINT_URL"
ENV_AWS_ACCESS_KEY_ID: str = "AWS_ACCESS_KEY_ID"
ENV_AWS_SECRET_ACCESS_KEY: str = "AWS_SECRET_ACCESS_KEY"


def configure_logging(level: int):
    logging.basicConfig(
        level=level,
        format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def validate_env(url: str, dry_run: bool, output_file: Optional[str], env):
    if url.startswith("s3://"):
        # if s3 url is provided, the credentials are required?
        missing_vars = []
        if ENV_S3_ENDPOINT_URL not in env:
            missing_vars.append(ENV_S3_ENDPOINT_URL)

        if ENV_AWS_ACCESS_KEY_ID not in env:
            missing_vars.append(ENV_AWS_ACCESS_KEY_ID)

        if ENV_AWS_SECRET_ACCESS_KEY not in env:
            missing_vars.append(ENV_AWS_SECRET_ACCESS_KEY)

        if len(missing_vars) > 0:
            raise ValueError(f"The following enviroment variables are missing: {missing_vars}")

    if not dry_run and not output_file:
        if ENV_STAC_API_URL not in env:
            raise ValueError(f"The enviroment variable {ENV_STAC_API_URL} is missing")


def exit_on_error(exit_code: int = 1):
    logger.error("Exit on error")
    exit(exit_code)


def main():
    parser = argparse.ArgumentParser("eopf-stac.py")
    parser.add_argument("URL", help="Local file path or URL to the EOPF product", type=str)
    parser.add_argument(
        "--source-uri",
        help="Reference to the original product which was input for the EOPF conversion",
        action="store",
    )
    parser.add_argument(
        "--dry-run", help="Create STAC item without trying to insert it into the catalog", action="store_true"
    )
    parser.add_argument("--output-file", help="Save the STAC item as JSON to the specified file path", type=str)
    parser.add_argument("--debug", help="Enable verbose output", action="store_true")
    args = parser.parse_args()

    if args.debug:
        configure_logging(logging.DEBUG)
    else:
        configure_logging(logging.INFO)

    try:
        validate_env(args.URL, args.dry_run, args.output_file, os.environ)

        logger.debug("Opening metadata file ...")
        metadata = read_metadata(args.URL)

        logger.info(f"Creating STAC item for {args.URL} ...")
        item = create_item(metadata=metadata, eopf_href=args.URL, source_uri=args.source_uri)
        logger.debug(json.dumps(item.to_dict(), indent=4))

        if not args.dry_run:
            if args.output_file:
                logger.info(f"Writing STAC item to {args.output_file}")
                with open(args.output_file, "w") as f:
                    json.dump(item.to_dict(), f, indent=4)
            else:
                logger.info(f"Registering STAC item to {os.environ[ENV_STAC_API_URL]}")
                item = register_item(item=item, stac_api_url=os.environ[ENV_STAC_API_URL])

    except Exception as e:
        logger.error(str(e))
        exit_on_error()


if __name__ == "__main__":
    main()
