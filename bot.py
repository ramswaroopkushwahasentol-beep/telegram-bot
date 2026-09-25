import telebot
from telebot import types
import json
import os

# ==================================================
# BOT SETTINGS
# ==================================================

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# यहां अपना Telegram numeric ID डालें
ADMIN_ID = 123456789

DATA_FILE = "buttons.json"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Temporary admin states
states = {}


# ==================================================
# DEFAULT BUTTONS
# ==================================================

DEFAULT_BUTTONS = [
    {
        "name": "🥵 Viral Videos",
        "link": "https://t.me/+06Gaex_LDztmZjI9"
    },
    {
        "name": "🔥 Trending Videos",
        "link": "https://t.me/+S8zcYhsp4zYwYjE1"
    },
    {
        "name": "📱 Insta Viral",
        "link": "https://t.me/+R1-GvohMkHgyZTE1"
    },
    {
        "name": "🎬 Diskwala Movies",
        "link": "https://t.me/+J0AAsSMybNFhOWNl"
    },
    {
        "name": "🤖 Viral Video Bot",
        "link": "https://t.me/Jhsjdjsjsiwisdbot"
    },
    {
        "name": "🍿 Bollywood Movies",
        "link": "https://t.me/diskwalamovi"
    }
]


# ==================================================
# LOAD DATA
# ==================================================

def load_data():

    if not os.path.exists(DATA_FILE):

        data = {
            "buttons": DEFAULT_BUTTONS.copy(),
            "users": []
        }

        save_data(data)

        return data

    try:

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception:

        data = {
            "buttons": DEFAULT_BUTTONS.copy(),
            "users": []
        }

        save_data(data)

    # पुराने/अधूरे JSON में missing keys ठीक करें
    if "buttons" not in data:
        data["buttons"] = DEFAULT_BUTTONS.copy()

    if "users" not in data:
        data["users"] = []

    return data


# ==================================================
# SAVE DATA
# ==================================================

def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


data = load_data()


# ==================================================
# ADMIN CHECK
# ==================================================

def is_admin(user_id):

    return user_id == ADMIN_ID


# ==================================================
# USER BUTTONS
# ==================================================

def user_keyboard():

    markup = types.InlineKeyboardMarkup(row_width=1)

    for button in data["buttons"]:

        markup.add(
            types.InlineKeyboardButton(
                button["name"],
                url=button["link"]
            )
        )

    return markup


# ==================================================
# ADMIN PANEL
# ==================================================

def admin_keyboard():

    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        types.InlineKeyboardButton(
            "➕ Add Button",
            callback_data="add_button"
        ),
        types.InlineKeyboardButton(
            "📋 All Buttons",
            callback_data="all_buttons"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "✏️ Rename",
            callback_data="rename_button"
        ),
        types.InlineKeyboardButton(
            "🔗 Change Link",
            callback_data="change_link"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🗑️ Delete",
            callback_data="delete_button"
        ),
        types.InlineKeyboardButton(
            "↕️ Order",
            callback_data="order_buttons"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "👥 User Count",
            callback_data="user_count"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔄 Refresh",
            callback_data="admin_refresh"
        )
    )

    return markup


# ==================================================
# /START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id

    # User save करें
    if user_id not in data["users"]:

        data["users"].append(user_id)

        save_data(data)

    text = """
<b>╭━━━━━━━━━━━━━━━━━━━━╮</b>
<b>🔥 TRENDING ZONE 🔥</b>
<b>╰━━━━━━━━━━━━━━━━━━━━╯</b>

🎬 <b>MOVIES • VIRAL • TRENDING</b>
✨ Everything in one place!

━━━━━━━━━━━━━━━━━━━━

👇 <b>Choose an option below</b> 👇

🚀 <b>JOIN • EXPLORE • STAY UPDATED</b>
"""

    if data["buttons"]:

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=user_keyboard(),
            disable_web_page_preview=True
        )

    else:

        bot.send_message(
            message.chat.id,
            text + "\n\n⚠️ अभी कोई button available नहीं है।"
        )


