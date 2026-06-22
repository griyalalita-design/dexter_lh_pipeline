from datetime import datetime

from config.settings import GSHEET

import pandas as pd

from utils.gsheet import (
    read_sheet,
    read_sheet_with_header_row,
    flatten_master_tracker,
    write_sheet,
)



def get_snapshot_month() -> str:
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    today = datetime.today()

    if today.month == 1:
        month_num = 12
        year = today.year - 1
    else:
        month_num = today.month - 1
        year = today.year

    return f"{months[month_num - 1]}-{year}"


def run():
    print("=== MoM flatten data mulai ===")

    df_master = read_sheet_with_header_row(
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["master_tracker_by_hub"],
        header_row=6,
    )

    print("Master tracker shape:", df_master.shape)
    print("Columns:", df_master.columns.tolist())

    snapshot_month = get_snapshot_month()
    print("Snapshot month:", snapshot_month)

    df_flatten = flatten_master_tracker(
        df_master,
        snapshot_month,
    )

    print("Flatten shape:", df_flatten.shape)
    print(df_flatten.head(20).to_string(index=False))

    recap_sheet_id = GSHEET["lm_mom_recap"]["sheet_id"]
    recap_tab = GSHEET["lm_mom_recap"]["tabs"]["monthly_snapshot"]

    try:
        df_existing = read_sheet(
            recap_sheet_id,
            recap_tab,
        )
    except Exception:
        df_existing = pd.DataFrame()

    if df_existing.empty:
        df_final = df_flatten.copy()
    else:
        df_final = pd.concat(
            [df_existing, df_flatten],
            ignore_index=True,
        )

    write_sheet(
        spreadsheet_id=recap_sheet_id,
        sheet_name=recap_tab,
        df=df_final,
        start_cell="A1",
        include_header=True,)

    print("=== MoM flatten selesai dan dumped ke recap ===")

    return df_flatten


if __name__ == "__main__":
    run()
