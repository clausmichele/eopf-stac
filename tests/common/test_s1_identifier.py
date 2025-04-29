from eopf_stac.sentinel1.stac import construct_identifier_s1


class TestSentinel1Identifier:
    def test_product_name_s1(self):
        grd_expected_identifier = "S1A_IW_GRDH_1SDV_20250319T002519_20250319T002544_058366_07377B_ABA5"
        grd_args = {
            "product_type": "S01SIWGRH",
            "polarization": ["VV", "VH"],
            "startTime": "2025-03-19T00:25:19.166197Z",
            "endTime": "2025-03-19T00:25:44.165074Z",
            "platform": "sentinel-1a",
            "orbit": 58366,
            "component": "S01SIWGRD_20250319T002519_0025_A334_ABA5_07377B_VH",
        }

        slc_iw_expected_identifier = "S1A_IW_SLC__1SDV_20250130T161959_20250130T162026_057676_071BB7_3B7C"
        slc_iw_args = {
            "product_type": "S01SIWSLC",
            "polarization": ["VV", "VH"],
            "startTime": "2025-01-30T16:19:59.443577Z",
            "endTime": "2025-01-30T16:20:26.529642Z",
            "platform": "sentinel-1a",
            "orbit": 57676,
            "component": "S01SIWSLC_20250130T161959_0027_A330_3B7C_071BB7_VH_IW1_604570",
        }

        slc_wv_expected_identifier = "S1C_WV_SLC__1SSV_20250414T005618_20250414T005803_001882_0039A3_AE9F"
        slc_wv_args = {
            "product_type": "S01SWVSLC",
            "polarization": ["VV"],
            "startTime": "2025-04-14T00:56:18.175594Z",
            "endTime": "2025-04-14T00:58:03.656057Z",
            "platform": "sentinel-1c",
            "orbit": 1882,
            "component": "S01SWVSLC_20250414T005618_0105_C011_AE9F_0039A3_VV_WV1_001",
        }

        ocn_expected_identifier = "S1A_IW_OCN__2SDV_20250321T063156_20250321T063221_058399_0738CE_2479"
        ocn_args = {
            "product_type": "S01SIWOCN",
            "polarization": None,
            "startTime": "2025-03-21T06:31:56.675155Z",
            "endTime": "2025-03-21T06:32:21.673897Z",
            "platform": "sentinel-1a",
            "orbit": 58399,
            "component": "S01SIWOCN_20250321T063156_0025_A334_2479_0738CE_VV",
        }

        ocn_ew_hh_expected_identifier = "S1C_EW_OCN__2SDH_20250404T180906_20250404T180927_001747_003100_31EF"
        ocn_ew_hh_args = {
            "product_type": "S01SEWOCN",
            "polarization": None,
            "startTime": "2025-04-04T18:09:06.863005Z",
            "endTime": "2025-04-04T18:09:27.763186Z",
            "platform": "sentinel-1c",
            "orbit": 1747,
            "component": "S01SEWOCN_20250404T180906_0021_C010_31EF_003100_HH",
        }

        ocn_ew_dv_expected_identifier = "S1C_EW_OCN__2SDV_20250404T180906_20250404T180927_001747_003100_31EF"
        ocn_ew_dv_args = {
            "product_type": "S01SEWOCN",
            "polarization": None,
            "startTime": "2025-04-04T18:09:06.863005Z",
            "endTime": "2025-04-04T18:09:27.763186Z",
            "platform": "sentinel-1c",
            "orbit": 1747,
            "component": "S01SEWOCN_20250404T180906_0021_C010_31EF_003100_VV",
        }

        # ocn_sm_vv_expected_identifier = "S1A_S4_OCN__2SDV_20250408T073117_20250408T073136_058662_074370_9E64"
        ocn_sm_vv_expected_identifier = "S1A_SM_OCN__2SDV_20250408T073117_20250408T073136_058662_074370_9E64"
        ocn_sm_vv_args = {
            "product_type": "S01SSMOCN",
            "polarization": None,
            "startTime": "2025-04-08T07:31:17.537272Z",
            "endTime": "2025-04-08T07:31:36.699804Z",
            "platform": "sentinel-1a",
            "orbit": 58662,
            "component": "S01SS4OCN_20250408T073117_0019_A335_9E64_074370_VV",
        }

        tests = {
            grd_expected_identifier: grd_args,
            slc_iw_expected_identifier: slc_iw_args,
            slc_wv_expected_identifier: slc_wv_args,
            ocn_expected_identifier: ocn_args,
            ocn_ew_hh_expected_identifier: ocn_ew_hh_args,
            ocn_ew_dv_expected_identifier: ocn_ew_dv_args,
            ocn_sm_vv_expected_identifier: ocn_sm_vv_args,
        }

        # create identifier
        for expected_identifier, args in tests.items():
            constructed_identifier = construct_identifier_s1(**args)
            print(constructed_identifier)
            print(expected_identifier)
            assert constructed_identifier == expected_identifier