# ==================================================
# /ADMIN
# ==================================================

@bot.message_handler(commands=["admin"])
def admin(message):

    if not is_admin(message.from_user.id):

        bot.reply_to(
            message,
            "❌ <b>Access Denied</b>"
        )

        return

    bot.send_message(
        message.chat.id,
        "<b>⚙️ ADMIN PANEL</b>\n\n"
        "नीचे से कोई option चुनें:",
        reply_markup=admin_keyboard()
    )


# ==================================================
# SEND BUTTON SELECTION
# ==================================================

def send_button_selection(chat_id, text, prefix):

    markup = types.InlineKeyboardMarkup(row_width=1)

    for i, button in enumerate(data["buttons"]):

        markup.add(
            types.InlineKeyboardButton(
                button["name"],
                callback_data=f"{prefix}_{i}"
            )
        )

    bot.send_message(
        chat_id,
        text,
        reply_markup=markup
    )


# ==================================================
# MAIN CALLBACK HANDLER
# ==================================================

@bot.callback_query_handler(
    func=lambda call: (
        call.data in [
            "add_button",
            "all_buttons",
            "rename_button",
            "change_link",
            "delete_button",
            "order_buttons",
            "user_count",
            "admin_refresh"
        ]
    )
)
def main_callback(call):

    user_id = call.from_user.id

    if not is_admin(user_id):

        bot.answer_callback_query(
            call.id,
            "❌ Admin only",
            show_alert=True
        )

        return

    action = call.data

    # ==============================================
    # ADD BUTTON
    # ==============================================

    if action == "add_button":

        states[user_id] = {
            "action": "add_name"
        }

        bot.send_message(
            call.message.chat.id,
            "➕ <b>Add New Button</b>\n\n"
            "पहले button का नाम भेजें।\n\n"
            "Example:\n"
            "🎬 Bollywood Movies"
        )

    # ==============================================
    # ALL BUTTONS
    # ==============================================

    elif action == "all_buttons":

        if not data["buttons"]:

            bot.send_message(
                call.message.chat.id,
                "📋 अभी कोई button नहीं है।"
            )

            return

        text = "<b>📋 ALL BUTTONS</b>\n\n"

        for i, button in enumerate(data["buttons"], 1):

            text += (
                f"<b>{i}. {button['name']}</b>\n"
                f"🔗 {button['link']}\n\n"
            )

        bot.send_message(
            call.message.chat.id,
            text
        )

    # ==============================================
    # RENAME
    # ==============================================

    elif action == "rename_button":

        if not data["buttons"]:

            bot.send_message(
                call.message.chat.id,
                "❌ पहले कोई button add करें।"
            )

            return

        send_button_selection(
            call.message.chat.id,
            "✏️ <b>Button चुनें</b>\n\n"
            "जिसका नाम बदलना है:",
            "rename"
        )

    # ==============================================
    # CHANGE LINK
    # ==============================================

    elif action == "change_link":

        if not data["buttons"]:

            bot.send_message(
                call.message.chat.id,
                "❌ पहले कोई button add करें।"
            )

            return

        send_button_selection(
            call.message.chat.id,
            "🔗 <b>Button चुनें</b>\n\n"
            "जिसका link बदलना है:",
            "link"
        )

    # ==============================================
    # DELETE
    # ==============================================

    elif action == "delete_button":

        if not data["buttons"]:

            bot.send_message(
                call.message.chat.id,
                "❌ कोई button मौजूद नहीं है।"
            )

            return

        send_button_selection(
            call.message.chat.id,
            "🗑️ <b>Delete Button</b>\n\n"
            "जिस button को delete करना है उसे चुनें:",
            "delete"
        )

    # ==============================================
    # ORDER
    # ==============================================

    elif action == "order_buttons":

        if not data["buttons"]:

            bot.send_message(
                call.message.chat.id,
                "❌ कोई button मौजूद नहीं है।"
            )

            return

        send_button_selection(
            call.message.chat.id,
            "↕️ <b>Button चुनें</b>\n\n"
            "जिसे ऊपर/नीचे करना है:",
            "move"
        )

    # ==============================================
    # USER COUNT
    # ==============================================

    elif action == "user_count":

        count = len(data["users"])

        bot.send_message(
            call.message.chat.id,
            f"👥 <b>Total Users:</b> {count}"
        )

    # ==============================================
    # REFRESH
    # ==============================================

    elif action == "admin_refresh":

        bot.send_message(
            call.message.chat.id,
            "⚙️ <b>ADMIN PANEL</b>\n\n"
            "Panel refreshed:",
            reply_markup=admin_keyboard()
        )

    bot.answer_callback_query(call.id)


