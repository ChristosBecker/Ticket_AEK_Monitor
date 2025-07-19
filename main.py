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

# Target URL and interval
URL = "https://www.ticketmaster.gr/ticketmaster_se_2005795.html"
CHECK_INTERVAL = 60  # 15 minutes

def send_email(subject, body):
    print(f"[{datetime.now()}] 📧 Preparing to send email")
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(GMAIL_SENDER, GMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def check_for_tickets():
    try:
        print(f"[{datetime.now()}] 🔁 Starting ticket check cycle...")
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        found_links = [link["href"] for link in links if "aek" in link["href"].lower()]

        if found_links:
            message = "🎫 New AEK Ticket Alert!\n\nTickets found at:\n" + "\n".join(found_links)
            send_email("📣 AEK Tickets Found!", message)
            print(f"[{datetime.now()}] ✅ Email sent with links: {found_links}")
        else:
            print(f"[{datetime.now()}] ❌ No tickets found.")

    except Exception as e:
        print(f"[{datetime.now()}] 🛑 Error during check: {e}")

if __name__ == "__main__":
    while True:
        check_for_tickets()
        time.sleep(CHECK_INTERVAL)
