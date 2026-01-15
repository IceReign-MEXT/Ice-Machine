import os
import time
import requests
import telebot
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.getenv("SOLSCAN_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID") # Your channel -1002384609234

# YOUR RECEIVING WALLET (For Payments & Tracking)
SAFE_WALLET = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

# WHALES TO TRACK (The Alien Brains)
TRACKED_WALLETS = [
    "3KJZZxQ7yYNLqNzsxN33x1V3pav2nRybtXXrBpNm1Zqf",
    "3JqvK1ZAt67nipBVgZj6zWvuT8icMWBMWyu5AwYnhVss",
    SAFE_WALLET
]

bot = telebot.TeleBot(BOT_TOKEN)

# --- 1. USER INTERACTION (How they talk to the bot) ---

@bot.message_handler(commands=['start'])
def welcome(m):
    text = (
        "🛸 <b>ALIEN BRAIN SIGNAL TERMINAL</b>\n\n"
        "I am live-tracking 3 high-profit whale wallets on Solana.\n\n"
        "✅ <b>Status:</b> Monitoring Active\n"
        "📢 <b>Channel:</b> Signals are sent to the VIP channel.\n\n"
        "💰 <b>Want VIP Access?</b> Use /pay to get the payment address."
    )
    bot.reply_to(m, text, parse_mode='HTML')

@bot.message_handler(commands=['pay', 'subscribe'])
def payment_info(m):
    text = (
        "💎 <b>VIP LIFETIME ACCESS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Price: <b>0.5 SOL</b>\n\n"
        "⚠️ <b>SEND PAYMENT TO (Solana):</b>\n"
        f"<code>{SAFE_WALLET}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<i>After paying, send your Transaction ID to @YourUsername to be added to the Private Feed.</i>"
    )
    bot.reply_to(m, text, parse_mode='HTML')

# --- 2. THE SIGNAL GENERATOR (Keeps the channel alive) ---

def monitor_whales():
    print("🚀 ALIEN BRAIN MONITORING STARTING...")

    # Send "Online" notification to the channel
    try:
        bot.send_message(CHANNEL_ID, "🟢 <b>TERMINAL ONLINE</b>\n<i>The Alien Brain is now scanning the blockchain...</i>", parse_mode='HTML')
    except Exception as e:
        print(f"Channel Startup Error: {e}")

    last_txs = {wallet: None for wallet in TRACKED_WALLETS}
    headers = {"token": API_KEY}

    while True:
        for wallet in TRACKED_WALLETS:
            try:
                # Use Universal Transaction endpoint for maximum reliability
                url = f"https://pro-api.solscan.io/v2.0/account/transactions?address={wallet}&limit=1"
                resp = requests.get(url, headers=headers).json()

                if resp.get("success") and resp.get("data"):
                    tx = resp["data"][0]
                    tx_hash = tx.get("tx_hash")

                    if last_txs[wallet] is None:
                        last_txs[wallet] = tx_hash
                        continue

                    if tx_hash != last_txs[wallet]:
                        # A NEW TRADE DETECTED!
                        signal = (
                            f"🧠 <b>ALIEN BRAIN: SIGNAL DETECTED</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"👤 <b>Whale:</b> <code>{wallet[:4]}...{wallet[-4:]}</code>\n"
                            f"🔗 <a href='https://solscan.io/tx/{tx_hash}'>View Transaction</a>\n"
                            f"📊 <a href='https://dexscreener.com/solana/{wallet}'>View Wallet Chart</a>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"⚡ <a href='https://photon-sol.tinyastro.io/en/lp/{wallet}'>Quick Snipe (Photon)</a>\n"
                            f"🛡️ <a href='https://rugcheck.xyz/tokens/{wallet}'>Check Safety</a>"
                        )
                        bot.send_message(CHANNEL_ID, signal, parse_mode='HTML', disable_web_page_preview=True)
                        last_txs[wallet] = tx_hash
                        print(f"✅ ALERT SENT: {wallet}")

            except Exception as e:
                print(f"Error checking {wallet}: {e}")
            time.sleep(2) # Protect API credits

        time.sleep(25) # Check cycle speed

# --- 3. SERVER & EXECUTION ---

@app.route('/')
def health():
    return "ONLINE", 200

if __name__ == "__main__":
    # Run Whale Monitoring in Background
    Thread(target=monitor_whales, daemon=True).start()
    # Run Telegram Command Listener in Background
    Thread(target=lambda: bot.polling(non_stop=True), daemon=True).start()
    # Start Web Server for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
