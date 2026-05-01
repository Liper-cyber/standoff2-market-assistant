import pytesseract

from actions import template_finder

from core.driver_manager import driver_manager

from actions import click_action
from core.session_manager import SessionManager

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import time
import random


ZAPROS = [286, 112, 196, 16] # текст вашзапрос на покупку
OK_FIELD = [950, 530] # Кнопка ОКЕЙ  в полле ввода цены
TAP_SKIN = [277 , 125] # Координаты Скина при выбори продажи
GOLD_BALANCE = [770, 0, 192, 50] # Координаты для получения баланса

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

session_manager = SessionManager()
class TraidingServices:
    def __init__(self):
        self.driver_manager = driver_manager
        driver_manager.driver.activate_app('com.axlebolt.standoff2')
        
    def open_need_skin(self, skin_url , skin_name , attempts=0):
        max_attempts = 3
        print('начал опен скин')
        try:
            shop = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/shop.png", threshold=0.7)
            print('нажал ШОП') 
            if shop is False:
                self.driver_manager.driver.back()
                if attempts < max_attempts:
                    return self.open_need_skin(skin_url , skin_name , attempts + 1)
                else:
                    session_manager.reconnect_to_session()
                    return self.open_need_skin(skin_url , skin_name , attempts=0)

            time.sleep(1)
            filter = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/filter.png", threshold=0.8)
            print('нажал ФИЛЬТРЫ')
            time.sleep(1)
            searchFilter = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/searchNameSkinFilter.png", threshold=0.8)
            print('нажал СЕРЧ')
            time.sleep(1)
            searchFilterFill = WebDriverWait(self.driver_manager.driver, 5).until(
                    EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
            if searchFilterFill:

                searchFilterFill[0].clear()

                searchFilterFill[0].send_keys(skin_name)
                print("✅ Текст введен успешно")
                OK_Button = WebDriverWait(self.driver_manager.driver, 5).until(
                    EC.presence_of_all_elements_located((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("ОК")')))
                OK_Button[0].click()
                time.sleep(0.3)
                ApplyFilterSkin = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/applySkinFilter.png", threshold=0.8)
                time.sleep(1)
                Skin = template_finder.find_item_region(self.driver_manager.driver, f"./img/skins/{skin_url}.png", threshold=0.6)
                time.sleep(1)
                return True
            else:
                print("❌ Поля ввода не найдены")
        except Exception as e:
            print(f"❌ Ошибка при открытии скина: {e}")
            session_manager.reconnect_to_session(e)
            self.driver_manager.driver.back()
            self.open_need_skin(skin_url, skin_name)

    def buy_skin(self, buy_price):
        """Вернет True если покупка успешн или количество скинов запросе"""
        try:
            checkBuy = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/CheckBuySkin.png", threshold=0.95 ,click=False)
            if checkBuy is not False:
                numbers = template_finder.parse_quantity_from_text(self.driver_manager.driver , ZAPROS[0] , ZAPROS[1] , ZAPROS[2] , ZAPROS[3])
                if numbers is None: 
                    numbers = 1 
                    print(int(numbers) , "ПРОВЕРКА КОЛ-ВА ЗАПРОСОВ")
                    return numbers
                else:
                    if int(numbers) > 100:
                        numbers = int(numbers) // 10
                        print(int(numbers) , "ПРОВЕРКА КОЛ-ВА ЗАПРОСОВ")
                    return int(numbers)                
            print('НЕТУ ЗАПРОСА')
            requestPrice = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/request.png", threshold=0.9)
            time.sleep(1)
            selectCount = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/selectCount.png", threshold=0.9 ,click=False)
            if selectCount: 
                click_action.random_click(self.driver_manager.driver, selectCount, max_offset=7 , offsetN_x=200)
                CountFill = WebDriverWait(self.driver_manager.driver, 5).until(
                        EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
                if CountFill:
                    CountFill[0].clear()
                    CountFill[0].send_keys('100')
                    OK_Button = WebDriverWait(self.driver_manager.driver, 5).until(
                            EC.presence_of_all_elements_located((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("ОК")')))
                    OK_Button[0].click()

                click_action.random_click(self.driver_manager.driver, selectCount, max_offset=7 , offsetN_x=200 , offsetN_y=-40)
                PriceFill = WebDriverWait(self.driver_manager.driver, 5).until(
                        EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
                if PriceFill:
                    PriceFill[0].clear()
                    PriceFill[0].send_keys(str(buy_price))
                    OK_Button = WebDriverWait(self.driver_manager.driver, 5).until(
                            EC.presence_of_all_elements_located((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("ОК")')))
                    OK_Button[0].click()
            time.sleep(2)
            LastBuyButton = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/BuyFinnuly.png", threshold=0.95,regionX=230,regionY=302,regionW=502,regionH=120)
            time.sleep(1)
            self.driver_manager.driver.back()
            return True
        except Exception as e:
            print(f"❌ Ошибка при открытии скина: {e}")
            session_manager.reconnect_to_session(e)
            self.driver_manager.driver.back()
            return self.buy_skin(buy_price)
    

    def sell_skin(self, sell_price, url_check_nackl, count , checkNakl=True):
        sellSkin = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/sellSkin.png", threshold=0.9)
        click_action.random_click(self.driver_manager.driver, (TAP_SKIN[0], TAP_SKIN[1]), max_offset=5)
        selectedSkin = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/selectedSkin.png", threshold=0.9)
        selectedPriceSkin = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/selectedPriceMeSkin.png", threshold=0.9)

        if selectedPriceSkin is not False:
            click_action.random_click(self.driver_manager.driver, selectedPriceSkin, max_offset=4, offsetN_x=230)
        
        price = str(sell_price)
        if checkNakl:
                    CheckNackl = template_finder.find_item_region(
                        self.driver_manager.driver, f"./img/skins/{url_check_nackl}CheckNackl.png",
                        regionX=180, regionY=132, regionW=400, regionH=228,
                        threshold=0.99, click=False
                    )

                    if CheckNackl is False: price = '222.54'
                    
        try:
            Fill = WebDriverWait(self.driver_manager.driver, 5).until(
                EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
            if Fill:
                Fill[0].clear()
                Fill[0].send_keys(price)
                time.sleep(0.35)
                click_action.random_click(self.driver_manager.driver, (OK_FIELD[0], OK_FIELD[1]))
        except:
            print('нет скина')
            return 0
        createdLotSkin = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/createdLotSkin.png", threshold=0.9)
        now_count = 0
        timeS = time.time()
        time.sleep(1)


        while now_count < count:
            timeE = time.time()
            print('выставил скин', now_count, "время:", timeE - timeS)
            
            price = str(sell_price)
            try:
                click_action.random_click(self.driver_manager.driver, sellSkin)
                time.sleep(random.randint(10 , 20) / 100)
                click_action.random_click(self.driver_manager.driver, (277, 125), max_offset=12)
                click_action.random_click(self.driver_manager.driver, selectedSkin)
                time.sleep(random.randint(10 , 35) / 100)

                if checkNakl:
                    CheckNackl = template_finder.find_item_region(
                        self.driver_manager.driver, f"./img/skins/{url_check_nackl}CheckNackl.png",
                        regionX=180, regionY=132, regionW=400, regionH=228,
                        threshold=0.99, click=False
                    )

                    if CheckNackl is False: price = '222.54'

                click_action.random_click(self.driver_manager.driver, selectedPriceSkin, max_offset=5, offsetN_x=230)
                
                Fill = WebDriverWait(self.driver_manager.driver, 5).until(
                    EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, 'android.widget.EditText')))
                if Fill:
                    Fill[0].clear()
                    Fill[0].send_keys(price)
                    time.sleep(0.15)
                    click_action.random_click(self.driver_manager.driver, (OK_FIELD[0], OK_FIELD[1]))

                click_action.random_click(self.driver_manager.driver, createdLotSkin)
                time.sleep(random.randint(50 , 85) / 100)
                now_count += 1

            except Exception as e:
                print(f"❌ Ошибка при выставлении скина: {e}")
                session_manager.reconnect_to_session(e)
                self.driver_manager.driver.back()
                return now_count
        return now_count
        
    def clean_skin_buy(self):
        try:
            CleanOrder = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/CleanOrder.png", 
                                                          threshold=0.8 , regionX=818 , regionY=94 , 
                                                          regionW=134, regionH=52)
        except Exception as e:
            print(f"❌ Ошибка при очистке заказа: {e}")
            session_manager.reconnect_to_session(e)
            return self.clean_skin_buy()

    def get_gold_balance(self):
        try:
            gold_icon = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/iconGold.png", 
                                                         threshold=0.8 , click=False , regionX=GOLD_BALANCE[0], 
                                                         regionY=GOLD_BALANCE[1], regionW=GOLD_BALANCE[2], regionH=GOLD_BALANCE[3])
            if gold_icon is False:
                print("❌ Иконка золота не найдена")
                driver_manager.driver.back()
                return self.get_gold_balance()
            print(gold_icon)
            gold_balance = template_finder.find_number_on_screen(self.driver_manager.driver, regionX=gold_icon[0]+10, 
                                                           regionY=gold_icon[1]-20, regionW=200, regionH=40)
            return gold_balance
        except Exception as e:
            print(f"❌ Ошибка при получении баланса: {e}")
            session_manager.reconnect_to_session(e)
            return self.get_gold_balance()
    
    def test(self):
        old_order_price = None
        tew = template_finder.find_number_on_screen21(self.driver_manager.driver , regionX=746 , regionY=188 , regionW=56, regionH=28)
        return
        tew = template_finder.find_number_on_screen21(self.driver_manager.driver , regionX=754 , regionY=192 , regionW=48, regionH=18)
        print(tew)
        time.sleep(5)
        while True:
            try:
                str_t = time.time()
                new_order_price = template_finder.find_number_on_screen21(self.driver_manager.driver , regionX=718 , regionY=66 , regionW=82, regionH=16)
                if old_order_price is not None and old_order_price < new_order_price:
                    print('новая цена cтавлюскин')
                    tew = template_finder.find_number_on_screen23(self.driver_manager.driver , regionX=754 , regionY=192 , regionW=48, regionH=18)
                    print("последняя цена запроса: " , tew)
                    time.sleep(10)
                    old_order_price = new_order_price
                else:
                    print('цена старая')
                    old_order_price = new_order_price

                end_t = time.time()
                print(new_order_price , "Время: " ,  end_t - str_t)
            except Exception as e:
                print(f"❌ Ошибка при получении цены: {e}")
                session_manager.reconnect_to_session(e)
                return self.test()