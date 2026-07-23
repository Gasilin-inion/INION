# Функция чтения файла конфигурации

from pathlib import Path
import json

def set_config():
# Импортируем файл конфигурации путей
    # Определяем корневую папку
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # Строим путь к JSON-файлу
    CONFIG_PATH = BASE_DIR / "data" / "config" / "path_config.json"

    # Читаем JSON в словарь
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)
    return config