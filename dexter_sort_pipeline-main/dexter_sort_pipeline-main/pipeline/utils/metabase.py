# ============================================================
# utils/metabase.py - Semua extract data dari Metabase
# Tidak ada transformasi di sini.
# ============================================================

import json
import os
from urllib.parse import quote

import pandas as pd
import requests

from config.settings import GSHEET
from utils.gsheet import get_cell_value


import os

from config.settings import GSHEET
from utils.gsheet import get_cell_value


def get_token() -> str:
    """
    Ambil token Metabase dari env dulu.
    Kalau tidak ada, fallback ke Google Sheet config.
    """
    env_token = (os.getenv("METABASE_TOKEN") or "").strip().strip("'").strip('"')
    if env_token:
        print("Using METABASE_TOKEN from environment.")
        return env_token

    print("METABASE_TOKEN not found in environment. Fallback to Google Sheet config...")

    config_sheet = GSHEET["config"]
    token = get_cell_value(
        sheet_id=config_sheet["sheet_id"],
        tab_name=config_sheet["tabs"]["main"],
        cell=config_sheet["token_cell"],
    )

    token = (token or "").strip().strip("'").strip('"')

    if not token:
        raise ValueError("Token Metabase kosong di environment dan config sheet.")

    print("Using token from Google Sheet config.")
    return token

def tarik_metabase(url, parameters, token, desc):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Metabase-Session": token,
    }

    payload = "parameters=" + quote(json.dumps(parameters))

    print(f"Pulling {desc} ...")

    r = requests.post(
        url,
        headers=headers,
        data=payload,
        timeout=300,
    )

    if r.status_code != 200:
        print(f"[{desc}] FAILED: {r.status_code} | {r.text[:500]}")
        return pd.DataFrame()

    try:
        data = r.json()
    except Exception as e:
        print(f"[{desc}] Invalid JSON response")
        print(repr(e))
        print(r.text[:500])
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    # =====================
    # Normal Metabase JSON API
    # Usually: list[dict]
    # =====================
    if isinstance(data, list):
        return pd.DataFrame(data)

    # =====================
    # Dict response
    # Could be error object or nested result format
    # =====================
    if isinstance(data, dict):
        print(
            f"[{desc}] Metabase response is dict. "
            f"Keys: {list(data.keys())}"
        )

        # =====================
        # Metabase error object
        # =====================
        if "error" in data or "error_type" in data:
            print(f"[{desc}] Metabase query error")
            print("status:", data.get("status"))
            print("error_type:", data.get("error_type"))
            print("class:", data.get("class"))
            print("error:", data.get("error"))

            if isinstance(data.get("data"), dict):
                print("data keys:", list(data["data"].keys()))

            stacktrace = data.get("stacktrace")
            if stacktrace:
                if isinstance(stacktrace, list):
                    print("stacktrace preview:")
                    print("\n".join(map(str, stacktrace[:5])))
                else:
                    print("stacktrace:", str(stacktrace)[:500])

            return pd.DataFrame()

        # {"data": [...]}
        if isinstance(data.get("data"), list):
            return pd.DataFrame(data["data"])

        # {"rows": [...]}
        if isinstance(data.get("rows"), list):
            return pd.DataFrame(data["rows"])

        # {"columns": [...], "rows": [...]}
        if "columns" in data and "rows" in data:
            cols = data.get("columns")
            rows = data.get("rows")

            if isinstance(cols, list) and isinstance(rows, list):
                try:
                    return pd.DataFrame(rows, columns=cols)
                except Exception as e:
                    print(f"[{desc}] Failed create dataframe from columns/rows")
                    print(repr(e))
                    return pd.DataFrame()

        # Metabase nested format sometimes:
        # {"data": {"cols": [...], "rows": [...]}}
        if isinstance(data.get("data"), dict):
            inner_data = data["data"]

            cols = inner_data.get("cols")
            rows = inner_data.get("rows")

            if isinstance(cols, list) and isinstance(rows, list):
                try:
                    col_names = [
                        col.get("name") if isinstance(col, dict) else str(col)
                        for col in cols
                    ]
                    return pd.DataFrame(rows, columns=col_names)
                except Exception as e:
                    print(f"[{desc}] Failed create dataframe from data.cols/data.rows")
                    print(repr(e))
                    return pd.DataFrame()

        print(f"[{desc}] Unexpected dict response. Returning empty dataframe.")
        return pd.DataFrame()

    print(f"[{desc}] Unexpected response type: {type(data)}")
    return pd.DataFrame()


def build_params(common_params, extra_params):
    return common_params + extra_params
