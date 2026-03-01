import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
import config
from bot import user, admin
from db import init_db
from scheduler import scheduler
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    init_db()
    print("База данных инициализирована")

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(user.router)
    dp.include_router(admin.router)

    commands = [
        BotCommand(command="start", description="Начало"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="set_floor", description="Установить флор"),
        BotCommand(command="set_deviation", description="Установить отклонение %"),
        BotCommand(command="add_model", description="Добавить модель"),
        BotCommand(command="remove_model", description="Удалить модель"),
        BotCommand(command="list_models", description="Список моделей"),
        BotCommand(command="add_background", description="Добавить фон"),
        BotCommand(command="remove_background", description="Удалить фон"),
        BotCommand(command="list_backgrounds", description="Список фонов"),
        BotCommand(command="add_gift_name", description="Добавить название подарка"),
        BotCommand(command="remove_gift_name", description="Удалить название"),
        BotCommand(command="list_gift_names", description="Список названий"),
        BotCommand(command="show_filters", description="Мои фильтры"),
    ]
    await bot.set_my_commands(commands)

    asyncio.create_task(scheduler(bot))
    print("Планировщик запущен")

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
