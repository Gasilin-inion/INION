# -*- coding: utf-8 -*-
"""
Конвертер библиографических данных
Excel → ИРБИС 64

Автор исходного алгоритма: Andrey Gasilin
Рефакторинг под контракт: Flask / CLI / tests
"""

from pathlib import Path
from typing import Iterable, List
import datetime
import json
import logging
import pandas as pd
import importlib.util

from src.utils.file_manager import IRBIS_OUTPUT_DIR
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

rubricator = pd.read_json(config_paths["rubricator"])


# ---------------------------------------------------------------------
# КОНСТАНТЫ ИРБИС
# ---------------------------------------------------------------------

FIELD_102 = '#102: RU\n'
FIELD_181 = '#181: ^Ai\n'
FIELD_182 = '#182: ^An\n'
FIELD_905 = '#905: ^22^B1^D3^M1^S1\n'
FIELD_905_J = '#905: ^B1^D3^M1^S1\n'
FIELD_919 = '#919: ^rus^N02^KPSBO\n'
FIELD_920 = '#920: ASP\n'
FIELD_920_J = '#920: NJ\n'
FIELD_999 = '#999: 0000000\n'
SEPARATOR = '*****\n'


# ---------------------------------------------------------------------
# ПУБЛИЧНЫЙ КОНВЕРТЕР (КОНТРАКТ)
# ---------------------------------------------------------------------

