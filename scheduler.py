import asyncio
from typing import List
from models import Gift
import db
import config
from parsers import GetGemsParser

async def parse_all() -> List[Gift]:
    parsers = [
        GetGemsParser(),
    ]
    
    tasks = [parser.parse() for parser in parsers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_gifts = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f"❌ Ошибка в парсере {parsers[i].get_platform_name()}: {res}")
        else:
            all_gifts.extend(res)
    
    return all_gifts

def check_gift_for_user(gift: Gift, user_filters: dict) -> bool:
    if user_filters["floor_price"] > 0 and gift.price > user_filters["floor_price"]:
        return False
    
    if user_filters["models"] and gift.model not in user_filters["models"]:
        return False
    
    if user_filters["backgrounds"] and gift.background not in user_filters["backgrounds"]:
        return False
    
    if user_filters.get("gift_names"):
        found = False
        for name in user_filters["gift_names"]:
            if name.lower() in gift.title.lower():
                found = True
                break
        if not found:
            return False
    
    return True

async def process_gifts(bot):
    print("🔍 Запуск парсинга...")
    gifts = await parse_all()
    print(f"📦 Найдено {len(gifts)} подарков")
    
    users = db.get_all_users(only_active=True)
    if not users:
        print("👤 Нет активных пользователей")
        return
    
    new_gifts_count = 0
    for gift in gifts:
        if db.gift_already_sent(gift.gift_id):
            continue
        
        for tg_id in users:
            filters = db.get_user_filters(tg_id)
            if not filters:
                continue
            
            if check_gift_for_user(gift, filters):
                text = f"""
🎁 **Новый подарок!**
🏷 **Площадка:** {gift.platform}
📌 **Название:** {gift.title}
💰 **Цена:** {gift.price} TON
📦 **Модель:** {gift.model or 'не указана'}
🎨 **Фон:** {gift.background or 'не указан'}
🔗 [Ссылка]({gift.url})
                """
                try:
                    await bot.send_message(tg_id, text, parse_mode="Markdown")
                    new_gifts_count += 1
                    print(f"📤 Отправлено пользователю {tg_id}: {gift.title}")
                except Exception as e:
                    print(f"❌ Ошибка отправки пользователю {tg_id}: {e}")
        
        db.add_sent_gift(
            gift.gift_id,
            gift.platform,
            gift.price,
            gift.model,
            gift.background,
            gift.title,
            gift.url
        )
    
    print(f"✅ Отправлено уведомлений: {new_gifts_count}")

async def scheduler(bot):
    while True:
        await process_gifts(bot)
        await asyncio.sleep(config.PARSE_INTERVAL)
