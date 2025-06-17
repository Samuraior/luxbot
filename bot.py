import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1002703116591
ADMIN_ID = 5611365099
sponsors = []  # заміни на свої юзернейми або інвайт-лінки

bot = telebot.TeleBot(TOKEN)

# --- Головне меню ---
@bot.message_handler(commands=['start'])
def start(msg):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📤 Створити пост", callback_data="create_post"),
        InlineKeyboardButton("➕ Додати спонсора", callback_data="add_sponsor")
    )
    markup.row(
        InlineKeyboardButton("❌ Видалити спонсора", callback_data="remove_sponsor"),
        InlineKeyboardButton("🔗 Вступити в команду", callback_data="join_team")
    )
    bot.send_message(msg.chat.id, "👋 Вітаю! Обери дію:", reply_markup=markup)

# --- Обробка кнопок ---
@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.data == "create_post":
        bot.send_message(call.message.chat.id, "📝 Напиши текст поста:")
        bot.register_next_step_handler(call.message, process_post_text)

    elif call.data == "join_team":
        check_subscriptions(call)

    elif call.data == "add_sponsor":
        bot.send_message(call.message.chat.id, "🔗 Надішли @юзернейм або лінк на спонсора")
        bot.register_next_step_handler(call.message, add_sponsor)

    elif call.data == "remove_sponsor":
        if sponsors:
            markup = InlineKeyboardMarkup()
            for sponsor in sponsors:
                markup.add(InlineKeyboardButton(sponsor, callback_data=f"remove_{sponsor}"))
            bot.send_message(call.message.chat.id, "Оберіть спонсора для видалення:", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Список спонсорів пустий")

    elif call.data.startswith("remove_"):
        sponsor_to_remove = call.data.replace("remove_", "")
        if sponsor_to_remove in sponsors:
            sponsors.remove(sponsor_to_remove)
            bot.send_message(call.message.chat.id, f"✅ {sponsor_to_remove} видалено зі списку.")

# --- Обробка створення поста ---
def process_post_text(msg):
    post_text = msg.text
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Вступити в команду", callback_data="join_team"))

    try:
        bot.send_message(CHANNEL_ID, post_text, reply_markup=markup, parse_mode="HTML")
        bot.send_message(msg.chat.id, "✅ Пост опубліковано!")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Помилка при публікації: {e}")

# --- Додати спонсора ---
def add_sponsor(msg):
    sponsor = msg.text.strip()
    if sponsor not in sponsors:
        sponsors.append(sponsor)
        bot.send_message(msg.chat.id, f"✅ Додано спонсора: {sponsor}")
    else:
        bot.send_message(msg.chat.id, "⚠️ Цей спонсор вже є у списку")

# --- Перевірка підписок ---
def check_subscriptions(call):
    user_id = call.from_user.id
    not_subscribed = []

    for sponsor in sponsors:
        try:
            sponsor_id = sponsor
            if sponsor.startswith("https://t.me/"):
                sponsor_id = sponsor.split("/")[-1]
                if sponsor_id.startswith("+"):
                    sponsor_id = sponsor  # інвайт-лінки залишаємо як є

            member = bot.get_chat_member(sponsor_id, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(sponsor)
        except:
            not_subscribed.append(sponsor)

    if not_subscribed:
        bot.answer_callback_query(call.id, "❌ Ти не підписався на всіх спонсорів!", show_alert=True)
    else:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "✅ Вітаю! Ти підписався на всіх спонсорів!")

bot.infinity_polling()
