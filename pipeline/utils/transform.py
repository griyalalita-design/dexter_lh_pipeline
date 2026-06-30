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
        df_raw.groupby(["orig_hub_region", "orig_hub_name"], as_index=False)
        .agg(
            {
                "shipment_compliance_flag": "sum",
                "shipment_id": "count",
            }
        )
        .sort_values(by=["orig_hub_region", "orig_hub_name"])
    )

    return tracker_df


def transform_into_hub_completion(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw.empty:
        return df_raw

    tracker_df = (
        df_raw.groupby(["dest_hub_region", "dest_hub_name"], as_index=False)
        .agg(
            hit_count=("mmda_adoption", lambda x: (x == "MMDA").sum()),
            trip_count=("shipment_id", "count"),
        )
        .sort_values(by=["dest_hub_region", "dest_hub_name"])
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

def transform_cs_iv(df, db):
    import pandas as pd
    import numpy as np

    df = df.copy()
    db = db.copy()

    # =========================
    # CLEAN DATETIME
    # =========================
    df["orig_shipment_close_datetime"] = pd.to_datetime(df["orig_shipment_close_datetime"], errors="coerce")
    df["orig_shipment_van_inbound_datetime"] = pd.to_datetime(df["orig_shipment_van_inbound_datetime"], errors="coerce")

    db["Start Close Reguler"] = pd.to_datetime(db["Start Close Reguler"], errors="coerce")
    db["End Close Reguler"] = pd.to_datetime(db["End Close Reguler"], errors="coerce")
    db["Departure Datetime"] = pd.to_datetime(db["Departure Datetime"], errors="coerce")

    # =========================
    # BUILD OD
    # =========================
    df["od"] = (
        df["orig_hub_name"].fillna("").astype(str).str.strip()
        + " "
        + df["dest_hub_name"].fillna("").astype(str).str.strip()
    )

    db["OD Trip Pairing"] = db["OD Trip Pairing"].astype(str).str.strip()

    # =========================
    # LOOKUP EARLIEST DEPART
    # =========================
    def get_earliest_depart(row):
        matched = db[
            (db["OD Trip Pairing"] == row["od"]) &
            (row["orig_shipment_close_datetime"] > db["Start Close Reguler"]) &
            (row["orig_shipment_close_datetime"] <= db["End Close Reguler"])
        ]

        if matched.empty:
            return pd.NaT

        return matched.iloc[0]["Departure Datetime"]

    df["earliest_depart"] = df.apply(get_earliest_depart, axis=1)

    # =========================
    # APPLY LOGIC
    # =========================
    df["earliest_depart_buffer"] = df["earliest_depart"] + pd.Timedelta(minutes=30)
    df["earliest_depart_date"] = df["earliest_depart"].dt.date

    df["csiv_verdict"] = np.where(
        df["earliest_depart_date"].isna(),
        "N/A",
        np.where(
            df["orig_shipment_van_inbound_datetime"].isna(),
            "No iv",
            np.where(
                df["orig_shipment_van_inbound_datetime"] > df["earliest_depart_buffer"],
                "Miss",
                "Hit"
            )
        )
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
        "miss_check"
    ] = "Late depart"

    df.loc[
        df["csiv_verdict"].eq("Miss") & (duration_num > 3),
        "miss_check"
    ] = "Roll over / Offload?"

    return df

def pivot_cs_iv(df):
    pivot = (
        df.groupby("orig_hub_name", dropna=False)
        .agg(
            hit=("csiv_verdict", lambda x: (x == "Hit").sum()),
            total_shipment=("shipment_id", "count")
        )
        .reset_index()
    )

    pivot["cs_iv_%"] = pivot["hit"] / pivot["total_shipment"]

    return pivot
