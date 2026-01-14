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
WALLETS = os.getenv("TRACKED_WALLETS", "").split(",")

def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def monitor():
    print(f"🚀 WEAPON ACTIVE: Monitoring {len(WALLETS)} Smart Wallets...")
    last_tx = {wallet: None for wallet in WALLETS}
    headers = {"token": API_KEY}

    while True:
        for wallet in WALLETS:
            wallet = wallet.strip()
            if not wallet: continue

            try:
                # Solscan V2 DeFi Activity (Swaps/Trades)
                url = f"https://pro-api.solscan.io/v2.0/account/defi/activities?address={wallet}&activity_type=ACTIVITY_TOKEN_SWAP&page=1&page_size=1"
                resp = requests.get(url, headers=headers).json()

                if resp.get("success") and resp.get("data"):
                    activity = resp["data"][0]
                    tx_hash = activity.get("trans_id")

                    if tx_hash != last_tx[wallet]:
                        # Extract trade data
                        # Note: Solscan V2 often uses token1/token2 or from_symbol/to_symbol
                        from_token = activity.get("from_symbol", activity.get("token1_symbol", "Unknown"))
                        to_token = activity.get("to_symbol", activity.get("token2_symbol", "Unknown"))
                        to_amount = activity.get("to_amount", activity.get("amount2", 0))
                        to_address = activity.get("to_address", activity.get("token2", ""))

                        alert_msg = (
                            f"🧠 <b>ALIEN BRAIN DETECTED TRADE</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"👤 <b>Wallet:</b> <code>{wallet[:4]}...{wallet[-4:]}</code>\n"
                            f"🔄 <b>Action:</b> Swapped {from_token} for <b>{to_amount} {to_token}</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"📈 <a href='https://dexscreener.com/solana/{to_address}'>View Live Chart</a>\n"
                            f"🔬 <a href='https://solscan.io/tx/{tx_hash}'>Solscan Details</a>"
                        )

                        send_alert(alert_msg)
                        last_tx[wallet] = tx_hash
                        print(f"✅ Signal sent for {wallet}")

            except Exception as e:
                print(f"Error tracking {wallet}: {e}")

        # Check every 15 seconds (Aggressive tracking)
        time.sleep(15)

@app.route('/')
def health():
    return "WEAPON STATUS: ONLINE"

if __name__ == "__main__":
    Thread(target=monitor, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
