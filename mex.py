import os
import requests
from web3 import Web3

PRIVATE_KEY = "your_private_key_here"
SAFE_ADDRESS = "0x08D171685e51bAf7a929cE8945CF25b3D1Ac9756"
WATCH_ADDRESS = "0x374a4f86B2BD66A382Ffbd61613D5C779e20e0aD"
RPC_URL = "https://eth.llamarpc.com"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "6453658778"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def sweep_funds():
    balance = w3.eth.get_balance(WATCH_ADDRESS)
    if balance > 0:
        gas_price = w3.eth.gas_price
        tx = {
            "from": WATCH_ADDRESS,
            "to": SAFE_ADDRESS,
            "value": balance - (gas_price * 21000),
            "gas": 21000,
            "gasPrice": gas_price,
            "nonce": w3.eth.get_transaction_count(account.address),
        }
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        send_telegram_alert(f"✅ Funds swept! TX: https://etherscan.io/tx/{tx_hash.hex()}")
    else:
        send_telegram_alert("⚠️ No balance to sweep.")

if __name__ == "__main__":
    try:
        sweep_funds()
    except Exception as e:
        send_telegram_alert(f"❌ Error: {str(e)}")