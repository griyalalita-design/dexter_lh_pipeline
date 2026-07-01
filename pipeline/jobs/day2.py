import copy
import json
import os
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config.settings import GSHEET, METABASE_CONFIG, CS_IV_DETAIL_DRIVE_FOLDER_ID

try:
    # Optional. Bisa berupa DataFrame, atau dict config GSheet.
    from config.settings import CS_IV_DB
except ImportError:
    CS_IV_DB = None

from utils.gsheet import read_sheet, write_sheet
from utils.metabase import get_token, tarik_metabase
from utils.transform import (
    transform_into_hub_completion,
    transform_n0_completion,
    transform_poa_iv,
    transform_rdo_rtd,
    transform_rsvn_completed,
    transform_shipment_completion,
)


SHIPPER_GROUPS = {
    "agg_fsbd": ["FSBD Key Shipper", "Aggregator Keyshipper"],
    "b2c_cc_agg_fsbd": [
        "B2C Cold Sameday",
        "B2C Cold Next Day",
        "FSBD Key Shipper",
        "Aggregator Keyshipper",
    ],
    "b2b_all_b2c_cc": [
        "B2B Dry Reguler",
        "B2B Cold Next Day",
        "B2B Dry Next Day",
        "B2C Cold Next Day",
    ],
    "b2b_dry_cc_next": [
        "B2B Dry Reguler",
        "B2B Cold Next Day",
        "B2B Dry Next Day",
    ],
    "b2b_sds_dry_cold_prem": ["B2B Sameday Premium"],
    "b2b_sds_dry_cold_reg": ["B2B Sameday Reguler", "B2C Cold Sameday"],
    "b2br_key_shipper": [
        "B2B Dry Reguler",
        "B2B Sameday Reguler",
        "B2B Sameday Premium",
        "FSBD Key Shipper",
        "Aggregator Keyshipper",
    ],
    "sds_cc": [
        "B2B Sameday Reguler",
        "B2B Sameday Premium",
        "B2C Cold Chain Sameday",
        "B2C Cold Chain Next Day",
    ],
    "aggregator": ["Aggregator Keyshipper"],
    "key_shipper": ["FSBD Key Shipper"],
    "shopee_lazada": [],
}


LH_REPORT_PLAN = [
    {"report_key": "iv_poa", "segment_key": "shopee_lazada"},
    {"report_key": "iv_poa", "segment_key": "key_shipper"},
    {"report_key": "iv_poa", "segment_key": "b2b_all_b2c_cc"},

    {"report_key": "cs_iv", "segment_key": "shopee_lazada"},
    {"report_key": "cs_iv", "segment_key": "key_shipper"},
    {"report_key": "cs_iv", "segment_key": "b2b_all_b2c_cc"},

    {"report_key": "n0_completion", "segment_key": "b2b_all_b2c_cc"},
    {
        "report_key": "no_rsvn_completed_b2b_all_b2c_cc",
        "segment_key": "b2b_all_b2c_cc",
        "result_key": "no_rsvn_completed_b2b_all_b2c_cc",
    },
    {"report_key": "shipment_compliance"},
    {"report_key": "into_hub_compliance"},
    # {"report_key": "rdo_rtd_b2b"},
]


TRANSFORM_MAP = {
    "iv_poa_shopee_lazada": transform_poa_iv,
    "iv_poa_key_shipper": transform_poa_iv,
    "iv_poa_b2b_all_b2c_cc": transform_poa_iv,
    "n0_completion_b2b_all_b2c_cc": transform_n0_completion,
    "no_rsvn_completed_b2b_all_b2c_cc": transform_rsvn_completed,
    "shipment_compliance": transform_shipment_completion,
    "into_hub_compliance": transform_into_hub_completion,
    "rdo_rtd_b2b": transform_rdo_rtd,
}


TRACKER_WRITE_MAP = {
    "iv_poa_shopee_lazada": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "BL6"},
    ],
    "iv_poa_key_shipper": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "AF6"},
    ],
    "iv_poa_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "Z6"},
    ],
    "n0_completion_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "AL6"},
    ],
    "no_rsvn_completed_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "H6"},
    ],
    "shipment_compliance": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "AX6"},
    ],
    "into_hub_compliance": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "BE6"},
    ],
    "rdo_rtd_b2b": [
        {"tracker_key": "rdo_comp", "tab_key": "raw_data", "start_cell": "B6"},
    ],
    "cs_iv_shopee_lazada": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "BR6"},
    ],
    "cs_iv_key_shipper": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "N6"},
    ],
    "cs_iv_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "T6"},
    ],
}


