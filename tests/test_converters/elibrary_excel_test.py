"""
Конвертер библиографических записей e-Library
HTML → Excel (редактируемый)

Автор исходного алгоритма: Andrey Gasilin
Рефакторинг под контракт: Flask / CLI / tests

Дата: 2026
"""

from pathlib import Path
from typing import Iterable, List
import time
import json
import pandas as pd
import xlsxwriter
import importlib.util

from src.utils.file_manager import EDITABLE_XLSX_DIR
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


# ---------------------------------------------------------------------
# ПАТТЕРНЫ (1:1 из исходного кода)
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


# ---------------------------------------------------------------------
# ПУБЛИЧНЫЙ КОНВЕРТЕР (КОНТРАКТ)
# ---------------------------------------------------------------------

def convert_html_to_excel(
    html_files: Iterable[Path],
    *,
    output_dir: Path | None = None,
    use_ai: bool = True
) -> List[Path]:
    """
    Конвертация HTML e-Library → Excel

    :param html_files: iterable Path к HTML-файлам
    :param output_dir: каталог для XLSX
    :param use_ai: использовать AI (перевод / GPT)
    :return: список созданных XLSX-файлов
    """

    output_dir = output_dir or Path(EDITABLE_XLSX_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

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

    if not records:
        logger.warning("Нет данных для записи в Excel")
        return []

    output_filename = _build_output_filename(records[0])
    output_path = output_dir / output_filename

    _write_excel(records, output_path)

    elapsed = time.time() - start_time
    logger.info(f"Готово: {len(records)} записей, {elapsed:.1f} сек")

    return [output_path]


# ---------------------------------------------------------------------
# ОБРАБОТКА ОДНОГО HTML-ФАЙЛА
# ---------------------------------------------------------------------

def _process_html(path: Path, use_ai: bool) -> dict | None:
    strings = path.read_text(encoding="utf-8").splitlines()

    authors = _extract_authors(strings)
    title, keys_from_title = _extract_title(strings)
    journal = _extract_journal(strings)

    year = _extract_simple(strings, YEAR_PATTERN, 30)
    volume = _extract_simple(strings, VOLUME_PATTERN, 30)
    issue = _extract_simple(strings, ISSUE_PATTERN, 20).replace('&nbsp;', ' ')
    pages = _extract_simple(strings, PAGES_PATTERN, 35)
    lang = _extract_simple(strings, LANG_PATTERN, 31)

    abstract, keys_from_abstract = _extract_abstract(
        strings, journal["category"], lang, use_ai
    )

    DOI = _extract_simple(strings, DOI_PATTERN, 20)
    URL = _extract_simple(strings, URL_PATTERN, 32)

    keywords = _extract_keywords(
        strings,
        journal["category"],
        keys_from_title,
        keys_from_abstract,
        journal["journal_keyword"]
    )

    return {
        "author": " ; ".join(authors),
        "category": journal["category"],
        "title": title,
        "keywords": ", ".join(keywords),
        "abstract": abstract,
        "journal": journal["journal_ru"],
        "journal_eng": journal["journal_eng"],
        "year": year,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "URL": URL,
        "DOI": DOI,
        "ISSN": journal["ISSN"],
        "lang": lang,
        "founder": journal["founder"],
        "type": journal["type"],
        "serial": journal["serial"],
    }


# ---------------------------------------------------------------------
# EXTRACT-ФУНКЦИИ (ЛОГИКА СОХРАНЕНА)
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


def _write_excel(records: list[dict], output_path: Path) -> None:
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet()
    text_format = workbook.add_format({"text_wrap": True})

    headers = list(records[0].keys())
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, record in enumerate(records, start=1):
        for col, key in enumerate(headers):
            worksheet.write(row, col, record[key], text_format)

    workbook.close()
    logger.info(f"Создан Excel-файл: {output_path}")
