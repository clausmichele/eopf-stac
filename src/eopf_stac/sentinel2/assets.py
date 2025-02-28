import os

import numpy as np
import pystac
from constants import PRODUCT_METADATA_ASSET_KEY, PRODUCT_METADATA_PATH
from pystac.extensions.raster import RasterExtension
from pystac.extensions.xarray_assets import AssetXarrayAssetsExtension
from sentinel2.constants import (
    ASSET_TO_DESCRIPTION,
    DATASET_PATHS_TO_ASSET,
    L2A_AOT_WVP_PATHS_TO_ASSET,
    L2A_SCL_PATHS_TO_ASSET,
    MEDIA_TYPE_JSON,
    MEDIA_TYPE_ZARR,
    ROLE_DATA,
    ROLE_DATASET,
    ROLE_METADATA,
    ROLE_REFLECTANCE,
    ROLE_VISUAL,
)
from stactools.sentinel2.constants import (
    BANDS_TO_ASSET_NAME,
    SENTINEL_BANDS,
)


def metadata_asset_from_href(asset_href: str) -> pystac.Asset:
    return pystac.Asset(
        href=os.path.join(asset_href, PRODUCT_METADATA_PATH),
        title="Consolidated Metadata",
        description="Consolidated metadata of the EOPF product",
        media_type=MEDIA_TYPE_JSON,
        roles=[ROLE_METADATA],
    )


def product_asset_from_href(asset_href: str, owner: pystac.Item) -> pystac.Asset:
    asset = pystac.Asset(
        href=asset_href,
        title="EOPF Product",
        description="The full Zarr hierarchy of the EOPF product",
        media_type=MEDIA_TYPE_ZARR,
        roles=[ROLE_DATA, ROLE_METADATA],
    )
    asset.set_owner(owner)
    xr = AssetXarrayAssetsExtension.ext(asset, add_if_missing=True)
    xr.open_kwargs = {"consolidated": True, "chunks": {}, "engine": "sentinel-zarr"}
    return asset


def band_assets_from_dict(asset_defs: dict, asset_href: str, metadata: dict, item: pystac.Item):
    assets = {}
    for href_suffix, key in asset_defs.items():
        asset = create_asset(asset_href, href_suffix, key, [ROLE_DATA, ROLE_REFLECTANCE])
        update_bands(asset, key)

        attrs = metadata.get(f"{href_suffix}/.zattrs")
        if attrs:
            update_extra_fields_from_metadata(asset=asset, attrs=attrs, item=item)

        assets[key] = asset

    return assets


def aot_wvp_assets_from_href(asset_href: str, metadata: dict, item: pystac.Item):
    assets = {}
    for href_suffix, key in L2A_AOT_WVP_PATHS_TO_ASSET.items():
        asset = create_asset(asset_href, href_suffix, key, [ROLE_DATA])

        attrs = metadata.get(f"{href_suffix}/.zattrs")
        if attrs:
            update_extra_fields_from_metadata(asset=asset, attrs=attrs, item=item)

        assets[key] = asset

    # data_type
    # nodata
    # raster:scale
    # raster:offset

    return assets


def scl_assets_from_href(asset_href: str, metadata: dict, item: pystac.Item):
    assets = {}
    for href_suffix, key in L2A_SCL_PATHS_TO_ASSET.items():
        # SCL can be opened as zarr group / xarray dataset -> we remove the 'scl' part of the path
        asset = create_asset(asset_href, os.path.dirname(href_suffix), key, [ROLE_DATA, ROLE_DATASET])

        attrs = metadata.get(f"{href_suffix}/.zattrs")
        if attrs:
            update_extra_fields_from_metadata(asset=asset, attrs=attrs, item=item)

        asset.set_owner(item)
        xr = AssetXarrayAssetsExtension.ext(asset, add_if_missing=True)
        xr.open_kwargs = {"consolidated": False, "chunks": {}, "engine": "zarr"}

        assets[key] = asset

    # classification:classes
    # nodata
    # data_type

    return assets


def tci_assets_from_def(asset_defs: dict, asset_href: str, metadata: dict, item: pystac.Item):
    assets = {}
    for href_suffix, key in asset_defs.items():
        asset = create_asset(asset_href, href_suffix, key, [ROLE_VISUAL])
        update_bands_from_band_keys(asset, ["B04", "B03", "B02"])

        attrs = metadata.get(f"{href_suffix}/.zattrs")
        if attrs:
            update_extra_fields_from_metadata(asset=asset, attrs=attrs, item=item)

        assets[key] = asset

    # nodata
    # data_type

    return assets