def get_previous_month_period():
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    start_date = first_day_prev_month.strftime("%Y-%m-%d")
    end_date = last_day_prev_month.strftime("%Y-%m-%d")
    period_str = f"{start_date}~{end_date}"
    return start_date, end_date, period_str


def build_shipper_group_values():
    print("\n[1/4] Read Key Shipper...")

    df = read_sheet(
        GSHEET["key_shipper"]["sheet_id"],
        GSHEET["key_shipper"]["tabs"]["main"],
    )
    df.columns = df.columns.astype(str).str.strip()

    required_cols = ["Type", "Shipper ID"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom tidak ditemukan di key_shipper: {missing_cols}")

    df["Type"] = df["Type"].astype(str).str.strip()
    df["Shipper ID"] = (
        pd.to_numeric(df["Shipper ID"], errors="coerce")
        .dropna()
        .astype(int)
        .astype(str)
    )

    result = {}
    for group_key, type_list in SHIPPER_GROUPS.items():
        ids = (
            df[df["Type"].isin(type_list)]["Shipper ID"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )
        result[group_key] = ids
        print(f"{group_key}: {len(ids)} shipper_id | sample: {ids[:5]}")

    return result


def render_params(param_templates, runtime_values):
    rendered = []

    for param in param_templates or []:
        p = copy.deepcopy(param)

        if "value_key" in p:
            key = p.pop("value_key")
            p["value"] = runtime_values[key]
        elif isinstance(p.get("value"), str) and p["value"] in runtime_values:
            p["value"] = runtime_values[p["value"]]

        rendered.append(p)

    return rendered


def result_name_for(item):
    if item.get("result_key"):
        return item["result_key"]

    report_key = item["report_key"]
    segment_key = item.get("segment_key")
    return f"{report_key}_{segment_key}" if segment_key else report_key


def should_skip_report(report_key):
    if report_key not in METABASE_CONFIG["lh"]:
        return True

    url = METABASE_CONFIG["lh"][report_key].get("url", "")
    return not url or "PASTE_" in url


def run_report(report_key, runtime_values, token, segment_key=None, desc=None):
    cfg = METABASE_CONFIG["lh"][report_key]

    common_params = render_params(
        cfg.get("common_params_template", []),
        runtime_values,
    )

    segment_params = []
    if segment_key:
        segment_params = render_params(
            cfg.get("shipper_params_template", {}).get(segment_key, []),
            runtime_values,
        )

    final_params = common_params + segment_params
    desc = desc or (f"{report_key}_{segment_key}" if segment_key else report_key)

    print(f"\n[RUN] {desc}")
    print(f"URL: {cfg['url']}")
    print(f"Total params: {len(final_params)}")

    df_result = tarik_metabase(
        url=cfg["url"],
        parameters=final_params,
        token=token,
        desc=desc,
    )

    print(f"{desc} shape: {df_result.shape}")
    if not df_result.empty:
        print(df_result.head(5).to_string(index=False))
    else:
        print(f"WARNING: {desc} hasil kosong")

    time.sleep(2)
    return df_result


def sanitize_for_sheet(df):
    cleaned = df.copy()
    cleaned = cleaned.replace([float("inf"), float("-inf")], pd.NA)

    def convert_value(x):
        if pd.isna(x):
            return ""
        if isinstance(x, pd.Timestamp):
            return x.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(x, datetime):
            return x.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(x, date):
            return x.strftime("%Y-%m-%d")
        return x

    for col in cleaned.columns:
        cleaned[col] = cleaned[col].apply(convert_value)

    return cleaned


def write_with_destinations(result_key, df_to_write, destinations):
    if not destinations:
        print(f"[SKIP WRITE] {result_key}: belum ada mapping tujuan")
        return

    if df_to_write.empty:
        print(f"[SKIP WRITE] {result_key}: dataframe empty")
        return

    if isinstance(destinations, dict):
        destinations = [destinations]

    df_to_write = sanitize_for_sheet(df_to_write)

    for dest in destinations:
        tracker_key = dest["tracker_key"]
        tab_key = dest["tab_key"]
        start_cell = dest.get("start_cell", "A1")
        include_header = dest.get("include_header", False)

        if tracker_key not in GSHEET:
            print(f"[SKIP WRITE] {result_key}: tracker_key belum ada di GSHEET: {tracker_key}")
            continue

        tracker_cfg = GSHEET[tracker_key]
        sheet_id = tracker_cfg["sheet_id"]
        sheet_name = tracker_cfg["tabs"][tab_key]

        print(f"Writing {result_key} -> {tracker_key} | {sheet_name} | {start_cell}")

        write_sheet(
            spreadsheet_id=sheet_id,
            sheet_name=sheet_name,
            df=df_to_write,
            start_cell=start_cell,
            include_header=include_header,
        )


def write_tracker_result(result_key, df_to_write):
    write_with_destinations(
        result_key=result_key,
        df_to_write=df_to_write,
        destinations=TRACKER_WRITE_MAP.get(result_key, []),
    )


def export_cs_iv_detail_to_csv(result_key, detail_df, period_str):
    if detail_df.empty:
        print(f"[SKIP CS-IV CSV] {result_key}: dataframe empty")
        return None

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    safe_period = period_str.replace("~", "_")
    filename = f"{result_key}_detail_{safe_period}.csv"
    filepath = os.path.join(output_dir, filename)

    export_df = sanitize_for_sheet(detail_df)
    export_df.to_csv(filepath, index=False, encoding="utf-8-sig")

    print(f"[OK CSV] {result_key}: {filepath}")
    return filepath


def get_drive_service():
    """Build Drive service.

    Supports either:
    1. GOOGLE_SERVICE_ACCOUNT_JSON env containing service-account JSON string.
    2. GOOGLE_APPLICATION_CREDENTIALS / ADC.
    """
    scopes = ["https://www.googleapis.com/auth/drive.file"]

    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        from google.oauth2 import service_account

        info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=scopes,
        )
        return build("drive", "v3", credentials=credentials)

    import google.auth

    credentials, _ = google.auth.default(scopes=scopes)
    return build("drive", "v3", credentials=credentials)


def upload_file_to_drive(filepath, folder_id):
    if not filepath or not os.path.exists(filepath):
        print(f"[SKIP DRIVE UPLOAD] file tidak ditemukan: {filepath}")
        return None

    if not folder_id:
        print("[SKIP DRIVE UPLOAD] CS_IV_DETAIL_DRIVE_FOLDER_ID kosong")
        return None

    service = get_drive_service()

    file_metadata = {
        "name": os.path.basename(filepath),
        "parents": [folder_id],
    }

    media = MediaFileUpload(
        filepath,
        mimetype="text/csv",
        resumable=True,
    )

    uploaded_file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )

    print(f"[OK DRIVE UPLOAD] {uploaded_file.get('name')}")
    print(f"Link: {uploaded_file.get('webViewLink')}")
    return uploaded_file


