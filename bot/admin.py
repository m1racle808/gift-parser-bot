from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
import config
import db

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID

@router.message(Command("adduser"))
async def cmd_adduser(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        await message.answer("❌ Укажите Telegram ID. Пример: /adduser 123456789")
        return
    try:
        tg_id = int(command.args)
        if db.add_user(tg_id):
            await message.answer(f"✅ Пользователь {tg_id} добавлен.")
        else:
            await message.answer(f"⚠️ Пользователь {tg_id} уже существует.")
    except ValueError:
        await message.answer("❌ ID должен быть числом.")

@router.message(Command("removeuser"))
async def cmd_removeuser(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        await message.answer("❌ Укажите Telegram ID.")
        return
    try:
        tg_id = int(command.args)
        if db.remove_user(tg_id):
            await message.answer(f"✅ Пользователь {tg_id} удалён.")
        else:
            await message.answer(f"❌ Пользователь {tg_id} не найден.")
    except ValueError:
        await message.answer("❌ ID должен быть числом.")

@router.message(Command("listusers"))
async def cmd_listusers(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = db.get_all_users_full()
    if not users:
        await message.answer("📭 Нет пользователей.")
        return
    text = "📋 Список пользователей:\n"
    for u in users:
        text += f"• {u['telegram_id']} {'(активен)' if u['is_active'] else '(неактивен)'} | флор: {u['floor_price']}\n"
    await message.answer(text)

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        await message.answer("❌ Укажите сообщение для рассылки.")
        return
    text = command.args
    users = db.get_all_users(only_active=True)
    if not users:
        await message.answer("📭 Нет активных пользователей.")
        return
    success = 0
    fail = 0
    for uid in users:
        try:
            await message.bot.send_message(uid, f"📢 Рассылка:\n{text}")
            success += 1
        except Exception:
            fail += 1
    await message.answer(f"✅ Отправлено: {success}, ошибок: {fail}")
