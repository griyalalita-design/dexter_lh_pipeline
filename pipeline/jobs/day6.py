# jobs/day6.py
from utils.gsheet import read_sheet, write_sheet
from config.settings import GSHEET


def run():
    print("====== Kita Kerjain Day 6 Buat DWS ya =========")

    df_dws = read_sheet(
        GSHEET["dws"]["sheet_id"],
        GSHEET["dws"]["tabs"]["main"]
    )

    print("===== Ambil data dari DWS done =====")

    print("===== Mulai input ke Tracker dulu ya =====")
    write_sheet(
        spreadsheet_id=GSHEET["tracker"]["sheet_id"],
        sheet_name=GSHEET["tracker"]["tabs"]["raw_data_all"],
        df=df_dws,
        start_cell="BO4",
        include_header=False
    )
    print("===== Done Input ke Tracker =====")

    print("===== Mulai Input ke Sanggahan ya =====")
    write_sheet(
        spreadsheet_id=GSHEET["sanggahan"]["sheet_id"],
        sheet_name=GSHEET["sanggahan"]["tabs"]["dws"],
        df=df_dws,
        start_cell="A3",
        include_header=False
    )
    print("===== Done Input ke Sanggahan =====")


if __name__ == "__main__":
    run()
