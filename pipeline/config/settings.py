# ============================================================
# settings.py — Semua konfigurasi pipeline ada di sini
# Kamu cukup update file ini aja, ga perlu utak-atik file lain
# ============================================================

# ── Google Service Account ───────────────────────────────────
# Letakkan file JSON service account kamu di root project
# lalu isi nama file-nya di sini
SERVICE_ACCOUNT_FILE = "service_account.json"

# ── Google Sheets Links ──────────────────────────────────────
GSHEET = {
    # Tracker utama (tempat dump semua data performance)
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
            "raw_data_compile": ["A6:D500", "G6:J500", "M6:P500","S6:V500","Y6:AB500","AE6:AH500","AK6:AN500","AQ6:AT500","AW6:BA500", "BD6:BH500","BK6:BM500","BP6:BR500","BU6:BW16"],
            "movement_volume": ["A3:F"]
        },
    },
    

 # Gsheet PNS - sumber list shipper (JANGAN diedit, read only)
    "pns": {
        "url": "https://docs.google.com/spreadsheets/d/15ndhmW4gtQ14uMwMOl33IZ1iS67qQTFEaFhWr-UF7Ns/edit?gid=218596977#gid=218596977",
        "sheet_id": "15ndhmW4gtQ14uMwMOl33IZ1iS67qQTFEaFhWr-UF7Ns",
        "tabs": {
            "compile": "For KPI",
        },
        # Kolom yang diambil dari PNS (sesuaikan)
        "columns": {
            "global_id": "Shipper ID",
            "category": "Type",
        },
    },

    # Gsheet Key Shipper milik BI , copy dari PNS
    "key_shipper": {
        "url": "https://docs.google.com/spreadsheets/d/1Gk_pMm40hHs1jXGTtApLMWXD00HiiRchI2MO-q1HUPQ/edit?gid=1784764051#gid=1784764051",
        "sheet_id": "1Gk_pMm40hHs1jXGTtApLMWXD00HiiRchI2MO-q1HUPQ",
        "tabs": {
            "main": "check",
        },
        # Range yang di-clear sebelum update Key Shipper
        "clear_range": "A2:B",
        # Start cell untuk tulis data
        "start_cell": "A2",
    },

    # Gsheet RDO dari tim PSP
    "rdo_comp": {
        "url": "https://docs.google.com/spreadsheets/d/19uPlzTog3czwphQERVpjybfOB-CTy62yftjtulgcC3g/edit?gid=0#gid=0",
        "sheet_id": "19uPlzTog3czwphQERVpjybfOB-CTy62yftjtulgcC3g",
        "tabs": {
            "main": "USE THIS",
            "raw_data": "Raw Data RDO"# sesuaikan nama tab
        }


    # Gsheet CPP dari tim PSP
    "cpp": {
        "url": "https://docs.google.com/spreadsheets/d/155VQIcpKGH9Lbd3XUOWbzCxXUTFj8l8tMnU6t1NXitw/edit?gid=0#gid=0",
        "sheet_id": "155VQIcpKGH9Lbd3XUOWbzCxXUTFj8l8tMnU6t1NXitw",
        "tabs": {
            "main": "USE THIS", # sesuaikan nama tab
        }
    },


    # Gsheet config — tempat kamu simpen Metabase token
    "config": {
        "sheet_id": "1RJK6GFPVrourpdF91GQ1DWuxBBn2a9_SndoyraXckZ4",
        "tabs": {
            "main": "App Password & API Keys",  # nama tab tempat token disimpen
        },
        "token_cell": "B2",  # cell tempat token Metabase
    }
}
# ── Metabase ─────────────────────────────────────────────────
METABASE_CONFIG = {
    "lm": {
        "iv_poa": {
            "url": "https://metabase.ninjavan.co/api/card/123978/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"d6472180-efcd-48f3-a7bb-e6210b4a32ac","type":"date/single","value":"end_date","target":["variable",["template-tag", "exp_dep_end"]]},
                {"id":"522e86b9-f7ea-45c6-ac0a-92ab57ca33e8","type":"string/=","value":["COMPLETED", "ARRIVED"],"target":["variable",["dimension", ["template-tag", "status"]]]},
                {"id":"6f7bd3bb-7a76-49ae-9f5e-ee78d1531118","type":"date/single","value":"start_date","target":["variable",["template-tag", "exp_dep_start"]]},
                {"id":"e8a405ca-e034-4f56-a4ca-6f454452a5ce","type":"string/=","value":["LAND_HAUL"],"target":["dimension", ["template-tag", "movement_type"]]},
            
            ],
            "shipper_params_template": {
                "agg_fsbd": [
                    {"id":"054d3fb3-9f04-4d21-a56d-5f046d53281a","type":"string/=","value": "agg_fsbd","target":["dimension",["template-tag","shipper_id"]]},

                ],
                "b2b_all_b2c_cc": [
                    {"id":"054d3fb3-9f04-4d21-a56d-5f046d53281a","type":"string/=","value": "b2b_all_b2c_cc","target":["dimension",["template-tag","shipper_id"]]},
        
                ],
                "laz_shop_tt": [
                    {"id":"6d243afd-9693-4b71-bd9d-43ba83ae3112","type":"string/=","value":[341107,216977],"target":["dimension",["template-tag","parent_id"]]},

                ],
            },
          },  

        "n0_completion": {
            "url": "https://metabase.ninjavan.co/api/card/122260/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"987f60d5-d9cb-4a60-ac0d-982ed5a60a2f","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_5"]]},
                # {"id":"f304224f-3506-4723-8be1-128aa5d268c3","type":"number/=","value":[15],"target":["variable",["template-tag","cutoff_time"]]},
                {"id":"6637429a-e441-440b-b55c-0d12d4e8a187","type":"number/=","value":[1],"target":["variable",["template-tag","exclude_xcld"]]},
                {"id":"9b12da54-2115-48ad-bb4c-a1f601f5d8f4","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_3"]]},
                {"id":"0f4ec3a3-aef7-4da6-aa53-de9b05465d08","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_7"]]},
                {"id":"9bcc17a7-e96a-4068-b3a0-0e3cc6a6b548","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_2"]]},
                # {"id":"a3692197-cccd-458b-828c-9adec640d018","type":"string/=","value":[11043556,7127997,11377124,11501029,11347236,11545390,11347234,11578061,11006103,10748293],"target":["dimension",["template-tag","shipper_id"]]},
                {"id":"10dcf155-48f2-489d-ad91-b9375327ebe4","type":"category","value":["month"],"target":["variable",["template-tag","aggr"]]},
                {"id":"95aab3ce-921b-49ca-af4f-2843d926772a","type":"date/all-options","value":"period_str","target":["dimension",["template-tag","dest_hub_datetime"]]},
                {"id":"0e55fe86-ef1e-4cf5-b3fe-c77a76961bbe","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_4"]]},
                {"id":"0c6c599e-8675-4f20-94df-bd51ae0648b7","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_1"]]},
                {"id":"ae99fb31-181b-404f-8de7-ff6d22ccdeff","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_6"]]}
            ],
            "shipper_params_template": {
                "b2b_all_b2c_cc": [
                    {"id":"a3692197-cccd-458b-828c-9adec640d018","type":"string/=","value":"b2b_all_b2c_cc","target":["dimension",["template-tag","shipper_id"]]},
                    {"id":"f304224f-3506-4723-8be1-128aa5d268c3","type":"number/=","value":[12],"target":["variable",["template-tag","cutoff_time"]]},
                ],
                "b2b_dry_cc_next": [
                    {"id":"a3692197-cccd-458b-828c-9adec640d018","type":"string/=","value":"b2b_dry_cc_next","target":["dimension",["template-tag","shipper_id"]]},
                    {"id":"f304224f-3506-4723-8be1-128aa5d268c3","type":"number/=","value":[15],"target":["variable",["template-tag","cutoff_time"]]},
                ],
                "tt": [
                    {"id":"8cc079bf-483f-4ff4-bb30-8504ee5f8d16","type":"string/=","value":[7474545],"target":["dimension",["template-tag","parent_id"]]},
                    {"id":"f304224f-3506-4723-8be1-128aa5d268c3","type":"number/=","value":[15],"target":["variable",["template-tag","cutoff_time"]]},
                ],
            },
        },

        "n1_completion": {
            "url": "https://metabase.ninjavan.co/api/card/122260/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"987f60d5-d9cb-4a60-ac0d-982ed5a60a2f","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_5"]]},
                {"id":"f304224f-3506-4723-8be1-128aa5d268c3","type":"number/=","value":[15],"target":["variable",["template-tag","cutoff_time"]]},
                {"id":"6637429a-e441-440b-b55c-0d12d4e8a187","type":"number/=","value":[1],"target":["variable",["template-tag","exclude_xcld"]]},
                {"id":"9b12da54-2115-48ad-bb4c-a1f601f5d8f4","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_3"]]},
                {"id":"0f4ec3a3-aef7-4da6-aa53-de9b05465d08","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_7"]]},
                {"id":"9bcc17a7-e96a-4068-b3a0-0e3cc6a6b548","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_2"]]},
                {"id":"10dcf155-48f2-489d-ad91-b9375327ebe4","type":"category","value":["month"],"target":["variable",["template-tag","aggr"]]},
                {"id":"95aab3ce-921b-49ca-af4f-2843d926772a","type":"date/all-options","value":"period_str","target":["dimension",["template-tag","dest_hub_datetime"]]},
                {"id":"0e55fe86-ef1e-4cf5-b3fe-c77a76961bbe","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_4"]]},
                {"id":"0c6c599e-8675-4f20-94df-bd51ae0648b7","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_1"]]},
                {"id":"ae99fb31-181b-404f-8de7-ff6d22ccdeff","type":"number/=","value":[0],"target":["variable",["template-tag","whitelisted_day_6"]]},
                {"id":"9a4ba0ba-f4ec-4212-b8d0-63505d846bc9","type":"number/=","value":[1],"target":["variable",["template-tag","4pl_flag"]]}
            ]
        },
      
        "completion_within_timeslot": {
            "url": "https://metabase.ninjavan.co/api/card/124081/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"370cf3c3-3e21-4af9-98f4-58ddce2fb3cc","type":"string/=","value":"b2b_sds_dry_cold_prem","target":["dimension",["template-tag","sds_instant"]]},
                {"id":"45c4636d-b5ea-4e91-ac1c-d39eb785f808","type":"string/=","value":"b2b_sds_dry_cold_reg","target":["dimension",["template-tag","sds_reg"]]},
                {"id":"8837dec8-26c8-41f8-9016-2bf6f9eaa178","type":"date/single","value":"start_date","target":["variable",["template-tag","start"]]},
                {"id":"952ddad7-da28-44ef-bb00-f20871d02a55","type":"date/single","value":"end_date","target":["variable",["template-tag","end"]]},
                {"id":"786ee2aa-67f6-4494-b153-0c999b0080eb","type":"category","value":["month"],"target":["variable", ["template-tag", "aggr"]]}
            ],
        },

        "lnd_b2b_all_b2c_cc": {
            "url": "https://metabase.ninjavan.co/api/card/122299/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"d49289f0-e6be-cdae-aaba-c025c53fe61e","type":"category","value":["month"],"target":["variable",["template-tag","aggr"]]},
                {"id":"e6a1e9c8-8f83-9dfd-fecb-832d67512759","type":"date/single","value":"start_date","target":["variable",["template-tag","start"]]},
                {"id":"e017c9c6-0345-5b57-2d2c-a99a375ec2cb","type":"date/single","value":"end_date","target":["variable",["template-tag","end"]]},
                {"id":"b43a47f7-fe04-417d-8bce-ef5f111b8fa7","type":"string/=","value":"b2b_all_b2c_cc","target":["dimension",["template-tag","shipper_id"]]}
            ]
        },

        "no_rsvn_completed": {
            "url": "https://metabase.ninjavan.co/api/card/122256/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id": "190fb3a4-e6cb-4b4e-a78b-f4acb7cc5448", "type": "category", "value": "month", "target": ["variable", ["template-tag", "aggr"]]},
                {"id": "26473b49-9801-4240-ade1-6c07b7851c2a", "type": "date/single", "value": "start_end", "target": ["variable", ["template-tag", "start_date"]]},
                {"id": "8d72da7f-6a48-4384-a283-a1c81db37e2d", "type": "date/single", "value": "end_date", "target": ["variable", ["template-tag", "end_date"]]},
                {"id": "f1fca7d5-bddb-42ce-9771-1f17b2c6a1ec", "type": "string/=", "value": "driver_list", "target": ["dimension", ["template-tag", "route_driver_type"]]},
                {"id": "f72285e9-4c7f-4b94-9b22-9cf8c929946f", "type": "number/=", "value": [1], "target": ["variable", ["template-tag", "nv_not_liable"]]},
                {"id": "ecfc3da2-aca6-4303-bb42-aa3f9a21810d", "type": "string/contains", "value": ["B2BR"], "target": ["dimension", ["template-tag", "pickup_tags"]], "options": {"case-sensitive": False}},

            ],
            "shipper_params_template": {
                "b2br_key_shipper": [
                    {"id": "6980e48f-126e-48d9-a0d3-da79bbd63751", "type": "string/=", "value": "b2br_key_shipper", "target": ["dimension", ["template-tag", "shipper_id"]]},
                    # {"id": "452ee39f-7548-48f9-88aa-5348c9addd86", "type": "string/=","value":["7474545"],"target":["variable",["template-tag","parent_id_coalesce"]]},
                ],
                "sds_cc": [
                    {"id": "6980e48f-126e-48d9-a0d3-da79bbd63751", "type": "string/=", "value": "sds_cc", "target": ["dimension", ["template-tag", "shipper_id"]]},
                ],
            },
        },

        "poda_val_sho_laz": {
            "url": "https://metabase.ninjavan.co/api/card/122274/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"bd6a4239-0385-8972-2a17-0dae89833d44","type":"date/single","value":"start_date","target":["variable",["template-tag","start"]]},
                {"id":"f5d97598-03a0-4812-5396-9a7e48dff486","type":"category","value":["month"],"target":["variable",["template-tag","aggr"]]},
                {"id":"eea9787b-32e5-4f45-a751-8205f3fa5853","type":"string/=","value":[341107,216977],"target":["dimension",["template-tag","parent_id"]]},
                {"id":"cd2c4e8c-cba2-d597-7cd1-04acca8e86ca","type":"date/single","value":"end_date","target":["variable",["template-tag","end"]]}
            ]
        },

        "pu_rot": {
            "url": "https://metabase.ninjavan.co/api/card/122256/query/json",
            "report_type": "lm",
            "common_params_template": [
                {"id":"8d72da7f-6a48-4384-a283-a1c81db37e2d","type":"date/single","value":"end_date","target":["variable",["template-tag","end_date"]]},
                {"id":"f1fca7d5-bddb-42ce-9771-1f17b2c6a1ec","type":"string/=","value":"driver_list","target":["dimension",["template-tag","route_driver_type"]]},
                {"id":"6980e48f-126e-48d9-a0d3-da79bbd63751","type":"string/=","value":"b2br_key_shipper","target":["dimension",["template-tag","shipper_id"]]},
                {"id":"190fb3a4-e6cb-4b4e-a78b-f4acb7cc5448","type":"category","value":["month"],"target":["variable",["template-tag","aggr"]]},
                {"id":"ecfc3da2-aca6-4303-bb42-aa3f9a21810d","type":"string/contains","value":["B2BR"],"options":{"case-sensitive":False},"target":["dimension",["template-tag","pickup_tags"]]},
                {"id":"26473b49-9801-4240-ade1-6c07b7851c2a","type":"date/single","value":"start_date","target":["variable",["template-tag","start_date"]]}
            ]
        },

        "td6": {
            "url": "https://metabase.ninjavan.co/api/card/122261/query/json",
            "report_type": "fm",
            "common_params_template": [
                # {"id":"4e3825b2-b673-4bc2-850a-6653df4b0e52","type":"id","value":[9691851,9691856,9691857,9691878,9691882,9691900,9691927,9691947,9691966,9692052,9692053],"target":["dimension",["template-tag","shipper_id"]]},
                {"id":"adef369b-762a-ad76-c4e0-cbd4e2bc53ef","type":"category","value":["month"],"target":["variable",["template-tag","aggr"]]},
                {"id":"6eb39d69-fa95-fdcf-3ef7-7944e8945867","type":"date/all-options","value":"period_str","target":["dimension",["template-tag","d6_cutoff_date"]]},
                {"id":"1c3908b4-daad-4747-b1eb-f23c291acfcc","type":"number/=","value":[1],"target":["variable",["template-tag","exclude_shipper_5x_attempt"]]}
            ],
            "shipper_params_template": {
                "shop_laz": [
                    {"id":"08abe0d9-db20-4471-bf32-2ff223991971","type":"string/=","value":[341107,216977],"target":["dimension",["template-tag","parent_id"]]},
                ],
                "aggregator": [
                    {"id":"4e3825b2-b673-4bc2-850a-6653df4b0e52","type":"id","value":"aggregator","target":["dimension",["template-tag","shipper_id"]]},
                ],
                "4pl": [
                    {"id": "93050463-b83a-4b79-9176-c9baa78b5365", "type": "number/=", "value": [1], "target": ["variable", ["template-tag", "4pl_flag"]]},
                ],
            },
        },

        "rdo_rtd_b2b": {
            "url": "https://metabase.ninjavan.co/api/card/116132/query/json",
            "report_type": "fm",
            "common_params_template": [
                {"id":"0c07a704-c667-4468-a4e5-76e76367de31","type":"date/single","value":"start_date","target":["variable",["template-tag","start"]]},
                {"id":"5dfa2a9b-1df1-4b15-abcc-b44bf7f0fe16","type":"date/single","value":"end_date","target":["variable",["template-tag","end"]]}
            ],
        },
    }
}
# ── Archieved File ─────────────────────────────────────────────────────
ARCHIVE_CONFIG = {
    "tracker": {
        "source_file_id": "10jwwERVKLvdrk7tkmqVXeZHGp3Q1lV_2IjFsc6fXQhQ",
        "target_folder_id": "18BwwadT0kgyPgvdmOg3b7CP29zqrTFB4",
    },
    "sanggahan": {
        "source_file_id": "1q1CkYFiZQKRvfYDjZGOJmqNOndbH3hd7Du_Pq0Wn7AU",
        "target_folder_id": "12d8VANvDb2earFpAJOgQLj4kW1ITZm_U",
    },
    "converter": {
        "source_file_id": "1Sn2HisZcT81duWuWtKpVx_E_8192XeFIwtXrrDoSpGQ",
        "target_folder_id": "1Dx2EJoddhhdSqJs5qkNG8rWB9ydCc1Sl",
    },
}

# ── Pipeline Schedule ─────────────────────────────────────────
# Ini untuk referensi GitHub Actions
# Tanggal yang pipeline jalan tiap bulan
SCHEDULE_DAYS = [1, 2, 6, 10, 14, 15, 16]
