import os
import time
import requests
import telebot
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- CONFIG ---
API_KEY = os.getenv("SOLSCAN_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")
SAFE_WALLET = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

# Wallets to monitor
TRACKED_WALLETS = [
    "GJqcJCSCntX3FXoA3FxZdWFpQijfKK73ux6D6Towpump",
    "DZaUsRPR5daQw3UZLz5p4aDaa2a2wDeQXkgtXhXJKx6m",
    SAFE_WALLET
]

bot = telebot.TeleBot(BOT_TOKEN)

# --- COMMANDS FOR USERS ---

@bot.message_handler(commands=['start'])
def start(m):
    msg = (
        "🛸 <b>ALIEN BRAIN TERMINAL</b>\n\n"
        "Tracking the most profitable Solana insiders.\n"
        "To get VIP access to the signal channel, use /pay"
    )
    bot.reply_to(m, msg, parse_mode='HTML')

@bot.message_handler(commands=['pay'])
def pay(m):
    msg = (
        "💎 <b>VIP ACCESS PLAN</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Price: <b>0.5 SOL</b>\n"
        "Duration: <b>Lifetime Access</b>\n\n"
        "⚠️ <b>SEND SOL TO:</b>\n"
        f"<code>{SAFE_WALLET}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<i>DM @YourUsername with TX hash after payment.</i>"
    )
    bot.reply_to(m, msg, parse_mode='HTML')

# --- THE TRACKER ---

def monitor():
    print("🚀 MONITOR STARTING...")
    # This proves the bot is connected to your channel
    try:
        bot.send_message(CHANNEL_ID, "✅ <b>ALIEN BRAIN v3.0 DEPLOYED</b>\n<i>Universal Tracking Mode: Active</i>", parse_mode='HTML')
    except Exception as e:
        print(f"FAILED TO SEND STARTUP MSG: {e}")

    last_txs = {wallet: None for wallet in TRACKED_WALLETS}
    headers = {"token": API_KEY}

    while True:
        for wallet in TRACKED_WALLETS:
            try:
                # UNIVERSAL ENDPOINT (Works with more API keys)
                url = f"https://pro-api.solscan.io/v2.0/account/transactions?address={wallet}&limit=2"
                resp = requests.get(url, headers=headers).json()

                if resp.get("success") and resp.get("data"):
                    # Get the most recent transaction
                    tx = resp["data"][0]
                    tx_hash = tx.get("tx_hash")

                    if last_txs[wallet] is None:
                        last_txs[wallet] = tx_hash
                        continue

                    if tx_hash != last_txs[wallet]:
                        # A NEW MOVEMENT HAPPENED
                        alert = (
                            f"🧠 <b>ALIEN BRAIN: WHALE MOVEMENT</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"👤 <b>Wallet:</b> <code>{wallet[:6]}...</code>\n"
                            f"🔗 <a href='https://solscan.io/tx/{tx_hash}'>View Transaction</a>\n"
                            f"📊 <a href='https://dexscreener.com/solana/{wallet}'>Wallet Chart</a>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"⚡ <a href='https://photon-sol.tinyastro.io/en/lp/{wallet}'>Quick Snipe</a>"
                        )
                        bot.send_message(CHANNEL_ID, alert, parse_mode='HTML', disable_web_page_preview=True)
                        last_txs[wallet] = tx_hash
                        print(f"✅ ALERT SENT FOR {wallet}")

            except Exception as e:
                print(f"Error checking {wallet}: {e}")
            time.sleep(2) # Anti-rate limit

        time.sleep(30) # Wait 30 seconds before next scan

@app.route('/')
def home():
    return "ONLINE", 200

if __name__ == "__main__":
    # Start tracking thread
    Thread(target=monitor, daemon=True).start()
    # Start command polling
    Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    # Start Web Server
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
