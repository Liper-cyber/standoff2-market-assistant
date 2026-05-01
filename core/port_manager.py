import socket
import random
import subprocess
import os

from dotenv import load_dotenv
load_dotenv()

class PortManager:
    """Класс для управления портами"""
    
    @staticmethod
    def is_port_open(port, host=os.getenv('APPIUM_HOST')):
        """Проверяет, открыт ли порт"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, port))
                return True
            except:
                return False
    
    @staticmethod
    def get_free_port(min_port=6000, max_port=7000):
        """Находит свободный порт"""
        for i in range(10):
            port = random.randint(min_port, max_port)
            if not PortManager.is_port_open(port):
                return port
        raise Exception(f"Не найден свободный порт в диапазоне {min_port}-{max_port}")
    
    @staticmethod
    def kill_process_on_port(port):
        """Убивает процесс на порту"""
        if not port:
            return False
        try:
            port_int = int(port)
        except Exception:
            return False

        try:
            if os.name == 'nt':
                result = subprocess.run(
                    f'netstat -ano | findstr :{port_int}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            parts = line.split()
                            pid = parts[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                            return True
            return False
        except Exception as e:
            print(f"Ошибка при убийстве процесса: {e}")
            return False