# ==================================================
# BUTTON ACTION CALLBACK
# ==================================================

@bot.callback_query_handler(
    func=lambda call: (
        call.data.startswith("rename_")
        or call.data.startswith("link_")
        or call.data.startswith("delete_")
        or call.data.startswith("move_")
    )
)
def button_action(call):

    user_id = call.from_user.id

    if not is_admin(user_id):

        bot.answer_callback_query(
            call.id,
            "❌ Admin only",
            show_alert=True
        )

        return

    parts = call.data.split("_")

    action = parts[0]

    try:
        index = int(parts[1])
    except:

        bot.answer_callback_query(
            call.id,
            "❌ Invalid button",
            show_alert=True
        )

        return

    if index < 0 or index >= len(data["buttons"]):

        bot.answer_callback_query(
            call.id,
            "❌ Button नहीं मिला",
            show_alert=True
        )

        return

    # ==============================================
    # RENAME
    # ==============================================

    if action == "rename":

        states[user_id] = {
            "action": "rename",
            "index": index
        }

        bot.send_message(
            call.message.chat.id,
            f"✏️ Current name:\n\n"
            f"<b>{data['buttons'][index]['name']}</b>\n\n"
            f"अब नया नाम भेजें:"
        )

    # ==============================================
    # CHANGE LINK
    # ==============================================

    elif action == "link":

        states[user_id] = {
            "action": "link",
            "index": index
        }

        bot.send_message(
            call.message.chat.id,
            f"🔗 Current link:\n\n"
            f"{data['buttons'][index]['link']}\n\n"
            f"अब नया Telegram link भेजें:"
        )

    # ==============================================
    # DELETE
    # ==============================================

    elif action == "delete":

        deleted = data["buttons"].pop(index)

        save_data(data)

        bot.send_message(
            call.message.chat.id,
            f"🗑️ <b>Button Deleted</b>\n\n"
            f"{deleted['name']}"
        )

    # ==============================================
    # MOVE
    # ==============================================

    elif action == "move":

        markup = types.InlineKeyboardMarkup(row_width=2)

        markup.add(
            types.InlineKeyboardButton(
                "⬆️ Up",
                callback_data=f"up_{index}"
            ),
            types.InlineKeyboardButton(
                "⬇️ Down",
                callback_data=f"down_{index}"
            )
        )

        bot.send_message(
            call.message.chat.id,
            f"↕️ <b>{data['buttons'][index]['name']}</b>\n\n"
            f"Button को move करें:",
            reply_markup=markup
        )

    bot.answer_callback_query(call.id)


# ==================================================
# MOVE UP / DOWN
# ==================================================

@bot.callback_query_handler(
    func=lambda call: (
        call.data.startswith("up_")
        or call.data.startswith("down_")
    )
)
def move_button(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Admin only",
            show_alert=True
        )

        return

    parts = call.data.split("_")

    direction = parts[0]

    try:
        index = int(parts[1])
    except:

        bot.answer_callback_query(
            call.id,
            "❌ Invalid",
            show_alert=True
        )

        return

    # ==============================================
    # MOVE UP
    # ==============================================

    if direction == "up":

        if index > 0:

            data["buttons"][index], data["buttons"][index - 1] = (
                data["buttons"][index - 1],
                data["buttons"][index]
            )

            save_data(data)

            bot.send_message(
                call.message.chat.id,
                "⬆️ <b>Button moved up!</b>"
            )

        else:

            bot.send_message(
                call.message.chat.id,
                "⚠️ यह पहला button है।"
            )

    # ==============================================
    # MOVE DOWN
    # ==============================================

    elif direction == "down":

        if index < len(data["buttons"]) - 1:

            data["buttons"][index], data["buttons"][index + 1] = (
                data["buttons"][index + 1],
                data["buttons"][index]
            )

            save_data(data)

            bot.send_message(
                call.message.chat.id,
                "⬇️ <b>Button moved down!</b>"
            )

        else:

            bot.send_message(
                call.message.chat.id,
                "⚠️ यह आखिरी button है।"
            )

    bot.answer_callback_query(call.id)


