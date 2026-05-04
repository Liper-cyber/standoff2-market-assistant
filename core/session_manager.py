# core/session_manager.py
import time
from config.appium_config import appium_config
from core.port_manager import PortManager
from actions import template_finder
from core.driver_manager import driver_manager
import subprocess

ADB_PATH = r"B:\Nox\bin\adb.exe" # путь adb


class SessionManager:
    """Управление сессией Appium и переподключениями"""
    
    def __init__(self):
        self.driver_manager = driver_manager
        self.port_manager = PortManager()
        self.timeerror = None
        
        self.UID_devices = appium_config.devices_port

    def kill_uiautomator_on_device(self):
        try:
            commands = [
                ['shell', 'killall', '-9', 'uiautomator'],
                ['shell', 'killall', '-9', 'uiautomator2'],
                ['shell', 'am', 'force-stop', 'io.appium.uiautomator2.server'],
                ['shell', 'am', 'force-stop', 'io.appium.uiautomator2.server.test'],
            ]
            for cmd in commands:
                full_cmd = [ADB_PATH, '-s', f'127.0.0.1:{self.UID_devices}'] + cmd
                subprocess.run(full_cmd, capture_output=True, timeout=5)
            
            print(f"🔪 uiautomator2 убит на устройстве 127.0.0.1:{self.UID_devices}")

        except FileNotFoundError:
            print(f"❌ Не найден adb.exe по пути: {ADB_PATH}")
        except Exception as e:
            print(f"⚠️ Не удалось убить uiautomator на устройстве: {e}")


    def _kill_port_if_set(self, port):
        if not port:
            return False
        return self.port_manager.kill_process_on_port(port)


    def _is_anr_dialog_present(self) -> bool:
        """Проверяет, появилось ли окно 'Приложение не отвечает'"""
        try:
            result = subprocess.run(
                [ADB_PATH, '-s', f'127.0.0.1:{self.UID_devices}', 'shell', 'dumpsys', 'window'],
                capture_output=True,
                text=True,
                timeout=6,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = result.stdout.lower()
            
            # Основные признаки ANR
            if "application not responding" in output or "приложение не отвечает" in output:
                print("🚨 ОБНАРУЖЕН ANR: Приложение Standoff 2 не отвечает!")
                # Для отладки показываем строку с фокусом
                for line in result.stdout.splitlines():
                    if "not responding" in line.lower() or "mcurrentfocus" in line.lower():
                        print("   →", line.strip())
                return True
                
            return False
            
        except subprocess.TimeoutExpired:
            print("⚠️ Таймаут при проверке ANR через dumpsys")
            return False
        except Exception as e:
            print(f"⚠️ Ошибка при проверке ANR: {e}")
            return False
        
    def _reconnect_application(self):
        print('рекконект запускаю')
        driver_manager.driver.activate_app('com.axlebolt.standoff2')
        time.sleep(100)
        LoginGoogle = template_finder.find_item_region(self.driver_manager.driver, "./img/interfeces/LoginGoogle.png", threshold=0.7)
        time.sleep(60)


    def reconnect_to_session(self, error_msg=None):
        error_msg = str(error_msg or "")
        
        # Случай 1: Проблемы с UiAutomator2 сервером
        if "instrumentation process is not running" in error_msg or \
        "cannot be proxied to UiAutomator2 server" in error_msg:
            
            print("🔄 Перезапускаем UiAutomator2 сервер...")
            
            try:
                driver_manager.driver.quit()
            except:
                pass

            self.kill_uiautomator_on_device()
            self._kill_port_if_set(self.driver_manager.config.system_port)
            self._kill_port_if_set(self.driver_manager.config.local_port_appium)
            driver_manager.appium_process = None
            driver_manager.driver = None
            
            time.sleep(3)
            
            driver_manager.start_driver()
            
            time.sleep(7)
            print("✅ UiAutomator2 сервер перезапущен")
            return False
        
        # Случай 2: Другие ошибки
        else:
            try:
                # Проверяем, активна ли сессия
                if self._is_anr_dialog_present():
                    try:
                        from appium.webdriver.common.appiumby import AppiumBy
                        close_app = driver_manager.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().text("Закрыть приложение")')
                        if close_app:
                            close_app[0].click()
                            print('Перезапускаю питложение')
                            self._reconnect_application()
                            time.sleep(20)
                            return True
                        else:
                            print('Закрываю виртуалку полсностью')
                            from core.devices_manager import DevicesManager
                            #DevicesManager().close_device(driver_manager.config.device_udid_port)
                    except Exception as e:
                        print(e)

                    
                
                packag = driver_manager.driver.current_package
                if packag == 'com.axlebolt.standoff2':
                    activity = driver_manager.driver.current_activity
                    print("✅ Сессия активна" , 'Activity: ' , activity)
                    return True
                else:
                    print("⚠️ Игра вылетела, перезапускаем...")
                    self._reconnect_application()
                return True
                
            except Exception as e:
                print("🔄 Сессия устарела, создаем новую...")
                self.kill_uiautomator_on_device()
                self._kill_port_if_set(self.driver_manager.config.system_port)
                self._kill_port_if_set(self.driver_manager.config.local_port_appium)
                self._reset_driver_ports()
                driver_manager.appium_process = None
                driver_manager.driver = None
                
                driver_manager.start_driver()
                
                return False
