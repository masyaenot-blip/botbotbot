import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Не задана переменная окружения: {name}")
    return v

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
WEB_APP_URL        = env("WEB_APP_URL")  # ваш Vercel URL, напр. https://tour-app.vercel.app

@dp.message(CommandStart())
async def on_start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="Забронировать тур", web_app=WebAppInfo(url=WEB_APP_URL))
        ]],
        resize_keyboard=True,
        is_persistent=True
    )
    text = (
        "Нажмите кнопку ниже чтобы забронировать тур.\n"
        "Кнопка называется «Забронировать тур»."
    )
    await message.answer(text, reply_markup=kb)

@dp.message(F.web_app_data)
async def on_webapp_data(message: Message):
    await message.answer(
        f"Получены данные из мини-приложения:\n<code>{message.web_app_data.data}</code>"
    )

async def main():
    bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
