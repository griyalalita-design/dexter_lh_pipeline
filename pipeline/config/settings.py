SERVICE_ACCOUNT_FILE = "service_account.json"


GSHEET = {
    "tracker": {
        "url": "https://docs.google.com/spreadsheets/d/1IdZJMXcBYcD8b7WU0P6joAepfiNcNdUmh2m1fMt0A_w/edit?gid=47925641#gid=47925641",
        "sheet_id": "1IdZJMXcBYcD8b7WU0P6joAepfiNcNdUmh2m1fMt0A_w",  # ambil dari URL
        "tabs": {
            "raw_data_compile":  "Raw Data Compile",
            "movement_volume": "Movement Volume",
            "recipients": "recipients",
        },
        # Range yang di-clear saat Day 1 (sesuaikan)
        "clear_ranges": {
            "raw_data_compile": ["B6:D500", "H6:J500", "N6:P500","T6:V500","Z6:AB500","AF6:AH500","AL6:AN500","AR6:AT500","AX6:BA500", "BE6:BH500","BL6:BN500","BR6:BT500","BW6:BY16"],
            "movement_volume": ["A3:F"]
        },
    },
    "pns": {
        "url": "https://docs.google.com/spreadsheets/d/15ndhmW4gtQ14uMwMOl33IZ1iS67qQTFEaFhWr-UF7Ns/edit",
        "sheet_id": "15ndhmW4gtQ14uMwMOl33IZ1iS67qQTFEaFhWr-UF7Ns",
        "tabs": {
            "compile": "For KPI",
        },
        "columns": {
            "global_id": "Shipper ID",
            "category": "Type",
        },
    },
    "key_shipper": {
        "url": "https://docs.google.com/spreadsheets/d/1Gk_pMm40hHs1jXGTtApLMWXD00HiiRchI2MO-q1HUPQ/edit",
        "sheet_id": "1Gk_pMm40hHs1jXGTtApLMWXD00HiiRchI2MO-q1HUPQ",
        "tabs": {
            "main": "check",
        },
        "clear_range": "A2:B",
        "start_cell": "A2",
    },
    "rdo_comp": {
        "url": "https://docs.google.com/spreadsheets/d/19uPlzTog3czwphQERVpjybfOB-CTy62yftjtulgcC3g/edit",
        "sheet_id": "19uPlzTog3czwphQERVpjybfOB-CTy62yftjtulgcC3g",
        "tabs": {
            "main": "USE THIS",
            "raw_data": "Raw Data RDO",
        },
    },
    "cpp": {
        "url": "https://docs.google.com/spreadsheets/d/155VQIcpKGH9Lbd3XUOWbzCxXUTFj8l8tMnU6t1NXitw/edit",
        "sheet_id": "155VQIcpKGH9Lbd3XUOWbzCxXUTFj8l8tMnU6t1NXitw",
        "tabs": {
            "main": "USE THIS",
        },
    },
    "cs_iv_db": {
        "url": "https://docs.google.com/spreadsheets/d/13zH3d2jXEgN6tcBqlnapG-XELZsmzjNZ8HnVLgWr3Bg/edit?gid=602572585#gid=602572585",
        "sheet_id": "13zH3d2jXEgN6tcBqlnapG-XELZsmzjNZ8HnVLgWr3Bg",
        "tabs": {
            "main": "COMPILE_WAVE_UNPIV",
        },
    },
    "cs_iv_detail": {
        "url": "https://docs.google.com/spreadsheets/d/11owrtLI2CdSHQjDXODN8BtRWN0GT6rvM8ZIMObUQwYw/edit?gid=602572585#gid=602572585",
        "sheet_id": "11owrtLI2CdSHQjDXODN8BtRWN0GT6rvM8ZIMObUQwYw",
        "tabs": {
            "shopee_lazada": "Shopee Lazada",
            "key_shipper": "Key Shipper",
            "b2b_all_b2c_cc": "B2B All B2C CC"
        },
    },
    "config": {
        "sheet_id": "1RJK6GFPVrourpdF91GQ1DWuxBBn2a9_SndoyraXckZ4",
        "tabs": {
            "main": "App Password & API Keys",
        },
        "token_cell": "B2",
    },
}


