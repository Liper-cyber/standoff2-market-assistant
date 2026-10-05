from config.appium_config import appium_config
from core.port_manager import PortManager
from appium import webdriver
from appium.options.android import UiAutomator2Options
import subprocess
import time

import os
from dotenv import load_dotenv
load_dotenv()

class DriverManager:
    """Запускает сервер и управляет драйвером"""
    
    def __init__(self):
        self.config = appium_config
        self.driver = None
        self.appium_process = None
    
    def start_appium_server(self):
        """Запускает Appium сервер"""        
        # Проверяем, не запущен ли уже
        if PortManager.is_port_open(self.config.local_port_appium ):
            print(f"✅ Appium сервер уже запущен на {self.config.local_port_appium }")
            return True
        
        # Запускаем сервер
        print(f"🚀 Запуск Appium сервера на порту {self.config.local_port_appium }...")
        
        try:
            self.appium_process = subprocess.Popen(
                f'appium {self.config.plugins} -p {self.config.local_port_appium }',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Ждем запуска
            for i in range(10):
                time.sleep(1)
                if PortManager.is_port_open(self.config.local_port_appium ):
                    print(f"✅ Appium сервер запущен на {self.config.local_port_appium }")
                    return True
            
            print("❌ Не удалось запустить Appium сервер при первом запуске , попробуйсте снова")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            return False
    
    def start_driver(self):
        """Запускает драйвер (и сервер если нужно)"""
        capabilities = appium_config.capabilities
        if not self.start_appium_server():
            raise Exception("Не удалось запустить Appium сервер")

        server_url = f'http://{os.getenv("APPIUM_HOST")}:{self.config.local_port_appium }'
        
        self.driver = webdriver.Remote(
            server_url,
            options=UiAutomator2Options().load_capabilities(capabilities)
        )
        return self.driver
    


driver_manager = DriverManager()
driver_manager.start_driver()
