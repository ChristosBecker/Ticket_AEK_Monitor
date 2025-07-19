import time
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from datetime import datetime

URL = "https://www.ticketmaster.gr/ticketmaster_se_2005795.html"
CHECK_INTERVAL = 900  # 15 minutes

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = "your_email@gmail.com"
    msg["To"] = "your_email@gmail.com"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("your_email@gmail.com", "your_app_password")
    server.send_message(msg)
    server.quit()

def check_for_tickets():
    try:
        print(f"[{datetime.now()}] 🔍 Checking for AEK tickets...")
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        found_links = [link["href"] for link in links if "aek" in link["href"].lower()]

        if found_links:
            message = f"🎫 New AEK Ticket Alert!\n\nTickets found at:\n" + "\n".join(found_links)
            send_email("🎫 AEK Tickets Found!", message)
            print(f"[{datetime.now()}] 📧 Email sent with links: {found_links}")
        else:
            print(f"[{datetime.now()}] ❌ No tickets found.")
    except Exception as e:
        print(f"[{datetime.now()}] ❗ Error during check: {e}")

if __name__ == "__main__":
    while True:
        check_for_tickets()
        time.sleep(CHECK_INTERVAL)
