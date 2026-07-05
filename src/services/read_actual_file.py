# Функция получает адрес наиболее актуального файла в целевой папке
# Сортировка идёт по последним 10 знакам в имени факла, включащим в себя дату создания

from src.services.multifile_import import get_files_in_folder # type: ignore
import logging
from pathlib import Path

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def read_actual(folder_path):

    file_list = get_files_in_folder(folder_path)
    if not file_list:
        logger.warning("В папке %s нет файлов", folder_path)
        raise FileNotFoundError(f"Нет файлов в папке {folder_path}")

    # Сортируем по последним 10 символам (дата YYYY_MM_DD)
    sorted_files = sorted(file_list, key=lambda x: str(x)[-10:], reverse=True)
    newest_raw = sorted_files[0]
    logger.info("Используем актуальный файл: %s", newest_raw)

    # Преобразуем в Path один раз и используем везде
    newest_path = Path(newest_raw)

    return newest_path