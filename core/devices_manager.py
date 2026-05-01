import os
import subprocess
import time

class DevicesManager:
    def __init__(self):
        self.devices = []
    
    def create_device(self, nox_id , port , path_nox = r'B:\Nox\bin' , path_shadowsocks = r'D:\shadowsocks_all'):
        pass
        process = subprocess.Popen(
            f'Nox.exe -clone:Nox_{nox_id}',
            cwd=path_nox,
            shell=True
        )
        self.start_shadowsocks(port, path_shadowsocks)
        

    def start_shadowsocks(self, port , path = r'D:\shadowsocks_all'):
        ss_path = rf'{path}\Shadowsocks{port}\Shadowsocks.exe'
        process = subprocess.Popen(ss_path)

    def stop_shadowsocks(self, port , path = r'D:\shadowsocks_all'):
        ss_path = rf'{path}\Shadowsocks{port}\Shadowsocks.exe'
        subprocess.run(f'taskkill /F /IM {os.path.basename(ss_path)}', shell=True)

    def close_device(self, nox_id):
        process = subprocess.Popen(
            f'Nox.exe -clone:Nox_{nox_id} -quit',
            shell=True
        )
        time.sleep(10)