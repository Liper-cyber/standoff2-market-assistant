 # models.py
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional
from enum import Enum

# Константы
STEPBUY = Decimal('0.01')
MAX_WAIT_ATTEMPTS = 3
MAX_FAST_ORDER = 3
SELL_COUNT_RANGE = (20, 25)


class NoxDeviceStatus(str, Enum):
    """Статус устройства Nox"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class Skin:
    """Модель скина из таблицы skins"""
    id: int
    name: str
    rarity: str
    url: str
    interval_minutes: int
    sell_global_price: Optional[Decimal]
    sell_price: Decimal
    max_buy: Decimal
    min_buy: Decimal
    buy_price: Decimal
    
    @classmethod
    def from_db_row(cls, row: dict) -> 'Skin':
        """Создает объект из строки БД"""
        return cls(
            id=row['id'],
            name=row['name'],
            rarity=row['rarity'],
            url=row['url'],
            interval_minutes=row['interval_minutes'],
            sell_global_price=Decimal(row['sell_global_price']) if row['sell_global_price'] is not None else None,
            sell_price=Decimal(row['sell_price']),
            max_buy=Decimal(row['max_buy']),
            min_buy=Decimal(row['min_buy']),
            buy_price=Decimal(row['buy_price'])
        )
    

class HistoryAccount:
    """Модель истории аккаунта из таблицы account_history"""
    id: int
    id_account: int
    history_json: str
    created_at: datetime
    
    @classmethod
    def from_db_row(cls, row: dict) -> 'HistoryAccount':
        return cls(
            id=row['id'],
            id_account=row['id_account'],
            history_json=row['history_json'],
            created_at=row['created_at']
        )

@dataclass
class Account:
    """Модель аккаунта из таблицы account"""
    id: int
    nox_devices_id: int
    gold: int
    name: str
    gmail: str
    user_id: int
    create_at: datetime
    
    @classmethod
    def from_db_row(cls, row: dict) -> 'Account':
        return cls(
            id=row['id'],
            nox_devices_id=row['nox_devices_id'],
            gold=row['gold'],
            name=row['name'],
            gmail=row['gmail'],
            user_id=row['user_id'],
            create_at=row['create_at']
        )


@dataclass
class NoxDevice:
    """Модель устройства Nox из таблицы nox_devices"""
    id: int
    id_nox: int
    create_at: datetime
    status: str
    proxy_port: int
    
    @classmethod
    def from_db_row(cls, row: dict) -> 'NoxDevice':
        return cls(
            id=row['id'],
            id_nox=row['id_nox'],
            create_at=row['create_at'],
            status=row['status'],
            proxy_port=row['proxy_port']
        )


@dataclass
class AccountSkin:
    """Модель связи аккаунта со скином из таблицы account_skins"""
    account_id: int
    skin_id: int
    last_buy: Optional[datetime]
    last_sell: Optional[datetime]
    count: int
    sell_count: int
    wait_attempts: int # попыток поставить запрос
    is_buy: bool
    is_sale: bool
    fast_order: int # количесво выполненых запросов без доп wait_attemts , если за 10 минут запрос завершился значит у скина сменилась цена
    

    
    @classmethod
    def from_db_row(cls, row: dict) -> 'AccountSkin':
        return cls(
            account_id=row['account_id'],
            skin_id=row['skin_id'],
            last_buy=row.get('last_buy'),
            last_sell=row.get('last_sell'),
            count=row.get('count', 0),
            sell_count=row.get('sell_count', 0),
            wait_attempts=row.get('wait_attempts', 0),
            is_buy=row.get('is_buy', True),
            is_sale=row.get('is_sale', False),
            fast_order=row.get('fast_order', 0)
        )
