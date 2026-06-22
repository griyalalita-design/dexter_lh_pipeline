# jobs/day17.py
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config.settings import SERVICE_ACCOUNT_FILE, ARCHIVE_CONFIG


def get_prev_month_label() -> str:
    """
    Return previous month label like 'Aug 25'
    """
    now = datetime.today()
    first_of_this_month = now.replace(day=1)
    last_of_prev_month = first_of_this_month - timedelta(days=1)

    mons = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    mon = mons[last_of_prev_month.month - 1]
    yy = str(last_of_prev_month.year)[-2:]
    return f"{mon} {yy}"


def get_google_creds():
    """
    Build credentials from:
    1) SERVICE_ACCOUNT_FILE
    2) GSHEET_SERVICE_ACCOUNT_JSON env var
    """
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        return Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=scopes
        )

    raw = os.getenv("GSHEET_SERVICE_ACCOUNT_JSON")
    if raw:
        info = json.loads(raw)
        return Credentials.from_service_account_info(
            info,
            scopes=scopes
        )

    raise FileNotFoundError(
        "Service account not found. Set SERVICE_ACCOUNT_FILE or GSHEET_SERVICE_ACCOUNT_JSON."
    )


def get_drive_service(creds):
    return build("drive", "v3", credentials=creds)


def get_sheets_service(creds):
    return build("sheets", "v4", credentials=creds)


def archive_file(drive_service, source_file_id: str, target_folder_id: str) -> tuple[str, str]:
    """
    Copy a Google file to archive folder with previous month suffix.
    Returns:
        (new_file_id, new_file_name)
    """
    src_file = drive_service.files().get(
        fileId=source_file_id,
        fields="id,name"
    ).execute()

    suffix = f" - {get_prev_month_label()}"
    new_name = f"{src_file['name']}{suffix}"

    copied_file = drive_service.files().copy(
        fileId=source_file_id,
        body={
            "name": new_name,
            "parents": [target_folder_id]
        },
        fields="id,name"
    ).execute()

    return copied_file["id"], copied_file["name"]


def convert_all_sheets_to_values(sheets_service, spreadsheet_id: str) -> None:
    """
    Replace formulas with displayed values in all tabs of the copied spreadsheet.
    This makes the archive a true snapshot.
    """
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    sheets = spreadsheet.get("sheets", [])

    for sheet in sheets:
        sheet_name = sheet["properties"]["title"]
        print(f"===== Convert to values: {sheet_name} =====")

        # get displayed values (not formulas)
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueRenderOption="FORMATTED_VALUE"
        ).execute()

        values = result.get("values", [])

        if not values:
            print(f"Sheet {sheet_name} kosong, skip.")
            continue

        # write back as raw values only
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption="RAW",
            body={"values": values}
        ).execute()

        print(f"===== Done convert: {sheet_name} =====")


def run():
    print("===== Kita Mulai Run Day 17 Archive =====")

    creds = get_google_creds()
    drive_service = get_drive_service(creds)
    sheets_service = get_sheets_service(creds)

    for label, cfg in ARCHIVE_CONFIG.items():
        print(f"\n===== Archive {label} mulai =====")

        new_file_id, new_file_name = archive_file(
            drive_service=drive_service,
            source_file_id=cfg["source_file_id"],
            target_folder_id=cfg["target_folder_id"],
        )

        print(f"Archive success: {new_file_name} (ID: {new_file_id})")

        convert_all_sheets_to_values(
            sheets_service=sheets_service,
            spreadsheet_id=new_file_id
        )

        print(f"===== Archive {label} selesai =====")

    print("\n===== Day 17 Archive Done =====")


if __name__ == "__main__":
    run()
