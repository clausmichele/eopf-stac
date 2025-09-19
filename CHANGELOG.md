# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.10.0] - 2025-09-??

### Added

- Add support for products converted with CPM 2.5.9, 2.6.0 and 2.6.1
- Add alternate link to corresponding STAC item at CDSE [#37](https://github.com/EOPF-Sample-Service/eopf-stac/issues/37)
- Add support for Sentinel-3 SLSTR L2 FRP product [#12](https://github.com/EOPF-Sample-Service/eopf-stac/issues/12)
- Add field `processing:version` to STAC item [#28](https://github.com/EOPF-Sample-Service/eopf-stac/issues/28)
- Add CPM version to `processing:software` field in STAC item [#31](https://github.com/EOPF-Sample-Service/eopf-stac/issues/31)
- Add `deprecated` field from [version extension](https://github.com/stac-extensions/version) to STAC item [#43](https://github.com/EOPF-Sample-Service/eopf-stac/issues/43)
- Add CLI option to provide source URI of converted product [#41](https://github.com/EOPF-Sample-Service/eopf-stac/issues/41)

### Changed

- The STAC item id will be identical to the name of the Zarr store, except the `.zarr` extension [#42](https://github.com/EOPF-Sample-Service/eopf-stac/issues/42)

### Fixed

- Add support for Sentinel-1 GRD and SLC products converted with CPM 2.6.0 [#33](https://github.com/EOPF-Sample-Service/eopf-stac/issues/33)
- Correct antimeridian and polar crossing geometries [#39](https://github.com/EOPF-Sample-Service/eopf-stac/issues/39)

## [0.9.1] - 2025-05-20

### Fixed

- Add version for package dependencies [#19](https://github.com/EOPF-Sample-Service/eopf-stac/issues/19)

## [0.9.0] - 2025-04-29

### Added

- Add support for the following Sentinel 3 OLCI products: `S03OLCEFR`, `S03OLCERR`, `S03OLCLFR`, `S03OLCLRR` [#9](https://github.com/EOPF-Sample-Service/eopf-stac/issues/9)
- Add support for the following Sentinel 3 SLSTR products: `S03SLSRBT`, `S03SLSLST` [#11](https://github.com/EOPF-Sample-Service/eopf-stac/issues/11)
- Add tests [#10](https://github.com/EOPF-Sample-Service/eopf-stac/issues/10)

## [0.8.0] - 2025-04-15

### Added

- Add support for HTTPS product URLs ([#5](https://github.com/EOPF-Sample-Service/eopf-stac/issues/5))
- Add support for Sentinel 1 instrument modes `EW`, `SM`, `WV` and corresponding EOPF product types `S01SSMGRH`, `S01SEWGRH`, `S01SWVSLC`, `S01SSMSLC`, `S01SEWSLC`, `S01SEWOCN`, `S01SSMOCN`, `S01SWVOCN` ([#7](https://github.com/EOPF-Sample-Service/eopf-stac/issues/7))

## [0.7.1] - 2025-04-14

### Fixed

- Added `xarray` dependency ([#8](https://github.com/EOPF-Sample-Service/eopf-stac/issues/8))

## [0.7.0] - 2025-04-14

### Changed

- Change name of [EOPF Xarray backend](https://github.com/EOPF-Sample-Service/xarray-eopf) parameter `mode` to `op_mode` ([#3](https://github.com/EOPF-Sample-Service/eopf-stac/issues/3))


## [0.6.0] - 2025-03-24

### Added

- Add support for Sentinel EOPF product types `S01SIWGRH`, `S01SIWSLC`, `S01SIWOCN`, `S02MSIL1C`, `S02MSIL2A`
