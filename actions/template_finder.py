import io
from PIL import Image
import cv2
import numpy as np
import time
from actions import click_action
import pytesseract
import easyocr
import re
from config.configall import MODEL_EasyOCR_PATH
# Глобальный reader (инициализируем один раз вне функции — важно для производительности!)

from config.devices_config import DevicesConfig

class TemplateFinder:
    def __init__(self):
        self.reader = None
        self.model_dir = MODEL_EasyOCR_PATH

    def get_reader(self):
        """Возвращает EasyOCR reader. Создаёт новый при каждом вызове."""
        if self.reader is not None:
            return self.reader
        
        else:
            download_enabled = False
            print("✅ Модели EasyOCR найдены")

        try:
            self.reader = easyocr.Reader(
                ['en', 'ru'],
                gpu=True,
                download_enabled=download_enabled,
                model_storage_directory=self.model_dir,
                quantize=False,           # важно для стабильности
                detector=True,
                recognizer=True
            )
            print("✅ EasyOCR Reader успешно создан")
            return self.reader
        except Exception as e:
            print(f"❌ Ошибка при создании EasyOCR Reader: {e}")
            raise

reader = TemplateFinder().get_reader()

def find_item_region(driver, template_path, regionX = 0, regionY = 0, 
                                   regionW = DevicesConfig().weidth, regionH = DevicesConfig().height, 
                                   threshold=0.5 , click = True , name = 'Имя'):
    """
    Ищет шаблон в указанной области с помощью OpenCV
    если ничего не нашел возвращает false , если нашел возвращает центральные координаты элемента на экране
    
    ИСПОЛЬЗОВНИЕ element = find_template_in_region_opencv(driver, "./img/interfeces/checkBuySkin.png", threshold=0.9 , click=False)
    random_click_on_element(driver , (element.location['x'] , element.location['y']), offsetN_x=250)
    """
    time.sleep(1)
    # Делаем скриншот
    screenshot = driver.get_screenshot_as_png()
    screenshot_img = Image.open(io.BytesIO(screenshot))
    
    # Обрезаем область для поиска
    search_region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
    
    # Конвертируем в формат OpenCV
    search_region_cv = cv2.cvtColor(np.array(search_region), cv2.COLOR_RGB2BGR)
    
    # Загружаем шаблон
    template = cv2.imread(template_path)
    
    # Ищем совпадение
    result = cv2.matchTemplate(search_region_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    print(f"📊 Максимальная схожесть в области: {max_val * 100:.1f}%")
    
    if max_val >= threshold:
        # Нашли! Координаты относительно области
        template_x = regionX + max_loc[0]
        template_y = regionY + max_loc[1]
        
        print(f"✅ Шаблон {name} , путь: {template_path} найден в области! Координаты: ({template_x}, {template_y})")
        
        # Возвращаем "виртуальный" элемент
        class VirtualElement:
            def __init__(self, x, y, w, h):
                self.location = {'x': x, 'y': y}
                self.size = {'width': w, 'height': h}
                
            def random_click(self):
                click_action.random_click(driver, (location_center_x , location_center_y))
        h, w = template.shape[:2]

        element = VirtualElement(template_x , template_y , w , h)
        location_center_x = element.location['x'] + (element.size['width'] // 2)
        location_center_y = element.location['y'] + (element.size['height'] // 2)
        
        if click:     
            element.random_click()
            return (location_center_x,location_center_y)

        # ВОЗВРАЩАЕТ КОРДЫ ОБЩАРАТЬСЯ переменная.location['x']
        
        return (location_center_x,location_center_y)
    
    print(f"❌ Шаблон {name} не найден в области")
    return False



def find_number_in_balance(driver, regionX, regionY, regionW, regionH):
    """Распознает баланс голды"""
    print(f"🔍 Распознаем баланс в области: X={regionX}, Y={regionY}, W={regionW}, H={regionH}")

    try:
        # 1. Скриншот + обрезка
        screenshot = driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        search_region = screenshot_img.crop(
            (regionX, regionY, regionX + regionW, regionY + regionH)
        )
        img_bgr = cv2.cvtColor(np.array(search_region), cv2.COLOR_RGB2BGR)

        # 2. HSV
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # 3. Основная маска — ТЕКСТ (светло-жёлтый)
        lower_text = np.array([15, 80, 190], dtype=np.uint8)
        upper_text = np.array([35, 180, 255], dtype=np.uint8)
        mask_text = cv2.inRange(hsv, lower_text, upper_text)

        # 3. Инверсия: EasyOCR ждёт ЧЁРНЫЙ текст на БЕЛОМ
        mask_final = cv2.bitwise_not(mask_text)

        # 4. Увеличение
        final_img = cv2.resize(mask_final, None, fx=3.0, fy=3.0,
                               interpolation=cv2.INTER_CUBIC)

        # 5. Отладка
        cv2.imwrite("debug_01_original.png", img_bgr)
        cv2.imwrite("debug_02_hsv.png", hsv)
        cv2.imwrite("debug_final.png", final_img)

        # 11. EasyOCR
        results = reader.readtext(
            final_img,
            detail=1,
            paragraph=False,
            text_threshold=0.4,
            low_text=0.3,
        )

        if not results:
            print("❌ Ничего не найдено")
            return None

        # 12. Извлекаем число
        full_text = ' '.join(text for (_, text, prob) in results if prob > 0.3)

        match = re.search(r'\d+(?:[.,]\d+)?', full_text)
        if not match:
            print("❌ Число не найдено")
            return None

        value = float(match.group().replace(',', '.'))
        print(f"✅ Найдено число: {value}")
        return value

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    

def find_count_on_screen(driver, regionX, regionY, regionW, regionH):
    print(f"🔍 Ищем число в области: X={regionX}, Y={regionY}, W={regionW}, H={regionH}")
    try:
        screenshot = driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        search_region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
        img_cv = cv2.cvtColor(np.array(search_region), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # CLAHE для усиления контраста
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Бинаризация с инверсией: получаем чёрный текст на белом фоне
        _, binary = cv2.threshold(enhanced, 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Увеличение без размытия
        enlarged = cv2.resize(binary, None, fx=3.0, fy=3.0,
                              interpolation=cv2.INTER_CUBIC)

        # Сохраняем для отладки ДО OCR
        cv2.imwrite("debug_final.png", enlarged)

        # OCR без allowlist — вытащим цифры регуляркой
        results = reader.readtext(
            enlarged,
            detail=1,
            paragraph=False,
            text_threshold=0.5,
            low_text=0.3,
            min_size=10,
        )

        if not results:
            print("❌ Ничего не найдено")
            return None

        # Собираем весь распознанный текст
        full_text = ' '.join(text for (_, text, prob) in results if prob > 0.3)
        print(f"📝 Распознано: {full_text!r}")

        # Ищем первое число
        match = re.search(r'\d+(?:[.,]\d+)?', full_text)
        if not match:
            print("❌ Число не найдено в тексте")
            return None

        value = float(match.group().replace(',', '.'))
        print(f"✅ Найдено число: {value}")
        return value

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


# в pixels_to_check указать координаты пикселя ,на фигме разсмещаем фотку оригинала и стави пиксель смотри X Y
def debug_specific_pixels(driver, regionX, regionY, regionW, regionH):
    """
    Проверяем RGB пикселей в конкретных координатах
    """
    
    # Делаем скриншот
    screenshot = driver.get_screenshot_as_png()
    screenshot_img = Image.open(io.BytesIO(screenshot))
    
    # Обрезаем регион
    region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
    
    # Конвертируем в OpenCV (BGR)
    img = cv2.cvtColor(np.array(region), cv2.COLOR_RGB2BGR)
    
    # Сохраняем оригинал с разметкой
    debug_img = img.copy()
    
    # Координаты для проверки (относительно региона)
    pixels_to_check = [
        (79, 6), # соеденение края
        (77, 8), # центр шестреки
        (68, 8), # 9 центр
    ]
    
    print("\n🎨 RGB значения пикселей (в формате BGR и RGB):")
    print("=" * 60)
    
    results = []
    
    for x, y in pixels_to_check:
        # Проверяем что координаты в пределах изображения
        h, w = img.shape[:2]
        if x < w and y < h:
            pixel_bgr = img[y, x]
            pixel_rgb = (pixel_bgr[2], pixel_bgr[1], pixel_bgr[0])  # BGR -> RGB
            
            print(f"\n📍 Координаты ({x}, {y}):")
            print(f"   BGR: ({pixel_bgr[0]:3d}, {pixel_bgr[1]:3d}, {pixel_bgr[2]:3d})")
            print(f"   RGB: ({pixel_rgb[0]:3d}, {pixel_rgb[1]:3d}, {pixel_rgb[2]:3d})")
            print(f"   HEX: #{pixel_rgb[0]:02x}{pixel_rgb[1]:02x}{pixel_rgb[2]:02x}")
            
            results.append({
                'coord': (x, y),
                'bgr': pixel_bgr,
                'rgb': pixel_rgb
            })
            
            # Рисуем точку на изображении
            cv2.circle(debug_img, (x, y), 2, (0, 0, 255), -1)
            cv2.putText(debug_img, f"{x},{y}", (x+5, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        else:
            print(f"\n⚠️ Координаты ({x}, {y}) выходят за пределы изображения {w}x{h}")
    
    # Сохраняем изображение с отмеченными точками
    cv2.imwrite("debug_marked_pixels.png", debug_img)
    
    # Анализируем диапазон цветов
    if results:
        bgr_values = [r['bgr'] for r in results]
        bgr_min = np.min(bgr_values, axis=0)
        bgr_max = np.max(bgr_values, axis=0)
        
        print("\n" + "=" * 60)
        print("📊 Анализ диапазона цветов:")
        print(f"   BGR min = ({bgr_min[0]}, {bgr_min[1]}, {bgr_min[2]})")
        print(f"   BGR max = ({bgr_max[0]}, {bgr_max[1]}, {bgr_max[2]})")
        
        # Добавляем допуск ±5 для маски
        lower = np.array([max(0, bgr_min[0]-5), max(0, bgr_min[1]-5), max(0, bgr_min[2]-5)])
        upper = np.array([min(255, bgr_max[0]+5), min(255, bgr_max[1]+5), min(255, bgr_max[2]+5)])
        
        print(f"\n🎯 Рекомендуемый диапазон для маски (с допуском ±5):")
        print(f"   lower = ({lower[0]}, {lower[1]}, {lower[2]})")
        print(f"   upper = ({upper[0]}, {upper[1]}, {upper[2]})")
        
        # Создаем маску с этим диапазоном
        mask = cv2.inRange(img, lower, upper)
        cv2.imwrite("debug_mask_from_pixels.png", mask)
        
        print(f"\n✅ Маска сохранена в debug_mask_from_pixels.png")
        
        # Подсчитываем сколько пикселей попало в маску
        mask_pixels = np.sum(mask > 0)
        print(f"   Пикселей в маске: {mask_pixels}")
    
    print("\n" + "=" * 60)
    print("📝 Инструкция:")
    print("1. Откройте debug_marked_pixels.png - красные точки это ваши координаты")
    print("2. Проверьте что точки действительно на цифрах")
    print("3. Если точки не на цифрах - скажите правильные координаты")
    
    return img, results

def find_number_003(driver, regionX, regionY, regionW, regionH ,regionPrice=(5,15),debug=False):
    """
    Функция для темных цифр на темном фоне
    """
    
    # Делаем скриншот
    screenshot = driver.get_screenshot_as_png()
    screenshot_img = Image.open(io.BytesIO(screenshot))
    
    # Обрезаем регион
    region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
    
    # Конвертируем в OpenCV (BGR)
    img = cv2.cvtColor(np.array(region), cv2.COLOR_RGB2BGR)
    #увеличиваем
    bigOrig = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    # Создаем маску
    maskBigOrig = np.zeros(bigOrig.shape[:2], dtype=np.uint8)
    
    # Диапазон цветов цифр (на основе ваших данных)
    # Минимальные и максимальные значения из пикселей цифры:
    lower = np.array([44, 45, 52])  # BGR нижняя граница
    upper = np.array([65, 85, 100]) # BGR верхняя граница
    
    # Создаем маску по диапазону
    maskBigOrig = cv2.inRange(bigOrig, lower, upper)
    

    if debug:
        cv2.imwrite("debug_01_original.png", img)
        cv2.imwrite("debug_02_BigOriginal.png", bigOrig)
        cv2.imwrite("debug_03_mask_.png", maskBigOrig)


    results = reader.readtext(
        maskBigOrig,
        detail=1,
        paragraph=False,
        allowlist='0123456789.G.',  # тот же белый список
        text_threshold=0.3,          # ниже порог = больше находк
        low_text=0.2,
        contrast_ths=0.1,
        adjust_contrast=0.8,
        width_ths=0.7,               # уже - лучше разделяет символы
        height_ths=0.7,
        min_size=5                   # меньше минимальный размер
    )
    best_text = None
    best_conf = 0
    
    for bbox, text, conf in results:
        # Очистка
        cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
        
        if cleaned and conf > best_conf:
            best_text = float(cleaned)
            best_conf = conf
            if best_text > regionPrice[0] and best_text < regionPrice[1]:
                return best_text
            else:
                print('определил цену: ', best_text)
                print('Больше деапазона , скорее все ошибка , ИЗМЕНИТЕ ДЕАПАЗОН regionPrice')
                return None

    return None