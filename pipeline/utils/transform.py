# ============================================================
# utils/transform.py — Semua transformasi data pake pandas
# TIDAK ada API calls di sini, murni transformasi aja
# ============================================================

import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def get_last_month_range():
    """
    Hitung range bulan lalu.
    Contoh: kalau sekarang April 2026, return (2026-03-01, 2026-03-31, 'Maret')
    """
    today = date.today()
    start_day = (today.replace(day=1) - relativedelta(months=1))
    end_day = today.replace(day=1) - relativedelta(days=1)
    bulan_names = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    bulan_name = bulan_names[first_day.month]
    return start_day, end_day, bulan_name


def categorize_shippers(df_pns: pd.DataFrame):
    """
    Bagi shipper dari Key Shipper ke kategori Day 2.

    Returns:
        dict dengan keys: "b2b_cc", "key_shipper", "lazada_shopee"
        masing-masing berisi list Global ID (int).
    """
    required_cols = ["Global ID", "Shipper Service Category"]
    missing_cols = [c for c in required_cols if c not in df_pns.columns]
    if missing_cols:
        raise ValueError(
            f"Kolom wajib tidak ditemukan di key shipper sheet: {missing_cols}. "
            "Pastikan header: 'Global ID' dan 'Shipper Service Category'."
        )

    df = df_pns.copy()
    df["Shipper Service Category"] = df["Shipper Service Category"].astype(str).str.strip()
    df["Global ID"] = pd.to_numeric(df["Global ID"], errors="coerce")
    df = df[df["Global ID"].notna()]
    df["Global ID"] = df["Global ID"].astype(int)

    b2b_cc_categories = ["B2BR", "B2BR Sameday", "LTL Reguler"]
    key_shipper_category = "FS / BD Key Shipper"

    b2b_cc = (
        df[df["Shipper Service Category"].isin(b2b_cc_categories)]["Global ID"]
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )

    key_shipper = (
        df[df["Shipper Service Category"] == key_shipper_category]["Global ID"]
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )


    print(f"Shipper B2B+CC: {len(b2b_cc)}")
    print(f"Key Shipper: {len(key_shipper)}")

    return {
        "b2b_cc": b2b_cc,
        "key_shipper": key_shipper,
    }

def transform_poa_iv(df_raw):

    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw
        .groupby("origin_hub_name", as_index=False)
        .agg(
            ontime_count=("arrival_status", lambda x: (x == "Ontime").sum()),
            trip_count=("trip_id", "count")
        )
        .sort_values("origin_hub_name")
    )

    return tracker_df

def transform_n0_completion(df_raw):
    """
    Tracker Output:
    Row Labels (dest_hub_name)
    Sum of n0_delivery_complete_flag
    Sum of vol
    """
    if df_raw.empty:
        return df_raw
    tracker_df = (
    df_raw
    .groupby(["dest_hub_name"], as_index=False)
    .agg({
        "n0_delivery_complete_flag":"sum",
        "vol": "sum"
    })
    .sort_values("dest_hub_name")
)

    return tracker_df

def transform_shipment_completion(df_raw):

    if df_raw.empty:
        return df_raw
    tracker_df = (
    df_raw
    .groupby(["orig_hub_name"], as_index=False)
    .agg({
        "shipment_compliance_flag":"sum",
        "trip_id": "count"
    })
    .sort_values("orig_hub_name")
)

    return tracker_df

def transform_into_hub_completion(df_raw):

    if df_raw.empty:
        return df_raw
    tracker_df = (
    df_raw
    .groupby(["dest_hub_name"], as_index=False)
    .agg(
            hit_count=("mmda_adoption", lambda x: (x == "MMDA").sum()),
            trip_count=("trip_id", "count")
        )
    .sort_values("dest_hub_name")
)

    return tracker_df

def transform_rsvn_completed(df_raw):

    if df_raw.empty:
        return df_raw
    tracker_df = (
    df_raw
    .groupby(["hub_name"], as_index=False)
    .agg({
        "rsvn_n0_success_hit":"sum",
        "rsvn_ready": "sum"
    })
    .sort_values("hub_name")
)

    return tracker_df


def transform_rdo_rtd(df_raw):
    if df_raw.empty:
        return df_raw

    cols = [
        "bundle_tracking_id",
        "rdo_tracking_id",
        "hub_name",
        "hub_region",
        "fwd_success_datetime",
        "add_to_shipment_datetime",
        "orig_shipment_van_inbound_datetime",
        "sla_ats_days",
        "sla_vi_days",
        "sla_ats_hit_flag",
        "sla_vi_hit_flag"  
    ]

    missing_cols = [c for c in cols if c not in df_raw.columns]
    if missing_cols:
        raise ValueError(f"Kolom RDO tidak ditemukan: {missing_cols}")

    return df_raw[cols].copy()
    
