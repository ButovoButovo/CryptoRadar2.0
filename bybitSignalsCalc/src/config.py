import os
import asyncio
from dotenv import load_dotenv

# Загрузить переменные окружения из .env
load_dotenv()

# Строка подключения к базе данных (разбита на составляющие)
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql+asyncpg")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Pfvjxtr2023!Ujdytwj")
DB_HOST = os.getenv("DB_HOST", "postgres_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Путь к лог-файлу (по умолчанию: log/app.log в корневой директории проекта)
LOG_FILE = os.getenv("LOG_FILE", "log/app.log")

# Параметры ротации логов
LOG_ROTATION_WHEN = os.getenv("LOG_ROTATION_WHEN", "D")         # "D" – ротация каждый день
LOG_ROTATION_INTERVAL = int(os.getenv("LOG_ROTATION_INTERVAL", 1))
LOG_ROTATION_BACKUP_COUNT = int(os.getenv("LOG_ROTATION_BACKUP_COUNT", 14))

# Параметры для создания движка базы данных
POOL_SIZE = int(os.getenv("POOL_SIZE", 10))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", 20))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", 30))
ECHO = os.getenv("ECHO", "False").lower() in ("true", "1", "t")

# Ограничение количества одновременных соединений (семафор)
SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT", 10))
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
