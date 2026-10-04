import os
import subprocess
import time
from config.configall import PATH_EMULATOR , START_PORT_VM , LOCAL_IP_PC , PATH_SHADOWSOCKS

class DevicesManager:
    def __init__(self):
        self.devices = []
    
    def create_device(self, VM_id , port = None , boot_timeout=30):
        """Запускает эмулятор"""
        process = subprocess.Popen(
            f'ldconsole.exe launch --index {VM_id}',
            cwd=PATH_EMULATOR,
            shell=True
        )
        self.devices.append(process)
        #self.start_shadowsocks(port, path_shadowsocks)
        if port is not None:
            adb_serial = START_PORT_VM + VM_id * 2
            if self.wait_for_device(adb_serial, timeout=boot_timeout):
                self.change_ip_by_3proxy(port=port, adb_serial=adb_serial)
            else:
                print(f'[!] Устройство {adb_serial} не появилось в ADB за {boot_timeout} сек.')
        else:
            print('Запускаю без прокси - Порт не указан')
        

    def start_shadowsocks(self, port , path = r'D:\shadowsocks_all'):
        """Если есть впн с получением пароля порта можно использовать shadowsocks"""
        ss_path = rf'{path}\Shadowsocks{port}\Shadowsocks.exe'
        process = subprocess.Popen(ss_path)

    def stop_shadowsocks(self, port , path = r'D:\shadowsocks_all'):
        ss_path = rf'{path}\Shadowsocks{port}\Shadowsocks.exe'
        subprocess.run(f'taskkill /F /IM {os.path.basename(ss_path)}', shell=True)

    def close_device(self, VM_id):
        process = subprocess.Popen(
            f'ldconsole.exe quit --index {VM_id}',
            shell=True,
            cwd=PATH_EMULATOR
        )
        time.sleep(10)

    def change_ip_by_3proxy(self , port , adb_serial):
        import requests
        try:
            proxies = {
                "http":  f"http://{LOCAL_IP_PC}:{port}",
                "https": f"http://{LOCAL_IP_PC}:{port}",
            }

            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
            print("Ответ от httpbin.org:", response.json())
            process = subprocess.Popen(
                f'adb -s emulator-{adb_serial} shell settings put global http_proxy {LOCAL_IP_PC}:{port}',
                shell=True,
                cwd=PATH_EMULATOR
            )
            print(f'поменял ip у {adb_serial - START_PORT_VM} на ', port)
            
        except requests.exceptions.ProxyError:
            print(f"Ошибка: Не удалось подключиться к прокси. Проверьте, запущен ли 3proxy на {LOCAL_IP_PC}:{port}")

    def wait_for_device(self, adb_serial, timeout=180, poll_interval=2):
        """Ждёт, пока устройство появится в adb devices и будет в статусе device"""
        deadline = time.time() + timeout
        ADB_PATH = rf'{PATH_EMULATOR}\adb.exe'

        while time.time() < deadline:
            try:
                result = subprocess.run(
                    [ADB_PATH, 'devices'],
                    capture_output=True, text=True, timeout=10
                )
                lines = result.stdout.strip().splitlines()[1:]  # пропускаем заголовок
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == f'emulator-{adb_serial}' and parts[1] == 'device':
                        return True
            except subprocess.TimeoutExpired:
                pass
            time.sleep(poll_interval)

        return False