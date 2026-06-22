# ============================================================
# main.py — Entry point pipeline
# Cek tanggal hari ini, lalu jalanin job yang sesuai
# ============================================================

from datetime import date
import importlib
import sys


JOB_SCHEDULE = {
    1:  "jobs.day1",
    2:  "jobs.day2",
    6:  "jobs.day6",
    10: "jobs.day10",
    14: "jobs.day14",
    15: "jobs.day15",
    16: "jobs.day16",
}


def run(day: int = None):
    """
    Jalanin job sesuai tanggal.

    Args:
        day: override tanggal (untuk testing). Kalau None, pakai tanggal hari ini.
    """
    today = day or date.today().day
    print(f"Pipeline jalan di tanggal: {today}")

    if today not in JOB_SCHEDULE:
        print(f"Tidak ada job untuk tanggal {today}. Pipeline selesai.")
        return

    module_path = JOB_SCHEDULE[today]
    print(f"Menjalankan: {module_path}")

    module = importlib.import_module(module_path)
    module.run()


if __name__ == "__main__":
    # Bisa di-override dari command line: python main.py 2
    override_day = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(override_day)
