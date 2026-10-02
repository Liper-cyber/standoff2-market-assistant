import os
import random
import socket
from pathlib import Path
from dotenv import load_dotenv
from core.port_manager import PortManager
from config.configall import START_PORT_VM

load_dotenv()

class AppiumConfig:
    """Класс для управления динамическими портами Appium"""
    
    def __init__(self):
        self.appium_host = os.getenv('APPIUM_HOST') # api appium server
        self.local_port_appium = None
        # Динамические порты (будут установлены при вызове)
        self.appium_server_port = None  # Порт для Appium сервера
        self.system_port = None         # systemPort для UiAutomator2
        self.device_udid_port = None  # Порт для udid (эмулятор)
        self.devices_port = None
        self.capabilities = None
        self.plugins = '--use-plugins=images'
        
        # Флаги
        self.is_initialized = False

    def get_capabilities(self,  nox_id=1):
        
        """Возвращает capabilities для Appium драйвера"""
        self.device_udid_port = int(nox_id)
        if not self.system_port:
            self.system_port = PortManager.get_free_port(8200 , 9200)
        if not self.local_port_appium:
            self.local_port_appium = PortManager.get_free_port(6000 , 7000)

        self.devices_port = int(self.device_udid_port * 2) + START_PORT_VM 
        print('КАПАБИЛИТИ НОКС АЙДИ: ' , nox_id , self.devices_port)
        capabilities = {
            "platformName": "Android",
            "appium:deviceName":'Nox',
            "appium:udid": f"emulator-{self.devices_port}", # NOX менять на 127.0.0.1:
            "appium:automationName": "UiAutomator2",
            "newCommandTimeout": 300,
            "uiautomator2ServerLaunchTimeout": 60000,
            "uiautomator2ServerInstallTimeout": 60000,
            "appium:uiautomator2ServerReadTimeout": 60000,
            "appium:adbExecTimeout": 60000,
            "appium:autoGrantPermissions": True,
            "appium:noReset": True,
            "appium:nativeWebScreenshot": True,
            "appium:ensureWebviewsHavePages": True,
            "appium:systemPort": self.system_port,
            "appium:skipServerInstallation": False,
            "appium:skipDeviceInitialization": False,
        }
        self.capabilities = capabilities
        return capabilities
    
    def print_config(self):
        """Выводит текущую конфигурацию"""
        print("\n" + "="*50)
        print("📱 Appium Конфигурация:")
        print(f"  Appium Server port: {self.local_port_appium}")
        print(f"  System Port: {self.system_port}")
        print(f"  Device UDID: emulator-{self.devices_port}") # NOX менять на 127.0.0.1:
        print("="*50 + "\n")

appium_config = AppiumConfig()
capability_me = None
