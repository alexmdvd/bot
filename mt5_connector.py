"""
Коннектор к MetaTrader 5

Этот модуль предоставляет класс для подключения и работы с MetaTrader 5.
"""

import MetaTrader5 as mt5
from datetime import datetime
from typing import Optional, List, Dict, Any


class MT5Connector:
    """Класс для подключения и взаимодействия с MetaTrader 5."""
    
    def __init__(self, path: Optional[str] = None, login: int = 0, password: str = "", 
                 server: str = "", timeout: int = 3000):
        """
        Инициализация коннектора.
        
        Args:
            path: Путь к исполняемому файлу MetaTrader 5 (по умолчанию ищет в системе)
            login: Номер торгового счета
            password: Пароль от счета
            server: Название сервера брокера
            timeout: Таймаут соединения в миллисекундах
        """
        self.path = path
        self.login = login
        self.password = password
        self.server = server
        self.timeout = timeout
        self.connected = False
    
    def connect(self) -> bool:
        """
        Подключение к MetaTrader 5.
        
        Returns:
            bool: True если подключение успешно, иначе False
        """
        if self.path:
            result = mt5.initialize(path=self.path, login=self.login, 
                                   password=self.password, server=self.server,
                                   timeout=self.timeout)
        else:
            result = mt5.initialize(login=self.login, password=self.password,
                                   server=self.server, timeout=self.timeout)
        
        if result:
            self.connected = True
            print(f"Успешное подключение к MetaTrader 5")
            account_info = self.get_account_info()
            if account_info:
                print(f"Счет: {account_info['login']}, Баланс: {account_info['balance']}")
        else:
            error = mt5.last_error()
            print(f"Ошибка подключения: {error}")
        
        return result
    
    def disconnect(self) -> None:
        """Отключение от MetaTrader 5."""
        mt5.shutdown()
        self.connected = False
        print("Отключено от MetaTrader 5")
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Получение информации о торговом счете.
        
        Returns:
            Dict с информацией о счете или None при ошибке
        """
        if not self.connected:
            return None
        
        account_info = mt5.account_info()
        if account_info is None:
            return None
        
        return {
            'login': account_info.login,
            'server': account_info.server,
            'currency': account_info.currency,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'profit': account_info.profit,
            'leverage': account_info.leverage
        }
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о торговом инструменте.
        
        Args:
            symbol: Название инструмента (например, "EURUSD")
        
        Returns:
            Dict с информацией об инструменте или None при ошибке
        """
        if not self.connected:
            return None
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return None
        
        return {
            'name': symbol_info.name,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'spread': symbol_info.spread,
            'digits': symbol_info.digits,
            'volume_min': symbol_info.volume_min,
            'volume_max': symbol_info.volume_max,
            'volume_step': symbol_info.volume_step
        }
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Получение текущей цены инструмента.
        
        Args:
            symbol: Название инструмента
        
        Returns:
            Dict с ценами bid/ask или None при ошибке
        """
        if not self.connected:
            return None
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def get_historical_data(self, symbol: str, timeframe: int, 
                           from_date: datetime, to_date: datetime,
                           count: int = 1000) -> Optional[List[Dict[str, Any]]]:
        """
        Получение исторических данных (свечей).
        
        Args:
            symbol: Название инструмента
            timeframe: Таймфрейм (mt5.TIMEFRAME_M1, M5, H1, D1 и т.д.)
            from_date: Дата начала
            to_date: Дата окончания
            count: Максимальное количество баров
        
        Returns:
            Список словарей с данными OHLCV или None при ошибке
        """
        if not self.connected:
            return None
        
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        if rates is None or len(rates) == 0:
            return None
        
        data = []
        for rate in rates:
            data.append({
                'time': datetime.fromtimestamp(rate['time']),
                'open': rate['open'],
                'high': rate['high'],
                'low': rate['low'],
                'close': rate['close'],
                'tick_volume': rate['tick_volume']
            })
        
        return data
    
    def buy(self, symbol: str, volume: float, sl: float = 0, tp: float = 0, 
            deviation: int = 20, magic: int = 234000, comment: str = "") -> Optional[Dict[str, Any]]:
        """
        Открытие позиции на покупку.
        
        Args:
            symbol: Название инструмента
            volume: Объем лота
            sl: Stop Loss (цена)
            tp: Take Profit (цена)
            deviation: Максимальное отклонение цены
            magic: Магический номер ордера
            comment: Комментарий к ордеру
        
        Returns:
            Результат операции или None при ошибке
        """
        if not self.connected:
            return None
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result is None:
            return None
        
        return {
            'retcode': result.retcode,
            'deal': result.deal,
            'order': result.order,
            'volume': result.volume,
            'price': result.price,
            'comment': result.comment
        }
    
    def sell(self, symbol: str, volume: float, sl: float = 0, tp: float = 0,
             deviation: int = 20, magic: int = 234000, comment: str = "") -> Optional[Dict[str, Any]]:
        """
        Открытие позиции на продажу.
        
        Args:
            symbol: Название инструмента
            volume: Объем лота
            sl: Stop Loss (цена)
            tp: Take Profit (цена)
            deviation: Максимальное отклонение цены
            magic: Магический номер ордера
            comment: Комментарий к ордеру
        
        Returns:
            Результат операции или None при ошибке
        """
        if not self.connected:
            return None
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result is None:
            return None
        
        return {
            'retcode': result.retcode,
            'deal': result.deal,
            'order': result.order,
            'volume': result.volume,
            'price': result.price,
            'comment': result.comment
        }
    
    def close_position(self, position_id: int) -> Optional[Dict[str, Any]]:
        """
        Закрытие позиции по ID.
        
        Args:
            position_id: ID позиции для закрытия
        
        Returns:
            Результат операции или None при ошибке
        """
        if not self.connected:
            return None
        
        position = mt5.positions_get(ticket=position_id)
        if position is None or len(position) == 0:
            return None
        
        pos = position[0]
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            return None
        
        if pos.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": position_id,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result is None:
            return None
        
        return {
            'retcode': result.retcode,
            'deal': result.deal,
            'order': result.order,
            'volume': result.volume,
            'price': result.price,
            'comment': result.comment
        }
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получение списка открытых позиций.
        
        Args:
            symbol: Фильтр по инструменту (None - все позиции)
        
        Returns:
            Список позиций
        """
        if not self.connected:
            return []
        
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()
        
        if positions is None:
            return []
        
        result = []
        for pos in positions:
            result.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'time': datetime.fromtimestamp(pos.time)
            })
        
        return result
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """
        Получение списка активных отложенных ордеров.
        
        Returns:
            Список отложенных ордеров
        """
        if not self.connected:
            return []
        
        orders = mt5.orders_get()
        if orders is None:
            return []
        
        result = []
        for order in orders:
            order_type = {
                mt5.ORDER_TYPE_BUY: 'BUY',
                mt5.ORDER_TYPE_SELL: 'SELL',
                mt5.ORDER_TYPE_BUY_LIMIT: 'BUY LIMIT',
                mt5.ORDER_TYPE_SELL_LIMIT: 'SELL LIMIT',
                mt5.ORDER_TYPE_BUY_STOP: 'BUY STOP',
                mt5.ORDER_TYPE_SELL_STOP: 'SELL STOP'
            }.get(order.type, 'UNKNOWN')
            
            result.append({
                'ticket': order.ticket,
                'symbol': order.symbol,
                'type': order_type,
                'volume': order.volume_current,
                'price_open': order.price_open,
                'sl': order.sl,
                'tp': order.tp,
                'time': datetime.fromtimestamp(order.time_setup)
            })
        
        return result


