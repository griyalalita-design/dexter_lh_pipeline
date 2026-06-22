"""
gsheet.py
---------
Responsibility: All Google Sheets operations.
Read, write, clear sheets. No transformation logic here.
"""

from __future__ import annotations

import json
import os
from typing import Iterable, List, Optional

import gspread
import pandas as pd

from config.settings import SERVICE_ACCOUNT_FILE


# --- Client helpers ---

def _get_client() -> gspread.Client:
    """
    Create gspread client from service account file or env var JSON.
    Priority:
      1) SERVICE_ACCOUNT_FILE (path)
      2) GSHEET_SERVICE_ACCOUNT_JSON (env var, raw JSON string)
    """
    if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        return gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    raw = os.getenv("GSHEET_SERVICE_ACCOUNT_JSON")
    if raw:
        info = json.loads(raw)
        return gspread.service_account_from_dict(info)

    raise FileNotFoundError(
        "Service account not found. Set SERVICE_ACCOUNT_FILE or GSHEET_SERVICE_ACCOUNT_JSON."
    )


def open_by_key(sheet_id: str) -> gspread.Spreadsheet:
    return _get_client().open_by_key(sheet_id)


def open_by_url(url: str) -> gspread.Spreadsheet:
    return _get_client().open_by_url(url)


# --- Core ops ---
def _a1(sheet_name, range_a1):
    safe_sheet_name = str(sheet_name).replace("'", "''")

    # Kalau nama tab simple tanpa spasi/simbol, tidak perlu quote
    if safe_sheet_name.replace("_", "").replace("-", "").isalnum():
        return f"{safe_sheet_name}!{range_a1}"

    return f"'{safe_sheet_name}'!{range_a1}"


def clear_range(spreadsheet_id: str, sheet_name: str, range_a1: str) -> None:
    """
    Clear a specific range (A1 notation) in a sheet tab.
    """
    wb = open_by_key(spreadsheet_id)
    wb.values_clear(_a1(sheet_name, range_a1))


def clear_sheet(spreadsheet_id: str, sheet_name: str) -> None:
    """
    Clear all data from a specific sheet tab.
    """
    wb = open_by_key(spreadsheet_id)
    worksheet = wb.worksheet(sheet_name)
    worksheet.clear()


def read_sheet(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    """
    Read data from a specific sheet tab and return as DataFrame.
    """
    wb = open_by_key(spreadsheet_id)
    worksheet = wb.worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)
    
def get_cell_value(sheet_id: str, tab_name: str, cell: str) -> str:
    """
    Read single cell value from a specific sheet tab.
    """
    wb = open_by_key(sheet_id)
    worksheet = wb.worksheet(tab_name)
    value = worksheet.acell(cell).value
    return (value or "").strip().strip("'").strip('"')


def write_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    df: pd.DataFrame,
    start_cell: str = "A1",
    include_header: bool = True,
) -> None:
    """
    Write a DataFrame to a specific sheet tab.
    """
    wb = open_by_key(spreadsheet_id)

    if include_header:
        values = [df.columns.tolist()] + df.values.tolist() if not df.empty else [df.columns.tolist()]
    else:
        values = df.values.tolist() if not df.empty else []

    if not values:
        return

    wb.values_update(
        _a1(sheet_name, start_cell),
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": values},
    )


def append_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    df: pd.DataFrame,
    start_cell: str = "A1",
) -> None:
    """
    Append a DataFrame to a sheet (no header by default).
    """
    wb = open_by_key(spreadsheet_id)
    values = df.values.tolist() if not df.empty else []
    if not values:
        return
    wb.values_append(
        _a1(sheet_name, start_cell),
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": values},
    )


def copy_range(
    source_sheet_id: str,
    source_tab: str,
    source_range: str,
    dest_sheet_id: str,
    dest_tab: str,
    dest_start_cell: str,
) -> None:
    """
    Copy values from one sheet range to another.
    """
    src = open_by_key(source_sheet_id)
    dest = open_by_key(dest_sheet_id)

    values = src.values_get(_a1(source_tab, source_range)).get("values", [])
    if not values:
        return

    dest.values_update(
        _a1(dest_tab, dest_start_cell),
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": values},
    )


