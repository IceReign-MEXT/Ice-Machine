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

# YOUR RECEIVING WALLET (The "Safe Wallet" for Payments)
MY_SAFE_WALLET = "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy"

# THE WHALES TO TRACK (The Alien Brains)
TRACKED_WALLETS = [
    "3KJZZxQ7yYNLqNzsxN33x1V3pav2nRybtXXrBpNm1Zqf",
    "3JqvK1ZAt67nipBVgZj6zWvuT8icMWBMWyu5AwYnhVss",
    MY_SAFE_WALLET # Keeping yours in the list to track your own moves too
]

bot = telebot.TeleBot(BOT_TOKEN)

# --- 1. TELEGRAM COMMAND HANDLERS (How you get paid) ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🛸 <b>WELCOME TO THE ALIEN BRAIN TERMINAL</b>\n\n"
        "I track the world's most profitable Solana Insiders in real-time.\n\n"
        "💰 <b>WANT VIP ACCESS?</b>\n"
        "Get instant buy/sell alerts with Photon & DexScreener links.\n\n"
        "Use /pay to see subscription plans."
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

@bot.message_handler(commands=['pay', 'vip', 'subscribe'])
def send_payment(message):
    payment_text = (
        "💎 <b>VIP SUBSCRIPTION PLANS</b>\n\n"
        "🟢 1 Month VIP: <b>0.5 SOL</b>\n"
        "🔵 Lifetime Access: <b>1.5 SOL</b>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚠️ <b>SEND PAYMENT TO:</b>\n"
        f"<code>{MY_SAFE_WALLET}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<i>After sending payment, DM @YourUsername with your transaction hash to be added to the Private Signal Channel.</i>"
    )
    bot.reply_to(message, payment_text, parse_mode='HTML')

# --- 2. WHALE TRACKER LOGIC (The Signal Generator) ---

def send_alert(msg):
    """Sends signal to the VIP Channel."""
    try:
        bot.send_message(CHANNEL_ID, msg, parse_mode='HTML', disable_web_page_preview=True)
    except Exception as e:
        print(f"Signal Error: {e}")

def monitor_whales():
    print("🚀 WHALE MONITOR ACTIVE...")
    # Initial startup message
    send_alert("<b>🛸 ALIEN BRAIN TERMINAL ONLINE</b>\n<i>Monitoring Elite Wallets...</i>")

    last_txs = {wallet: None for wallet in TRACKED_WALLETS}
    headers = {"token": API_KEY}

    while True:
        for wallet in TRACKED_WALLETS:
            try:
                # Track Swaps using Solscan Pro API
                url = f"https://pro-api.solscan.io/v2.0/account/defi/activities?address={wallet}&activity_type=ACTIVITY_TOKEN_SWAP&page=1&page_size=1"
                response = requests.get(url, headers=headers).json()

                if response.get("success") and response.get("data"):
                    trade = response["data"][0]
                    tx_hash = trade.get("trans_id")

                    if tx_hash != last_txs[wallet]:
                        token_name = trade.get("to_symbol", "Unknown")
                        token_addr = trade.get("to_address", "")
                        amount = trade.get("to_amount", 0)

                        signal = (
                            f"🔔 <b>INSIDER ACTION DETECTED!</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"👤 <b>Whale:</b> <code>{wallet[:4]}...{wallet[-4:]}</code>\n"
                            f"💰 <b>Bought:</b> {amount:,.2f} <b>{token_name}</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"🚀 <b>QUICK BUY:</b>\n"
                            f"🔗 <a href='https://photon-sol.tinyastro.io/en/lp/{token_addr}'>Photon (Fastest)</a>\n"
                            f"📊 <a href='https://dexscreener.com/solana/{token_addr}'>DexScreener</a>\n"
                            f"🛡️ <a href='https://rugcheck.xyz/tokens/{token_addr}'>RugCheck</a>\n"
                            f"━━━━━━━━━━━━━━━━━━"
                        )
                        send_alert(signal)
                        last_txs[wallet] = tx_hash

                time.sleep(2) # API Protection
            except Exception as e:
                print(f"Tracking Error: {e}")

        time.sleep(20) # Check cycle

# --- 3. FLASK SERVER & EXECUTION ---

@app.route('/')
def home():
    return "ALIEN BRAIN IS ACTIVE", 200

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Start Whale Tracker
    Thread(target=monitor_whales, daemon=True).start()
    # Start Telegram Command Listener
    Thread(target=run_bot, daemon=True).start()
    # Start Web Server for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