def convert_excel_to_irbis(
    excel_files: Iterable[Path],
    *,
    output_dir: Path | None = None
) -> List[Path]:
    """
    Конвертация Excel → формат ИРБИС 64

    :param excel_files: iterable Path к XLSX
    :param output_dir: каталог для TXT
    :return: список созданных TXT-файлов
    """

    output_dir = output_dir or Path(IRBIS_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    result_files: List[Path] = []

    for excel_path in excel_files:
        try:
            logger.info(f"Обработка Excel: {excel_path.name}")

            if not excel_path.exists():
                logger.warning(f"Файл не найден: {excel_path}")
                continue

            out_path = output_dir / excel_path.with_suffix(".txt").name
            _process_excel(excel_path, out_path)

            result_files.append(out_path)

        except Exception as exc:
            logger.exception(f"Ошибка {excel_path.name}: {exc}")

    return result_files


# ---------------------------------------------------------------------
# ОСНОВНАЯ ЛОГИКА (БЫВШИЙ main)
# ---------------------------------------------------------------------

def _process_excel(src: Path, tgt: Path) -> None:
    df = pd.read_excel(src)
    n = len(df)
    logger.info(f"Строк в Excel: {n}")

    wrong_categories: list[str] = []
    documents: list[str] = []

    today = datetime.date.today().strftime("%Y%m%d")

    authors_module = _load_module("authors")

    for idx in range(n):
        document, cipher, meta = _build_document(
            df, idx, authors_module, wrong_categories
        )
        documents.append(document)

    journal_issue = _build_journal_issue(meta, cipher, today)

    with open(tgt, "w", encoding="utf-8") as f:
        f.write(journal_issue)
        f.writelines(documents)

    logger.info(f"Создан файл ИРБИС: {tgt}")

    if wrong_categories:
        _write_wrong_categories(tgt, wrong_categories)


# ---------------------------------------------------------------------
# ПОСТРОЕНИЕ ОДНОЙ ЗАПИСИ
# ---------------------------------------------------------------------

def _build_document(df, idx, authors_module, wrong_categories):
    safe = lambda c: _safe_get(df, idx, c)

    field_19 = '#19: ^X0^A6 DOI^B'
    field_101 = '#101: '
    field_200 = '#200: '
    field_203 = '#203: '
    field_331 = '#331: '
    field_463 = '#463: '
    field_470 = '#470: ^0Рец. на кн.'
    field_690 = ''
    field_700 = '#700: '
    field_701 = '#701: '
    field_900 = '#900: '
    field_951 = '#951: '
    field_963 = '#963: '
    field_965 = ''

    # DOI
    doi = safe('DOI')
    field_19 = field_19 + doi + '\n' if doi else '\n'

    # Язык
    lang = safe('lang') or ''
    field_101 += 'eng\n' if 'англий' in lang.lower() else 'rus\n'

    # Авторы
    authors_dic = authors_module.authors_process(safe('author'))
    field_200 += authors_module.build_argument_200(safe('title'), authors_dic) + '\n'
    field_700, field_701 = authors_module.build_author_fields(
        authors_dic, field_700, field_701
    )

    # Аннотация
    abstract = safe('abstract')
    field_331 = field_331 + abstract + '\n' if abstract else '\n'

    # Рубрики
    category = safe('category') or ''
    if category:
        for cat in map(str.strip, category.split(',')):
            if _cat_check(cat):
                field_690 += f'#690: ^L{cat}\n'
            else:
                wrong_categories.append(safe('title') + '\n\n')

    # URL
    url = safe('URL')
    field_951 = field_951 + f'^I{url}^H05\n' if url else '\n'

    # ISSN / учредитель
    issn = safe('ISSN') or ''
    founder = safe('founder') or ''
    field_963 = field_963 + f'^F{founder}^I{issn}\n' if (issn or founder) else '\n'

    # Выходные данные
    journal = safe('journal') or ''
    journal_eng = safe('journal_eng') or ''
    year = safe('year') or ''
    volume = safe('volume') or ''
    issue = safe('issue') or ''
    pages = safe('pages') or ''
    serial = safe('serial') or ''

    if volume:
        cipher = f"{serial}/{year}/{volume}/{issue}"
        field_463 += f'^C{journal}^J{year}^VТ. {volume}^H№ {issue}^S{pages}^X{journal_eng}^W{cipher}\n'
    else:
        cipher = f"{serial}/{year}/{issue}"
        field_463 += f'^C{journal}^J{year}^H{issue}^S{pages}^X{journal_eng}^W{cipher}\n'

    # Тип документа
    doc_type = safe('type') or ''
    if doc_type == 'online':
        field_203 += '^AТекст^Cэлектронный\n'
        field_900 += '^Tl2\n'
    else:
        field_203 += '^AТекст^Cнепосредственный\n'
        field_900 += '^B08\n'

    # Ключевые слова
    kw = safe('keywords')
    if kw:
        for k in map(str.strip, kw.split(',')):
            field_965 += f'#965: {k}\n'

    document = (
        field_19 + field_101 + FIELD_102 + FIELD_181 + FIELD_182 +
        field_200 + field_203 + field_331 + field_463 + field_690 +
        field_700 + field_701 + field_900 + FIELD_905 +
        FIELD_919 + FIELD_920 + field_951 + field_963 +
        field_965 + FIELD_999 + SEPARATOR
    ).replace('\n\n', '\n')

    meta = {
        "serial": serial,
        "year": year,
        "volume": volume,
        "issue": issue,
        "doc_type": doc_type,
    }

    return document, cipher, meta


# ---------------------------------------------------------------------
# ЖУРНАЛЬНЫЙ ВЫПУСК
# ---------------------------------------------------------------------

def _build_journal_issue(meta, cipher, today):
    field_903 = '#903: ' + cipher + '\n'
    field_910 = '#910: ^AE^C' + today + '\n'
    field_933 = '#933: ' + meta["serial"] + '\n'
    field_934 = '#934: ' + meta["year"] + '\n'
    field_936 = '#936: ' + meta["issue"] + '\n'
    field_935 = '#935: ' + meta["volume"] + '\n' if meta["volume"] else ''

    return (
        FIELD_181 + FIELD_182 + field_903 + FIELD_905_J +
        field_910 + FIELD_920_J + field_933 + field_934 +
        field_935 + field_936 + FIELD_999 + SEPARATOR
    )


# ---------------------------------------------------------------------
# УТИЛИТЫ
# ---------------------------------------------------------------------

def _safe_get(df: pd.DataFrame, idx: int, col: str):
    try:
        val = df.at[idx, col]
        return None if pd.isna(val) else str(val)
    except Exception:
        return None


def _cat_check(category: str) -> bool:
    return rubricator['category'].str.contains(category, na=False).any()


def _load_module(key: str):
    path = config_paths[key]
    spec = importlib.util.spec_from_file_location(key, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_wrong_categories(tgt: Path, wrong_categories: list[str]):
    path = tgt.with_name(tgt.stem + "_wrong_cat.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "Внимание! В следующих статьях обнаружены ошибки в рубриках:\n\n"
        )
        f.writelines(wrong_categories)
    logger.warning(f"Создан файл ошибок рубрик: {path}")