def dataset_assets_from_href(asset_href: str, metadata: dict, item: pystac.Item):
    assets = {}
    for href_suffix, key in DATASET_PATHS_TO_ASSET.items():
        asset = create_asset(asset_href, href_suffix, key, [ROLE_DATA, ROLE_REFLECTANCE, ROLE_DATASET])
        if key == "SR_10m":
            update_bands_from_band_keys(asset, ["B02", "B03", "B04", "B08"])
        elif key == "SR_20m":
            update_bands_from_band_keys(asset, ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B8A", "B11", "B12"])
        elif key == "SR_60m":
            update_bands_from_band_keys(
                asset, ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B8A", "B09", "B11", "B12"]
            )

        attrs = metadata.get(f"{href_suffix}/.zattrs")
        if attrs:
            update_extra_fields_from_metadata(asset=asset, attrs=attrs, item=item)

        asset.set_owner(item)
        xr = AssetXarrayAssetsExtension.ext(asset, add_if_missing=True)
        xr.open_kwargs = {"consolidated": False, "chunks": {}, "engine": "zarr"}

        assets[key] = asset

    # xarray
    # nodata
    # data_type

    return assets


def extra_assets_from_href(asset_href: str):
    assets = {PRODUCT_METADATA_ASSET_KEY: metadata_asset_from_href(asset_href)}
    return assets


def create_asset(href_base: str, href_suffix: str, asset_key: str, roles: list[str]):
    gsd = unsuffixed_band_resolution(asset_key)
    band_key = band_key_from_asset_key(asset_key)

    asset = pystac.Asset(
        href=os.path.join(href_base, href_suffix),
        title=f"{ASSET_TO_DESCRIPTION[band_key]} - {gsd}m",
        media_type=MEDIA_TYPE_ZARR,
        roles=roles,
    )

    asset.extra_fields["gsd"] = int(gsd)

    return asset


def update_bands(asset: pystac.Asset, asset_key: str):
    band_key = band_key_from_asset_key(asset_key)
    update_bands_from_band_keys(asset, [band_key])


def update_bands_from_band_keys(asset: pystac.Asset, keys: list[str]):
    bands = []
    for band_key in keys:
        band = SENTINEL_BANDS[BANDS_TO_ASSET_NAME[band_key]]
        band.description = f"{ASSET_TO_DESCRIPTION[band_key]}"
        bands.append(band.to_dict())

    asset.extra_fields["bands"] = bands


def band_key_from_asset_key(asset_key: str) -> str:
    # asset_key e.g. B02_10m
    parts = asset_key.split("_")
    return parts[0]


def unsuffixed_band_resolution(asset_key: str) -> str:
    # asset_key e.g. B02_10m
    parts = asset_key.split("_")
    return parts[1][:2]


def update_extra_fields_from_metadata(asset: pystac.Asset, attrs: dict, item: pystac.Item):
    if attrs.get("long_name"):
        asset.description = attrs.get("long_name")

    if attrs.get("proj:bbox"):
        asset.extra_fields["proj:bbox"] = attrs.get("proj:bbox")

    if attrs.get("proj:shape"):
        asset.extra_fields["proj:shape"] = attrs.get("proj:shape")

    if attrs.get("proj:transform"):
        asset.extra_fields["proj:transform"] = attrs.get("proj:transform")

    if attrs.get("proj:epsg"):
        asset.extra_fields["proj:code"] = f"EPSG:{attrs.get('proj:epsg')}"

    scale = attrs.get("scale_factor")
    offset = attrs.get("add_offset")
    if any([scale, offset]):
        RasterExtension.add_to(item)
        if scale:
            asset.extra_fields["raster:scale"] = attrs.get("scale_factor")
        if offset:
            asset.extra_fields["raster:offset"] = attrs.get("add_offset")

    if attrs.get("fill_value") is not None:
        asset.extra_fields["nodata"] = attrs.get("fill_value")

    if attrs.get("dtype") is not None:
        asset.extra_fields["data_type"] = str(np.dtype(attrs.get("dtype")))
