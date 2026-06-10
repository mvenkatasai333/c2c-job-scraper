#!/usr/bin/env python3
"""
Send C2C Jobs Excel via Email
"""
import os
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

sender = os.environ.get("EMAIL_SENDER", "")
password = os.environ.get("EMAIL_PASSWORD", "")
receiver = os.environ.get("EMAIL_RECEIVER", "")

if not all([sender, password, receiver]):
    print("⚠️ Email credentials not set. Skipping email.")
    exit(0)

files = glob.glob('c2c_jobs_*.xlsx')
if not files:
    print("⚠️ No Excel files found. Skipping email.")
    exit(0)

latest_file = max(files, key=os.path.getctime)

msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = receiver
msg["Subject"] = "🔥 C2C Contract Jobs - New Opportunities"

body = """Hi!

New C2C contract jobs have been found!

📊 Excel file includes:
  ✅ Job titles
  ✅ Company names
  ✅ Direct apply links
  ✅ No duplicates

Roles: Data Engineer, Snowflake, Power BI, Data Analyst, ML Engineer

💼 Apply now!

-- C2C Job Scraper
"""

msg.attach(MIMEText(body, "plain"))

with open(latest_file, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={latest_file}")
    msg.attach(part)

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    print(f"✅ Email sent to {receiver}")
except Exception as e:
    print(f"❌ Email failed: {str(e)}")
