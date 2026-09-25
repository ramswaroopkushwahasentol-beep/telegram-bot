import os
import telebot
from pymongo import MongoClient
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================
# SETTINGS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

ADMIN_ID = 6278812118

# =========================
# CHECK SETTINGS
# =========================

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable missing")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable missing")

# =========================
# TELEGRAM
# =========================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================
# MONGODB
# =========================

client = MongoClient(MONGO_URI)

db = client["telegram_bot"]

posts_collection = db["posts"]

# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    first_post = posts_collection.find_one(
        {},
        sort=[("_id", 1)]
    )

    if not first_post:
        bot.send_message(
            message.chat.id,
            "👋 Welcome!\n\nअभी कोई post available नहीं है।"
        )
        return

    send_post(message.chat.id, first_post)


# =========================
# SEND POST
# =========================

def send_post(chat_id, post):

    text = post.get("text", "🎬 New Video")

    post_id = str(post["_id"])

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "▶️ Next Video",
            callback_data=f"next:{post_id}"
        )
    )

    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )


# =========================
# NEXT VIDEO
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("next:")
)
def next_video(call):

    current_id = call.data.split(":")[1]

    from bson.objectid import ObjectId

    try:
        current_object_id = ObjectId(current_id)
    except:
        bot.answer_callback_query(
            call.id,
            "Post नहीं मिला"
        )
        return

    next_post = posts_collection.find_one(
        {"_id": {"$gt": current_object_id}},
        sort=[("_id", 1)]
    )

    if not next_post:

        bot.answer_callback_query(
            call.id,
            "अभी कोई अगला video नहीं है"
        )

        return

    bot.answer_callback_query(call.id)

    send_post(
        call.message.chat.id,
        next_post
    )


# =========================
# ADD POST
# =========================

@bot.message_handler(commands=["addpost"])
def addpost(message):

    if message.from_user.id != ADMIN_ID:

        bot.reply_to(
            message,
            "❌ आप admin नहीं हैं।"
        )

        return

    msg = bot.reply_to(
        message,
        "📝 Post का text भेजें:"
    )

    bot.register_next_step_handler(
        msg,
        save_post
    )


# =========================
# SAVE POST
# =========================

def save_post(message):

    if message.from_user.id != ADMIN_ID:

        return

    text = message.text.strip()

    if not text:

        bot.reply_to(
            message,
            "❌ Text खाली नहीं हो सकता।"
        )

        return

    result = posts_collection.insert_one({
        "text": text
    })

    bot.reply_to(
        message,
        f"✅ Post successfully added!\n\nID: {result.inserted_id}"
    )


# =========================
# RUN BOT
# =========================

print("🤖 Bot is running...")

bot.infinity_polling(
    timeout=30,
    long_polling_timeout=30
)