def load_cs_iv_db():
    cfg = CS_IV_DB

    if isinstance(cfg, pd.DataFrame):
        return cfg.copy()

    if cfg is None:
        cfg = GSHEET.get("cs_iv_db")

    if cfg is None:
        raise ValueError(
            "CS_IV_DB belum diset. Tambahkan CS_IV_DB atau GSHEET['cs_iv_db'] di settings.py."
        )

    if isinstance(cfg, dict):
        sheet_id = cfg.get("sheet_id")
        if not sheet_id:
            raise ValueError("CS_IV_DB/GSHEET['cs_iv_db'] harus punya key 'sheet_id'.")

        if "tab_name" in cfg:
            sheet_name = cfg["tab_name"]
        else:
            tab_key = cfg.get("tab_key", "main")
            sheet_name = cfg.get("tabs", {}).get(tab_key)

        if not sheet_name:
            raise ValueError(
                "CS_IV_DB config harus punya 'tab_name' atau 'tabs' dengan tab_key yang valid."
            )

        db = read_sheet(sheet_id, sheet_name)
        db.columns = db.columns.astype(str).str.strip()
        return db

    raise TypeError("CS_IV_DB harus berupa pandas DataFrame atau dict config GSheet.")


def transform_cs_iv(raw_df, cs_iv_db):
    df = raw_df.copy()
    db = cs_iv_db.copy()

    required_df_cols = [
        "shipment_id",
        "orig_hub_name",
        "dest_hub_name",
        "orig_shipment_close_datetime",
        "orig_shipment_van_inbound_datetime",
    ]
    required_db_cols = [
        "OD Trip Pairing",
        "Start Close Reguler",
        "End Close Reguler",
        "Departure Datetime",
    ]

    missing_df_cols = [c for c in required_df_cols if c not in df.columns]
    missing_db_cols = [c for c in required_db_cols if c not in db.columns]
    if missing_df_cols:
        raise ValueError(f"Kolom Metabase CS-IV tidak ditemukan: {missing_df_cols}")
    if missing_db_cols:
        raise ValueError(f"Kolom DB CS-IV tidak ditemukan: {missing_db_cols}")

    df["orig_shipment_close_datetime"] = pd.to_datetime(
        df["orig_shipment_close_datetime"],
        errors="coerce",
    )
    df["orig_shipment_van_inbound_datetime"] = pd.to_datetime(
        df["orig_shipment_van_inbound_datetime"],
        errors="coerce",
    )

    db["Start Close Reguler"] = pd.to_datetime(db["Start Close Reguler"], errors="coerce")
    db["End Close Reguler"] = pd.to_datetime(db["End Close Reguler"], errors="coerce")
    db["Departure Datetime"] = pd.to_datetime(db["Departure Datetime"], errors="coerce")

    df["od"] = (
        df["orig_hub_name"].fillna("").astype(str).str.strip()
        + " "
        + df["dest_hub_name"].fillna("").astype(str).str.strip()
    )
    db["OD Trip Pairing"] = db["OD Trip Pairing"].astype(str).str.strip()

    def get_earliest_depart(row):
        matched = db[
            (db["OD Trip Pairing"] == row["od"])
            & (row["orig_shipment_close_datetime"] > db["Start Close Reguler"])
            & (row["orig_shipment_close_datetime"] <= db["End Close Reguler"])
        ]

        if matched.empty:
            return pd.NaT

        return matched.iloc[0]["Departure Datetime"]

    df["earliest_depart"] = df.apply(get_earliest_depart, axis=1)
    df["earliest_depart_buffer"] = df["earliest_depart"] + pd.Timedelta(minutes=30)
    df["earliest_depart_date"] = df["earliest_depart"].dt.date

    df["csiv_verdict"] = np.where(
        df["earliest_depart"].isna(),
        "N/A",
        np.where(
            df["orig_shipment_van_inbound_datetime"].isna(),
            "No iv",
            np.where(
                df["orig_shipment_van_inbound_datetime"] > df["earliest_depart_buffer"],
                "Miss",
                "Hit",
            ),
        ),
    )

    df["cs_iv_duration_round"] = "-"
    mask_miss = df["csiv_verdict"].eq("Miss")

    df.loc[mask_miss, "cs_iv_duration_round"] = (
        (
            df.loc[mask_miss, "orig_shipment_van_inbound_datetime"]
            - df.loc[mask_miss, "earliest_depart"]
        )
        .dt.total_seconds()
        .div(3600)
        .round(1)
    )

    duration_num = pd.to_numeric(df["cs_iv_duration_round"], errors="coerce")

    df["miss_check"] = "-"
    df.loc[
        df["csiv_verdict"].eq("Miss") & (duration_num <= 3),
        "miss_check",
    ] = "Late depart"
    df.loc[
        df["csiv_verdict"].eq("Miss") & (duration_num > 3),
        "miss_check",
    ] = "Roll over / Offload?"

    return df


