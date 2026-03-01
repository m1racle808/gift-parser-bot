import time
import re
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base import BaseParser
from models import Gift

class GetGemsParser(BaseParser):
    def get_platform_name(self) -> str:
        return "getgems"

    def setup_driver(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        firefox_options.set_preference("dom.max_script_run_time", 30)
        firefox_options.set_preference("dom.max_chrome_script_run_time", 30)
        
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.set_page_load_timeout(30)
        return driver

    async def parse(self) -> List[Gift]:
        gifts = []
        driver = None
        
        try:
            print("🚀 Запускаем Firefox...")
            driver = self.setup_driver()
            
            url = "https://getgems.io/gifts-collection"
            print(f"📡 Загружаем {url}...")
            driver.get(url)
            
            print("⏳ Ждём загрузку страницы...")
            time.sleep(10)
            
            print("📜 Прокручиваем страницу...")
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "NftItemNameContent__name")))
                print("✅ Элементы с названиями найдены")
            except:
                print("⚠️ Таймаут ожидания элементов, но пробуем дальше...")
            
            name_elements = driver.find_elements(By.CLASS_NAME, "NftItemNameContent__name")
            print(f"📦 Найдено названий: {len(name_elements)}")
            
            price_elements = driver.find_elements(By.CLASS_NAME, "LibraryCryptoPrice")
            print(f"💰 Найдено цен: {len(price_elements)}")
            
            link_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/collection/')]")
            print(f"🔗 Найдено ссылок: {len(link_elements)}")
            
            for i in range(min(len(name_elements), 30)):
                try:
                    title = name_elements[i].text.strip()
                    
                    price = 0
                    if i < len(price_elements):
                        price_text = price_elements[i].text.strip()
                        match = re.search(r'(\d+[.,]?\d*)', price_text)
                        if match:
                            price_str = match.group(1).replace(',', '.')
                            price = float(price_str)
                    
                    url = "https://getgems.io/gifts-collection"
                    if i < len(link_elements):
                        href = link_elements[i].get_attribute("href")
                        if href:
                            url = href
                    
                    model = "Обычный"
                    if any(word in title.lower() for word in ['victory', 'medal', 'rare', 'редкий']):
                        model = "Редкий"
                    elif any(word in title.lower() for word in ['bear', 'epic', 'эпический']):
                        model = "Эпический"
                    elif any(word in title.lower() for word in ['legend', 'легендарный']):
                        model = "Легендарный"
                    
                    background = "Стандартный"
                    if any(word in title.lower() for word in ['gold', 'золотой']):
                        background = "Золотой"
                    elif any(word in title.lower() for word in ['silver', 'серебряный']):
                        background = "Серебряный"
                    elif any(word in title.lower() for word in ['red', 'красный']):
                        background = "Красный"
                    elif any(word in title.lower() for word in ['blue', 'синий']):
                        background = "Синий"
                    elif any(word in title.lower() for word in ['green', 'зеленый']):
                        background = "Зелёный"
                    
                    gift_id = url.split('/')[-1] if url else f"gift_{i}"
                    
                    gift = Gift(
                        gift_id=f"getgems_{gift_id}",
                        platform="getgems",
                        title=title,
                        price=price,
                        model=model,
                        background=background,
                        url=url
                    )
                    gifts.append(gift)
                    print(f"✅ {title} - {price} TON")
                    
                except Exception as e:
                    print(f"❌ Ошибка обработки подарка {i}: {e}")
                    continue
            
            print(f"🎉 Всего собрано подарков: {len(gifts)}")
            
            if not gifts:
                print("⚠️ Реальных подарков не найдено, используем тестовые")
                gifts = self.get_test_gifts()
            
            return gifts
            
        except Exception as e:
            print(f"❌ Ошибка в парсере: {e}")
            return self.get_test_gifts()
            
        finally:
            if driver:
                driver.quit()
                print("👋 Firefox закрыт")
    
    def get_test_gifts(self):
        return [
            Gift(
                gift_id="test_1",
                platform="getgems",
                title="Victory Medal #32533",
                price=500,
                model="Редкий",
                background="Золотой",
                url="https://getgems.io/collection/EQC-ZdsouFU-xMa509yP8kzKceZnGV7lSQskxima1Mr3iDYB/EQC2vnBXZeWcx2UY2-aENDllaQfBLJYVbc075yij9G601vG9"
            ),
            Gift(
                gift_id="test_2",
                platform="getgems",
                title="Toy Bear #43552",
                price=54,
                model="Эпический",
                background="Серебряный",
                url="https://getgems.io/collection/EQC1gud6QO8NdJjVrqr7qFBMO0oQsktkvzhmIRoMKo8vxiyL/EQf_tg_gift_______________________8V9WjCAACqIPY6"
            ),
            Gift(
                gift_id="test_3",
                platform="getgems",
                title="Lol Pop #332807",
                price=4.5,
                model="Обычный",
                background="Красный",
                url="https://getgems.io/collection/EQC6zjid8vJNEWqcXk10XjsdDLRKbcPZzbHusuEW6FokOWIm/EQf_tg_gift_______________________9C96ihAAUUB1Hs"
            )
        ]
