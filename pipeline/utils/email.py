# ============================================================
# utils/email.py — Kirim email notifikasi
# ============================================================

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL


def send_email(recipients: list, subject: str, body: str):
    """
    Kirim email ke list recipients.

    Args:
        recipients : list email penerima
        subject    : subject email
        body       : body email (plain text)
    """
    sender = EMAIL["sender"]
    # Password diambil dari environment variable (GitHub Secrets)
    password = os.environ.get("EMAIL_PASSWORD")

    if not password:
        raise ValueError("EMAIL_PASSWORD tidak ditemukan di environment variable!")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL["smtp_server"], EMAIL["smtp_port"]) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"Email terkirim ke: {', '.join(recipients)}")


def notify_day2(bulan: str):
    send_email(
        recipients=EMAIL["recipients"]["day2_notification"],
        subject=f"[Performance] Data {bulan} Sudah Tersedia",
        body=EMAIL["body"]["day2"].format(
            bulan=bulan,
            tracker_url=EMAIL.get("tracker_url", "-"),
            sanggahan_url=EMAIL.get("sanggahan_url", "-"),
            start_date="-",  # TODO: isi dari settings
            end_date="-",
        ),
    )


def notify_day6_fst(bulan: str):
    send_email(
        recipients=EMAIL["recipients"]["day6_fst"],
        subject=f"[Reminder] Data DWS {bulan} Belum Diupdate",
        body=EMAIL["body"]["day6_fst"].format(
            bulan=bulan,
            dws_url="-",  # TODO: isi dari settings
        ),
    )


def notify_day10_reviewer(bulan: str):
    send_email(
        recipients=EMAIL["recipients"]["day10_reviewer"],
        subject=f"[Action Required] Sanggahan {bulan} Siap Direview",
        body=EMAIL["body"]["day10_reviewer"].format(
            bulan=bulan,
            sanggahan_url="-",
        ),
    )


def notify_day14_reviewer(bulan: str):
    send_email(
        recipients=EMAIL["recipients"]["day14_reviewer"],
        subject=f"[Reminder] Sanggahan {bulan} Belum Selesai Direview",
        body=EMAIL["body"]["day14_reviewer"].format(
            bulan=bulan,
            sanggahan_url="-",
        ),
    )


def notify_day16_psp(bulan: str):
    send_email(
        recipients=EMAIL["recipients"]["day16_psp"],
        subject=f"[Performance] Data Final {bulan} Sudah Ready",
        body=EMAIL["body"]["day16_psp"].format(
            bulan=bulan,
            tracker_url="-",
            sanggahan_url="-",
            converter_url="-",
        ),
    )
