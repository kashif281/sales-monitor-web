# Directive: Daily Retail Monitor and Alert

## Goal
Scrape retail sales data from selected brands (Proof of Concept: Khaadi) and placeholder data for others, then send an email alert with the top 10 discounts.

## Inputs
- Brand lists (Hardcoded in script)
- SMTP Configuration (from `.env`)

## Tools / Scripts
- `execution/scrape_retailers.py`
- `execution/send_email_alert.py`
- `execution/run_daily_monitor.py` (Orchestrator)

## Process
1.  **Scrape**: Run `execution/scrape_retailers.py`.
    - Attempts to scrape real data from Khaadi.
    - Generates placeholder data for other brands.
    - Outputs to `.tmp/live_retail_sales.csv`.
2.  **Email**: Run `execution/send_email_alert.py`.
    - Reads `.tmp/live_retail_sales.csv`.
    - Sorts by discount.
    - Takes top 10.
    - Formats HTML email.
    - Sends via SMTP to `ALERT_EMAIL_TO`.

## Output
- File: `.tmp/live_retail_sales.csv`
- Email: Sent to configured address.

## Edge Cases
- Scraper failure: Should log error and potentially skip that brand (or use placeholder fallback).
- SMTP failure: Should log error to console.