def copy_columns(
    source_sheet_id: str,
    source_tab: str,
    target_sheet_id: str,
    target_tab: str,
    columns: List[str],
    start_cell: str = "A1",
) -> None:
    """
    Copy selected columns by header name from source to target.
    """
    df = read_sheet(source_sheet_id, source_tab)
    if df.empty:
        return
    existing = [c for c in columns if c in df.columns]
    if not existing:
        return
    write_sheet(target_sheet_id, target_tab, df[existing], start_cell=start_cell)


def mark_sanggahan_open(spreadsheet_id: str, sheet_name: str) -> None:
    """
    Mark all sanggahan rows as 'open' in the tracker.
    TODO: Implement real logic if needed.
    """
    # Placeholder: implement column-based update when schema is final
    return

def read_sheet_allow_duplicate_headers(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    ws = open_by_key(spreadsheet_id).worksheet(sheet_name)
    values = ws.get_all_values()

    if not values:
        return pd.DataFrame()

    raw_header = values[0]
    data_rows = values[1:]

    headers = []
    seen = {}

    for col in raw_header:
        col = str(col).strip()

        if col == "":
            col = "blank"

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0

        headers.append(col)

    return pd.DataFrame(data_rows, columns=headers)

import pandas as pd

def read_sheet_with_header_row(
    spreadsheet_id: str,
    sheet_name: str,
    header_row: int,
) -> pd.DataFrame:
    ws = open_by_key(spreadsheet_id).worksheet(sheet_name)
    values = ws.get_all_values()

    if not values:
        return pd.DataFrame()

    header_idx = header_row - 1

    if len(values) <= header_idx:
        raise ValueError(f"Sheet tidak punya header_row={header_row}")

    raw_header = values[header_idx]
    data_rows = values[header_idx + 1:]

    headers = []
    seen = {}

    for col in raw_header:
        col = str(col).strip()

        if col == "":
            col = "blank"

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0

        headers.append(col)

    return pd.DataFrame(data_rows, columns=headers)


def flatten_master_tracker(df_master: pd.DataFrame, snapshot_month: str) -> pd.DataFrame:
    kpi_mapping = [
        {
            "kpi": "POA - IV | B2B All & B2C Cold",
            "value_col": "POA - IV | B2B All & B2C Cold",
            "tier_col": "Tier",
        },
        {
            "kpi": "POA - IV | Keyshipper",
            "value_col": "POA - IV | Keyshipper",
            "tier_col": "Tier_1",
        },
        {
            "kpi": "POA - IV | Others",
            "value_col": "POA - IV | Others",
            "tier_col": "Tier_2",
        },
        {
            "kpi": "LnD Rate | B2B All & B2C Cold",
            "value_col": "LnD Rate | B2B All & B2C Cold",
            "tier_col": "Tier_3",
        },
        {
            "kpi": "LnD Rate | Keyshipper",
            "value_col": "LnD Rate | Keyshipper",
            "tier_col": "Tier_4",
        },
        {
            "kpi": "LnD Rate | Others",
            "value_col": "LnD Rate | Others",
            "tier_col": "Tier_5",
        },
        {
            "kpi": "DWS",
            "value_col": "DWS",
            "tier_col": "Tier_6",
        },
        {
            "kpi": "CPP",
            "value_col": "CPP",
            "tier_col": "Tier_7",
        },
    ]

    rows = []

    df = df_master.copy()
    df.columns = df.columns.astype(str).str.strip()

    if "Hub" not in df.columns:
        raise ValueError(f"Kolom Hub tidak ditemukan. Kolom tersedia: {df.columns.tolist()}")

    for _, row in df.iterrows():
        hub = str(row.get("Hub", "")).strip()

        if not hub or hub.lower() in ["", "nan"]:
            continue

        for item in kpi_mapping:
            value_col = item["value_col"]
            tier_col = item["tier_col"]

            if value_col not in df.columns:
                print(f"[SKIP] value_col tidak ada: {value_col}")
                continue

            rows.append({
                "snapshot_month": snapshot_month,
                "hub": hub,
                "kpi": item["kpi"],
                "value": row.get(value_col, ""),
                "tier": row.get(tier_col, ""),
            })

    return pd.DataFrame(rows)
