# -*- coding: utf-8 -*-
"""
Мультиплатформный конвертер библиографических данных из формата Excel в формат ИРБИС 64
Ориентирован на работу с различными специальностями

Автор: Gasilin Andrey
Дата последнего обновления: 2025-10-21
"""

import os
import datetime
import logging
import pandas as pd
from typing import List, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Попытка импортировать проверку рубрики, если есть
try:
    from check_functions import cat_check
except Exception:
    def cat_check(x):
        # заглушка: возвращаем 1 (OK) — поменяйте поведение, если у вас есть реальная функция
        return 1


# -------------------- Параметры и шаблоны --------------------
FIELD_102 = '#102: RU\n'
FIELD_181 = '#181: ^Ai\n'
FIELD_182 = '#182: ^An\n'
FIELD_905 = '#905: ^22^B1^D3^M1^S1\n'
FIELD_919 = '#919: ^rus^N02^KPSBO\n'
FIELD_920 = '#920: ASP\n'
FIELD_999 = '#999: 0000000\n'
SEPARATOR = '*****\n'

# Пути исходного и результирующего файлов (по умолчанию в рабочей директории)
current_dir = os.getcwd()
path_to_the_source_file = os.path.join(current_dir, 'files_for_editing', 'JOURNAL_OF_APPLIED_ECONOMIC_RESEARCH', '2024', 'JOAER_2024_4.xlsx')
path_to_the_target_file = os.path.join(current_dir, 'files_for_import_in_IRBIS', 'JOURNAL_OF_APPLIED_ECONOMIC_RESEARCH', '2024', 'JOAER_2024_4.txt')

# -------------------- Вспомогательные функции --------------------

def safe_get(df: pd.DataFrame, idx: int, col: str):
    """Безопасно получить значение из DataFrame и вернуть либо строку, либо None."""
    try:
        val = df.at[idx, col]
    except Exception:
        return None
    if pd.isna(val):
        return None
    return str(val)


def normalize_authors(authors_raw: str) -> List[Dict[str, str]]:
    """Разбирает строку авторов в список словарей вида [{'family':..., 'initials':...}, ...]
    Поддерживает разделители ';' и ','; ожидает формат "Фамилия, И.О." для каждого автора.
    Если не удается распарсить инициалы — поле 'initials' будет пустой строкой.
    """
    if not authors_raw:
        return []
    authors_raw = authors_raw.strip()
    # Разделяем по ';' если он присутствует, иначе по ' and ' или просто по ',' (с осторожностью)
    if ';' in authors_raw:
        parts = [a.strip() for a in authors_raw.split(';') if a.strip()]
    else:
        # Проверим есть ли несколько авторов через ' and ' / '&' / ','
        if ' and ' in authors_raw.lower() or '&' in authors_raw:
            temp = authors_raw.replace('&', ' and ')
            parts = [a.strip() for a in temp.split(' and ') if a.strip()]
        else:
            # Попытка разделить по ', ' но это может разбить фамилию и инициалы
            # Если есть ровно одна запятая — это "Фамилия, И.О." одного автора
            comma_count = authors_raw.count(',')
            if comma_count <= 1 and ',' in authors_raw:
                parts = [authors_raw]
            elif ',' in authors_raw and comma_count > 1:
                # Считаем, что авторы разделены через ';' обычно. На случай 'Фамилия1, И.О., Фамилия2, И.О.'
                # разбиваем по шаблону: каждые 2 фрагмента образуют автора
                fragments = [f.strip() for f in authors_raw.split(',') if f.strip()]
                parts = []
                for i in range(0, len(fragments), 2):
                    fam = fragments[i]
                    init = fragments[i+1] if i+1 < len(fragments) else ''
                    parts.append(f"{fam}, {init}" if init else fam)
            else:
                parts = [authors_raw]

    authors = []
    for p in parts:
        if ',' in p:
            fam, init = [x.strip() for x in p.split(',', 1)]
            # Нормализация точек и пробелов в инициалах
            init = init.replace('.', '. ').replace('  ', ' ').strip()
            authors.append({'family': fam, 'initials': init})
        else:
            # если нет запятой — полное имя в поле family
            authors.append({'family': p, 'initials': ''})
    return authors


