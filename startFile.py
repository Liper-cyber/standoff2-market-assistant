from dotenv import load_dotenv
load_dotenv()
import os
from services.database_service import DatabaseService

id_nox = int(input('Введите ID NOX: '))

os.environ['DEVICE_UDID'] = str(id_nox)

import main