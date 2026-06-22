# jobs/day15.py
from utils.gsheet import copy_range
from config.settings import GSHEET


def run():
    print("===== Kita Mulai Run Day 15 Review Sanggahan =====")

    # POA IV B2B All & B2C Cold -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["poa_iv_b2b_all_b2c_cold"],
        source_range="O3:U",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="C4",
    )
    print("===== POA IV B2B All & B2C Cold -> Tracker Done =====")

    # POA IV Keyshipper -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["poa_iv_keyshipper"],
        source_range="O3:U",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="P4",
    )
    print("===== POA IV Keyshipper -> Tracker Done =====")

    # POA IV Others -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["poa_iv_others"],
        source_range="O3:U",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="AC4",
    )
    print("===== POA IV Others -> Tracker Done =====")

    # LND B2B All & B2C Cold -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["lnd_rate_b2b_all_b2c_cold"],
        source_range="J3:L",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="AP4",
    )
    print("===== LND B2B All & B2C Cold -> Tracker Done =====")

    # LND Keyshipper -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["lnd_rate_keyshipper"],
        source_range="J3:L",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="AY4",
    )
    print("===== LND Keyshipper -> Tracker Done =====")

    # LND Others -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["lnd_rate_others"],
        source_range="J3:L",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="BH4",
    )
    print("===== LND Others -> Tracker Done =====")

    # DWS -> Tracker
    copy_range(
        source_sheet_id=GSHEET["sanggahan"]["sheet_id"],
        source_tab=GSHEET["sanggahan"]["tabs"]["dws"],
        source_range="M3:R",
        dest_sheet_id=GSHEET["tracker"]["sheet_id"],
        dest_tab=GSHEET["tracker"]["tabs"]["raw_data_all"],
        dest_start_cell="BO4",
    )
    print("===== DWS -> Tracker Done =====")

    print("===== Day 15 Done =====")


if __name__ == "__main__":
    run()