# ==================================================
# ADMIN TEXT INPUT
# ==================================================

@bot.message_handler(
    func=lambda message: (
        message.from_user.id == ADMIN_ID
        and message.text is not None
        and not message.text.startswith("/")
    )
)
def admin_text_handler(message):

    user_id = message.from_user.id

    if user_id not in states:

        return

    state = states[user_id]

    action = state["action"]

    # ==============================================
    # ADD BUTTON NAME
    # ==============================================

    if action == "add_name":

        name = message.text.strip()

        if not name:

            bot.send_message(
                message.chat.id,
                "❌ Button name खाली नहीं हो सकता।"
            )

            return

        states[user_id] = {
            "action": "add_link",
            "name": name
        }

        bot.send_message(
            message.chat.id,
            "🔗 अब button का Telegram link भेजें।\n\n"
            "Example:\n"
            "https://t.me/example"
        )

    # ==============================================
    # ADD BUTTON LINK
    # ==============================================

    elif action == "add_link":

        link = message.text.strip()

        if not is_valid_telegram_link(link):

            bot.send_message(
                message.chat.id,
                "❌ Invalid Telegram link.\n\n"
                "Example:\n"
                "https://t.me/example"
            )

            return

        data["buttons"].append(
            {
                "name": state["name"],
                "link": link
            }
        )

        save_data(data)

        del states[user_id]

        bot.send_message(
            message.chat.id,
            f"✅ <b>Button Added!</b>\n\n"
            f"🔘 {state['name']}\n"
            f"🔗 {link}",
            reply_markup=admin_keyboard()
        )

    # ==============================================
    # RENAME
    # ==============================================

    elif action == "rename":

        index = state["index"]

        new_name = message.text.strip()

        if not new_name:

            bot.send_message(
                message.chat.id,
                "❌ नाम खाली नहीं हो सकता।"
            )

            return

        old_name = data["buttons"][index]["name"]

        data["buttons"][index]["name"] = new_name

        save_data(data)

        del states[user_id]

        bot.send_message(
            message.chat.id,
            f"✅ <b>Button Renamed!</b>\n\n"
            f"Old: {old_name}\n"
            f"New: {new_name}",
            reply_markup=admin_keyboard()
        )

    # ==============================================
    # CHANGE LINK
    # ==============================================

    elif action == "link":

        link = message.text.strip()

        if not is_valid_telegram_link(link):

            bot.send_message(
                message.chat.id,
                "❌ Invalid Telegram link.\n\n"
                "Example:\n"
                "https://t.me/example"
            )

            return

        index = state["index"]

        data["buttons"][index]["link"] = link

        save_data(data)

        del states[user_id]

        bot.send_message(
            message.chat.id,
            "✅ <b>Link Successfully Changed!</b>",
            reply_markup=admin_keyboard()
        )


# ==================================================
# TELEGRAM LINK VALIDATION
# ==================================================

def is_valid_telegram_link(link):

    return (
        link.startswith("https://t.me/")
        or link.startswith("http://t.me/")
        or link.startswith("https://telegram.me/")
        or link.startswith("http://telegram.me/")
    )


# ==================================================
# RUN BOT
# ==================================================

print("================================")
print("🤖 TRENDING ZONE BOT")
print("================================")
print("✅ Bot is running...")
print("✅ Data file:", DATA_FILE)
print("================================")

bot.infinity_polling(
    timeout=30,
    long_polling_timeout=30
)
