# MT5 Connector

Коннектор к MetaTrader 5 для Python. Предоставляет удобный класс для подключения и взаимодействия с торговой платформой MetaTrader 5.

## Требования

- Python 3.8+
- MetaTrader 5 (установленный на компьютере)
- Библиотека MetaTrader5

## Установка

```bash
pip install MetaTrader5
```

**Важно:** Библиотека MetaTrader5 работает только на Windows и требует установленного MetaTrader 5.

## Использование

### Базовый пример

```python
from mt5_connector import MT5Connector, TIMEFRAMES
from datetime import datetime

# Создание коннектора
connector = MT5Connector(
    login=12345678,           # Ваш номер счета
    password="your_password", # Ваш пароль
    server="YourBroker-Demo"  # Сервер брокера
)

# Подключение
if connector.connect():
    # Получение информации о счете
    account = connector.get_account_info()
    print(f"Баланс: {account['balance']}")
    
    # Получение текущей цены
    price = connector.get_current_price("EURUSD")
    print(f"EURUSD: Bid={price['bid']}, Ask={price['ask']}")
    
    # Открытие позиции на покупку
    result = connector.buy("EURUSD", volume=0.1, sl=1.05, tp=1.15)
    
    # Закрытие позиции
    # connector.close_position(position_id)
    
    # Отключение
    connector.disconnect()
```

### Доступные методы

#### Подключение/Отключение
- `connect()` - Подключение к MetaTrader 5
- `disconnect()` - Отключение от MetaTrader 5

#### Информация
- `get_account_info()` - Информация о торговом счете
- `get_symbol_info(symbol)` - Информация о торговом инструменте
- `get_current_price(symbol)` - Текущая цена инструмента
- `get_historical_data(symbol, timeframe, from_date, to_date)` - Исторические данные (свечи)
- `get_positions(symbol=None)` - Список открытых позиций
- `get_orders()` - Список отложенных ордеров

#### Торговые операции
- `buy(symbol, volume, sl=0, tp=0, ...)` - Открытие позиции на покупку
- `sell(symbol, volume, sl=0, tp=0, ...)` - Открытие позиции на продажу
- `close_position(position_id)` - Закрытие позиции по ID

### Таймфреймы

Используйте константу `TIMEFRAMES`:

```python
from mt5_connector import TIMEFRAMES

# Пример получения исторических данных
data = connector.get_historical_data(
    symbol="EURUSD",
    timeframe=TIMEFRAMES['H1'],  # Часовой таймфрейм
    from_date=datetime(2024, 1, 1),
    to_date=datetime.now()
)
```

Доступные таймфреймы:
- `M1`, `M5`, `M15`, `M30` - Минутные
- `H1`, `H4` - Часовые
- `D1` - Дневной
- `W1` - Недельный
- `MN1` - Месячный

## Важные замечания

1. **Только Windows:** Библиотека MetaTrader5 работает только на ОС Windows
2. **Запущенный MT5:** MetaTrader 5 должен быть установлен и запущен
3. **Торговый счет:** Необходим действующий торговый счет у брокера
4. **Безопасность:** Не храните пароли в коде, используйте переменные окружения

## Лицензия

MIT