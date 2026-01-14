import os
import subprocess
import sys

def main():
    print("--- Starting Daily Retail Monitor ---")
    
    # 1. Run Scraper
    print("Step 1: Running Scraper...")
    result = subprocess.run([sys.executable, "execution/scrape_retailers.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Scraper failed with error:\n{result.stderr}")
        return

    # 2. Run Emailer
    print("Step 2: Sending Email...")
    result = subprocess.run([sys.executable, "execution/send_email_alert.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Emailer failed with error:\n{result.stderr}")
        return

    print("--- Monitor Run Complete ---")

if __name__ == "__main__":
    main()
