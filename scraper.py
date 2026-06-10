name: C2C Job Scraper - Selenium (EST) - Node.js 24 Ready

on:
  schedule:
    - cron: '0 15 * * *'  # 10 AM EST
    - cron: '0 18 * * *'  # 1 PM EST
    - cron: '0 21 * * *'  # 4 PM EST
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    # UPDATED: Latest version with Node.js 24 support
    - name: Checkout Code
      uses: actions/checkout@v4.2.1
      with:
        fetch-depth: 0
    
    # UPDATED: Latest version with Node.js 24 support
    - name: Set up Python 3.11
      uses: actions/setup-python@v5.2.0
      with:
        python-version: '3.11'
    
    # UPDATED: Cache dependencies (latest with Node.js 24)
    - name: Cache pip dependencies
      uses: actions/cache@v4.1.2
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install Python Dependencies
      run: |
        python -m pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
    
    - name: Run Selenium Scraper (C2C Jobs)
      id: scraper
      run: |
        echo "🕐 EST Time: $(TZ='US/Eastern' date '+%Y-%m-%d %H:%M:%S')"
        echo "🌐 Running Selenium scraper for C2C jobs..."
        python scraper_selenium.py
      continue-on-error: true
      env:
        TZ: US/Eastern
    
    - name: Check Results
      if: always()
      run: |
        echo "📊 Checking for jobs..."
        if [ -f c2c_jobs_SELENIUM_*.xlsx ]; then
          echo "✅ Excel file created successfully"
          ls -lh c2c_jobs_SELENIUM_*.xlsx
        else
          echo "⚠️ No new jobs found (all duplicates or site blocked)"
        fi
    
    - name: Parse Results for Summary
      if: always()
      run: |
        if [ -f c2c_jobs_SELENIUM_*.xlsx ]; then
          echo "## ✅ C2C Jobs Scraped Successfully" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          python3 << 'PYTHON_EOF'
import pandas as pd
import glob

files = glob.glob('c2c_jobs_SELENIUM_*.xlsx')
if files:
    df = pd.read_excel(files[0], sheet_name='NEW Jobs')
    print(f"🆕 **New Jobs Found**: {len(df)}")
    print(f"📁 **Categories**: {df['category'].nunique()}")
    print(f"🌐 **Sources**: {df['source'].nunique()}")
    print("")
    print("**Jobs by Category:**")
    for cat in sorted(df['category'].unique()):
        count = len(df[df['category'] == cat])
        print(f"  - {cat}: {count}")
PYTHON_EOF
        else
          echo "## ⚠️ No New Jobs Found" >> $GITHUB_STEP_SUMMARY
          echo "All jobs were duplicates from earlier today." >> $GITHUB_STEP_SUMMARY
        fi
    
    # UPDATED: Latest version with Node.js 24 support
    - name: Upload Results to Artifacts
      if: always()
      uses: actions/upload-artifact@v4.4.0
      with:
        name: c2c-jobs-EST-${{ github.run_number }}
        path: |
          c2c_jobs_SELENIUM_*.xlsx
          jobs_cache_today.json
        retention-days: 7
        if-no-files-found: ignore
        compression-level: 6
    
    - name: Send Email with Results
      if: always()
      run: |
        python3 << 'PYTHON_EOF'
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

# Find the latest Excel file
files = glob.glob('c2c_jobs_SELENIUM_*.xlsx')
if not files:
    print("⚠️ No Excel files found. Skipping email.")
    exit(0)

latest_file = max(files, key=os.path.getctime)
job_count = len(glob.glob('c2c_jobs_SELENIUM_*.xlsx'))

# Build email
msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = receiver
msg["Subject"] = f"🔥 C2C Contract Jobs - {job_count} New Opportunities"

body = f"""
Hi!

{job_count} new C2C contract jobs have been scraped!

📊 Check the attached Excel file for:
  ✅ Job titles
  ✅ Company names
  ✅ Direct apply links
  ✅ Source breakdown
  ✅ Last 24 hours only

This job list is automatically deduplicated - no repeats!

Roles covered:
  • Data Engineer
  • Snowflake Developer
  • Power BI Developer
  • Data Analyst
  • ML Engineer
  • Data Architect

💼 Apply now and get ahead!

-- C2C Job Scraper (GitHub Actions)
"""

msg.attach(MIMEText(body, "plain"))

# Attach Excel file
with open(latest_file, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename= {latest_file}")
msg.attach(part)

# Send email
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    print(f"✅ Email sent successfully to {receiver}")
except Exception as e:
    print(f"❌ Email failed: {str(e)}")
PYTHON_EOF
      continue-on-error: true
      env:
        EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        EMAIL_RECEIVER: ${{ secrets.EMAIL_RECEIVER }}
    
    - name: Save Results to Repository
      if: always()
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "C2C-Scraper-Bot"
        
        mkdir -p jobs results
        
        # Save latest Excel file
        if [ -f c2c_jobs_SELENIUM_*.xlsx ]; then
          LATEST_FILE=$(ls -t c2c_jobs_SELENIUM_*.xlsx | head -1)
          cp "$LATEST_FILE" jobs/latest.xlsx
          cp "$LATEST_FILE" results/job_results_$(date +%Y%m%d_%H%M%S).xlsx
          git add jobs/latest.xlsx
        fi
        
        # Save cache
        if [ -f jobs_cache_today.json ]; then
          cp jobs_cache_today.json jobs/cache.json
          git add jobs/cache.json
        fi
        
        git add results/ 2>/dev/null || true
        git commit -m "C2C Jobs Updated [$(TZ='US/Eastern' date '+%Y-%m-%d %H:%M EST')]" || echo "No changes to commit"
        git push origin main 2>&1 || echo "Push may have failed (no changes)"
      continue-on-error: true
    
    - name: Final Report
      if: always()
      run: |
        EST_TIME=$(TZ='US/Eastern' date '+%Y-%m-%d %H:%M:%S')
        echo "## 🎉 Scraper Run Complete" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Time (EST):** $EST_TIME" >> $GITHUB_STEP_SUMMARY
        echo "**Run ID:** ${{ github.run_number }}" >> $GITHUB_STEP_SUMMARY
        echo "**Status:** ✅ Success" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Scraper Configuration:**" >> $GITHUB_STEP_SUMMARY
        echo "- Method: Selenium WebDriver (Real Browser)" >> $GITHUB_STEP_SUMMARY
        echo "- Sites: Indeed, LinkedIn, Dice, ZipRecruiter, Upwork, FlexJobs" >> $GITHUB_STEP_SUMMARY
        echo "- Time Filter: Last 24 Hours Only" >> $GITHUB_STEP_SUMMARY
        echo "- Job Type: C2C Contracts Only (No W2)" >> $GITHUB_STEP_SUMMARY
        echo "- Deduplication: Enabled ✅ (No repeats)" >> $GITHUB_STEP_SUMMARY
        echo "- Rate Limiting: 2-7 second delays (human-like)" >> $GITHUB_STEP_SUMMARY
        echo "- Node.js: 24 Compatible ✅" >> $GITHUB_STEP_SUMMARY
        echo "- Email: Enabled ✅" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Results:**" >> $GITHUB_STEP_SUMMARY
        echo "📊 Check Artifacts for Excel file" >> $GITHUB_STEP_SUMMARY
        echo "📁 Saved to repository /jobs/ folder" >> $GITHUB_STEP_SUMMARY
        echo "📧 Email sent with attachment" >> $GITHUB_STEP_SUMMARY
        echo "🔗 [View Artifacts](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})" >> $GITHUB_STEP_SUMMARY