METABASE_CONFIG = {
    "lh": {
        "iv_poa": {
            "url": "https://metabase.ninjavan.co/api/card/124929/query/json",
            "report_type": "lh",
            "common_params_template": [
                {"id": "d6472180-efcd-48f3-a7bb-e6210b4a32ac", "type": "date/single", "value": "end_date", "target": ["variable", ["template-tag", "exp_dep_end"]]},
                {"id": "522e86b9-f7ea-45c6-ac0a-92ab57ca33e8", "type": "string/=", "value": ["COMPLETED", "ARRIVED"], "target": ["dimension", ["template-tag", "status"]]},
                {"id": "6f7bd3bb-7a76-49ae-9f5e-ee78d1531118", "type": "date/single", "value": "start_date", "target": ["variable", ["template-tag", "exp_dep_start"]]},
            ],
            "shipper_params_template": {
                "shopee_lazada": [{"id": "327af4b4-52e1-413a-b3ae-411919069944", "type": "string/=", "value": [341107, 216977], "target": ["dimension", ["template-tag", "parent_id_coalesce"]]},],
                "key_shipper": [
                    {"id": "6a918c5e-b750-482a-a16f-739a420ac520", "type": "string/=", "value": "agg_fsbd", "target": ["dimension", ["template-tag", "shipper_id"]]},
                    {"id": "327af4b4-52e1-413a-b3ae-411919069944", "type": "string/=", "value": [7474545], "target": ["dimension", ["template-tag", "parent_id_coalesce"]]}],
                "b2b_all_b2c_cc": [{"id": "6a918c5e-b750-482a-a16f-739a420ac520", "type": "string/=", "value": "b2b_all_b2c_cc", "target": ["dimension", ["template-tag", "shipper_id"]]},],
            },
        },
        "cs_iv": {
            "url": "https://metabase.ninjavan.co/api/card/124774/query/json",
            "report_type": "lh",
            "common_params_template": [
                {"id": "07db785a-3342-4780-9da3-61d02a6b7b6a","type": "date/single","value": "end_date","target": ["variable", ["template-tag", "end_date"]],},
                {"id": "e4a256d8-bcc2-40c3-a626-14fa7b9dbd64","type": "date/single","value": "start_date","target": ["variable", ["template-tag", "start_date"]],},
                {"id": "c394ea62-23e0-4280-bea1-b833e5635471","type": "category","value": ["CROSSDOCK"],"target": ["variable", ["template-tag", "base_hub_facility_type"]],},
                {"id": "3c9c5724-3815-45e2-8643-43ad12d51005","type": "category","value": ["CROSSDOCK"],"target": ["variable", ["template-tag", "orig_hub_facility_type"]],},
            ],
            "shipper_params_template": {
                "shopee_lazada": [{"id": "586a906e-a676-432c-b1d8-dc3b098bcc3a","type": "string/contains","value": ["341107", "216977"],"target": ["dimension", ["template-tag", "sf_parent_acc_id_coalesce"]],"options": {"case-sensitive": False},},],
                "key_shipper": [{"id": "2939e663-5f31-4b48-890d-ef898ce1a0ea","type": "id","value":"agg_fsbd" ,"target": ["dimension", ["template-tag", "shipper_id"]]},
                               {"id": "586a906e-a676-432c-b1d8-dc3b098bcc3a","type": "string/contains","value": ["7474545"],"target": ["dimension", ["template-tag", "sf_parent_acc_id_coalesce"]],"options": {"case-sensitive": False}}],
                "b2b_all_b2c_cc": [{"id": "2939e663-5f31-4b48-890d-ef898ce1a0ea","type": "id","value":"b2b_all_b2c_cc" ,"target": ["dimension", ["template-tag", "shipper_id"]]}],
            },
        },
        "n0_completion": {
            "url": "https://metabase.ninjavan.co/api/card/122260/query/json",
            "report_type": "lh",
            "common_params_template": [
                {"id": "987f60d5-d9cb-4a60-ac0d-982ed5a60a2f", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_5"]]},
                {"id": "6637429a-e441-440b-b55c-0d12d4e8a187", "type": "number/=", "value": [1], "target": ["variable", ["template-tag", "exclude_xcld"]]},
                {"id": "9b12da54-2115-48ad-bb4c-a1f601f5d8f4", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_3"]]},
                {"id": "0f4ec3a3-aef7-4da6-aa53-de9b05465d08", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_7"]]},
                {"id": "9bcc17a7-e96a-4068-b3a0-0e3cc6a6b548", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_2"]]},
                {"id": "10dcf155-48f2-489d-ad91-b9375327ebe4", "type": "category", "value": ["month"], "target": ["variable", ["template-tag", "aggr"]]},
                {"id": "95aab3ce-921b-49ca-af4f-2843d926772a", "type": "date/all-options", "value": "period_str", "target": ["dimension", ["template-tag", "dest_hub_datetime"]]},
                {"id": "0e55fe86-ef1e-4cf5-b3fe-c77a76961bbe", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_4"]]},
                {"id": "0c6c599e-8675-4f20-94df-bd51ae0648b7", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_1"]]},
                {"id": "ae99fb31-181b-404f-8de7-ff6d22ccdeff", "type": "number/=", "value": [0], "target": ["variable", ["template-tag", "whitelisted_day_6"]]},
            ],
            "shipper_params_template": {
                "b2b_all_b2c_cc": [
                    {"id": "a3692197-cccd-458b-828c-9adec640d018", "type": "string/=", "value": "b2b_all_b2c_cc", "target": ["dimension", ["template-tag", "shipper_id"]]},
                    {"id": "f304224f-3506-4723-8be1-128aa5d268c3", "type": "number/=", "value": [12], "target": ["variable", ["template-tag", "cutoff_time"]]},
                ],
            },
        },
        "no_rsvn_completed_b2b_all_b2c_cc": {
            "url": "https://metabase.ninjavan.co/api/card/122256/query/json",
            "report_type": "lh",
            "common_params_template": [
                {"id": "190fb3a4-e6cb-4b4e-a78b-f4acb7cc5448", "type": "category", "value": "month", "target": ["variable", ["template-tag", "aggr"]]},
                {"id": "26473b49-9801-4240-ade1-6c07b7851c2a", "type": "date/single", "value": "start_end", "target": ["variable", ["template-tag", "start_date"]]},
                {"id": "8d72da7f-6a48-4384-a283-a1c81db37e2d", "type": "date/single", "value": "end_date", "target": ["variable", ["template-tag", "end_date"]]},
                {"id": "f1fca7d5-bddb-42ce-9771-1f17b2c6a1ec", "type": "string/=", "value": ["Linehaul Driver"], "target": ["dimension", ["template-tag", "route_driver_type"]]},
                {"id": "ecfc3da2-aca6-4303-bb42-aa3f9a21810d", "type": "string/contains", "value": ["B2BR"], "target": ["dimension", ["template-tag", "pickup_tags"]], "options": {"case-sensitive": False}},
            ],
            "shipper_params_template": {
                "b2b_all_b2c_cc": [
                    {"id": "6980e48f-126e-48d9-a0d3-da79bbd63751", "type": "string/=", "value": "b2b_all_b2c_cc", "target": ["dimension", ["template-tag", "shipper_id"]]},
                ],
            },
        },
        "shipment_compliance": {
            "url": "https://metabase.ninjavan.co/api/card/82724/query/json",
            "report_type": "lh",
            "common_params_template": [
                {"id": "71e58020-6764-cf05-040b-67d83febf1a8", "type": "string/=", "value": ["Completed", "At Transit Hub", "Closed", "Transit"], "target": ["dimension", ["template-tag", "status"]]},
                {"id": "180a98eb-40a8-6228-8e04-54d8509a818c", "type": "category", "value": ["day"], "target": ["variable", ["template-tag", "aggr"]]},
                {"id": "e2a4c28b-bfb7-f7b5-eada-261b5f755eec", "type": "string/=", "value": ["LAND_HAUL"], "target": ["dimension", ["template-tag", "shipment_type"]]},
                {"id": "9cbc5903-59a6-b2f5-d73f-3e59ffe00c02", "type": "date/all-options", "value": "period_str", "target": ["dimension", ["template-tag", "orig_shipment_close_datetime"]]},
            ],
        },
        "into_hub_compliance": {
            "url": "https://metabase.ninjavan.co/api/card/84219/query/json",
            "report_type": "lh",
            "common_params_template": [
                {"id": "36dcdc26-b630-cf67-57ca-a1e36336804b", "type": "category", "value": ["day"], "target": ["variable", ["template-tag", "aggr"]]},
                {"id": "af9f1c12-8827-6aad-418c-30fc4cca99ee", "type": "date/single", "value": "start_date", "target": ["variable", ["template-tag", "start"]]},
                {"id": "2da317e4-9fc0-13c0-2a71-059d435e64ed", "type": "date/single", "value": "end_date", "target": ["variable", ["template-tag", "end"]]},
                {"id": "82c5651d-4539-780a-1344-41c6779c502b", "type": "category", "value": ["LAND_HAUL"], "target": ["dimension", ["template-tag", "shipment_type"]]},
            ],
        },
    },
}


SCHEDULE_DAYS = [1, 2, 6, 10, 14, 15, 16]
