# jobs/day6.py
from utils.gsheet import read_sheet, write_sheet
from config.settings import GSHEET


def run():
    print("====== Kita Kerjain Day 10 Buat RDO ya =========")

    df_rdo = read_sheet(
        GSHEET["rdo_comp"]["sheet_id"],
        GSHEET["rdo_comp"]["tabs"]["main"]
    )

    print("===== Ambil data dari RDO done =====")


    

    print("===== Mulai input RDO ke Tracker dulu ya =====")
    write_sheet(
        spreadsheet_id=GSHEET["tracker"]["sheet_id"],
        sheet_name=GSHEET["tracker"]["tabs"]["raw_data_compile"],
        df=df_rdo,
        start_cell="B6",
        include_header=False
    )
   
    print("===== Done Input RDO ke Tracker =====")


   



if __name__ == "__main__":
    run()
