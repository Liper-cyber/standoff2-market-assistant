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
            # РАБОТА С ИЗМЕНЕНИЕМ ЦЕНЫ ПОКУПКИ ЕСЛИ ОНА БЕЗ ДОП. ОЖИДАНИЙ 3 раза- СНИЖАЕМ ЦЕНТУ НА STEPBUY

            if account_skin.wait_attempts == 0: #если купилось без ожиданий
                if account_skin.fast_order == 2: # если купилось с 1 попытка 2 раза подряд
                    if skin.buy_price > skin.min_buy:
                        print('Скупилось без ожиданий 2раза , снижаем цену на ' , STEPBUY)
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
            #   Проверяем если запрос еще не выполнился за 3 ожидания уменьшяем цену на покупку скина , а так же отменяет запрос
            # и обновляем количесво скинов , мы сначало при запросе + 100 , а тут если отсалось 56 , то общее колво - 56
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
            else: # если скин не закупился меньше 3 раз просто прибавляем попытку ожидания и минуты для ожидания исходя из количесво скинов, 
                # если укупилось уже 70 скинов например то ждем 7 минут
                wait_time = 11 - (result_buy // 10)
                print('⌛ Тут уже запрос ждем еще: ' , wait_time)
                data.execute_query('''
                        UPDATE account_skins 
                        SET last_buy = NOW() - (%s * INTERVAL '1 minute') , wait_attempts = wait_attempts + 1 , fast_order = 0
                        WHERE skin_id = %s AND account_id = %s
                ''', params=(wait_time, skin.id, account_id))
    else:
        # продажа разных скинов , исходя из last_sell , этот элемент заменяет обычное простаивания аккаунта
        # Пока запросы выполняются мы отчищаем инвентарь что бы не лагало 
        print(f"🍭 скинов для покупки нет , выставляю {skin_count_sell} скинов")

        skins_sell_row = data.execute_query("""SELECT s.id , s.sell_price ,s.sell_global_price , s.url , s.name FROM account_skins ask 
                                            JOIN skins s ON s.id = ask.skin_id
                                            WHERE account_id = %s and last_sell < NOW() - (2 || 'minutes')::INTERVAL and is_sale = true
                                            """ , fetch_all=True, params=(account_id,))
        if not skins_sell_row or len(skins_sell_row) == 0:
            print("⚠️ Нет скинов для продажи (все скины недавно продавались или их нет)")
            time.sleep(60)
            return
        # выбираем рандомный скин и рандомное количесто на продажу , что бы уменьшить риски бана за бота
        skin_sell = random.choice(skins_sell_row)
        trade.open_need_skin(skin_sell['url'] , skin_sell['name'])
        selling_count = trade.sell_skin(skin_sell[selling_price], skin_sell['url'] , random.randint(*skin_count_sell))
        data.execute_query('UPDATE account_skins SET last_sell = NOW() , sell_count = sell_count + %s  WHERE skin_id = %s and account_id = %s' , params=(selling_count, skin_sell['id'], account_id,))


def add_history_for_account(account_id):
    """Функция для добяления json всего аккаунта в иторию что бы смотреть изменения баланса скинов и прочего в интрефейсе"""
    account_data = data.execute_query("""
        SELECT a.name , a.gold , s.name , ask.count , ask.sell_count , s.buy_price FROM account_skins ask
        JOIN skins s ON ask.skin_id = s.id
        JOIN account a ON a.id = ask.account_id
        WHERE a.id = %s
    """, params=(account_id,), fetch_all=True)

    data.execute_query("INSERT INTO history_account (id_account, history_json) VALUES (%s, %s)", params=(account_id, str(account_data)))
    return account_data

        
def sell_random_skins(account_id):
    """Функция для скипа времени , если аккаунт выставил все запросы , то мы переходим в продажу скиннов что бы не забиват
    Инвентарь аккаунта , продаем по глобальной цене(выставлять скину -  долго , отменять если это нужно будет - быстро)"""
    skins = data.execute_query("""SELECT s.id , s.url , s.name , s.sell_price , s.sell_global_price FROM account_skins ask
        JOIN skins s ON s.id = ask.skin_id
        WHERE ask.account_id = %s and ask.is_sale = true""", params=(account_id,), fetch_all=True)
    skin = random.choice(skins)
    trade.open_need_skin(skin['url'] , skin['name'])
    selling_count =trade.sell_skin(skin['sell_global_price'], skin['url'] , random.randint(80, 140))
    data.execute_query('UPDATE account_skins SET last_sell = NOW() , sell_count = sell_count + %s WHERE skin_id = %s and account_id = %s' , params=(selling_count, skin['id'], account_id,))



def buy_action(account_id, actions = 'Тест функций' , gold_check = True):
    global trade , data
    print('начал функцию' , account_id)
    # Создаем глобальный экземпляр конфига
    
    
    data = DatabaseService()
    from core.devices_manager import DevicesManager
    from config.appium_config import capability_me , appium_config

    VM_id = data.execute_query("""SELECT nd.id_nox , nd.proxy_port FROM account a
                    JOIN nox_devices nd ON nd.id = a.nox_devices_id
                    WHERE a.id = %s """ , params=(account_id,) ,fetch_one=True)
    
    
    DevicesManager().create_device(VM_id=VM_id['id_nox'] , port=VM_id['proxy_port']) # создали VM
    time.sleep(20)
    capability_me = appium_config.get_capabilities(VM_id['id_nox']) # получили для него capability что бы подключиться 

    from services.traiding_services import TraidingServices
    trade = TraidingServices() # тут мы запускаем сервера , дарайвера, OPENCV - компьютерноее зрения

    time.sleep(40)
    
    count_def = 0
    if actions == 'Продажа по Глобальной цене' or actions == 'Продажа по обычной цене':
        # Глобальная цена - цена на долгий срок продажи например если купил за 0.05 , глобальная цена 0.09 - продажа будет через 2-3 месяца
        # Обычная цена - продажа скина по цене в маленькую прибыль (0.01gold) продается почти в тотже день или в течении недели
        if actions == 'Продажа по Глобальной цене':
            selling = 'sell_global_price'
        else:
            selling = 'sell_price'
        
        while True:
            """запускает функции , после 10 законченной функции мы делаем фотку баланса и записываем в базу данных"""
            TradeByuSell(account_id, (20,30) , selling)
            if count_def % 10 == 0 and gold_check == True:
                print('5 запуск функции получения баланса золота')
                gold_balance = trade.get_gold_balance()
                if gold_balance is None:
                    print("❌ Не удалось получить баланс золота. Пропускаем обновление.")
                else:
                    print(f"Баланс золота: {gold_balance}")
                    add_history_for_account(account_id)
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
                        add_history_for_account(account_id)
                        data.execute_query("UPDATE account SET gold = %s WHERE id = %s" , params=(gold_balance, account_id,))

                count_def += 1


def test(nox_id):
    # skin_data = data.execute_query("""
    #     SELECT s.id, s.name, s.sell_global_price, s.url, s.buy_price, 
    #            s.min_buy, s.max_buy, s.interval_minutes, s.rarity, 
    #            s.sell_price, ask.count
    #     FROM account_skins ask
    #     JOIN skins s ON ask.skin_id = s.id
    #     WHERE ask.last_buy < NOW() - (s.interval_minutes || 'minutes')::INTERVAL 
    #       AND ask.account_id = %s AND ask.is_buy = true
    # """, params=(account_id,), fetch_one=True)
    # skin = Skin.from_db_row(skin_data)
    # trade.open_need_skin(skin.url , skin.name)

    print('тест')
    from config.appium_config import capability_me , appium_config
    capability_me = appium_config.get_capabilities(nox_id)

    from services.traiding_services import TraidingServices , HuckPrice003
    trade = TraidingServices()
    while True:
        trade.test()
    # while True:
    #     # error = trade.test(regionPriceAll=(3,8))
    #     result = trade.main_huck(regionPriceAll=(40,70),attempts_search=150)
    #     if result is False:
    #         print('либо краш либо какая то ошибка')
    #         break
        # if error:
        #     print('пробую открыть скин')
            #trade.open_need_skin(skin.url , skin.name)

# test(24)

# -- Запуск интерфейса --


def buy_skins(action = None):
    account_id = DatabaseService().execute_query('SELECT id FROM account WHERE nox_devices_id = %s', params=(int(os.getenv('DEVICE_UDID')),) , fetch_one=True)

    from dotenv import load_dotenv
    load_dotenv()
    if action is None:
        user_select = int(input('Выберите вариант трейдинга\n1: Глобальная продажа - покупает скины и продает скины по глобальной цене(1-2месяца)\n2: Обычная продажа - покупает скины и продает по быстрой цене (1-2дня)\n3: Рандомная продажа - только продает скины , не ставит запросы\n4: Кастомная функция - если вы сделали только провреку чего то\nВаш выбор: '))
        if user_select == 1:
            action = 'Продажа по Глобальной цене'
        elif user_select == 2:
            action = 'Продажа по обычной цене'
        elif user_select == 3:
            action = 'Рандомная продажа'
        elif user_select == 4:
            custom_buy(nox_id=int(os.getenv('DEVICE_UDID')))
            return
    buy_action(account_id=account_id['id'] , actions=action)
    return


def custom_buy(account_id=1, skin_count_sell=(20,25) ,selling_price='sell_global_price'):

    from config.appium_config import capability_me , appium_config
    data = DatabaseService()
    VM_id = data.execute_query("""SELECT nd.id_nox , nd.proxy_port FROM account a
                            JOIN nox_devices nd ON nd.id = a.nox_devices_id
                            WHERE a.id = %s """ , params=(account_id,) ,fetch_one=True)
    
    capability_me = appium_config.get_capabilities(VM_id['id_nox'])
    from actions.template_finder import TemplateFinder , find_count_on_screen , find_number_in_balance , debug_specific_pixels
    from services.traiding_services import TraidingServices
    trade = TraidingServices()
    ZAPROS = [286, 112, 196, 16] # текст вашзапрос на покупку
    GOLD_BALANCE = [770, 0, 192, 50] # Координаты для получения баланса

    numbers = find_number_in_balance(trade.driver_manager.driver , 851 , 4 , 140 , 40)
    

    
    
    

