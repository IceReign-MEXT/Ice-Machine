import os
import time
import requests
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Load local .env if it exists
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
SOL_API_KEY = os.getenv("SOLSCAN_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# Wallets to track
WALLETS_STR = os.getenv("TRACKED_WALLETS", "")
TRACKED_WALLETS = [w.strip() for w in WALLETS_STR.split(",") if w.strip()]

def send_telegram(message):
    """Helper to send messages with error logging."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if not result.get("ok"):
            print(f"❌ Telegram Error: {result.get('description')}")
        else:
            print("✅ Telegram message sent.")
    except Exception as e:
        print(f"❌ Network Error (Telegram): {e}")

def monitor_wallets():
    """Background task to watch Solana wallets."""
    print(f"🚀 ALIEN BRAIN ACTIVE. Tracking: {len(TRACKED_WALLETS)} wallets.")

    # 1. TEST TELEGRAM IMMEDIATELY ON STARTUP
    send_telegram(f"👽 <b>ALIEN BRAIN ONLINE</b>\nTracking {len(TRACKED_WALLETS)} Smart Wallets.\n<i>If you see this, connection is perfect.</i>")

    # Store last seen transaction for each wallet
    last_txs = {wallet: None for wallet in TRACKED_WALLETS}
    headers = {"token": SOL_API_KEY}

    while True:
        for wallet in TRACKED_WALLETS:
            try:
                # Use the V2 Transactions endpoint
                url = f"https://pro-api.solscan.io/v2.0/account/transactions?address={wallet}&limit=1"
                response = requests.get(url, headers=headers)
                data = response.json()

                if data.get("success") and data.get("data"):
                    latest_tx = data["data"][0].get("tx_hash")

                    # If this is the first time checking, just save the hash
                    if last_txs[wallet] is None:
                        last_txs[wallet] = latest_tx
                        continue

                    # If we find a NEW transaction
                    if latest_tx != last_txs[wallet]:
                        msg = (
                            f"🧠 <b>NEW WHALE MOVEMENT</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"👤 <b>Wallet:</b> <code>{wallet}</code>\n"
                            f"🔗 <a href='https://solscan.io/tx/{latest_tx}'>View Transaction</a>\n"
                            f"📊 <a href='https://dexscreener.com/solana/{wallet}'>View Wallet Chart</a>\n"
                            f"━━━━━━━━━━━━━━━━━━"
                        )
                        send_telegram(msg)
                        last_txs[wallet] = latest_tx

                # Sleep briefly between wallets to avoid rate limits
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ Error checking {wallet}: {e}")

        # Wait 30 seconds before next full scan
        time.sleep(30)

@app.route('/')
def health_check():
    return "BOT IS RUNNING", 200

if __name__ == "__main__":
    # Start the monitoring thread
    monitor_thread = Thread(target=monitor_wallets, daemon=True)
    monitor_thread.start()

    # Start the web server (Render requires this)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



