import copy
import time
from datetime import datetime, timedelta

import pandas as pd

from config.settings import GSHEET, METABASE_CONFIG
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
    {"report_key": "n0_completion", "segment_key": "b2b_all_b2c_cc"},
    {
        "report_key": "no_rsvn_completed_b2b_all_b2c_cc",
        "segment_key": "b2b_all_b2c_cc",
        "result_key": "no_rsvn_completed_b2b_all_b2c_cc",
    },
    {"report_key": "shipment_compliance"},
    {"report_key": "into_hub_compliance"},
    # Uncomment after the report config is enabled in settings.py.
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
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "A6"},
    ],
    "iv_poa_key_shipper": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "G6"},
    ],
    "iv_poa_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "M6"},
    ],
    "n0_completion_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "S6"},
    ],
    "no_rsvn_completed_b2b_all_b2c_cc": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "Y6"},
    ],
    "shipment_compliance": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "AE6"},
    ],
    "into_hub_compliance": [
        {"tracker_key": "tracker", "tab_key": "raw_data_compile", "start_cell": "AK6"},
    ],
    "rdo_rtd_b2b": [
        {"tracker_key": "rdo_comp", "tab_key": "raw_data", "start_cell": "D2"},
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
    return cleaned.where(pd.notna(cleaned), "")


def write_tracker_result(result_key, df_to_write):
    destinations = TRACKER_WRITE_MAP.get(result_key, [])
    if not destinations:
        print(f"[SKIP WRITE] {result_key}: belum ada mapping tujuan")
        return

    if df_to_write.empty:
        print(f"[SKIP WRITE] {result_key}: dataframe empty")
        return

    df_to_write = sanitize_for_sheet(df_to_write)

    for dest in destinations:
        tracker_key = dest["tracker_key"]
        tab_key = dest["tab_key"]
        start_cell = dest["start_cell"]

        if tracker_key not in GSHEET:
            print(f"[SKIP WRITE] {result_key}: tracker_key belum ada di GSHEET: {tracker_key}")
            continue

        tracker_cfg = GSHEET[tracker_key]
        sheet_id = tracker_cfg["sheet_id"]
        sheet_name = tracker_cfg["tabs"][tab_key]

        print(f"Writing {result_key} -> {tracker_key} | {sheet_name} | {start_cell}")

        try:
            write_sheet(
                spreadsheet_id=sheet_id,
                sheet_name=sheet_name,
                df=df_to_write,
                start_cell=start_cell,
                include_header=False,
            )
        except TypeError:
            write_sheet(sheet_id, sheet_name, df_to_write)


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
    print("\n[4/4] Transform tracker outputs...")

    for result_key, transform_func in TRANSFORM_MAP.items():
        if result_key not in results:
            print(f"[SKIP TRANSFORM] {result_key}: not found in raw results")
            continue

        try:
            tracker_results[result_key] = transform_func(results[result_key])
            print(f"[OK TRANSFORM] {result_key}: {tracker_results[result_key].shape}")
        except Exception as e:
            print(f"[FAILED TRANSFORM] {result_key}")
            print(repr(e))
            tracker_results[result_key] = pd.DataFrame()

    print("\n[WRITE] Dump tracker outputs...")
    for result_key, tracker_df in tracker_results.items():
        write_tracker_result(result_key, tracker_df)

    print("\n=== LH DAY 2 DONE ===")
    return {"raw": results, "tracker": tracker_results}


if __name__ == "__main__":
    run()
