# jobs/day_mom.py

import pandas as pd

from config.settings import GSHEET
from utils.gsheet import read_sheet, write_sheet


ID_COLS = ["snapshot_month", "hub"]

EXCLUDE_COLS = [
    "snapshot_month",
    "hub",
]

TIER_COL_KEYWORDS = [
    "tier",
]


def clean_numeric(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "" or value.upper() in ["#DIV/0!", "#N/A", "N/A", "NULL"]:
        return None

    is_percent = "%" in value

    value = (
        value
        .replace("%", "")
        .replace(",", "")
        .strip()
    )

    try:
        num = float(value)
        return num
    except Exception:
        return None


def get_numeric_kpi_cols(df: pd.DataFrame) -> list[str]:
    kpi_cols = []

    for col in df.columns:
        col_lower = str(col).lower()

        if col in EXCLUDE_COLS:
            continue

        if any(keyword in col_lower for keyword in TIER_COL_KEYWORDS):
            continue

        kpi_cols.append(col)

    return kpi_cols


def build_mom_analysis(df_snapshot: pd.DataFrame) -> pd.DataFrame:
    df = df_snapshot.copy()
    df.columns = df.columns.astype(str).str.strip()

    required_cols = ["snapshot_month", "hub"]
    missing_cols = [c for c in required_cols if c not in df.columns]

    if missing_cols:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing_cols}")

    months = sorted(df["snapshot_month"].dropna().astype(str).unique())

    if len(months) < 2:
        raise ValueError(
            f"Butuh minimal 2 bulan untuk MoM comparison. Bulan tersedia: {months}"
        )

    previous_month = months[-2]
    current_month = months[-1]

    print(f"Previous month: {previous_month}")
    print(f"Current month : {current_month}")

    df_prev = df[df["snapshot_month"].astype(str) == previous_month].copy()
    df_curr = df[df["snapshot_month"].astype(str) == current_month].copy()

    kpi_cols = get_numeric_kpi_cols(df)

    print("KPI columns:")
    for col in kpi_cols:
        print(f"- {col}")

    for col in kpi_cols:
        df_prev[col] = df_prev[col].apply(clean_numeric)
        df_curr[col] = df_curr[col].apply(clean_numeric)

    compare = df_curr.merge(
        df_prev,
        on="hub",
        suffixes=("_current", "_previous"),
        how="inner",
    )

    rows = []

    for _, row in compare.iterrows():
        hub = row["hub"]

        for kpi in kpi_cols:
            current_value = row.get(f"{kpi}_current")
            previous_value = row.get(f"{kpi}_previous")

            if pd.isna(current_value) or pd.isna(previous_value):
                continue

            delta = current_value - previous_value

            rows.append({
                "current_month": current_month,
                "previous_month": previous_month,
                "hub": hub,
                "kpi": kpi,
                "previous_value": previous_value,
                "current_value": current_value,
                "delta": delta,
                "abs_delta": abs(delta),
                "movement": (
                    "Improve" if delta > 0
                    else "Worsen" if delta < 0
                    else "No Change"
                ),
            })

    df_mom = pd.DataFrame(rows)

    if df_mom.empty:
        return df_mom

    df_mom = df_mom.sort_values(
        ["kpi", "abs_delta"],
        ascending=[True, False],
    ).reset_index(drop=True)

    return df_mom


def run():
    print("=== MoM Analysis Start ===")

    recap_sheet_id = GSHEET["lm_mom_recap"]["sheet_id"]
    monthly_snapshot_tab = GSHEET["lm_mom_recap"]["tabs"]["monthly_snapshot"]
    mom_analysis_tab = GSHEET["lm_mom_recap"]["tabs"]["mom_analysis"]

    df_snapshot = read_sheet(
        recap_sheet_id,
        monthly_snapshot_tab,
    )

    print("Monthly Snapshot shape:", df_snapshot.shape)
    print("Columns:", df_snapshot.columns.tolist())

    df_mom = build_mom_analysis(df_snapshot)

    print("MoM Analysis shape:", df_mom.shape)

    if not df_mom.empty:
        print(df_mom.head(30).to_string(index=False))

    write_sheet(
        spreadsheet_id=recap_sheet_id,
        sheet_name=mom_analysis_tab,
        df=df_mom,
        start_cell="A1",
        include_header=True,
    )

    print("=== MoM Analysis Done ===")

    return df_mom


if __name__ == "__main__":
    run()
