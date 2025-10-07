import os
import sys
import asyncio
import logging
import traceback

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonWebApp
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bot")
dp = Dispatcher()

WEB_APP_URL: str = ""  # заполним в main()

def env(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise RuntimeError(f"Не задана переменная окружения: {key}")
    return v

@dp.message(CommandStart())
async def on_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Узнать подробней", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await message.answer(
        "Нажмите кнопку ниже "Узнать подробней".\n",
        reply_markup=kb
    )

@dp.message(F.web_app_data)
async def on_webapp_data(message: Message):
    await message.answer(f"Данные из мини-приложения:\n<code>{message.web_app_data.data}</code>")

async def main():
    print("BUILD_MARKER=railway_runtime_start")   # маркер, чтобы видеть запуск в Runtime Logs
    print("Python:", sys.version)
    print("CWD:", os.getcwd())

    token = env("TELEGRAM_BOT_TOKEN")
    url   = env("WEB_APP_URL")

    global WEB_APP_URL
    WEB_APP_URL = url

    # ✅ aiogram 3.7+: parse_mode задаём через DefaultBotProperties
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # убрать возможный вебхук, чтобы не было 409 при поллинге
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook removed (drop_pending_updates=True)")
    except Exception as e:
        logger.warning("delete_webhook failed: %r", e)

    # проверим логин бота
    me = await bot.get_me()
    logger.info("Bot logged in as @%s (id=%s)", me.username, me.id)

    # кнопка в нижнем меню (дополнительно к inline)
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Туры", web_app=WebAppInfo(url=WEB_APP_URL))
        )
        logger.info("Menu button set")
    except Exception as e:
        logger.warning("set_chat_menu_button failed: %r", e)

    logger.info("Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
