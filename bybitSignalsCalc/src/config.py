import os
import asyncio
from dotenv import load_dotenv

# Загрузить переменные окружения из .env
load_dotenv()

# Строка подключения к базе данных (разбита на составляющие)
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql+asyncpg")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Pfvjxtr2023!Ujdytwj")
DB_HOST = os.getenv("DB_HOST", "192.168.41.87")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Путь к лог-файлу (по умолчанию: log/app.log в корневой директории проекта)
LOG_FILE = os.getenv("LOG_FILE", "log/app.log")

# Параметры ротации логов
LOG_ROTATION_WHEN = os.getenv("LOG_ROTATION_WHEN", "D")         # "D" – ротация каждый день
LOG_ROTATION_INTERVAL = int(os.getenv("LOG_ROTATION_INTERVAL", 1))
LOG_ROTATION_BACKUP_COUNT = int(os.getenv("LOG_ROTATION_BACKUP_COUNT", 14))

# Настройки индикаторов
INDICATOR_PARAMS = {
    "ATR_PERIOD": int(os.getenv("ATR_PERIOD", 14)),
    "EMA14_PERIOD": int(os.getenv("EMA14_PERIOD", 14)),
    "EMA200_PERIOD": int(os.getenv("EMA200_PERIOD", 200)),
    "BB_PERIOD": int(os.getenv("BB_PERIOD", 20)),
    "LR_PERIOD": int(os.getenv("LR_PERIOD", 20)),
    "RSI_PERIOD": int(os.getenv("RSI_PERIOD", 14)),
    "MACD_FAST": int(os.getenv("MACD_FAST", 12)),
    "MACD_SLOW": int(os.getenv("MACD_SLOW", 26)),
    "MACD_SIGNAL": int(os.getenv("MACD_SIGNAL", 9)),
    "STOCH_K_PERIOD": int(os.getenv("STOCH_K_PERIOD", 14)),
    "ADX_PERIOD": int(os.getenv("ADX_PERIOD", 14)),
    "CCI_PERIOD": int(os.getenv("CCI_PERIOD", 20)),
    "ICHIMOKU_CONVERSION": int(os.getenv("ICHIMOKU_CONVERSION", 9)),
    "ICHIMOKU_BASE": int(os.getenv("ICHIMOKU_BASE", 26)),
}

MAX_PERIOD = max(
    INDICATOR_PARAMS["ATR_PERIOD"],
    INDICATOR_PARAMS["EMA14_PERIOD"],
    INDICATOR_PARAMS["EMA200_PERIOD"],
    INDICATOR_PARAMS["BB_PERIOD"],
    INDICATOR_PARAMS["LR_PERIOD"],
    INDICATOR_PARAMS["RSI_PERIOD"],
    INDICATOR_PARAMS["STOCH_K_PERIOD"],
    INDICATOR_PARAMS["ADX_PERIOD"],
    INDICATOR_PARAMS["CCI_PERIOD"],
    INDICATOR_PARAMS["ICHIMOKU_BASE"]
) + 1

# Параметры для создания движка базы данных
POOL_SIZE = int(os.getenv("POOL_SIZE", 10))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", 20))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", 30))
ECHO = os.getenv("ECHO", "False").lower() in ("true", "1", "t")

# Ограничение количества одновременных соединений (семафор)
SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT", 10))
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
