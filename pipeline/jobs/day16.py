from utils.gsheet import copy_range
from config.settings import GSHEET


def run():
    print("===== Kita Mulai Run Day 16 =====")

    copy_range(
        source_sheet_id=GSHEET["tracker"]["sheet_id"],
        source_tab=GSHEET["tracker"]["tabs"]["master_tracker_by_hub"],
        source_range="A7:Q",
        dest_sheet_id=GSHEET["converter"]["sheet_id"],
        dest_tab=GSHEET["converter"]["tabs"]["master_tracker_by_hub"],
        dest_start_cell="A7",
    )
    print("===== Copy summary tracker ke converter done =====")

    copy_range(
        source_sheet_id=GSHEET["staff_list"]["sheet_id"],
        source_tab=GSHEET["staff_list"]["tabs"]["main"],
        source_range="A2:E",
        dest_sheet_id=GSHEET["converter"]["sheet_id"],
        dest_tab=GSHEET["converter"]["tabs"]["staff_list"],
        dest_start_cell="B2",
    )
    print("===== Copy staff list ke converter done =====")


if __name__ == "__main__":
    run()
