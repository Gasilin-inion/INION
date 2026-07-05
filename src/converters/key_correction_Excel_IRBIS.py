# Функции преобразования отредактированной таблицы автозамены в файлы заданий для глобальной
# корректировки и автоматического обновления текущей версии таблицы автозамены и СНЛ
# @Author: Andrey Gasilin, 2026

import pandas as pd
import datetime
import json
import logging
from pathlib import Path
from typing import List
from src.services.multifile_import import get_files_in_folder # type: ignore

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Блок конфигурации
# -------------------------------------------------------

# Импорт файла конфигурации
config_path = Path("./data/config/path_config.json")
try:
    with config_path.open("r", encoding="utf-8") as pathfile:
        config_paths = json.load(pathfile)
except FileNotFoundError:
    logger.error("Не найден файл конфигурации путей: %s", config_path)
    raise
except json.JSONDecodeError:
    logger.error("Ошибка формата JSON в файле конфигурации: %s", config_path)
    raise

# Импорт директории для хранения заданий для оглобальной корректировки
tgt = config_paths.get("dir_for_GB")
if not tgt:
    logger.error('В config.json отсутствует ключ "dir_for_GB"')
    raise KeyError('В config.json отсутствует ключ "dir_for_GB"')

tgt_dir = Path(tgt)
tgt_dir.mkdir(parents=True, exist_ok=True)  # Гарантируем существование директории

# Импорт директории для СНЛ по Философии
SNL_02 = config_paths.get("SNL_02")
if not SNL_02:
    logger.error('В config.json отсутствует ключ "SNL_02"')
    raise KeyError('В config.json отсутствует ключ "SNL_02"')

SNL_02 = Path(SNL_02)
SNL_02.mkdir(parents=True, exist_ok=True)  # Гарантируем существование директории

# Импорт директории для СНЛ по Социологии

SNL_04 = config_paths.get("SNL_04")
if not SNL_04:
    logger.error('В config.json отсутствует ключ "SNL_04"')
    raise KeyError('В config.json отсутствует ключ "SNL_04"')

SNL_04 = Path(SNL_04)
SNL_04.mkdir(parents=True, exist_ok=True)  # Гарантируем существование директории

# Определение текущей даты для использования в имени файла 
today = datetime.date.today().strftime("%Y_%m_%d")

"""
    Функция считывает Excel, фильтрует строки, где synonym == keyword,
    генерирует .gbl файл и возвращает очищенный DataFrame + метаданные.

    Возвращает:
        df_result: DataFrame с колонками ['synonym', 'keyword'] (только обработанные строки)
        new_terms: список терминов, которые были отброшены (где synonym == keyword)
        spec: спецификатор ('02', '04' или None)
"""

