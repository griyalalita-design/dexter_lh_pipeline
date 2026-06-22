from __future__ import annotations

import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from utils.gsheet import read_sheet, get_cell_value
from config.settings import GSHEET


SENDER_DISPLAY_NAME = "ID BI-Reporting"
SENDER_ALIAS_EMAIL = "id-bi-reporting@ninjavan.co"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# hardcode links
# METABASE_URL = "https://docs.google.com/spreadsheets/d/10jwwERVKLvdrk7tkmqVXeZHGp3Q1lV_2IjFsc6fXQhQ/edit?gid=26110973#gid=26110973"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdgGuMdd39VF_cSJQ8XOVzK_tG24Y2Ue1HQR8FZJhh3I2Torw/viewform"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/176DKB0gr532W6t9WjTXSrkByDa8wYNghrS0w_pZ37yw/edit?gid=390142677#gid=390142677"


def get_previous_month_label() -> str:
    months_id = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    prev_month_date = datetime.today().replace(day=1) - timedelta(days=1)
    return f"{months_id[prev_month_date.month - 1]} {prev_month_date.year}"


def is_recipient_format(value: str) -> bool:
    value = str(value or "").strip()

    pattern_with_name = r'^.+<[^<>\s@]+@[^<>\s@]+\.[^<>\s@]+>$'
    pattern_email_only = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

    return bool(
        re.match(pattern_with_name, value) or
        re.match(pattern_email_only, value)
    )


def get_recipients_from_sheet(spreadsheet_id: str, sheet_name: str) -> list[str]:
    df = read_sheet(spreadsheet_id, sheet_name)
    if df.empty:
        return []

    first_col = df.columns[0]
    values = df[first_col].astype(str).str.strip().tolist()

    recipients = [x for x in values if is_recipient_format(x)]

    seen = set()
    uniq = []
    for r in recipients:
        if r not in seen:
            seen.add(r)
            uniq.append(r)

    return uniq


def get_email_sender_from_config():
    config_sheet = GSHEET["config"]

    email_sender = get_cell_value(
        sheet_id=config_sheet["sheet_id"],
        tab_name=config_sheet["tabs"]["main"],
        cell="B14",
    )

    app_password_sender = get_cell_value(
        sheet_id=config_sheet["sheet_id"],
        tab_name=config_sheet["tabs"]["main"],
        cell="C14",
    )

    if not email_sender:
        raise ValueError("Email sender kosong di config sheet (B14).")
    if not app_password_sender:
        raise ValueError("App password sender kosong di config sheet (C14).")

    return email_sender, app_password_sender


def build_html_sort_email(
    period_label: str,
    tracker_url: str,
    form_url: str,
    template_url: str,
) -> str:
    blue_color = "#1a73e8"
    red_color = "#c62828"
    link_common_style = f'style="color:{blue_color};text-decoration:underline;font-weight:600"'
    link_red_style = f'style="color:{red_color};text-decoration:underline;font-weight:700"'

    tracker_html = f'<a href="{tracker_url}" target="_blank" {link_common_style}>ID SORT KPI Tracker LINK</a>'
    form_html = f'<a href="{form_url}" target="_blank" {link_red_style}>LINK FORM SANGGAHAN</a>'
    template_html = f'<a href="{template_url}" target="_blank" {link_common_style}>LINK TEMPLATE</a>'

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 13.5px; color: #222; line-height: 1.55;">
      <p>Dear all,</p>

      <p>Tracker Linehaul KPI untuk periode <b>{period_label}</b> dapat diakses pada link berikut: {tracker_html}</p>

      <p><b>NOTE:</b></p>
      <ul>
        <li>Raw data dalam perhitungan tracker akan parallel diisi setelah email terkirim.</li>
        <li>Sanggahan untuk Tracker KPI maksimal dilakukan sampai tanggal <b>10 setiap bulannya.</b></li>
        <li>Sanggahan dapat langsung dikirimkan melalui form berikut:({form_html})</li>
        <li><b>Wajib menggunakan template</b>yang sudah disediakan pada link terkait ({template_html}) dengan mengisi raw data dan summary secara lengkap. Jika tidak sesuai, sanggahan ditolak.</li>
        <li><b>Selain data dari Metabase, sanggahan akan ditolak.</b></li>
        <li>Mohon isi data dengan lengkap dan jelas untuk memudahkan tim dalam validasi sanggahan. Jika terdapat sanggahan melalui email maka sanggahan tidak akan diterima.</li>
      </ul>


      <p>Terima kasih.</p>
      <p>Regards,<br><b>BI-Reporting</b></p>
    </body>
    </html>
    """


def build_plain_text(period_label: str) -> str:
    return (
        f"Dear all,\n\n"
        f"Berikut adalah email SORT KPI untuk periode {period_label}.\n\n"
        f"Regards,\n"
        f"BI-Reporting"
    )


def send_email_chunked(
    smtp_user: str,
    smtp_password: str,
    to_recipients: list[str],
    subject: str,
    html_body: str,
    plain_body: str,
    chunk_size: int = 50,
) -> None:
    context = ssl.create_default_context()

    for i in range(0, len(to_recipients), chunk_size):
        chunk = to_recipients[i:i + chunk_size]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SENDER_DISPLAY_NAME} <{SENDER_ALIAS_EMAIL}>"
        msg["To"] = ", ".join(chunk)

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, chunk, msg.as_string())

        print(f"Sent chunk {i // chunk_size + 1}: {len(chunk)} recipients")


def run():
    print("=== DAY 2 EMAIL START ===")

    smtp_user, smtp_password = get_email_sender_from_config()

    recipients = get_recipients_from_sheet(
        GSHEET["tracker"]["sheet_id"],
        GSHEET["tracker"]["tabs"]["recipients"]
    )

    if not recipients:
        raise ValueError("Tab Recipients kosong atau tidak ada recipient valid.")

    period_label = get_previous_month_label()
    subject = f"(ID) Linehaul KPI Progressive Tiering - {period_label}"

    html_body = build_html_sort_email(
        period_label=period_label,
        tracker_url=GSHEET["tracker"]["url"],
        form_url=FORM_URL,
        template_url=TEMPLATE_URL,
    )

    plain_body = build_plain_text(period_label)

    print(f"Recipients count: {len(recipients)}")
    print(f"Subject: {subject}")

    send_email_chunked(
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        to_recipients=recipients,
        subject=subject,
        html_body=html_body,
        plain_body=plain_body,
        chunk_size=50,
    )

    print("=== DAY 2 EMAIL DONE ===")


if __name__ == "__main__":
    run()
