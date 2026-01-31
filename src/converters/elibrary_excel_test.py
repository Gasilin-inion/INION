"""
Конвертер библиографических записей e-Library
HTML → Excel (редактируемый)

Автор исходного алгоритма: Andrey Gasilin
Рефакторинг под фреймворк: Flask / CLI

Дата: январь 2026
"""

from pathlib import Path
from typing import Dict, Any, Iterable, List, Optional
import time
import json
import pandas as pd
import xlsxwriter
import logging
import importlib.util

from src.utils.logger import get_logger


# ---------------------------------------------------------------------
# ЛОГИРОВАНИЕ
# ---------------------------------------------------------------------

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# КОНФИГУРАЦИЯ
# ---------------------------------------------------------------------

CONFIG_PATH = Path("data/config/path_config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_paths = json.load(f)

journal_list_df = pd.read_json(config_paths["journal_list"])
result_files_dir = config_paths["files_to_edit"]


# ---------------------------------------------------------------------
# ПАТТЕРНЫ
# ---------------------------------------------------------------------

AUTHOR_PATTERN = '<b><font color=#00008f>'
AUTHOR_START = 23
AUTHOR_END = '.</font></b>'

TITLE_PATTERN = '<title>'
TITLE_START = 7
TITLE_END = '</title>'

JOURNAL_PATTERN = 'Содержание выпусков этого журнала">'
JOURNAL_START = 35
JOURNAL_END = '</a>'

YEAR_PATTERN = 'Год:'
VOLUME_PATTERN = 'Том:'
ISSUE_PATTERN = 'Содержание выпуска">'
PAGES_PATTERN = 'Страницы:'
LANG_PATTERN = 'Язык:'

ABSTRACT_PATTERN = '<div id="abstract1"'
ABSTRACT_START = 133
ABSTRACT_END = '</div>'

KEYWORD_PATTERN = '<a href="keyword_items.asp?id='
KEYWORD_START = 38
KEYWORD_END = '</a>'

URL_PATTERN = 'meta property="og:url"'
DOI_PATTERN = 'name="doi"'

# Константы для _extract_simple (поясните их смысл в документации)

CONTEXT_WINDOW_YEAR = 30
CONTEXT_WINDOW_VOLUME = 30
CONTEXT_WINDOW_ISSUE = 20
CONTEXT_WINDOW_PAGES = 35
CONTEXT_WINDOW_LANG = 31
CONTEXT_WINDOW_DOI = 20
CONTEXT_WINDOW_URL = 32

# ---------------------------------------------------------------------
# ПУБЛИЧНЫЙ КОНВЕРТЕР
# ---------------------------------------------------------------------

def convert_html_to_excel(
    html_files: Iterable[Path],
    *,
    output_dir: Optional[Path] = None,
    use_ai: bool = True
) -> List[Path]:
    """
    Конвертирует HTML‑файлы из e‑Library в Excel‑формат.

    Args:
        html_files: Итерируемый объект с путями к HTML‑файлам.
        output_dir: Директория для сохранения XLSX‑файлов. Если None, 
            используется временная директория.
        use_ai: Флаг использования AI‑обработки (перевод/оптимизация через GPT).

    Returns:
        Список путей к созданным XLSX‑файлам.

    Raises:
        FileNotFoundError: Если входной файл не найден.
        PermissionError: Если нет прав на запись в output_dir.
        Exception: Для прочих ошибок обработки.
    """

    # Определяем выходную директорию
    if output_dir is None:
        output_dir = Path(result_files_dir)
    
    # Создаём директорию, если её нет
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        logger.error(f"Нет прав на создание директории {output_dir}: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании директории {output_dir}: {e}")
        raise

    start_time = time.time()
    records = []

    for html_path in html_files:
        try:
            logger.info(f"Обработка файла: {html_path.name}")
            record = _process_html(html_path, use_ai)
            if record:
                records.append(record)
        except Exception as exc:
            logger.exception(f"Ошибка при обработке {html_path.name}: {exc}")

    # Если записей нет — возвращаем пустой список
    if not records:
        logger.warning("Нет данных для записи в Excel")
        return []

    # Формируем имя выходного файла
    try:
        output_filename = _build_output_filename(records[0])
        output_path = output_dir / output_filename
    except Exception as e:
        logger.error(f"Ошибка при формировании имени файла: {e}")
        raise

    # Записываем в Excel
    try:
        _write_excel(records, output_path)
    except Exception as e:
        logger.error(f"Ошибка при записи в Excel {output_path}: {e}")
        raise

    # Логируем результат
    elapsed = time.time() - start_time
    logger.info(
        f"Готово: {len(records)} записей, {elapsed:.1f} сек, файл: {output_path.name}"
    )

    return [output_path]

# ---------------------------------------------------------------------
# ОБРАБОТКА ОДНОГО HTML-ФАЙЛА
# ---------------------------------------------------------------------

def _process_html(path: Path, use_ai: bool) -> Optional[Dict[str, Any]]:
    """
    Обрабатывает HTML‑файл, извлекает метаданные публикации.

    Args:
        path: Путь к HTML‑файлу.
        use_ai: Флаг использования AI для анализа аннотации/ключевых слов.

    Returns:
        Словарь с полями публикации или None при ошибке.
    """
    try:
        # Проверка существования файла
        if not path.exists():
            logger.error(f"Файл не найден: {path}")
            return None

        strings = path.read_text(encoding="utf-8").splitlines()
        if not strings:
            logger.warning(f"Пустой файл: {path}")
            return None

        # Извлечение данных
        authors = _extract_authors(strings)
        title, keys_from_title = _extract_title(strings)
        journal = _extract_journal(strings)

        year = _extract_simple(strings, YEAR_PATTERN, CONTEXT_WINDOW_YEAR)
        volume = _extract_simple(strings, VOLUME_PATTERN, CONTEXT_WINDOW_VOLUME)
        
        issue = _extract_simple(strings, ISSUE_PATTERN, CONTEXT_WINDOW_ISSUE)
        if issue is not None:
            issue = issue.replace('&nbsp;', ' ')  # Безопасная замена

        pages = _extract_simple(strings, PAGES_PATTERN, CONTEXT_WINDOW_PAGES)
        lang = _extract_simple(strings, LANG_PATTERN, CONTEXT_WINDOW_LANG)

        abstract, keys_from_abstract = _extract_abstract(
            strings, 
            journal.get("category", ""),
            lang or "",
            use_ai
        )

        DOI = _extract_simple(strings, DOI_PATTERN, CONTEXT_WINDOW_DOI)
        URL = _extract_simple(strings, URL_PATTERN, CONTEXT_WINDOW_URL)

        keywords = _extract_keywords(
            strings,
            journal.get("category", ""),
            keys_from_title,
            keys_from_abstract,
            journal.get("journal_keyword", "")
        )

        # Формирование результата с дефолтными значениями
        return {
            "author": " ; ".join(authors) if authors else "",
            "category": journal.get("category", ""),
            "title": title or "",
            "keywords": ", ".join(keywords) if keywords else "",
            "abstract": abstract or "",
            "journal": journal.get("journal_ru", ""),
            "journal_eng": journal.get("journal_eng", ""),
            "year": year or "",
            "volume": volume or "",
            "issue": issue or "",
            "pages": pages or "",
            "URL": URL or "",
            "DOI": DOI or "",
            "ISSN": journal.get("ISSN", ""),
            "lang": lang or "",
            "founder": journal.get("founder", ""),
            "type": journal.get("type", ""),
            "serial": journal.get("serial", ""),
        }

    except Exception as e:
        logger.exception(f"Ошибка при обработке {path}: {e}")
        return None


# ---------------------------------------------------------------------
# EXTRACT-ФУНКЦИИ
# ---------------------------------------------------------------------

def _extract_authors(strings):
    authors = []
    for line in strings:
        if AUTHOR_PATTERN in line:
            count = line.count(AUTHOR_PATTERN)
            for _ in range(count):
                start = line.find(AUTHOR_PATTERN) + AUTHOR_START
                end = line.find(AUTHOR_END) + 1
                name = line[start:end].replace('&nbsp;', ', ').title()
                authors.append(name)
                line = line[end + 12:]
    return authors


def _extract_title(strings):
    for line in strings:
        if TITLE_PATTERN in line:
            start = line.find(TITLE_PATTERN) + TITLE_START
            end = line.find(TITLE_END)
            title = line[start:end].capitalize()

            add_kw = _load_module("add_keywords")
            keys = add_kw.keys_from_text(title)

            corr = _load_module("correction")
            title = corr.persons_correction(title)
            title = corr.upper_sent(title)
            title = corr.upper_review(title)
            title = corr.upper_abb(title)
            title = corr.upper_comma(title)
            title = corr.delete_tag(title)
            title = corr.change_hyphen(title)
            title = corr.change_quotation(title)

            return title, keys
    return "", []


def _extract_journal(strings):
    journal_name = ""
    for line in strings:
        if JOURNAL_PATTERN in line:
            start = line.find(JOURNAL_PATTERN) + JOURNAL_START
            journal_name = line[start:line.find(JOURNAL_END)]

    for _, row in journal_list_df.iterrows():
        if journal_name in row.values:
            return {
                "journal_ru": row["journal"],
                "journal_eng": row["journal_eng"],
                "ISSN": row["ISSN"],
                "founder": row["founder"],
                "journal_keyword": row["journal_keyword"],
                "type": row["type"],
                "serial": row["serial_number"],
                "category": row["journal_category"],
            }

    return {
        "journal_ru": "",
        "journal_eng": "",
        "ISSN": "",
        "founder": "",
        "journal_keyword": "",
        "type": "",
        "serial": "",
        "category": "",
    }


def _extract_abstract(strings, category, lang, use_ai):
    abstract = ""
    keys = []

    for line in strings:
        if ABSTRACT_PATTERN in line:
            start = line.find(ABSTRACT_PATTERN) + ABSTRACT_START
            end = line.find(ABSTRACT_END)
            abstract = line[start:end]
            break

    if category == "A02" and abstract:
        add_kw = _load_module("add_keywords")
        keys = add_kw.keys_from_text(abstract)

        if use_ai and lang in ("английский", "французский", "немецкий"):
            tr = _load_module("translation")
            abstract = tr.abstracts_translator(abstract)

        if use_ai:
            gpt = _load_module("AI_processing")
            optimized = gpt.abstract_optimization_with_gpt(abstract)
            if optimized and "Я не могу обсуждать эту тему" not in optimized:
                abstract = optimized

    elif category in ("A04", "A13"):
        abstract = abstract[:500]

    return abstract, keys


def _extract_keywords(strings, category, k_title, k_abstract, journal_kw):
    if category != "A02":
        return [journal_kw]

    a_keywords = []
    for line in strings:
        if KEYWORD_PATTERN in line:
            start = line.find(KEYWORD_PATTERN) + KEYWORD_START
            end = line.find(KEYWORD_END)
            kw = (
                line[start:end]
                .replace(">", "")
                .replace('"', "")
                .lower()
            )
            a_keywords.append(kw)

    add_kw = _load_module("add_keywords")
    k_author = add_kw.keys_from_text(", ".join(a_keywords))

    return list(dict.fromkeys(k_title + k_author + k_abstract))[:10]


# ---------------------------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ---------------------------------------------------------------------

def _extract_simple(strings, pattern, shift):
    for line in strings:
        if pattern in line:
            return line[line.find(pattern) + shift: line.find("</")]
    return ""


def _load_module(key):
    path = config_paths[key]
    spec = importlib.util.spec_from_file_location(key, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_output_filename(record: dict) -> str:
    parts = [
        record["journal"] or "output",
        record["year"],
        record["volume"],
        record["issue"],
    ]
    return "_".join(p for p in parts if p) + ".xlsx"


def _write_excel(records: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Записывает список словарей в Excel‑файл с переносом текста в ячейках.

    Args:
        records: Список словарей с данными для записи.
        output_path: Путь к выходному XLSX‑файлу.

    Raises:
        IOError: Если не удалось создать/записать файл.
        Exception: Для прочих ошибок.
    """
    # Проверка входных данных
    if not records:
        logger.warning("Пустой список записей. Файл не создан: %s", output_path)
        return

    try:
        # Создаём родительскую директорию, если её нет
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Создаем книгу с явной кодировкой
        workbook = xlsxwriter.Workbook(
            str(output_path),
            {"constant_memory": True, "strings_to_urls": False}
        )
        worksheet = workbook.add_worksheet()

        # Формат для переноса текста
        text_format = workbook.add_format({"text_wrap": True})

        # Получаем заголовки (объединяем ключи всех записей для полноты)
        headers = list({key for record in records for key in record.keys()})
        headers.sort()  # Для предсказуемого порядка

        # Записываем заголовки
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Записываем данные
        for row_idx, record in enumerate(records, start=1):
            for col_idx, key in enumerate(headers):
                value = record.get(key, "")  # Безопасный доступ с дефолтом
                worksheet.write(row_idx, col_idx, value, text_format)

        # Сохраняем файл
        workbook.close()
        logger.info(
            "Создан Excel-файл: %s (записей: %d, столбцов: %d)",
            output_path,
            len(records),
            len(headers)
        )

    except PermissionError as e:
        logger.error("Нет прав на запись в %s: %s", output_path, e)
        raise IOError(f"Нет прав на запись: {output_path}") from e

    except OSError as e:
        logger.error("Ошибка дискового ввода-вывода при записи %s: %s", output_path, e)
        raise IOError(f"Ошибка диска: {output_path}") from e

    except Exception as e:
        logger.exception("Неожиданная ошибка при записи %s", output_path)
        # Попытка закрыть книгу при ошибке
        try:
            workbook.close()
        except:
            pass
        raise
