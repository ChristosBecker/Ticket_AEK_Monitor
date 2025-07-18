from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

# === CONFIG ===
URL = "https://www.ticketmaster.gr/aek/showProductList.html"
CHECK_INTERVAL = 900  # 15 minutes

# Load secrets from environment variables
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

app = Flask(__name__)

@app.route('/')
def home():
    return "AEK Ticket Monitor is running."

# === UTILITY FUNCTIONS ===
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open("log.txt", "a") as f:
        f.write(full_message + "\n")

def get_ticket_snapshot():
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        product_blocks = soup.find_all('div', class_='productInnerLeft')
        if not product_blocks:
            return None, None
        ticket_data = [block.get_text(strip=True) for block in product_blocks]
        snapshot = "\n".join(ticket_data)
        hash_value = hashlib.md5(snapshot.encode()).hexdigest()
        return snapshot, hash_value
    except Exception as e:
        log(f"❌ Error fetching ticket data: {e}")
        return None, None

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = GMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.send_message(msg)
    log("📧 Email sent successfully.")

# === MONITOR LOOP ===
def monitor():
    global last_hash
    log("🔍 Monitor started...")
    last_hash = None

    while True:
        snapshot, current_hash = get_ticket_snapshot()

        if snapshot is None:
            log("⚠️ No snapshot found, skipping.")
        elif last_hash is None:
            last_hash = current_hash
            log("📌 First snapshot stored.")
        elif current_hash != last_hash:
            log("🎟️ Change detected! Sending email.")
            send_email("🎫 New AEK Tickets Detected!", snapshot)
            last_hash = current_hash
        else:
            log("✅ No change detected.")

        time.sleep(CHECK_INTERVAL)

# === RUN ===
def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()
Thread(target=monitor).start()
