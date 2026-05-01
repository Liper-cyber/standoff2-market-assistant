import random
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder


def random_click(driver, positionElement, max_offset=7 ,offsetN_x=0, offsetN_y=0):
    """
    Клик по координатам со случайным смещением
    
    Args:
        driver: Appium driver
        positionElement: координаты (24 , 56)
        max_offset: максимальное случайное смещение в пикселях
        offsetN_x: отступ от центра например 150 - правее на 150 px
        возвращает : (24, 56)
    """
    # Случайное смещение
    offset_x = random.randint(-max_offset, max_offset)
    offset_y = random.randint(-max_offset, max_offset)
    
    # Итоговые координаты
    click_x = positionElement[0] + offset_x + offsetN_x
    click_y = positionElement[1] + offset_y + offsetN_y
    
    # Случайная задержка перед кликом (более человеческая)
    delay = random.uniform(0.07, 0.15)
    
    try:
        finger = PointerInput(POINTER_TOUCH, "finger")
        action = ActionBuilder(driver, mouse=finger)
        action.pointer_action.move_to_location(click_x, click_y)
        action.pointer_action.pause(delay)  # Задержка перед нажатием
        action.pointer_action.pointer_down()
        action.pointer_action.pause(random.uniform(0.05, 0.12))  # Задержка нажатия
        action.pointer_action.pointer_up()
        action.perform()
        
        return (click_x - offset_x , click_y - offset_y)
    except Exception as e:
        print(f"❌ Ошибка клика: {e}")
        return False