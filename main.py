from core.model import Skin , AccountSkin
from services.database_service import DatabaseService
import time
import random
import os

from decimal import Decimal

STEPBUY = Decimal('0.01')

def TradeByuSell(account_id , skin_count_sell=(20,25) ,selling_price='sell_global_price'):
    skin_data = data.execute_query("""
        SELECT s.id, s.name, s.sell_global_price, s.url, s.buy_price, 
               s.min_buy, s.max_buy, s.interval_minutes, s.rarity, 
               s.sell_price, ask.count
        FROM account_skins ask
        JOIN skins s ON ask.skin_id = s.id
        WHERE ask.last_buy < NOW() - (s.interval_minutes || 'minutes')::INTERVAL 
          AND ask.account_id = %s AND ask.is_buy = true
    """, params=(account_id,), fetch_one=True)

    if skin_data is not None:
        skin = Skin.from_db_row(skin_data)
        new_price = skin.buy_price - STEPBUY
        print(skin , new_price)

        trade.open_need_skin(skin.url , skin.name)

        account_skin_data = data.execute_query("""
                 SELECT account_id , skin_id , last_buy , last_sell , count , sell_count , wait_attempts , is_buy , is_sale , fast_order
                 FROM account_skins 
                 WHERE skin_id = %s AND account_id = %s
             """, params=(skin.id, account_id,), fetch_one=True)
        

        print(account_skin_data)
        account_skin = AccountSkin.from_db_row(account_skin_data)

        result_buy = trade.buy_skin(skin.buy_price)

        if result_buy == True: # если выставил запрос 100 скинов на покупку
            # РАБОТА С ИЗМЕНЕНИЕМ ЦЕНЫ ПОКУПКИ ЕСЛИ ОНА БЕЗ ДОП ОЖИДАНИЙ 3 раза- СНИЖАЕМ ЦЕНТУ НА STEPBUY

            if account_skin.wait_attempts == 0: #если купилось без ожиданий
                if account_skin.fast_order == 2: # если купилось с 1 попытка 2 раза подряд
                    if skin.buy_price > skin.min_buy:
                        print('Скупилось без ожиданий 2, снижаем цену на ' , STEPBUY)
                        new_price = skin.buy_price - STEPBUY
                        data.execute_query("""
                            UPDATE skins SET buy_price = %s WHERE id = %s;
                            UPDATE account_skins SET fast_order = 0 , last_buy = NOW() , count = count + 100 WHERE skin_id = %s AND account_id = %s;
                        """, params=(new_price, skin.id, skin.id, account_id,))
                        print(f'⬇️ Цена уменьшена на {STEPBUY}, новая цена: ' , new_price)
                    else:
                        print('Цена уже на минимальном уровне')
                        data.execute_query("UPDATE account_skins SET last_buy = NOW() WHERE skin_id = %s AND account_id = %s", params=(skin.id, account_id,))
                else: # если не купилось с 1 попытка 3 раза подряд
                    print('Скупилось без ожиданий, увеличиваем fast_order')
                    data.execute_query("UPDATE account_skins SET fast_order = fast_order + 1 , last_buy = NOW() , count = count + 100 WHERE skin_id = %s AND account_id = %s" , params=(skin.id, account_id,))
            else: #если купилось с ожиданием
                data.execute_query('UPDATE account_skins SET last_buy = NOW() , count = count + 100 , wait_attempts = 0 WHERE skin_id = %s and account_id = %s' , params=(skin.id,account_id,))
        else: # если запрос еще не завершился 
            print('⌛ Покуплка еще не завершена')

            if account_skin.wait_attempts == 3: # если скин не закупился уже 3 раза подряд
                print('⬆️ 3 неудачных попытки, увеличиваем цену')
                if skin.buy_price < skin.max_buy:
                    new_price = skin.buy_price + STEPBUY
                    data.execute_query("""
                        UPDATE skins SET buy_price = %s WHERE id = %s;
                        UPDATE account_skins SET wait_attempts = 0 , last_buy = NOW() - INTERVAL '10 minute' , count = count - %s WHERE skin_id = %s AND account_id = %s;
                    """, params=(new_price, skin.id, result_buy, skin.id, account_id,))
                    print(f'Цена увеличена на {STEPBUY}, новая цена: ' , new_price)
                    trade.clean_skin_buy()
                else:
                    print('Цена уже на максимальном уровне')
                    data.execute_query("UPDATE account_skins SET last_buy = NOW() WHERE skin_id = %s AND account_id = %s", params=(skin.id, account_id,))
            else: # если скин не закупился меньше 3 раз просто прибавляем попытку ожидания и минуты для ожидания если укупилось уже 70 скинов например
                wait_time = 11 - (result_buy // 10)
                print('⌛ Тут уже запрос ждем еще: ' , wait_time)
                data.execute_query('''
                        UPDATE account_skins 
                        SET last_buy = NOW() - (%s * INTERVAL '1 minute') , wait_attempts = wait_attempts + 1 , fast_order = 0
                        WHERE skin_id = %s AND account_id = %s
                ''', params=(wait_time, skin.id, account_id))
    else:
        print(f"🍭 скинов для покупки нет , выставляю {skin_count_sell} скинов")

        skins_sell_row = data.execute_query("""SELECT s.id , s.sell_price ,s.sell_global_price , s.url , s.name FROM account_skins ask 
                                            JOIN skins s ON s.id = ask.skin_id
                                            WHERE account_id = %s and last_sell < NOW() - (2 || 'minutes')::INTERVAL and is_sale = true
                                            """ , fetch_all=True, params=(account_id,))
        if not skins_sell_row or len(skins_sell_row) == 0:
            print("⚠️ Нет скинов для продажи (все скины недавно продавались или их нет)")
            time.sleep(60)
            return
        skin_sell = random.choice(skins_sell_row)
        trade.open_need_skin(skin_sell['url'] , skin_sell['name'])
        selling_count = trade.sell_skin(skin_sell[selling_price], skin_sell['url'] , random.randint(*skin_count_sell))
        data.execute_query('UPDATE account_skins SET last_sell = NOW() , sell_count = sell_count + %s  WHERE skin_id = %s and account_id = %s' , params=(selling_count, skin_sell['id'], account_id,))


def get_full_info_account(account_id):
    account_data = data.execute_query("""
        SELECT a.name , a.gold , s.name , ask.count , ask.sell_count , s.buy_price FROM account_skins ask
        JOIN skins s ON ask.skin_id = s.id
        JOIN account a ON a.id = ask.account_id
        WHERE a.id = %s
    """, params=(account_id,), fetch_all=True)

    data.execute_query("INSERT INTO history_account (id_account, history_json) VALUES (%s, %s)", params=(account_id, str(account_data)))
    return account_data

        
def sell_random_skins(account_id):
    skins = data.execute_query("""SELECT s.id , s.url , s.name , s.sell_price FROM account_skins ask
        JOIN skins s ON s.id = ask.skin_id
        WHERE ask.account_id = %s and ask.is_sale = true""", params=(account_id,), fetch_all=True)
    skin = random.choice(skins)
    trade.open_need_skin(skin['url'] , skin['name'])
    selling_count =trade.sell_skin(skin['sell_price'], skin['url'] , random.randint(80, 140))
    data.execute_query('UPDATE account_skins SET last_sell = NOW() , sell_count = sell_count + %s WHERE skin_id = %s and account_id = %s' , params=(selling_count, skin['id'], account_id,))


account_id = DatabaseService().execute_query('SELECT id FROM account WHERE nox_devices_id = %s', params=(int(os.getenv('DEVICE_UDID')),) , fetch_one=True)

from dotenv import load_dotenv
load_dotenv()




def buy_action(account_id, actions = 'Тест функций' , gold_check = True):
    global trade , data
    print('начал функцию' , account_id , account_id)
    # Создаем глобальный экземпляр конфига
    

    data = DatabaseService()
    from core.devices_manager import DevicesManager
    from config.appium_config import capability_me , appium_config

    nox_row = data.execute_query("""SELECT nd.id_nox , nd.proxy_port FROM account a
                    JOIN nox_devices nd ON nd.id = a.nox_devices_id
                    WHERE a.id = %s """ , params=(account_id,) ,fetch_one=True)
    
    
    DevicesManager().create_device(nox_id=nox_row['id_nox'] , port=nox_row['proxy_port'])
    time.sleep(20)
    capability_me = appium_config.get_capabilities(nox_row['id_nox'])
    from services.traiding_services import TraidingServices

    trade = TraidingServices()
    time.sleep(40)
    
    count_def = 0
    if actions == 'Продажа по Глобальной цене' or actions == 'Продажа по обычной цене':
        if actions == 'Продажа по Глобальной цене':
            selling = 'sell_global_price'
        else:
            selling = 'sell_price'
        
        while True:
            TradeByuSell(account_id, (20,30) , selling)
            if count_def % 10 == 0 and gold_check == True:
                print('5 запуск функции получения баланса золота')
                gold_balance = trade.get_gold_balance()
                if gold_balance is None:
                    print("❌ Не удалось получить баланс золота. Пропускаем обновление.")
                else:
                    print(f"Баланс золота: {gold_balance}")
                    get_full_info_account(account_id)
                    data.execute_query("UPDATE account SET gold = %s WHERE id = %s" , params=(gold_balance, account_id,))

            count_def += 1

    elif actions == 'Рандомная продажа':
            while True :
                sell_random_skins(account_id)
                if count_def % 10 == 0 and gold_check == True:
                    print('5 запуск функции получения баланса золота')
                    gold_balance = trade.get_gold_balance()
                    if gold_balance is None:
                        print("❌ Не удалось получить баланс золота. Пропускаем обновление.")
                    else:
                        print(f"Баланс золота: {gold_balance}")
                        get_full_info_account(account_id)
                        data.execute_query("UPDATE account SET gold = %s WHERE id = %s" , params=(gold_balance, account_id,))

                count_def += 1


def test(nox_id):
    print('тест')
    from config.appium_config import capability_me , appium_config
    capability_me = appium_config.get_capabilities(nox_id)

    from services.traiding_services import TraidingServices
    trade = TraidingServices()

    trade.test()

