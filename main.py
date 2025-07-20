import telebot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# In-memory user database
users = {}

# Referral and withdrawal config
REFERRAL_REWARD = 0.0015
WITHDRAWAL_THRESHOLD = 0.1

# Placeholder for required channels (can be empty or updated later)
REQUIRED_CHANNELS = []  # Example: ['@yourchannel']

# Dummy function to simulate channel membership check
def is_user_in_required_channels(user_id):
    return True  # Simulating user is always subscribed

# /start command handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    ref_id = None

    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]

    if user_id not in users:
        users[user_id] = {"balance": 0.0, "referrals": []}
        if ref_id and ref_id.isdigit():
            ref_id = int(ref_id)
            if ref_id != user_id and ref_id in users:
                users[ref_id]['balance'] += REFERRAL_REWARD
                users[ref_id]['referrals'].append(user_id)

    if not is_user_in_required_channels(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Required Channels", url="https://t.me/yourchannel"))
        bot.send_message(user_id, "Please join the required channels to use the bot.", reply_markup=markup)
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 Balance", callback_data="balance"))
    markup.add(InlineKeyboardButton("👥 Referrals", callback_data="referrals"))
    markup.add(InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"))
    bot.send_message(user_id, "Welcome to AutoPay Bot!", reply_markup=markup)

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data

    if user_id not in users:
        users[user_id] = {"balance": 0.0, "referrals": []}

    if data == "balance":
        balance = users[user_id]['balance']
        bot.answer_callback_query(call.id, f"Your balance: {balance:.4f} USDT")

    elif data == "referrals":
        refs = users[user_id]['referrals']
        bot.answer_callback_query(call.id, f"You referred {len(refs)} user(s).")

    elif data == "withdraw":
        balance = users[user_id]['balance']
        if balance >= WITHDRAWAL_THRESHOLD:
            bot.send_message(user_id, "✅ Your withdrawal request has been submitted!\n(For educational purposes only – no real payment.)")
            users[user_id]['balance'] = 0.0  # Reset after fake withdrawal
        else:
            bot.send_message(user_id, f"❌ Minimum withdrawal is {WITHDRAWAL_THRESHOLD} USDT.\nYour current balance: {balance:.4f} USDT")

# Start polling
bot.infinity_polling()
