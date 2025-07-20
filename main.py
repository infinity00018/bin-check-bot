import telebot
import json
import os

# Telegram bot token
BOT_TOKEN = "7856671589:AAGWcGfJCSoz1Ao-Hqu3nhEsF75R3HeP95M"
bot = telebot.TeleBot(BOT_TOKEN)

# Channel usernames (can be empty list if you add later)
CHANNELS = [
    # "@channel1", "@channel2", ...
]

USERS_FILE = "users.json"

# Load user data from file
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Save user data to file
def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Check if user joined all required channels
def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    users = load_users()

    ref_id = None
    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]

    if user_id not in users:
        users[user_id] = {"usdt": 0.0, "ref_by": ref_id}
        if ref_id and ref_id in users:
            users[ref_id]["usdt"] += 0.0015
        save_users(users)

    if CHANNELS:
        if not is_subscribed(user_id):
            channels_list = "\n".join([f"➡️ {ch}" for ch in CHANNELS])
            bot.send_message(message.chat.id, f"📢 Please join these channels first:\n{channels_list}\n\nThen press /start again.")
            return

    bot.send_message(message.chat.id,
        f"👋 Welcome {message.from_user.first_name}!\n"
        "🎁 Earn 0.0015 USDT per referral.\n"
        "💸 Withdraw when you reach 0.1 USDT!\n\n"
        "👥 Use your link to refer:\n"
        f"https://t.me/{bot.get_me().username}?start={user_id}"
    )

@bot.message_handler(commands=["balance"])
def balance(message):
    user_id = str(message.from_user.id)
    users = load_users()
    usdt = users.get(user_id, {}).get("usdt", 0.0)
    bot.send_message(message.chat.id, f"💰 Your Balance: {usdt:.4f} USDT")

@bot.message_handler(commands=["withdraw"])
def withdraw(message):
    user_id = str(message.from_user.id)
    users = load_users()
    usdt = users.get(user_id, {}).get("usdt", 0.0)

    if usdt < 0.1:
        bot.send_message(message.chat.id,
            f"❌ Minimum 0.1 USDT required to withdraw.\n💸 Your current balance: {usdt:.4f} USDT")
    else:
        bot.send_message(message.chat.id,
            "✅ Withdrawal request received!\n💳 (This is a simulation — no real payout.)")

# Run the bot
print("🤖 Bot is running...")
bot.infinity_polling()