def key_decoder(file_path, tgt_dir: Path):
    
    file_path_str = str(file_path)

    # Читаем Excel
    try:
        df = pd.read_excel(file_path_str)
    except FileNotFoundError:
        logger.error("Файл не найден: %s", file_path_str)
        raise
    except Exception as e:
        logger.exception("Ошибка чтения Excel-файла: %s", e)
        raise

    # Проверка колонок
    required_cols = {"synonym", "keyword"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        logger.error("В Excel отсутствуют обязательные колонки: %s", missing_cols)
        raise ValueError(f"Отсутствуют колонки: {missing_cols}")

    # Подготовка временных колонок для сравнения (очистка пробелов)
    df["s"] = df["synonym"].astype(str).str.rstrip()
    df["k"] = df["keyword"].astype(str).str.rstrip()

    # Сбор совпадающих терминов (которые не пойдут в файл .gbl)
    mask_match = (
        (df["s"] == df["k"]) &
        (~pd.isna(df["keyword"])) &
        (df["k"] != "nan")
    )
    matched_rows = df.loc[mask_match]
    new_terms = matched_rows["k"].tolist()
    if new_terms:
        logger.info("Найдено %d совпадающих пар synonym==keyword, они не попадут в .gbl", len(new_terms))

    # Фильтрация: оставляем строки, где значения разные или keyword пуст
    mask_keep = (
        (df["s"] != df["k"]) |
        pd.isna(df["keyword"])
    )
    sorted_df = df.loc[mask_keep].copy()

    # Сортировка по очищенному synonym
    sorted_df = sorted_df.sort_values(by="s", ascending=True).reset_index(drop=True)

    # Генерация файла в формате .gbl
    file_lines = ["0\n"]
    for _, row in sorted_df.iterrows():
        synonym = row["s"]
        keyword_raw = row["keyword"]

        if pd.isna(keyword_raw) or str(keyword_raw).rstrip() == "":
            task = f"REP\n965\nF\n(if v965= '{synonym}' then # else v965 fi/)\n"
        else:
            keyword_str = row["k"]
            task = f"REP\n965\nF\n(if v965= '{synonym}' then '{keyword_str}' else v965 fi/)\n"

        file_lines.append(task)

    # Определение имени файла и спецификатора
    spec = None
    if "02_SD" in file_path_str:
        file_name = f"02_key_correction_{today}.gbl"
        spec = '02'
    elif "04_SD" in file_path_str:
        file_name = f"04_key_correction_{today}.gbl"
        spec = '04'
    else:
        file_name = f"key_correction_{today}.gbl"

    # Превращаем tgt_dir в Path, если он пришёл строкой
    tgt_dir_obj = Path(tgt_dir) if isinstance(tgt_dir, str) else tgt_dir
    tgt_file_path = tgt_dir_obj / file_name

    try:
        with tgt_file_path.open("w", encoding="windows-1251") as fout:
            fout.writelines(file_lines)
        logger.info("Файл успешно создан: %s", tgt_file_path)
    except Exception as e:
        logger.exception("Ошибка при записи файла: %s", e)
        raise

    # Создаем новый DataFrame только с нужными колонками, используя очищенные значения
    df_result = pd.DataFrame({
        "synonym": sorted_df["s"],
        "keyword": sorted_df["k"]
    })
    
    # Восстанавливаем оригинальный индекс или сбрасываем его
    df_result = df_result.reset_index(drop=True)

    return df_result, new_terms, spec

"""
    Функция импортирует новые термины, просматривает содержимое папок SNL в соответствии с 
    избранной специальностью (идентификатор специальности передаётся через переменную spec),
    открывает наиболее актуальный список нормализованной лексики,
    интегрирует туда новые термины, сортирует и сохраняет новый список в виде отдельного 
    файла, датированного актуальным числом.
    
    Возвращает путь к созданному файлу.
    
"""

def add_terms(new_terms: List[str], spec: str):
    
    if spec is None:
        spec = ''
    spec = str(spec).strip()

    # Определяем целевую папку в зависимости от spec
    if spec == '02':
        base_dir = SNL_02
    elif spec == '04':
        base_dir = SNL_04
    else:
        logger.error('Некорректный ключ специальности: %s', spec)
        raise KeyError('Некорректный ключ специальности')

    # Получаем список файлов
    file_list = get_files_in_folder(base_dir)
    if not file_list:
        logger.warning("В папке %s нет файлов для специальности %s", base_dir, spec)
        raise FileNotFoundError(f"Нет файлов в папке {base_dir} для spec={spec}")

    # Сортируем по последним 10 символам (дата YYYY_MM_DD)
    sorted_files = sorted(file_list, key=lambda x: str(x)[-10:], reverse=True)
    newest_raw = sorted_files[0]
    logger.info("Используем актуальный файл: %s", newest_raw)

    # Преобразуем в Path один раз и используем везде
    newest_path = Path(newest_raw)

    # Читаем существующие термины
    with newest_path.open('r', encoding='utf-8') as f:
        SNL_terms = f.readlines()

    # Очищаем строки от пробелов и переносов, оставляем непустые
    clean_terms = [t.strip() for t in SNL_terms if t.strip()]

    # Добавляем новые термины (тоже чистим)
    cleaned_new = [t.strip() for t in new_terms if isinstance(t, str) and t.strip()]
    actual_SNL_terms = clean_terms + cleaned_new

    # Убираем дубликаты (сохраняя первое вхождение) и сортируем по алфавиту без учёта регистра
    unique_terms = list(dict.fromkeys(actual_SNL_terms))
    sorted_terms = sorted(unique_terms, key=str.lower)

    # Формируем имя нового файла: заменяем дату в имени на сегодняшнюю
    today_str = datetime.date.today().strftime("%Y_%m_%d")
    name_parts = newest_path.stem.split('_')

    if len(name_parts) >= 3:
        # Проверяем, что последние три части похожи на дату YYYY_MM_DD
        if (
            len(name_parts[-3]) == 4 and
            len(name_parts[-2]) == 2 and
            len(name_parts[-1]) == 2
        ):
            new_stem = '_'.join(name_parts[:-3] + [today_str])
        else:
            # Если формат не совпадает, просто добавляем дату в конец
            new_stem = newest_path.stem + '_' + today_str
    else:
        new_stem = newest_path.stem + '_' + today_str

    new_file_path = newest_path.with_name(f"{new_stem}{newest_path.suffix}")

    # Записываем новый файл (каждая строка с переносом)
    with new_file_path.open('w', encoding='utf-8') as f:
        f.writelines(term + '\n' for term in sorted_terms)

    logger.info(
        "Новый файл создан: %s, добавлено терминов: %d",
        new_file_path,
        len(cleaned_new)
    )