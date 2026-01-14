import os
import time
import requests
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.getenv("SOLSCAN_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")
# Split the wallet list from .env
WALLETS_RAW = os.getenv("TRACKED_WALLETS", "")
WALLETS = [w.strip() for w in WALLETS_RAW.split(",") if w.strip()]

def send_alert(msg):
    """Sends a message to the Telegram Channel."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"❌ Telegram Error: {r.text}")
        else:
            print("✅ Telegram alert sent successfully.")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def monitor():
    print(f"🚀 WEAPON ACTIVE: Monitoring {len(WALLETS)} Smart Wallets...")

    # --- STARTUP PING ---
    # This tells you immediately if the bot is working
    send_alert("👽 <b>ALIEN BRAIN IS ONLINE</b>\nStatus: Tracking Smart Money...")

    last_tx = {wallet: None for wallet in WALLETS}
    headers = {"token": API_KEY}

    while True:
        for wallet in WALLETS:
            try:
                # Solscan V2 DeFi Activity (Token Swaps)
                url = f"https://pro-api.solscan.io/v2.0/account/defi/activities?address={wallet}&activity_type=ACTIVITY_TOKEN_SWAP&page=1&page_size=1"
                resp = requests.get(url, headers=headers).json()

                if resp.get("success") and resp.get("data"):
                    activity = resp["data"][0]
                    tx_hash = activity.get("trans_id")

                    # If this is a new transaction we haven't seen yet
                    if tx_hash != last_tx[wallet]:
                        # Extract trade details
                        from_token = activity.get("from_symbol", "???")
                        to_token = activity.get("to_symbol", "???")
                        to_amount = activity.get("to_amount", 0)
                        to_address = activity.get("to_address", "")

                        alert_msg = (
                            f"🧠 <b>ALIEN BRAIN DETECTED TRADE</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"👤 <b>Wallet:</b> <code>{wallet[:6]}...{wallet[-4:]}</code>\n"
                            f"🔄 <b>Action:</b> Swapped {from_token} ➡️ <b>{to_amount} {to_token}</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"📈 <a href='https://dexscreener.com/solana/{to_address}'>View Live Chart</a>\n"
                            f"🔬 <a href='https://solscan.io/tx/{tx_hash}'>Solscan Details</a>"
                        )

                        send_alert(alert_msg)
                        last_tx[wallet] = tx_hash

                # Small delay to avoid API rate limits
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error tracking {wallet}: {e}")

        # Check every 20 seconds
        time.sleep(20)

@app.route('/')
def health():
    return "ALIEN BRAIN STATUS: ONLINE"

if __name__ == "__main__":
    # Start monitor in a separate thread
    Thread(target=monitor, daemon=True).start()
    # Port for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