# Константы таймфреймов для удобства
TIMEFRAMES = {
    'M1': mt5.TIMEFRAME_M1,
    'M5': mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'M30': mt5.TIMEFRAME_M30,
    'H1': mt5.TIMEFRAME_H1,
    'H4': mt5.TIMEFRAME_H4,
    'D1': mt5.TIMEFRAME_D1,
    'W1': mt5.TIMEFRAME_W1,
    'MN1': mt5.TIMEFRAME_MN1
}


if __name__ == "__main__":
    # Пример использования
    print("=== Пример использования MT5Connector ===\n")
    
    # Создание коннектора (без подключения к реальному счету)
    connector = MT5Connector(
        login=12345678,  # Замените на ваш номер счета
        password="your_password",  # Замените на ваш пароль
        server="YourBroker-Demo"  # Замените на ваш сервер
    )
    
    # Подключение
    if connector.connect():
        # Получение информации о счете
        account = connector.get_account_info()
        if account:
            print(f"\nИнформация о счете: {account}")
        
        # Получение текущей цены EURUSD
        price = connector.get_current_price("EURUSD")
        if price:
            print(f"\nЦена EURUSD: Bid={price['bid']}, Ask={price['ask']}")
        
        # Получение позиций
        positions = connector.get_positions()
        print(f"\nОткрытые позиции: {len(positions)}")
        
        # Отключение
        connector.disconnect()
    else:
        print("\nНе удалось подключиться к MetaTrader 5")
        print("Убедитесь, что:")
        print("1. MetaTrader 5 установлен и запущен")
        print("2. Указаны правильные учетные данные")
        print("3. Библиотека MetaTrader5 установлена (pip install MetaTrader5)")
