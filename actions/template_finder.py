import io
from PIL import Image
import cv2
import numpy as np
import time
from actions import click_action
import pytesseract
import easyocr

# Глобальный reader (инициализируем один раз вне функции — важно для производительности!)


from config.devices_config import DevicesConfig


class TemplateFinder:
    def __init__(self):
        self.reader = None
        self.model_dir = r"C:\Users\Mjis\.EasyOCR\model"

    def get_reader(self):
        """Возвращает EasyOCR reader. Создаёт новый при каждом вызове."""
        if self.reader is not None:
            return self.reader
        
        else:
            download_enabled = False
            print("✅ Модели EasyOCR найдены")

        try:
            self.reader = easyocr.Reader(
                ['en'],
                gpu=False,
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
                                   threshold=0.5 , click = True):
    """
    Ищет шаблон в указанной области с помощью OpenCV
    если ничего не нашел возвращает false , если нашел возвращает элемент в паняти который хранит X Y Ширину Длину
    
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
        
        print(f"✅ Шаблон {template_path} найден в области! Координаты: ({template_x}, {template_y})")
        
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
    
    print("❌ Шаблон не найден в области")
    return False

def find_number_on_screen(driver, regionX, regionY, regionW, regionH):
    """
    Улучшенная версия для распознавания баланса типа "G 1651.25"
    """
    print(f"🔍 Ищем число в области: X={regionX}, Y={regionY}, W={regionW}, H={regionH}")
    
    try:
        screenshot = driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        
        # Обрезаем нужную область
        search_region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
        img_cv = cv2.cvtColor(np.array(search_region), cv2.COLOR_RGB2BGR)
        
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # === Предобработка специально под низкий контраст жёлтого текста ===
        # Усиливаем контраст именно в диапазоне текста
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Дополнительно повышаем яркость и контраст через gamma
        gamma = 0.5                    # чем меньше — тем ярче становятся средние тона
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        enhanced = cv2.LUT(enhanced, table)

        # Бинаризация (пытаемся отделить текст от фона)
        _, binary = cv2.threshold(enhanced, 110, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Увеличение изображения
        enlarged = cv2.resize(binary, None, fx=2.8, fy=2.8, interpolation=cv2.INTER_CUBIC)

        # Финальное сглаживание
        final_img = cv2.GaussianBlur(enlarged, (3, 3), 0)

        # === EasyOCR ===
        results = reader.readtext(
            final_img,
            detail=1,
            paragraph=False,
            allowlist='0123456789.G',
            text_threshold=0.6,
            low_text=0.35,
            height_ths=0.7,
            width_ths=0.85,
            min_size=10,
            contrast_ths=0.1,
            adjust_contrast=0.8
        )

        if not results:
            print("❌ Ничего не найдено")
            return None

        texts = []
        for (bbox, text, prob) in results:
            if prob < 0.5:
                continue
            cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
            if cleaned:
                texts.append((cleaned, prob))

        if not texts:
            print("❌ После очистки ничего не осталось")
            return None

        best_text, best_prob = max(texts, key=lambda x: x[1])
        final = ''.join(c for c in best_text if c.isdigit() or c == '.')

        try:
            value = float(final)
            print(f"✅ EasyOCR: '{best_text}' (conf: {best_prob:.3f}) → {value}")
            return value
        except:
            print(f"⚠️ Не удалось конвертировать: {final}")
            return None

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    

import re


def parse_quantity_from_text(driver, regionX, regionY, regionW, regionH):
    """
    Находит ТОЛЬКО ЦИФРЫ в указанной области
    """
    print(f"🔍 Ищем текст в области: X={regionX}, Y={regionY}, W={regionW}, H={regionH}")
    try:
        # Делаем скриншот
        screenshot = driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        
        # Обрезаем область
        search_region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
        
        # Конвертируем в grayscale
        search_region_cv = cv2.cvtColor(np.array(search_region), cv2.COLOR_RGB2GRAY)
        
        # Увеличиваем контрастность
        search_region_cv = cv2.convertScaleAbs(search_region_cv, alpha=1.5, beta=0)
        
        # Применяем бинаризацию
        _, thresh = cv2.threshold(search_region_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Инвертируем если нужно (белый фон, черный текст)
        # thresh = cv2.bitwise_not(thresh)
        
        # Распознаем ТОЛЬКО цифры (конфиг для цифр)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        
        # Очищаем текст
        text = text.strip()
        
        print(f"🔍 Распознано: '{text}'")
        return text
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return ""
    




def find_number_on_screen21(driver, regionX, regionY, regionW, regionH):
    """
    Специальная версия под твои цвета текста (#564838, #664F37 и т.д.)
    """
    print(f"🔍 Ищем число в области: X={regionX}, Y={regionY}, W={regionW}, H={regionH}")
    
    try:
        screenshot = driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        
        # Обрезаем область
        search_region = screenshot_img.crop((regionX, regionY, regionX + regionW, regionY + regionH))
        img_cv = cv2.cvtColor(np.array(search_region), cv2.COLOR_RGB2BGR)

        # === HSV ===
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

        # Диапазон специально под твои 4 цвета
        lower = np.array([15,  35,  35])   # H, S, V
        upper = np.array([50, 255, 255])

        # Создаём маску только по твоим цветам
        mask = cv2.inRange(hsv, lower, upper)

        # Улучшаем маску
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)   # утолщаем буквы
        # mask = cv2.erode(mask, kernel, iterations=1)  # можно включить, если будет шум

        # Увеличение (не слишком сильное)
        enlarged = cv2.resize(mask, None, fx=2.6, fy=2.6, interpolation=cv2.INTER_LINEAR)

        # Слабое сглаживание
        final_img = cv2.GaussianBlur(enlarged, (3, 3), 0)

        # ==================== DEBUG ====================
        ts = int(time.time())
        cv2.imwrite(f"debug_01_original.png", img_cv) 
        cv2.imwrite(f"debug_hsv_mask_{ts}.png", mask)
        cv2.imwrite(f"debug_final_{ts}.png", final_img)
        print(f"Debug сохранён → debug_hsv_mask_{ts}.png")
        # ===============================================

        # EasyOCR
        results = reader.readtext(
            final_img,
            detail=1,
            paragraph=False,
            allowlist='0123456789.',
            text_threshold=0.70,
            low_text=0.45,
            height_ths=0.8,
            width_ths=0.9,
            min_size=10
        )

        if not results:
            print("❌ Ничего не найдено")
            return None

        texts = []
        for (bbox, text, prob) in results:
            if prob < 0.55:
                continue
            cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
            if cleaned:
                texts.append((cleaned, prob))

        if not texts:
            print("❌ После очистки ничего не осталось")
            return None

        best_text, best_prob = max(texts, key=lambda x: x[1])
        final = ''.join(c for c in best_text if c.isdigit() or c == '.')

        value = float(final)
        print(f"✅ EasyOCR: '{best_text}' (conf: {best_prob:.3f}) → {value}")
        return value

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None