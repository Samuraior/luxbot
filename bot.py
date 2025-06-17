import telebot
from telebot import types
import json
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1002703116591
ADMIN_ID = 5611365099

bot = telebot.TeleBot(TOKEN)
CONFIG_FILE = "config.json"
user_state = {}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "sponsors": [],
            "join_link": "",
            "post_text": "👇 Підпишись на спонсорів і натисни «Вступити в команду»",
            "button_labels": {
                "join_team": "Вступити в команду",
                "sponsor": "Спонсор"
            }
        }, f, indent=2)

def load_data():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@bot.message_handler(commands=["start"])
def start(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("➕ Додати спонсора", "🗑 Видалити спонсора")
    keyboard.add("✏ Змінити посилання спонсора", "📝 Змінити текст")
    keyboard.add("🔘 Змінити кнопку", "🔗 Змінити лінк на вступ")
    keyboard.add("🚀 Створити пост", "📤 Опублікувати в канал")
    bot.send_message(msg.chat.id, "Привіт! Обери дію:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: True)
def handle(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    text = msg.text
    data = load_data()

    if text == "➕ Додати спонсора":
        user_state[msg.chat.id] = "add_sponsor"
        bot.send_message(msg.chat.id, "Введи посилання на спонсора:")
    elif text == "🗑 Видалити спонсора":
    user_state[msg.chat.id] = "delete_sponsor"
    sponsors = "\n".join([f"{i+1}. {link}" for i, link in enumerate(data["sponsors"])])
    bot.send_message(msg.chat.id, f"Введи номер спонсора, якого хочеш видалити:\n{sponsors}")
    elif text == "✏ Змінити посилання спонсора":
        user_state[msg.chat.id] = "edit_sponsor"
        sponsors = "\n".join([f"{i+1}. {link}" for i, link in enumerate(data["sponsors"])])
        bot.send_message(msg.chat.id, f"Введи номер і нове посилання (через пробіл):
{sponsors}")
    elif text == "📝 Змінити текст":
        user_state[msg.chat.id] = "edit_text"
        bot.send_message(msg.chat.id, "Введи новий текст для посту (можна з емодзі, посиланнями):")
    elif text == "🔘 Змінити кнопку":
        user_state[msg.chat.id] = "edit_buttons"
        bot.send_message(msg.chat.id, "Формат: sponsor=Текст_кнопки, join=Текст_вступу")
    elif text == "🔗 Змінити лінк на вступ":
        user_state[msg.chat.id] = "edit_join"
        bot.send_message(msg.chat.id, "Введи новий лінк для кнопки 'Вступити в команду':")
    elif text == "🚀 Створити пост" or text == "📤 Опублікувати в канал":
        markup = types.InlineKeyboardMarkup()
        for i, sponsor in enumerate(data["sponsors"]):
            label = f"{data['button_labels']['sponsor']} {i+1}"
            markup.add(types.InlineKeyboardButton(label, url=sponsor))
        join_label = data["button_labels"].get("join_team", "Вступити в команду")
        markup.add(types.InlineKeyboardButton(join_label, url=data["join_link"]))

        if text == "📤 Опублікувати в канал":
            try:
                bot.send_message(CHANNEL_ID, data["post_text"], reply_markup=markup, parse_mode="HTML")
                bot.send_message(msg.chat.id, "✅ Пост опубліковано в каналі.")
            except Exception as e:
                bot.send_message(msg.chat.id, f"❌ Помилка при публікації: {e}")
        else:
            bot.send_message(msg.chat.id, data["post_text"], reply_markup=markup, parse_mode="HTML")
    else:
        state = user_state.get(msg.chat.id)
        if state == "add_sponsor":
            data["sponsors"].append(text)
            save_data(data)
            bot.send_message(msg.chat.id, "✅ Спонсор доданий.")
        elif state == "delete_sponsor":
            try:
                num = int(text) - 1
                deleted = data["sponsors"].pop(num)
                save_data(data)
                bot.send_message(msg.chat.id, f"✅ Видалено: {deleted}")
            except:
                bot.send_message(msg.chat.id, "❌ Невірний номер.")
        elif state == "edit_sponsor":
            try:
                parts = text.strip().split(" ", 1)
                num = int(parts[0]) - 1
                new_link = parts[1]
                data["sponsors"][num] = new_link
                save_data(data)
                bot.send_message(msg.chat.id, f"✅ Спонсор {num+1} змінено.")
            except:
                bot.send_message(msg.chat.id, "❌ Формат: номер нове_посилання")
        elif state == "edit_text":
            data["post_text"] = text
            save_data(data)
            bot.send_message(msg.chat.id, "✅ Текст оновлено.")
        elif state == "edit_join":
            data["join_link"] = text.strip()
            save_data(data)
            bot.send_message(msg.chat.id, "✅ Лінк оновлено.")
        elif state == "edit_buttons":
            try:
                parts = dict(x.strip().split("=") for x in text.strip().split(","))
                data["button_labels"].update(parts)
                save_data(data)
                bot.send_message(msg.chat.id, "✅ Назви кнопок оновлено.")
            except:
                bot.send_message(msg.chat.id, "❌ Формат: sponsor=..., join=...")
        user_state[msg.chat.id] = None

bot.polling(none_stop=True)
