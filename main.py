import logging
import asyncio
from datetime import datetime, timezone, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from flask import Flask

TOKEN = "7764144868:AAE33JoxFweP3b_lFvG9ETGkbiWfYVdG6ZU"
ADMIN_ID = 7718841139  # Замени на свой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Устанавливаем часовой пояс Украины
UA_TIMEZONE = timezone(timedelta(hours=2))


def is_working_hours():
    now = datetime.now(UA_TIMEZONE)
    hour = now.hour
    weekday = now.weekday()

    if weekday < 5:  # Понедельник - Пятница
        return 11 <= hour < 22
    else:  # Суббота - Воскресенье
        return 10 <= hour < 23


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать, вас приветствует D0SKA store! 🎉 Мы ценим качество, надежность и удобство для клиентов. Спасибо, что выбрали нас!"
    )

    keyboard_rules = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я согласен, хочу уже аккаунт😒", callback_data="understood")]
        ]
    )

    await message.answer(
        "📜 *Правила общения в D0SKA store:*\n\n"
        "1️⃣ *Будьте вежливы и уважительны* — общение должно быть корректным, без оскорблений и ненормативной лексики.\n"
        "2️⃣ *Не спамьте* — излишние сообщения мешают работе с другими пользователями.\n"
        "3️⃣ *Уточняйте все детали перед покупкой* — задавайте вопросы, чтобы избежать недоразумений.\n"
        "4️⃣ *Гарантия на аккаунт после покупки — 5 дней* ⏳:\n"
        "   - Распространяется только на случаи восстановления аккаунта владельцем.\n"
        "   - Если аккаунт был заблокирован по вашей вине — гарантия не действует.\n"
        "   - Необходимо предоставить доказательства того, что аккаунт был восстановлен (скриншотом или видео).\n\n"
        "🕒 *График работы (по Киеву):*\n"
        "📅 *Понедельник - Пятница:* 11:00 - 22:00\n"
        "📅 *Суббота - Воскресенье:* 10:00 - 23:00\n\n"
        "✅ Если согласны с правилами, нажмите кнопку ниже.",
        parse_mode="Markdown",
        reply_markup=keyboard_rules
    )


@dp.callback_query(lambda c: c.data == "understood")
async def understood_callback(callback: CallbackQuery):
    await callback.message.answer(
        "📝 *Заполните анкету:*\n"
        "- Игровая площадка 🎮\n"
        "- Что должно быть на аккаунте 🔍\n"
        "- Бюджет аккаунта в грн/руб 💰\n\n"
        "✍ Пожалуйста, введите ваши данные одним сообщением!",
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.message()
async def receive_survey(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    survey_data = message.text

    # Отправляем анкету продавцу с кликабельным ID пользователя
    keyboard_admin = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Ответить пользователю", url=f"tg://user?id={user_id}")]
        ]
    )
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новая анкета от @{username} (ID: {user_id}):\n{survey_data}",
        reply_markup=keyboard_admin
    )

    # Если продавец отдыхает – уведомляем пользователя
    if not is_working_hours():
        await message.answer("😴 Продавец сейчас отдыхает. Он получил вашу анкету, но ответит вам в рабочее время! 🕒")
    else:
        await message.answer("✅ Ваша анкета отправлена продавцу! Он скоро свяжется с вами.")


async def main():
    await dp.start_polling(bot)


# Flask-сервер для health check
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!", 200


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # Запускаем Flask-сервер для обработки health check
    app.run(host="0.0.0.0", port=8000)