import subprocess
import csv
import os

# Configuration
PYTHON_EXE = "C:/Users/Alton/AppData/Local/Programs/Python/Python312/python.exe"
SCRAPER_PATH = "C:/TenderAgent/scraper.py"
EMAIL_PATH = "C:/TenderAgent/send_email.py"
CSV_PATH = "C:/TenderAgent/tenders.csv"

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {cmd}: {e.stderr}")
        return False

def main():
    print("🚀 Starting Daily Tender Scan...")
    
    # 1. Run Scraper
    if run_cmd(f'"{PYTHON_EXE}" {SCRAPER_PATH}'):
        print("✅ Scraper completed successfully.")
    else:
        print("❌ Scraper failed.")

    # 2. Process and Print Summary for Cron Output
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                tenders = list(reader)
            
            if tenders:
                # Sort by Priority (High first)
                tenders.sort(key=lambda x: x['Priority'], reverse=True)
                
                print("\n--- 📢 DAILY TENDER SUMMARY ---")
                for i, t in enumerate(tenders[:5], 1):
                    print(f"{i}. [{t['Priority']}] {t['Province']}: {t['Title']} (Closing: {t['Closing Date']})")
                print("------------------------------\n")
            else:
                print("\nNo matching tenders found for today.\n")
        except Exception as e:
            print(f"Error reading CSV: {e}")
    else:
        print("Tenders CSV not found.")

    # 3. Run Emailer
    print("Sending email notifications...")
    if run_cmd(f'"{PYTHON_EXE}" {EMAIL_PATH}'):
        print("✅ Email sent successfully.")
    else:
        print("❌ Email failed (Network/Auth issue).")

if __name__ == "__main__":
    main()
