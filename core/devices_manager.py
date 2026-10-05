import os
import subprocess
import time
from config.configall import PATH_EMULATOR , VM_NAME, START_PORT_VM , LOCAL_IP_PC , PATH_SHADOWSOCKS , PATH_EMULATOR_ADB

class DevicesManager:
    def __init__(self):
        self.devices = []
    
    def create_device(self, VM_id , port = None , boot_timeout=40):
        """Запускает эмулятор"""
        process = subprocess.Popen(
            f'ldconsole.exe launch --index {VM_id}',
            cwd=PATH_EMULATOR,
            shell=True
        )
        self.devices.append(process)
        #self.start_shadowsocks(port, path_shadowsocks)
        if port is not None:
            adb_serial = f'{VM_NAME}{START_PORT_VM + VM_id * 2}'
            if self.wait_for_device(adb_serial, timeout=boot_timeout):
                try:
                    self.change_ip_by_3proxy(port=port, adb_serial=adb_serial)
                except RuntimeError as e:
                    print(f"❌ Проблема с прокси: {e}")
                    self.close_device(VM_id=VM_id)   # ← закрываем VM
                    return None
            else:
                print(f'[!] Устройство {adb_serial} не появилось в ADB')
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

    def change_ip_by_3proxy(self, port, adb_serial):
        import requests
        import re
        proxies = {
            "http":  f"http://{LOCAL_IP_PC}:{port}",
            "https": f"http://{LOCAL_IP_PC}:{port}",
        }

        # 1. Проверяем прокси — если проблема, выбрасываем исключение
        try:
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        except requests.exceptions.ProxyError as e:
            raise RuntimeError(f"Прокси {LOCAL_IP_PC}:{port} недоступен") from e
        except requests.exceptions.ReadTimeout:
            raise RuntimeError(f"Прокси {LOCAL_IP_PC}:{port} не ответил за 10 сек")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка запроса через прокси: {e}") from e

        # 2. Проверяем, что ответ содержит валидный IP
        try:
            data = response.json()
        except ValueError:
            raise RuntimeError(f"Прокси вернул не JSON: {response.text[:100]!r}")

        ip = data.get("origin", "").strip()
        # origin может быть '1.2.3.4' или '1.2.3.4, 5.6.7.8' — берём первый
        ip = ip.split(",")[0].strip()

        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            raise RuntimeError(f"Прокси вернул не IP: {ip!r}")

        print(f"✅ Прокси {LOCAL_IP_PC}:{port} → IP {ip}")

        # 3. Устанавливаем прокси в Android через adb
        serial = adb_serial

        try:
            result = subprocess.run(
                [PATH_EMULATOR_ADB, '-s', serial, 'shell', 'settings', 'put', 'global',
                 'http_proxy', f'{LOCAL_IP_PC}:{port}'],
                capture_output=True, text=True, timeout=15
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"adb не ответил за 15 сек для {serial}")

        if result.returncode != 0:
            raise RuntimeError(f"adb вернул ошибку: {result.stderr.strip()}")

        print(f"✅ Прокси установлен для {serial} → {LOCAL_IP_PC}:{port}")
        return True

    def wait_for_device(self, adb_serial, timeout=180, poll_interval=2):
        """Ждёт, пока устройство появится в adb devices и будет в статусе device"""
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                result = subprocess.run(
                    [PATH_EMULATOR_ADB, 'devices'],
                    capture_output=True, text=True, timeout=10
                )
                lines = result.stdout.strip().splitlines()[1:]  # пропускаем заголовок
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == adb_serial and parts[1] == 'device':
                        return True
            except subprocess.TimeoutExpired:
                pass
            time.sleep(poll_interval)

        return False