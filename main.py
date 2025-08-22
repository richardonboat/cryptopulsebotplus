import telebot
import requests
from flask import Flask, request
import os

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# Welcome message
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🚀 Welcome to CryptoPulseBot! Use:\n/price <coin> (e.g., /price BTC)\n/trends - Top 5 coins\n/help - This menu\n/subscribe - Whale alerts ($3/month, demo free)")

# Price query
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        coin = message.text.split()[1].lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        response = requests.get(url).json()
        price = response.get(coin, {}).get("usd", "Unknown")
        bot.reply_to(message, f"The price of {coin.upper()} is ${price} USD")
    except:
        bot.reply_to(message, "Invalid coin or API error. Try /price BTC")

# Trends
@bot.message_handler(commands=['trends'])
def get_trends(message):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1"
        response = requests.get(url).json()
        trends = "\n".join([f"{i+1}. {coin['name']}: {coin['price_change_percentage_24h']}%"
                            for i, coin in enumerate(response)])
        bot.reply_to(message, f"📈 Top 5 Trends:\n{trends}")
    except:
        bot.reply_to(message, "API error. Try again later.")

# Premium subscription for whale alerts
premium_users = set()

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    premium_users.add(message.chat.id)
    bot.reply_to(message, "Subscribed to whale alerts for $3/month! (Demo: Free)")

# Whale alert webhook
@app.route('/whale', methods=['POST'])
def whale_alert():
    data = request.get_json()
    amount = data.get('amount')
    token = data.get('token')
    blockchain = data.get('blockchain')
    tx_hash = data.get('txHash')
    message = f"🐳 Whale Alert! {amount} {token} moved on {blockchain}. Details: etherscan.io/tx/{tx_hash}"
    for user_id in premium_users:
        bot.send_message(user_id, message)
    return "OK", 200

# Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('KOYEB_PUBLIC_DOMAIN')}/webhook")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
  