def pivot_cs_iv(detail_df):
    if detail_df.empty:
        return pd.DataFrame(columns=["orig_hub_name", "hit", "total_shipment", "cs_iv_%"])

    summary_df = (
        detail_df.groupby("orig_hub_name", dropna=False)
        .agg(
            hit=("csiv_verdict", lambda x: (x == "Hit").sum()),
            total_shipment=("shipment_id", "count"),
        )
        .reset_index()
    )

    summary_df["cs_iv_%"] = np.where(
        summary_df["total_shipment"].eq(0),
        0,
        summary_df["hit"] / summary_df["total_shipment"],
    )

    return summary_df


def run():
    print("=== LH DAY 2 START ===")

    start_date, end_date, period_str = get_previous_month_period()

    print("\n[0/4] Period")
    print(f"start_date : {start_date}")
    print(f"end_date   : {end_date}")
    print(f"period_str : {period_str}")

    print("\n[1/4] Get Metabase token...")
    token = get_token()
    print("Token loaded:", bool(token))

    shipper_runtime = build_shipper_group_values()
    runtime_values = {
        "start_date": start_date,
        "end_date": end_date,
        "period_str": period_str,
        "start_end": start_date,
        **shipper_runtime,
    }

    results = {}
    print("\n[2/4] Pull selected LH reports...")

    for item in LH_REPORT_PLAN:
        report_key = item["report_key"]
        segment_key = item.get("segment_key")
        result_key = result_name_for(item)

        if should_skip_report(report_key):
            print(f"SKIP {result_key}: report_key tidak ada atau URL kosong")
            continue

        try:
            results[result_key] = run_report(
                report_key=report_key,
                runtime_values=runtime_values,
                token=token,
                segment_key=segment_key,
                desc=result_key,
            )
        except Exception as e:
            print(f"\n[FAILED] {result_key}")
            print(repr(e))
            results[result_key] = pd.DataFrame()

    print("\n[3/4] Summary raw result shapes:")
    for key, df in results.items():
        print(f"- {key}: {df.shape}")

    tracker_results = {}
    cs_iv_detail_results = {}
    cs_iv_db_cache = None

    print("\n[4/4] Transform tracker outputs...")

    for item in LH_REPORT_PLAN:
        result_key = result_name_for(item)

        if result_key not in results:
            print(f"[SKIP TRANSFORM] {result_key}: not found in raw results")
            continue

        raw_df = results[result_key]

        try:
            if result_key.startswith("cs_iv"):
                if raw_df.empty:
                    print(f"[SKIP CS-IV TRANSFORM] {result_key}: raw dataframe empty")
                    tracker_results[result_key] = pd.DataFrame()
                    continue

                if cs_iv_db_cache is None:
                    print("[CS-IV] Load schedule DB...")
                    cs_iv_db_cache = load_cs_iv_db()
                    print(f"[CS-IV] DB shape: {cs_iv_db_cache.shape}")

                detail_df = transform_cs_iv(raw_df, cs_iv_db_cache)
                cs_iv_detail_results[result_key] = detail_df
                print(f"[OK CS-IV DETAIL] {result_key}: {detail_df.shape}")

                csv_path = export_cs_iv_detail_to_csv(
                    result_key=result_key,
                    detail_df=detail_df,
                    period_str=period_str,
                )

                try:
                    upload_file_to_drive(
                        filepath=csv_path,
                        folder_id=CS_IV_DETAIL_DRIVE_FOLDER_ID,
                    )
                except Exception as upload_error:
                    print(f"[WARNING DRIVE UPLOAD FAILED] {result_key}: {repr(upload_error)}")
                    print("CSV tetap tersimpan di folder output lokal.")

                tracker_results[result_key] = pivot_cs_iv(detail_df)

            else:
                if result_key not in TRANSFORM_MAP:
                    print(f"[SKIP TRANSFORM] {result_key}: belum ada TRANSFORM_MAP")
                    tracker_results[result_key] = pd.DataFrame()
                    continue

                transform_func = TRANSFORM_MAP[result_key]
                tracker_results[result_key] = transform_func(raw_df)

            print(f"[OK TRANSFORM] {result_key}: {tracker_results[result_key].shape}")

        except Exception as e:
            print(f"[FAILED TRANSFORM] {result_key}")
            print(repr(e))
            tracker_results[result_key] = pd.DataFrame()

    print("\n[WRITE] Dump tracker outputs...")
    for result_key, tracker_df in tracker_results.items():
        write_tracker_result(result_key, tracker_df)

    print("\n=== LH DAY 2 DONE ===")
    return {"raw": results, "cs_iv_detail": cs_iv_detail_results, "tracker": tracker_results}


if __name__ == "__main__":
    run()
