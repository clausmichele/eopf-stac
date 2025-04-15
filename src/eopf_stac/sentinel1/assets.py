import os

import pystac

from eopf_stac.constants import (
    PRODUCT_ASSET_KEY,
    PRODUCT_METADATA_ASSET_KEY,
    PRODUCT_METADATA_PATH,
    get_item_asset_metadata,
    get_item_asset_product,
)
from eopf_stac.sentinel1.constants import (
    S1_ASSET_KEY_TO_PATH,
    S1_ASSET_KEYS_FOR_POLARIZATION,
    S1_GRD_ASSETS,
    S1_OCN_ASSETS,
)


def create_grd_assets(asset_href_prefix: str, components: list[str]) -> dict[str, pystac.Asset]:
    assets = {}

    # Create assets for current polarisation
    for polarisation, product_name in components.items():
        item_asset_keys = S1_ASSET_KEYS_FOR_POLARIZATION[polarisation]
        for key in item_asset_keys:
            item_asset = S1_GRD_ASSETS.get(key)
            asset = item_asset.create_asset(os.path.join(asset_href_prefix, product_name, S1_ASSET_KEY_TO_PATH[key]))
            assets[key] = asset

    # Create product and metadata assets
    assets[PRODUCT_ASSET_KEY] = get_item_asset_product().create_asset(asset_href_prefix)
    assets[PRODUCT_METADATA_ASSET_KEY] = get_item_asset_metadata().create_asset(
        os.path.join(asset_href_prefix, PRODUCT_METADATA_PATH)
    )

    return assets


def create_slc_assets(asset_href_prefix: str, components: list[str]) -> dict[str, pystac.Asset]:
    assets = {}

    # Create assets for current swath and polarisation

    # Create product and metadata assets
    assets[PRODUCT_ASSET_KEY] = get_item_asset_product().create_asset(asset_href_prefix)
    assets[PRODUCT_METADATA_ASSET_KEY] = get_item_asset_metadata().create_asset(
        os.path.join(asset_href_prefix, PRODUCT_METADATA_PATH)
    )
    return assets


def create_ocn_assets(asset_href_prefix: str, components: list[str], instrument_mode: str) -> dict[str, pystac.Asset]:
    assets = {}

    # For WV mode the measurements data set are one per vignette. Not creating assets for each burst at the moment.
    if instrument_mode != "WV":
        # Create assets for product components (osw, owi, rvl)
        for comp_key, comp_name in components.items():
            item_asset = S1_OCN_ASSETS[comp_key.upper()]
            asset = item_asset.create_asset(
                os.path.join(asset_href_prefix, comp_key, comp_name, S1_ASSET_KEY_TO_PATH[comp_key.upper()])
            )
            assets[comp_key] = asset

    # Create product and metadata assets
    assets[PRODUCT_ASSET_KEY] = get_item_asset_product().create_asset(asset_href_prefix)
    assets[PRODUCT_METADATA_ASSET_KEY] = get_item_asset_metadata().create_asset(
        os.path.join(asset_href_prefix, PRODUCT_METADATA_PATH)
    )

    return assets
