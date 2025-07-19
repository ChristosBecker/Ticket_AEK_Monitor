import os
import time
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Load secrets from environment variables
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Target URL for AEK tickets
URL = "https://www.ticketmaster.gr/ticketmaster_se_2005795.html"

# Check every 15 minutes
CHECK_INTERVAL = 900  # seconds

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[{datetime.now()}] 📧 Email sent successfully.")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Failed to send email: {e}")

def check_for_tickets():
    try:
        print(f"[{datetime.now()}] 🔍 Checking for AEK tickets...")
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        found_links = [link["href"] for link in links if "aek" in link["href"].lower()]

        if found_links:
            message = "🎉 AEK Tickets Found!\n\nTickets available at:\n" + "\n".join(found_links)
            send_email("🎟️ AEK Tickets Alert!", message)
        else:
            print(f"[{datetime.now()}] ❌ No tickets found.")
    except Exception as e:
        print(f"[{datetime.now()}] ❗ Error during check: {e}")

if __name__ == "__main__":
    while True:
        check_for_tickets()
        time.sleep(CHECK_INTERVAL)
