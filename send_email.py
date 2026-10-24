import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
EMAIL_ADDRESS = "tenders@mecsolutions.co.za"
EMAIL_PASSWORD = "MEC@1solutionsT"
RECIPIENT_EMAIL = "tenders@mecsolutions.co.za"
INPUT_FILE = "C:/TenderAgent/tenders.csv"
SMTP_SERVER = "smtp.axxess.co.za"
SMTP_PORT = 25

def send_tenders_email():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tenders = list(reader)
    except FileNotFoundError:
        print("Tenders file not found. Run scraper.py first.")
        return

    if not tenders:
        print("No tenders to send.")
        return

    # Sort by priority (High first)
    tenders.sort(key=lambda x: x['Priority'], reverse=True)

    # Construct email body
    body = "Here are the latest low-barrier-entry tenders:\n\n"
    for t in tenders:
        body += f"Priority: {t['Priority']}\nProvince: {t['Province']}\nTitle: {t['Title']}\nClosing: {t['Closing Date']}\n{'-'*30}\n"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "🚀 New Low-Barrier Tenders Alert"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Using Port 25 with no encryption and plain authentication
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_tenders_email()
