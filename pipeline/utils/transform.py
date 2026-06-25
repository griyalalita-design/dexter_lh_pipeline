from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta


def get_last_month_range():
    today = date.today()
    start_day = today.replace(day=1) - relativedelta(months=1)
    end_day = today.replace(day=1) - relativedelta(days=1)
    bulan_names = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember",
    }
    bulan_name = bulan_names[start_day.month]
    return start_day, end_day, bulan_name


def transform_poa_iv(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw.groupby("origin_hub_name", as_index=False)
        .agg(
            ontime_count=("arrival_status", lambda x: (x == "Ontime").sum()),
            trip_count=("trip_id", "count"),
        )
        .sort_values("origin_hub_name")
    )

    return tracker_df


def transform_n0_completion(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw.groupby(["dest_hub_name"], as_index=False)
        .agg(
            {
                "n0_delivery_complete_flag": "sum",
                "vol": "sum",
            }
        )
        .sort_values("dest_hub_name")
    )

    return tracker_df


def transform_shipment_completion(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw.groupby(["orig_hub_region","orig_hub_name"], as_index=False)
        .agg(
            {
                "shipment_compliance_flag": "sum",
                "shipment_id": "count",
            }
        )
        .sort_values("orig_hub_region","orig_hub_name")
    )

    return tracker_df


def transform_into_hub_completion(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw.groupby(["dest_hub_region","dest_hub_name"], as_index=False)
        .agg(
            hit_count=("mmda_adoption", lambda x: (x == "MMDA").sum()),
            trip_count=("shipment_id", "count"),
        )
        .sort_values("dest_hub_region","dest_hub_name")
    )

    return tracker_df


def transform_rsvn_completed(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw.groupby(["hub_name"], as_index=False)
        .agg(
            {
                "rsvn_n0_success_hit": "sum",
                "rsvn_ready": "sum",
            }
        )
        .sort_values("hub_name")
    )

    return tracker_df


def transform_rdo_rtd(df_raw: pd.DataFrame) -> pd.DataFrame:
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
        "sla_vi_hit_flag",
    ]

    missing_cols = [c for c in cols if c not in df_raw.columns]
    if missing_cols:
        raise ValueError(f"Kolom RDO tidak ditemukan: {missing_cols}")

    return df_raw[cols].copy()