def build_200_field(title: str, authors: List[Dict[str, str]]) -> str:
    """Формирует содержимое поля 200 из заголовка и списка авторов."""
    title = title or ''
    if not authors:
        return f'^A{title}^F\n'
    # Для каждого автора берем инициалы + фамилию (если есть инициалы — ставим перед фамилией)
    authors_strs = []
    for a in authors:
        if a['initials']:
            authors_strs.append(f"{a['initials']}{a['family']}")
        else:
            authors_strs.append(a['family'])
    authors_joined = ', '.join(authors_strs)
    return f'^A{title}^F{authors_joined}\n'


def build_700_701_fields(authors: List[Dict[str, str]]) -> (str, str):
    """Возвращает строки для поля 700 (основной автор) и 701 (повторяющиеся поля для соавторов)."""
    if not authors:
        return '\n', '\n'
    main = authors[0]
    if main['initials']:
        field_700 = f"#700: ^A{main['family']}^B{main['initials']}\n"
    else:
        field_700 = f"#700: ^A{main['family']}\n"

    field_701 = ''
    for co in authors[1:]:
        if co['initials']:
            field_701 += f"#701: ^A{co['family']}^B{co['initials']}\n"
        else:
            field_701 += f"#701: ^A{co['family']}\n"

    if not field_701:
        field_701 = '\n'

    return field_700, field_701


# -------------------- Основная логика --------------------

