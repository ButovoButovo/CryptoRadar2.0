# src/logger_config.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from src.config import LOG_FILE, LOG_ROTATION_WHEN, LOG_ROTATION_INTERVAL, LOG_ROTATION_BACKUP_COUNT

def setup_logger(log_file: str = LOG_FILE, level: int = logging.DEBUG) -> None:
    """
    Настраивает логгер с ротацией логов: ежедневное создание нового файла и сохранение резервных копий за заданное количество дней.
    
    :param log_file: Путь к файлу для записи логов.
    :param level: Уровень логгирования.
    """
    # Убедимся, что папка для логов существует
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Удаляем все существующие обработчики (если есть)
    while logger.handlers:
        logger.handlers.pop()
    
    # Создаем обработчик с ротацией
    handler = TimedRotatingFileHandler(
        filename=log_file,
        when=LOG_ROTATION_WHEN,           # тип ротации (например, "D" для ежедневной)
        interval=LOG_ROTATION_INTERVAL,     # интервал (обычно 1)
        backupCount=LOG_ROTATION_BACKUP_COUNT,  # сколько файлов хранить
        encoding="utf-8"
    )
    
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
