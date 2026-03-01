from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import db

router = Router()

async def check_user(message: Message) -> bool:
    if not db.user_exists(message.from_user.id):
        await message.answer("❌ Вы не зарегистрированы. Обратитесь к администратору.")
        return False
    if not db.is_user_active(message.from_user.id):
        await message.answer("❌ Ваш аккаунт деактивирован.")
        return False
    return True

@router.message(Command("start"))
async def cmd_start(message: Message):
    if db.user_exists(message.from_user.id):
        await message.answer("👋 С возвращением! Используйте /help для списка команд.")
    else:
        await message.answer("⛔ Доступ запрещён. Вы не в списке пользователей.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    if not await check_user(message):
        return
    text = """
📋 **Доступные команды:**

💰 **Цена:**
/set_floor <число> — установить максимальную цену (флор)
/set_deviation <число> — установить % отклонения от цены (например, 10 или -5)

📦 **Модели:**
/add_model <название> — добавить модель для отслеживания
/remove_model <название> — удалить модель
/list_models — показать выбранные модели

🎨 **Фоны:**
/add_background <название> — добавить фон
/remove_background <название> — удалить фон
/list_backgrounds — показать выбранные фоны

📝 **Названия подарков:**
/add_gift_name <название> — добавить конкретное название подарка
/remove_gift_name <название> — удалить название
/list_gift_names — показать все названия

📊 **Фильтры:**
/show_filters — показать текущие фильтры
    """
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("set_floor"))
async def set_floor(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("❌ Укажите число. Пример: /set_floor 500")
        return
    floor = int(args[1])
    db.update_filters(message.from_user.id, floor_price=floor)
    await message.answer(f"✅ Флор установлен: {floor}")

@router.message(Command("set_deviation"))
async def set_deviation(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Пример: /set_deviation 10  (разрешить +-10%)\n/set_deviation 0  (только точная цена)")
        return
    try:
        deviation = int(args[1])
        if deviation < -100 or deviation > 100:
            await message.answer("❌ Процент должен быть от -100 до 100")
            return
        db.update_price_deviation(message.from_user.id, deviation)
        if deviation == 0:
            await message.answer("✅ Теперь ищем только точную цену")
        elif deviation > 0:
            await message.answer(f"✅ Разрешаем цену выше рыночной на {deviation}%")
        else:
            await message.answer(f"✅ Ищем цену ниже рыночной на {abs(deviation)}%")
    except ValueError:
        await message.answer("❌ Введите число")

@router.message(Command("add_model"))
async def add_model(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите название модели. Пример: /add_model Редкий")
        return
    model = args[1].strip()
    filters = db.get_user_filters(message.from_user.id)
    models = filters["models"]
    if model in models:
        await message.answer("⚠️ Такая модель уже есть в списке.")
        return
    models.append(model)
    db.update_filters(message.from_user.id, models=models)
    await message.answer(f"✅ Модель «{model}» добавлена.")

@router.message(Command("remove_model"))
async def remove_model(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите название модели.")
        return
    model = args[1].strip()
    filters = db.get_user_filters(message.from_user.id)
    models = filters["models"]
    if model not in models:
        await message.answer("⚠️ Такой модели нет в списке.")
        return
    models.remove(model)
    db.update_filters(message.from_user.id, models=models)
    await message.answer(f"✅ Модель «{model}» удалена.")

@router.message(Command("list_models"))
async def list_models(message: Message):
    if not await check_user(message):
        return
    filters = db.get_user_filters(message.from_user.id)
    models = filters["models"]
    if models:
        await message.answer("📌 **Ваши модели:**\n" + "\n".join(f"• {m}" for m in models), parse_mode="Markdown")
    else:
        await message.answer("📭 Список моделей пуст (отслеживаются все).")

@router.message(Command("add_background"))
async def add_background(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите название фона. Пример: /add_background Золотой")
        return
    bg = args[1].strip()
    filters = db.get_user_filters(message.from_user.id)
    backgrounds = filters["backgrounds"]
    if bg in backgrounds:
        await message.answer("⚠️ Такой фон уже есть в списке.")
        return
    backgrounds.append(bg)
    db.update_filters(message.from_user.id, backgrounds=backgrounds)
    await message.answer(f"✅ Фон «{bg}» добавлен.")

@router.message(Command("remove_background"))
async def remove_background(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите название фона.")
        return
    bg = args[1].strip()
    filters = db.get_user_filters(message.from_user.id)
    backgrounds = filters["backgrounds"]
    if bg not in backgrounds:
        await message.answer("⚠️ Такого фона нет в списке.")
        return
    backgrounds.remove(bg)
    db.update_filters(message.from_user.id, backgrounds=backgrounds)
    await message.answer(f"✅ Фон «{bg}» удалён.")

@router.message(Command("list_backgrounds"))
async def list_backgrounds(message: Message):
    if not await check_user(message):
        return
    filters = db.get_user_filters(message.from_user.id)
    backgrounds = filters["backgrounds"]
    if backgrounds:
        await message.answer("🎨 **Ваши фоны:**\n" + "\n".join(f"• {bg}" for bg in backgrounds), parse_mode="Markdown")
    else:
        await message.answer("📭 Список фонов пуст (отслеживаются все).")

@router.message(Command("add_gift_name"))
async def add_gift_name(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Пример: /add_gift_name Victory Medal")
        return
    gift_name = args[1].strip()
    filters = db.get_user_filters(message.from_user.id)
    gift_names = filters.get("gift_names", [])
    if gift_name in gift_names:
        await message.answer("⚠️ Такое название уже есть в списке.")
        return
    gift_names.append(gift_name)
    db.update_gift_names(message.from_user.id, gift_names)
    await message.answer(f"✅ Название «{gift_name}» добавлено.")

@router.message(Command("remove_gift_name"))
async def remove_gift_name(message: Message):
    if not await check_user(message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Пример: /remove_gift_name Victory Medal")
        return
    gift_name = args[1].strip()
    filters = db.get_user_filters(message.from_user.id)
    gift_names = filters.get("gift_names", [])
    if gift_name not in gift_names:
        await message.answer("⚠️ Такого названия нет в списке.")
        return
    gift_names.remove(gift_name)
    db.update_gift_names(message.from_user.id, gift_names)
    await message.answer(f"✅ Название «{gift_name}» удалено.")

@router.message(Command("list_gift_names"))
async def list_gift_names(message: Message):
    if not await check_user(message):
        return
    filters = db.get_user_filters(message.from_user.id)
    gift_names = filters.get("gift_names", [])
    if gift_names:
        await message.answer("📝 **Отслеживаемые названия:**\n" + "\n".join(f"• {name}" for name in gift_names), parse_mode="Markdown")
    else:
        await message.answer("📭 Список названий пуст (отслеживаются все).")

@router.message(Command("show_filters"))
async def show_filters(message: Message):
    if not await check_user(message):
        return
    filters = db.get_user_filters(message.from_user.id)
    
    deviation_text = ""
    if filters['price_deviation'] == 0:
        deviation_text = "только точная цена"
    elif filters['price_deviation'] > 0:
        deviation_text = f"до +{filters['price_deviation']}% от цены"
    else:
        deviation_text = f"до {filters['price_deviation']}% от цены"
    
    text = f"""
💰 **Флор:** {filters['floor_price']} TON
📊 **Отклонение:** {deviation_text}
📦 **Модели:** {', '.join(filters['models']) if filters['models'] else 'все'}
🎨 **Фоны:** {', '.join(filters['backgrounds']) if filters['backgrounds'] else 'все'}
📝 **Названия:** {', '.join(filters.get('gift_names', [])) if filters.get('gift_names') else 'все'}
    """
    await message.answer(text, parse_mode="Markdown")
