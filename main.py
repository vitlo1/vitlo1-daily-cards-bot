import os
import random
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command
from aiogram.types import ChatMember, ChatMemberOwner, ChatMemberAdministrator
import logging

# -----------------------------
# 🔑 Настройки
# -----------------------------
BOT_TOKEN = "8385761559:AAGNPCA8dgBGuyHIoBqFS9LZe56yQT8PXhU"
CHANNEL_USERNAME = "@yejcards"

# -----------------------------
# 📚 Данные
# -----------------------------

HOLIDAYS = {
    "01-01": "С Новым годом!",
    "01-07": "С Рождеством!",
    "02-14": "С Днём святого Валентина!",
    "02-23": "С Днём защитника Отечества!",
    "03-08": "С Международным женским днём!",
    "05-01": "С Праздником весны и труда!",
    "05-09": "С Днём Победы!",
    "06-12": "С Днём России!",
    "11-04": "С Днём народного единства!",
    "12-09": "С Днём Героев Отечества!",
}

QUOTES = [
    "Пусть день будет таким же прекрасным, как твоя улыбка!",
    "Ты справишься! Верь в себя — у тебя всё получится.",
    "Сегодня — отличный день для маленького чуда.",
    "Ты делаешь мир лучше просто своим присутствием.",
    "Даже маленький шаг — это движение вперёд.",
    "Ты заслуживаешь счастья, любви и спокойствия.",
    "Пусть удача будет твоей спутницей сегодня!",
    "Ты — источник света для многих. Не гасни!",
]

def generate_card(text: str, time_of_day: str = "day") -> str:
    bg_color = {
        "morning": (70, 130, 180),
        "day": (135, 206, 235),
        "evening": (255, 165, 0),
        "night": (25, 25, 112),
    }.get(time_of_day, (240, 240, 240))

    width, height = 800, 600
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2

    draw.text((x + 2, y + 2), text, fill="black", font=font)
    draw.text((x, y), text, fill="white", font=font)

    filename = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    img.save(filename)
    return filename

def get_theme_and_text() -> tuple[str, str]:
    now = datetime.now()
    today = date.today()
    month_day = today.strftime("%m-%d")

    if month_day in HOLIDAYS:
        return "day", HOLIDAYS[month_day]

    hour = now.hour
    if 6 <= hour < 12:
        time_key = "morning"
        base_text = "Доброе утро! ☀️"
    elif 12 <= hour < 18:
        time_key = "day"
        base_text = "Хорошего дня! 🌼"
    elif 18 <= hour < 24:
        time_key = "evening"
        base_text = "Доброго вечера! 🌙"
    else:
        time_key = "night"
        base_text = "Спокойной ночи! 🌌"

    quote = random.choice(QUOTES)
    full_text = f"{base_text}\n\n{quote}"
    return time_key, full_text

router = Router()

@router.message(Command("start", "card"))
async def send_card(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    try:
        chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if isinstance(chat_member, (ChatMember, ChatMemberOwner, ChatMemberAdministrator)):
            pass
        else:
            await ask_to_subscribe(message)
            return
    except Exception as e:
        logging.error(f"Ошибка подписки: {e}")
        await message.answer("Не удалось проверить подписку. Попробуйте позже.")
        return

    time_key, text = get_theme_and_text()
    card_path = generate_card(text, time_key)

    photo = FSInputFile(card_path)
    await message.answer_photo(photo, caption="Ваша ежедневная открытка! 💌")

    os.remove(card_path)

async def ask_to_subscribe(message: types.Message):
    btn = InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    kb = InlineKeyboardMarkup(inline_keyboard=[[btn]])
    await message.answer(
        f"Чтобы получать ежедневные открытки, подпишись на канал {CHANNEL_USERNAME}!",
        reply_markup=kb
    )

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio
    asyncio.run(main())
