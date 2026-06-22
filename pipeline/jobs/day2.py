import copy
from datetime import datetime, timedelta

import pandas as pd

from utils.metabase import tarik_metabase, get_token
from utils.gsheet import read_sheet, write_sheet, clear_range
from config.settings import METABASE_CONFIG, GSHEET


# =========================
# RUN CONTROL
# =========================
RUN_POA = False
RUN_LND = True

DUMP_TRACKER = True
DUMP_SANGGAHAN = True


def get_previous_month_period():
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    return (
        first_day_prev_month.strftime("%Y-%m-%d"),
        last_day_prev_month.strftime("%Y-%m-%d"),
    )


def render_params(param_templates, runtime_values):
    rendered = []

    for param in param_templates:
        p = copy.deepcopy(param)

        if "value_key" in p:
            key = p.pop("value_key")
            if key not in runtime_values:
                raise KeyError(f"runtime_values tidak punya key: {key}")
            p["value"] = runtime_values[key]

        rendered.append(p)

    return rendered


def sanitize_for_sheet(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.replace([float("inf"), float("-inf")], pd.NA)
    cleaned = cleaned.where(pd.notna(cleaned), "")
    return cleaned


def build_shipper_lists():
    print("\n[1] Read Google Sheet key_shipper...")

    df = read_sheet(
        GSHEET["key_shipper"]["sheet_id"],
        GSHEET["key_shipper"]["tabs"]["main"],
    )

    df.columns = df.columns.astype(str).str.strip()

    required_cols = ["Type", "Shipper ID"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom tidak ditemukan di sheet key_shipper: {missing_cols}")

    df["Type"] = df["Type"].astype(str).str.strip()

    b2b_cc_categories = [
        "B2C Cold Chain Sameday",
        "B2C Cold Chain Next Day",
        "B2B Dry Reguler",
        "B2B Sameday Reguler",
        "B2B Sameday Premium",
    ]

    fsbd_categories = [
        "FSBD Key Shipper",
        "Aggregator Keyshipper",
    ]

    def extract_ids(mask):
        return (
            pd.to_numeric(df.loc[mask, "Shipper ID"], errors="coerce")
            .dropna()
            .astype(int)
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

    b2b_cc_list = extract_ids(df["Type"].isin(b2b_cc_categories))
    fsbd_list = extract_ids(df["Type"].isin(fsbd_categories))

    print(f"Total b2b_cc_list: {len(b2b_cc_list)} | sample: {b2b_cc_list[:5]}")
    print(f"Total fsbd_list: {len(fsbd_list)} | sample: {fsbd_list[:5]}")

    return b2b_cc_list, fsbd_list


def run_report(report_group, report_key, segment_key, runtime_values, token):
    cfg = METABASE_CONFIG[report_group][report_key]

    common_params = render_params(
        cfg["common_params_template"],
        runtime_values,
    )

    segment_params = render_params(
        cfg["shipper_params_template"][segment_key],
        runtime_values,
    )

    final_params = common_params + segment_params
    desc = f"{report_key}_{segment_key}"

    print(f"\n[RUN] {desc}")
    print(f"Group: {report_group}")
    print(f"Total params: {len(final_params)}")

    df_result = tarik_metabase(
        url=cfg["url"],
        parameters=final_params,
        token=token,
        desc=desc,
    )

    print(f"{desc} shape: {df_result.shape}")

    if df_result.empty:
        print(f"WARNING: {desc} hasil kosong")
    else:
        print(df_result.head(5).to_string(index=False))

    return df_result


# =========================
# POA
# =========================
def reduce_poa_columns(df):
    if df.empty:
        return pd.DataFrame(columns=["orig_hub_name", "remarks", "total_vol"])

    required_cols = [
        "orig_hub_name",
        "remarks",
        "total_vol_poa_iv_closest_wave",
    ]

    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom POA tidak ditemukan: {missing_cols}")

    out = df[required_cols].copy()
    out = out.rename(columns={"total_vol_poa_iv_closest_wave": "total_vol"})

    out["orig_hub_name"] = out["orig_hub_name"].astype(str).str.strip()
    out["remarks"] = out["remarks"].astype(str).str.strip().str.lower()
    out["total_vol"] = pd.to_numeric(out["total_vol"], errors="coerce").fillna(0)

    return out


def compile_poa_segment(results, segment_key):
    compiled = []

    for report_key in ["poa_iv_1", "poa_iv_2", "poa_iv_3", "poa_iv_4"]:
        result_key = f"{report_key}_{segment_key}"
        df = results.get(result_key, pd.DataFrame())
        compiled.append(reduce_poa_columns(df))

    if not compiled:
        return pd.DataFrame(columns=["orig_hub_name", "remarks", "total_vol"])

    return pd.concat(compiled, ignore_index=True)


def build_poa_pivot(df_compiled):
    expected_cols = [
        "hit",
        "hit: offload",
        "miss",
        "miss: potential hit",
    ]

    final_cols = [
        "orig_hub_name",
        "hit",
        "hit: offload",
        "miss",
        "miss: potential hit",
        "grand_total",
        "total_hit",
    ]

    if df_compiled.empty:
        return pd.DataFrame(columns=final_cols)

    df = df_compiled.copy()

    df["remarks"] = df["remarks"].astype(str).str.strip().str.lower()
    df["total_vol"] = pd.to_numeric(df["total_vol"], errors="coerce").fillna(0)

    df = df[df["remarks"] != "others"]

    pivot = (
        df.pivot_table(
            index="orig_hub_name",
            columns="remarks",
            values="total_vol",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    for col in expected_cols:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot["total_hit"] = pivot["hit"] + pivot["hit: offload"]

    pivot["grand_total"] = (
        pivot["hit"]
        + pivot["hit: offload"]
        + pivot["miss"]
        + pivot["miss: potential hit"]
    )

    return pivot[final_cols].sort_values("orig_hub_name").reset_index(drop=True)


def dump_poa_to_tracker(
    pivot_poa_b2b_cc: pd.DataFrame,
    pivot_poa_fsbd: pd.DataFrame,
    pivot_poa_others: pd.DataFrame,
) -> None:
    tracker_cfg = GSHEET["tracker"]
    tracker_sheet_id = tracker_cfg["sheet_id"]
    tracker_tab = tracker_cfg["tabs"]["raw_data_all"]

    poa_clear_ranges = [
        "C4:I",
        "P4:V",
        "AC4:AI",
    ]

    for r in poa_clear_ranges:
        clear_range(
            spreadsheet_id=tracker_sheet_id,
            sheet_name=tracker_tab,
            range_a1=r,
        )

    write_sheet(
        spreadsheet_id=tracker_sheet_id,
        sheet_name=tracker_tab,
        df=sanitize_for_sheet(pivot_poa_b2b_cc),
        start_cell="C4",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=tracker_sheet_id,
        sheet_name=tracker_tab,
        df=sanitize_for_sheet(pivot_poa_fsbd),
        start_cell="P4",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=tracker_sheet_id,
        sheet_name=tracker_tab,
        df=sanitize_for_sheet(pivot_poa_others),
        start_cell="AC4",
        include_header=False,
    )

    print("POA tracker updated successfully.")


def dump_poa_to_sanggahan(
    pivot_poa_b2b_cc: pd.DataFrame,
    pivot_poa_fsbd: pd.DataFrame,
    pivot_poa_others: pd.DataFrame,
) -> None:
    sanggahan_cfg = GSHEET["sanggahan"]
    sanggahan_sheet_id = sanggahan_cfg["sheet_id"]
    tabs = sanggahan_cfg["tabs"]

    write_sheet(
        spreadsheet_id=sanggahan_sheet_id,
        sheet_name=tabs["poa_iv_b2b_all_b2c_cold"],
        df=sanitize_for_sheet(pivot_poa_b2b_cc),
        start_cell="A3",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=sanggahan_sheet_id,
        sheet_name=tabs["poa_iv_keyshipper"],
        df=sanitize_for_sheet(pivot_poa_fsbd),
        start_cell="A3",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=sanggahan_sheet_id,
        sheet_name=tabs["poa_iv_others"],
        df=sanitize_for_sheet(pivot_poa_others),
        start_cell="A3",
        include_header=False,
    )

    print("POA sanggahan updated successfully.")


# =========================
# LND
# =========================
def reduce_lnd_columns(df):
    if df.empty:
        return pd.DataFrame(columns=["hub", "total_loss_damage", "total_volume"])

    required_cols = [
        "hub",
        "total_loss_damage",
        "total_volume",
    ]

    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Kolom LND tidak ditemukan: {missing_cols}")

    out = df[required_cols].copy()

    out["hub"] = out["hub"].astype(str).str.strip()
    out["total_loss_damage"] = pd.to_numeric(
        out["total_loss_damage"], errors="coerce"
    ).fillna(0)
    out["total_volume"] = pd.to_numeric(
        out["total_volume"], errors="coerce"
    ).fillna(0)

    return out.sort_values("hub").reset_index(drop=True)


def dump_lnd_to_tracker(
    lnd_b2b_cc: pd.DataFrame,
    lnd_fsbd: pd.DataFrame,
    lnd_others: pd.DataFrame,
) -> None:
    tracker_cfg = GSHEET["tracker"]
    tracker_sheet_id = tracker_cfg["sheet_id"]
    tracker_tab = tracker_cfg["tabs"]["raw_data_all"]

    lnd_clear_ranges = [
        "AP4:AR",
        "AY4:BA",
        "BH4:BJ",
    ]

    for r in lnd_clear_ranges:
        clear_range(
            spreadsheet_id=tracker_sheet_id,
            sheet_name=tracker_tab,
            range_a1=r,
        )

    write_sheet(
        spreadsheet_id=tracker_sheet_id,
        sheet_name=tracker_tab,
        df=sanitize_for_sheet(lnd_b2b_cc),
        start_cell="AP4",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=tracker_sheet_id,
        sheet_name=tracker_tab,
        df=sanitize_for_sheet(lnd_fsbd),
        start_cell="AY4",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=tracker_sheet_id,
        sheet_name=tracker_tab,
        df=sanitize_for_sheet(lnd_others),
        start_cell="BH4",
        include_header=False,
    )

    print("LND tracker updated successfully.")


def dump_lnd_to_sanggahan(
    lnd_b2b_cc: pd.DataFrame,
    lnd_fsbd: pd.DataFrame,
    lnd_others: pd.DataFrame,
) -> None:
    sanggahan_cfg = GSHEET["sanggahan"]
    sanggahan_sheet_id = sanggahan_cfg["sheet_id"]
    tabs = sanggahan_cfg["tabs"]

    write_sheet(
        spreadsheet_id=sanggahan_sheet_id,
        sheet_name=tabs["lnd_rate_b2b_all_b2c_cold"],
        df=sanitize_for_sheet(lnd_b2b_cc),
        start_cell="A3",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=sanggahan_sheet_id,
        sheet_name=tabs["lnd_rate_keyshipper"],
        df=sanitize_for_sheet(lnd_fsbd),
        start_cell="A3",
        include_header=False,
    )

    write_sheet(
        spreadsheet_id=sanggahan_sheet_id,
        sheet_name=tabs["lnd_rate_others"],
        df=sanitize_for_sheet(lnd_others),
        start_cell="A3",
        include_header=False,
    )

    print("LND sanggahan updated successfully.")


def run():
    print("=== DAY 2 POA + LND START ===")

    start_date, end_date = get_previous_month_period()
    print(f"\n[0] Period: {start_date} to {end_date}")

    print("\n[1] Get Metabase token...")
    token = get_token()
    print("Token loaded:", bool(token))

    print("\n[2] Build shipper lists...")
    b2b_cc_list, fsbd_list = build_shipper_lists()

    runtime_values = {
        "start_date": start_date,
        "end_date": end_date,
        "b2b_cc": b2b_cc_list,
        "fsbd": fsbd_list,
    }

    segment_keys = ["b2b_cc", "fsbd", "others"]

    poa_results = {}
    compiled_poa_b2b_cc = pd.DataFrame()
    compiled_poa_fsbd = pd.DataFrame()
    compiled_poa_others = pd.DataFrame()
    pivot_poa_b2b_cc = pd.DataFrame()
    pivot_poa_fsbd = pd.DataFrame()
    pivot_poa_others = pd.DataFrame()

    lnd_results = {}
    lnd_b2b_cc = pd.DataFrame()
    lnd_fsbd = pd.DataFrame()
    lnd_others = pd.DataFrame()

    # =========================
    # POA
    # =========================
    if RUN_POA:
        print("\n[3] Pull POA reports...")

        poa_report_keys = [
            "poa_iv_1",
            "poa_iv_2",
            "poa_iv_3",
            "poa_iv_4",
        ]

        for report_key in poa_report_keys:
            for segment_key in segment_keys:
                result_name = f"{report_key}_{segment_key}"

                poa_results[result_name] = run_report(
                    report_group="poa",
                    report_key=report_key,
                    segment_key=segment_key,
                    runtime_values=runtime_values,
                    token=token,
                )

        print("\n[4] Compile and pivot POA...")

        compiled_poa_b2b_cc = compile_poa_segment(poa_results, "b2b_cc")
        compiled_poa_fsbd = compile_poa_segment(poa_results, "fsbd")
        compiled_poa_others = compile_poa_segment(poa_results, "others")

        pivot_poa_b2b_cc = build_poa_pivot(compiled_poa_b2b_cc)
        pivot_poa_fsbd = build_poa_pivot(compiled_poa_fsbd)
        pivot_poa_others = build_poa_pivot(compiled_poa_others)

        print("pivot_poa_b2b_cc shape:", pivot_poa_b2b_cc.shape)
        print("pivot_poa_fsbd shape:", pivot_poa_fsbd.shape)
        print("pivot_poa_others shape:", pivot_poa_others.shape)

    else:
        print("\n[SKIP] POA disabled")

    # =========================
    # LND
    # =========================
    if RUN_LND:
        print("\n[5] Pull LND reports...")

        for segment_key in segment_keys:
            result_name = f"lnd_1_{segment_key}"

            lnd_results[result_name] = run_report(
                report_group="lnd",
                report_key="lnd_1",
                segment_key=segment_key,
                runtime_values=runtime_values,
                token=token,
            )

        print("\n[6] Reduce LND columns...")

        lnd_b2b_cc = reduce_lnd_columns(
            lnd_results.get("lnd_1_b2b_cc", pd.DataFrame())
        )
        lnd_fsbd = reduce_lnd_columns(
            lnd_results.get("lnd_1_fsbd", pd.DataFrame())
        )
        lnd_others = reduce_lnd_columns(
            lnd_results.get("lnd_1_others", pd.DataFrame())
        )

        print("lnd_b2b_cc shape:", lnd_b2b_cc.shape)
        print("lnd_fsbd shape:", lnd_fsbd.shape)
        print("lnd_others shape:", lnd_others.shape)

    else:
        print("\n[SKIP] LND disabled")

    # =========================
    # DUMP
    # =========================
    if DUMP_TRACKER:
        print("\n[7] Dump to tracker...")

        if RUN_POA:
            dump_poa_to_tracker(
                pivot_poa_b2b_cc=pivot_poa_b2b_cc,
                pivot_poa_fsbd=pivot_poa_fsbd,
                pivot_poa_others=pivot_poa_others,
            )

        if RUN_LND:
            dump_lnd_to_tracker(
                lnd_b2b_cc=lnd_b2b_cc,
                lnd_fsbd=lnd_fsbd,
                lnd_others=lnd_others,
            )
    else:
        print("\n[SKIP] DUMP_TRACKER disabled")

    if DUMP_SANGGAHAN:
        print("\n[8] Dump to sanggahan...")

        if RUN_POA:
            dump_poa_to_sanggahan(
                pivot_poa_b2b_cc=pivot_poa_b2b_cc,
                pivot_poa_fsbd=pivot_poa_fsbd,
                pivot_poa_others=pivot_poa_others,
            )

        if RUN_LND:
            dump_lnd_to_sanggahan(
                lnd_b2b_cc=lnd_b2b_cc,
                lnd_fsbd=lnd_fsbd,
                lnd_others=lnd_others,
            )
    else:
        print("\n[SKIP] DUMP_SANGGAHAN disabled")

    print("\n=== DAY 2 POA + LND DONE ===")

    return {
        "poa_results": poa_results,
        "lnd_results": lnd_results,
        "compiled_poa_b2b_cc": compiled_poa_b2b_cc,
        "compiled_poa_fsbd": compiled_poa_fsbd,
        "compiled_poa_others": compiled_poa_others,
        "pivot_poa_b2b_cc": pivot_poa_b2b_cc,
        "pivot_poa_fsbd": pivot_poa_fsbd,
        "pivot_poa_others": pivot_poa_others,
        "lnd_b2b_cc": lnd_b2b_cc,
        "lnd_fsbd": lnd_fsbd,
        "lnd_others": lnd_others,
    }


if __name__ == "__main__":
    run()
