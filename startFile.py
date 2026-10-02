from dotenv import load_dotenv
load_dotenv()
import os
from services.database_service import DatabaseService

#фапйл нужен что бы вводитть значние виртуалки и получаить account_id , а не искать его в айле main 

id_nox = int(input('Введите ID NOX: '))

os.environ['DEVICE_UDID'] = str(id_nox)

import main