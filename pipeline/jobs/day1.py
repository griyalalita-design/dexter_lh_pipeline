# ============================================================
# jobs/day1.py - Tanggal 1: Cleansing + Update Key Shipper
# File ini hanya orkestasi, logic ada di utils/
# ============================================================

from config.settings import GSHEET
from utils.gsheet import clear_range, open_by_key, read_sheet
from utils.transform import get_last_month_range
import pandas as pd


def _iter_ranges(value):
    if isinstance(value, dict):
        return list(value.values())
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        return [value]
    return []


def _ranges_for_tab(clear_ranges, tab_key):
    if isinstance(clear_ranges, dict):
        return _iter_ranges(clear_ranges.get(tab_key, []))
    return _iter_ranges(clear_ranges)


# ===========Buat Narik Data Key Shipper PNS ========================== #
def _read_sheet_header_row2(sheet_id: str, tab_name: str) -> pd.DataFrame:
    """
    Read sheet where header is on row 2 (index 1).
    """
    ws = open_by_key(sheet_id).worksheet(tab_name)
    all_values = ws.get_all_values()
    if len(all_values) < 2:
        raise ValueError("Sheet kurang dari 2 baris - header row 2 tidak ada.")

    raw_header = all_values[1]
    data_rows = all_values[2:]

    cleaned = []
    occ = {}
    for h in raw_header:
        h0 = (h or "").strip()
        if h0 in occ:
            occ[h0] += 1
            h0 = f"{h0}_{occ[h0]}"
        else:
            occ[h0] = 0
        cleaned.append(h0)

    return pd.DataFrame(data_rows, columns=cleaned)


def _update_key_shipper_from_pns() -> None:
    """
    Update Key Shipper sheet from PNS compile list.
    """
    if "pns" not in GSHEET:
        raise ValueError("Config GSHEET['pns'] belum diisi.")
    if "key_shipper" not in GSHEET:
        raise ValueError("Config GSHEET['key_shipper'] belum diisi.")

    pns = GSHEET["pns"]
    key = GSHEET["key_shipper"]

    # ✅ pakai read_sheet (header row 1)
    df = read_sheet(
        pns["sheet_id"],
        pns["tabs"]["compile"]
    )
    df.columns = df.columns.astype(str).str.strip()

    col_global = pns["columns"]["global_id"]   # "Shipper ID"
    col_cat = pns["columns"]["category"]       # "Type"

    # ✅ validasi kolom
    missing_cols = [c for c in [col_global, col_cat] if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Kolom PNS tidak ditemukan: {missing_cols}. "
            f"Kolom tersedia: {df.columns.tolist()}"
        )

    # ✅ filter ID valid (buang NA, teks aneh, dll)
    valid_mask = pd.to_numeric(
        df[col_global].replace(r"^\s*#?N/?A.*$", pd.NA, regex=True),
        errors="coerce"
    ).notna()

    df = df[valid_mask].copy()

    # ✅ ambil kolom yang dibutuhkan
    key_df = df[[col_global, col_cat]].copy()

    # formatting
    key_df[col_global] = pd.to_numeric(key_df[col_global], errors="coerce").astype(int)
    key_df[col_cat] = key_df[col_cat].astype(str).str.strip()

    # optional: drop duplicates biar bersih
    key_df = key_df.drop_duplicates()

    # ✅ write ke gsheet
    ws = open_by_key(key["sheet_id"]).worksheet(key["tabs"]["main"])

    clear_range(
        key["sheet_id"],
        key["tabs"]["main"],
        key["clear_range"]
    )

    ws.update(
        key["start_cell"],
        key_df.values.tolist()
    )

    print(f"✅ Key Shipper updated: {len(key_df)} rows")


# =================== Buat Cleaning Data Tracker dan Sanggahan ========================== #
def run():
    # _, _, bulan = get_last_month_range()
    # print(f"=== DAY 1 - Persiapan data bulan {bulan} ===")

    # STEP 1: Cleansing Tracker
    print("\n[1/2] Cleansing tracker...")

    tracker_id = GSHEET["tracker"]["sheet_id"]

    # Clear Raw Data [All]
    raw_all_tab = GSHEET["tracker"]["tabs"]["raw_data_compile"]
    raw_all_ranges = _iter_ranges(GSHEET["tracker"].get("clear_ranges", {}).get("raw_data_compile", []))
    for rng in raw_all_ranges:
        clear_range(tracker_id, raw_all_tab, rng)


    # STEP 2: Update Key Shipper dari PNS
    print("\n[2/2] Update Key Shipper dari PNS...")
    _update_key_shipper_from_pns()

    print("\nDay 1 selesai! Tracker & sanggahan sudah bersih, Key Shipper updated.")


if __name__ == "__main__":
    run()