def main(src: str = path_to_the_source_file, tgt: str = path_to_the_target_file):
    # Проверки путей
    if not os.path.exists(src):
        logger.error('Исходный файл не найден: %s', src)
        return
    os.makedirs(os.path.dirname(tgt), exist_ok=True)

    try:
        df = pd.read_excel(src)
    except Exception as e:
        logger.exception('Ошибка при чтении Excel: %s', e)
        return

    n = len(df)
    logger.info('Обработано %d строк(и).', n)

    documents: List[str] = []

    for idx in range(n):
        # Инициализация полей
        field_19 = '#19: ^X0^A6 DOI^B'
        field_101 = '#101: '
        field_200 = '#200: '
        field_203 = '#203: '
        field_331 = '#331: '
        field_463 = '#463: '
        field_470 = '#470: ^0Рец. на кн.'
        field_610 = '#610: '
        field_690 = '#690: ^L'
        field_700 = '#700: '
        field_701 = ''
        field_900 = '#900: '
        field_951 = '#951: '
        field_963 = '#963: '
        field_964 = '#964: '
        field_965 = ''

        # Текущая дата для формирования шифров
        today = datetime.date.today()

        # DOI
        doi = safe_get(df, idx, 'DOI')
        if doi:
            field_19 += doi + '\n'
        else:
            field_19 = '\n'

        # Язык
        lang = safe_get(df, idx, 'lang')
        if lang and 'англий' in lang.lower():
            argument_101 = 'eng'
        else:
            argument_101 = 'rus'
        field_101 += argument_101 + '\n'

        # Авторы
        authors_raw = safe_get(df, idx, 'author') or ''
        authors = normalize_authors(authors_raw)

        # Заголовок
        title = safe_get(df, idx, 'title') or ''
        field_200 += build_200_field(title, authors)

        # Аннотация
        abstract = safe_get(df, idx, 'abstract')
        if abstract:
            field_331 += abstract + '\n'
        else:
            field_331 = '\n'

        # Рубрика
        category = safe_get(df, idx, 'category') or ''
        write_cat = cat_check(category)
        if write_cat != 1:
            logger.warning('Некорректная рубрика в строке %d: %s — будет пропущена', idx, category)
            category = ''
        field_690 += category + '\n' if category else '\n'

        # BU / 610
        if 'A02' in category:
            # Примерная логика, оставим как в оригинале, но корректно обработаем
            # Здесь можно вынести правила в отдельную функцию при необходимости
            BU_number = 'online_journals_archive'
            # (Можно реализовать детальные правила по датам при необходимости)
        else:
            BU_number = 'online_journals_archive'
        field_610 = '#610: ' + BU_number + '\n'

        # Поля 700/701
        field_700_built, field_701_built = build_700_701_fields(authors)
        field_700 = field_700_built
        field_701 = field_701_built

        # URL -> 951
        url = safe_get(df, idx, 'URL')
        if url:
            field_951 += '^I' + url + '^H05\n'
        else:
            field_951 = '\n'

        # ISSN и учредитель -> 963
        issn = safe_get(df, idx, 'ISSN') or ''
        founder = safe_get(df, idx, 'founder') or ''
        if issn or founder:
            argument_963 = '^F' + founder + '^I' + issn
            field_963 += argument_963 + '\n'
        else:
            field_963 = '\n'

        # Название журнала
        journal = safe_get(df, idx, 'journal') or ''
        journal_eng = safe_get(df, idx, 'journal_eng') or ''

        # year, volume, issue, pages, serial
        year = safe_get(df, idx, 'year') or ''
        volume = safe_get(df, idx, 'volume')
        issue = safe_get(df, idx, 'issue') or ''
        pages = safe_get(df, idx, 'pages') or ''
        serial = safe_get(df, idx, 'serial') or ''

        # Составляем 463 и шифр
        if volume:
            cipher = f"{serial}/{year}/{volume}/{issue}"
            argument_463 = (f"^C{journal}^J{year}^VТ. {volume}^H№ {issue}^S{pages}^X{journal_eng}^W{cipher}\n")
        else:
            cipher = f"{serial}/{year}/{issue}"
            argument_463 = (f"^C{journal}^J{year}^H{issue}^S{pages}^X{journal_eng}^W{cipher}\n")
        field_463 += argument_463

        # Рецензия
        review_author = safe_get(df, idx, 'review_author')
        review_marker = 1 if review_author else 0
        if review_marker:
            review_title = safe_get(df, idx, 'review_title') or ''
            review_output_data = safe_get(df, idx, 'review_output_data') or ''
            argument_470 = '^C' + review_title + '^D' + review_output_data + '^F' + review_author
            field_470 += argument_470 + '\n'
        else:
            field_470 = '\n'

        # Тип документа
        document_type = safe_get(df, idx, 'type') or ''
        if document_type == 'online' and not review_marker:
            argument_203 = '^AТекст^Cэлектронный\n'
            argument_900 = '^Tl2\n'
        elif document_type == 'online' and review_marker:
            argument_203 = '^AТекст^Cэлектронный\n'
            argument_900 = '^Cd2^Tl2\n'
        else:
            argument_203 = '^AТекст^Cнепосредственный\n'
            argument_900 = '^B08\n'
        field_203 += argument_203
        field_900 += argument_900

        # 964 из категории (защищаем длину)
        if 'A02' in category:
            argument_964 = category[1:6] if category and len(category) >= 6 else ''
            field_964 += argument_964 + '\n' if argument_964 else '\n'
        else:
            argument_964 = category[1:3] if category and len(category) >= 3 else ''
            field_964 += argument_964 + '\n' if argument_964 else '\n'

        # Ключевые слова -> 965
        keywords_str = safe_get(df, idx, 'keywords')
        if keywords_str and keywords_str.strip():
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            for kw in keywords:
                field_965 += '#965: ' + kw + '\n'
        else:
            field_965 = '\n'

        # Сборка документа по вариантам (как в оригинале)
        if (review_marker == 0) and (document_type == 'online'):
            document = (field_19 + field_101 + FIELD_102 + FIELD_181 + FIELD_182
                        + field_200 + field_203 + field_331 + field_463 + field_610 + field_690
                        + field_700 + field_701 + field_900 + FIELD_905
                        + FIELD_919 + FIELD_920 + field_951 + field_963 + field_964 + field_965
                        + FIELD_999 + SEPARATOR)
        elif (review_marker == 1) and (document_type == 'online'):
            document = (field_19 + field_101 + FIELD_102 + FIELD_181 + FIELD_182
                        + field_200 + field_203 + field_331 + field_463 + field_470 + field_610
                        + field_690 + field_700 + field_701 + field_900 + FIELD_905
                        + FIELD_919 + FIELD_920 + field_951 + field_963 + field_964 + field_965
                        + FIELD_999 + SEPARATOR)
        else:
            document = (field_19 + field_101 + FIELD_102 + FIELD_181 + FIELD_182
                        + field_200 + field_203 + field_331 + field_463 + field_610 + field_690
                        + field_700 + field_701 + field_900 + FIELD_905
                        + FIELD_919 + FIELD_920 + field_963 + field_964 + field_965
                        + FIELD_999 + SEPARATOR)

        # Убираем двойные пустые строки
        document = document.replace('\n\n', '\n')
        documents.append(document)

    # Запись в файл
    try:
        with open(tgt, 'w', encoding='utf-8') as fout:
            fout.writelines(documents)
        logger.info('Файл успешно создан: %s', tgt)
    except Exception as e:
        logger.exception('Ошибка при записи файла: %s', e)


if __name__ == '__main__':
    main()
