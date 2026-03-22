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
    
    # Предотвращаем распространение логов на корневой логгер
    logger.propagate = False

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
        module_name: имя модуля (например, 'converters.elibrary_excel', 'web.app')

    Returns:
        Логгер с иерархическим именем (eLibrary_to_IRBIS.module_name)
    """
    if module_name:
        # Создаем дочерний логгер
        logger = logging.getLogger(f"eLibrary_to_IRBIS.{module_name}")
        # Устанавливаем тот же уровень, что и у родительского
        logger.setLevel(PROJECT_LOGGER.level)
        # Не добавляем свои обработчики, используем родительские
        logger.propagate = True
        return logger
    return PROJECT_LOGGER


# Упрощенная версия для быстрого доступа
def get_logger_simple(name: str = "app") -> logging.Logger:
    """
    Простая версия для быстрого доступа к логгеру.
    Используется в небольших скриптах.
    
    Args:
        name: имя логгера
        
    Returns:
        Настроенный логгер
    """
    return get_logger(name)


# Функция для изменения уровня логирования во время выполнения
def set_log_level(level: int):
    """
    Изменяет уровень логирования для всех логгеров проекта.
    
    Args:
        level: уровень логирования (logging.DEBUG, logging.INFO и т.д.)
    """
    PROJECT_LOGGER.setLevel(level)
    for handler in PROJECT_LOGGER.handlers:
        handler.setLevel(level)
    
    # Изменяем уровень для всех дочерних логгеров
    for name in logging.root.manager.loggerDict:
        if name.startswith("eLibrary_to_IRBIS"):
            logger = logging.getLogger(name)
            logger.setLevel(level)


# Функция для временного отключения файлового логирования
def disable_file_logging():
    """Отключает запись логов в файл (оставляет только консоль)"""
    for handler in PROJECT_LOGGER.handlers[:]:
        if isinstance(handler, RotatingFileHandler):
            PROJECT_LOGGER.removeHandler(handler)


# Функция для временного отключения консольного логирования
def disable_console_logging():
    """Отключает вывод логов в консоль (оставляет только файл)"""
    for handler in PROJECT_LOGGER.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            PROJECT_LOGGER.removeHandler(handler)


# Проверка доступности директории для логов
def check_log_directory():
    """Проверяет, доступна ли директория для записи логов"""
    log_path = Path("logs") / "app.log"
    log_dir = log_path.parent
    
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            return True
        except PermissionError:
            print(f"Нет прав на создание директории: {log_dir}")
            return False
        except Exception as e:
            print(f"Ошибка при создании директории логов: {e}")
            return False
    
    # Проверяем права на запись
    if not os.access(log_dir, os.W_OK):
        print(f"Нет прав на запись в директорию: {log_dir}")
        return False
    
    return True


# Инициализация проверки при импорте модуля
if not check_log_directory():
    print("ВНИМАНИЕ: Проблема с директорией логов. Логи будут только в консоли.")