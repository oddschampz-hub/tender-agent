import os
import csv
import base64
import requests

# --- CONFIGURATION ---
API_KEY = os.environ.get("RESEND_API_KEY")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
FROM_EMAIL = "onboarding@resend.dev" # Must use this for free tier!
INPUT_FILE = "tenders.csv"

def send_tenders_email():
    if not API_KEY or not RECIPIENT_EMAIL:
        print("Error: RESEND_API_KEY or RECIPIENT_EMAIL environment variables not set.")
        return

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
    tenders.sort(key=lambda x: x.get('Priority', 'Low'), reverse=True)

    # Construct email body
    body = "Here are the latest low-barrier-entry tenders:\n\n"
    for t in tenders:
        body += f"Priority: {t.get('Priority', 'N/A')}\n"
        body += f"Province: {t.get('Province', 'N/A')}\n"
        body += f"Title: {t.get('Title', 'N/A')}\n"
        body += f"Closing: {t.get('Closing Date', 'N/A')}\n"
        body += "-" * 30 + "\n"

    # Read file for attachment and base64 encode it
    try:
        with open(INPUT_FILE, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading file for attachment: {e}")
        return

    # Prepare Resend API request
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": FROM_EMAIL,
        "to": [RECIPIENT_EMAIL],
        "subject": "New Low-Barrier Tenders Alert",
        "text": body,
        "attachments": [
            {
                "filename": "tenders.csv",
                "content": encoded_content
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Email sent successfully via Resend API!")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    send_tenders_email()
