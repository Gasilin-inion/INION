"""
Модуль логирования для проекта e-Library_to_IRBIS.
Обеспечивает централизованное логирование с ротацией файлов.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path



def setup_logger(
    name: str = "eLibrary_to_IRBIS",
    log_file: str = "app.log",
    level: int = logging.INFO,
    console_level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,  # 5 МБ
    backup_count: int = 3,
) -> logging.Logger:
    """
    Настраивает логгер с ротацией файлов и выводом в консоль.

    Args:
        name: имя логгера (обычно имя проекта/модуля)
        log_file: путь к файлу лога
        level: уровень логирования для файла
        console_level: уровень для консоли
        max_bytes: максимальный размер файла лога перед ротацией
        backup_count: количество архивных логов

    Returns:
        Настроенный экземпляр логгера
    """
    # Преобразуем в Path для удобства работы с путями
    log_path = Path(log_file)

    # Создаём директорию для логов, если её нет
    log_dir = log_path.parent
    if log_dir != Path("."):  # Если лог не в текущей папке
        log_dir.mkdir(parents=True, exist_ok=True)

    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Избегаем дублирования логов при многократном вызове
    if logger.hasHandlers():
        return logger

    # Форматировщик
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler для файла с ротацией
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Handler для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    # Добавляем handlers к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger



# Глобальный логгер проекта (можно переопределить в main.py/run.py)
PROJECT_LOGGER = setup_logger(
    name="eLibrary_to_IRBIS",
    log_file=Path("logs") / "app.log",  # Логи будут в папке logs/
    level=logging.DEBUG,           # В файл пишем всё (включая DEBUG)
    console_level=logging.INFO     # В консоль — только INFO и выше
)



def get_logger(module_name: str = None) -> logging.Logger:
    """
    Возвращает логгер для конкретного модуля.
    Если module_name не указан, возвращает глобальный логгер проекта.

    Args:
        module_name: имя модуля (например, 'converters.elibrary_excel')

    Returns:
        Логгер с иерархическим именем (eLibrary_to_IRBIS.module_name)
    """
    if module_name:
        return logging.getLogger(f"eLibrary_to_IRBIS.{module_name}")
    return PROJECT_LOGGER
