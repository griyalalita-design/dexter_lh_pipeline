# jobs/day10.py 
from utils.gsheet import read_sheet, write_sheet
from config.settings import GSHEET


def run():
    print("===== Kita Mulai Run Day 10 CPP =====")

    df_cpp = read_sheet(
        GSHEET["cpp"]["sheet_id"],
        GSHEET["cpp"]["tabs"]["main"]
    )
    print("===== Ambil Data CPP Done =====")
    print(f"CPP shape: {df_cpp.shape}")

    print("===== Input ke Tracker =====")
    write_sheet(
        spreadsheet_id=GSHEET["tracker"]["sheet_id"],
        sheet_name=GSHEET["tracker"]["tabs"]["raw_data_cost"],
        df=df_cpp,
        start_cell="B3",
        include_header=False
    )
    print("===== Input Data ke Tracker Done =====")

    print("===== Input CPP ke Sanggahan =====")
    write_sheet(
        spreadsheet_id=GSHEET["sanggahan"]["sheet_id"],
        sheet_name=GSHEET["sanggahan"]["tabs"]["cpp"],
        df=df_cpp,
        start_cell="A3",
        include_header=False
    )
    print("===== Input CPP ke Sanggahan Done =====")


if __name__ == "__main__":
    run()
