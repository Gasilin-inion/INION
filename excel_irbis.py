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
from check_functions import cat_check

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)



# -------------------- Параметры и шаблоны --------------------
FIELD_102 = '#102: RU\n'
FIELD_181 = '#181: ^Ai\n'
FIELD_182 = '#182: ^An\n'
FIELD_905 = '#905: ^22^B1^D3^M1^S1\n'
FIELD_905_J = '#905: ^B1^D3^M1^S1\n'
FIELD_919 = '#919: ^rus^N02^KPSBO\n'
FIELD_920 = '#920: ASP\n'
FIELD_920_J =  '#920: NJ\n'
FIELD_999 = '#999: 0000000\n'
SEPARATOR = '*****\n'
wrong_categories = []

# Пути исходного и результирующего файлов (по умолчанию в рабочей директории)
current_dir = os.getcwd()
path_to_the_source_file = os.path.join(current_dir, 'files_to_edit', 'table_of_articles.xlsx')
path_to_the_target_file = os.path.join(current_dir, 'files_to_import_to_IRBIS', 'list_of_documents.txt')
path_to_wrong_categories = os.path.join(current_dir, 'files_for_import_in_IRBIS', 'wrong_categories.txt')

# Безопасно получить значение из DataFrame и вернуть либо строку, либо None

def safe_get(df: pd.DataFrame, idx: int, col: str):
    try:
        val = df.at[idx, col]
    except Exception:
        return None
    if pd.isna(val):
        return None
    return str(val)


# Основная логика

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
        field_690 = ''
        field_700 = '#700: '
        field_701 = ''
        field_900 = '#900: '
        field_903 = '#903: '
        field_910 = '#910: ^AE^C'
        field_933 = '#933: '
        field_934 = '#934: '
        field_935 = '#935: '
        field_936 = '#936: '
        field_951 = '#951: '
        field_963 = '#963: '
        field_965 = ''

        # Текущая дата для формирования шифров
        today = datetime.date.today()
        actual_data = str(today)
        actual_data = actual_data.replace('-', '')

        # DOI (19)
        doi = safe_get(df, idx, 'DOI')
        if doi:
            field_19 += doi + '\n'
        else:
            field_19 = '\n'

        # Язык (101)
        lang = safe_get(df, idx, 'lang')
        if lang and 'англий' in lang.lower():
            argument_101 = 'eng'
        else:
            argument_101 = 'rus'
        field_101 += argument_101 + '\n'

        # Авторы
        authors_str = safe_get(df, idx, 'author')
        if ';' in authors_str:
            authors_list = authors_str.split(' ; ')
            number_of_authors = len(authors_list)
            if number_of_authors == 2:
                author_1 = authors_list[0]
                author_2 = authors_list[1]
                author_1_xx = author_1.split(', ')
                author_2_xx = author_2.split(', ')
                author_1_abb = str(author_1_xx[1])
                author_1_abb = author_1_abb.replace('.', '. ')
                author_2_abb = str(author_2_xx[1])
                author_2_abb = author_2_abb.replace('.', '. ')
            elif number_of_authors == 3:
                author_1 = authors_list[0]
                author_2 = authors_list[1]
                author_3 = authors_list[2]
                author_1_xx = author_1.split(', ')
                author_2_xx = author_2.split(', ')
                author_3_xx = author_3.split(', ')
                author_1_abb = str(author_1_xx[1])
                author_1_abb = author_1_abb.replace('.', '. ')
                author_2_abb = str(author_2_xx[1])
                author_2_abb = author_2_abb.replace('.', '. ')
                author_3_abb = str(author_3_xx[1])
                author_3_abb = author_3_abb.replace('.', '. ')
            elif number_of_authors == 4:
                author_1 = authors_list[0]
                author_2 = authors_list[1]
                author_3 = authors_list[2]
                author_4 = authors_list[3]
                author_1_xx = author_1.split(', ')
                author_2_xx = author_2.split(', ')
                author_3_xx = author_3.split(', ')
                author_4_xx = author_4.split(', ')
                author_1_abb = str(author_1_xx[1])
                author_1_abb = author_1_abb.replace('.', '. ')
                author_2_abb = str(author_2_xx[1])
                author_2_abb = author_2_abb.replace('.', '. ')
                author_3_abb = str(author_3_xx[1])
                author_3_abb = author_3_abb.replace('.', '. ')
                author_4_abb = str(author_4_xx[1])
                author_4_abb = author_4_abb.replace('.', '. ')
            elif number_of_authors == 5:
                author_1 = authors_list[0]
                author_2 = authors_list[1]
                author_3 = authors_list[2]
                author_4 = authors_list[3]
                author_5 = authors_list[4]
                author_1_xx = author_1.split(', ')
                author_2_xx = author_2.split(', ')
                author_3_xx = author_3.split(', ')
                author_4_xx = author_4.split(', ')
                author_5_xx = author_5.split(', ')
                author_1_abb = str(author_1_xx[1])
                author_1_abb = author_1_abb.replace('.', '. ')
                author_2_abb = str(author_2_xx[1])
                author_2_abb = author_2_abb.replace('.', '. ')
                author_3_abb = str(author_3_xx[1])
                author_3_abb = author_3_abb.replace('.', '. ')
                author_4_abb = str(author_4_xx[1])
                author_4_abb = author_4_abb.replace('.', '. ')
                author_5_abb = str(author_5_xx[1])
                author_5_abb = author_5_abb.replace('.', '. ')
        elif (',' in authors_str):
            author_1_xx = authors_str.split(', ')
            author_1_abb = str(author_1_xx[1])
            author_1_abb = author_1_abb.replace('.', '. ')
        else:
            author_1_xx = authors_str
            author_1_abb = ''

        # Заголовок (200)
        title = safe_get(df, idx, 'title')
        if ';' in authors_str:
            if number_of_authors == 2:
                argument_200 = ('^A' + title + '^F' + author_1_abb
                                + author_1_xx[0] + ', '
                                + author_2_abb + author_2_xx[0])
            elif number_of_authors == 3:
                argument_200 = ('^A' + title + '^F' + author_1_abb
                                + author_1_xx[0] + ', '
                                + author_2_abb + author_2_xx[0]
                                + ', ' + author_3_abb + author_3_xx[0])
            elif number_of_authors == 4:
                argument_200 = ('^A' + title + '^F' + author_1_abb
                                + author_1_xx[0] + ', '
                                + author_2_abb + author_2_xx[0]
                                + ', ' + author_3_abb + author_3_xx[0]
                                + ', ' + author_4_abb + author_4_xx[0])
            elif number_of_authors == 5:
                argument_200 = ('^A' + title + '^F' + author_1_abb
                                + author_1_xx[0] + ', '
                                + author_2_abb + author_2_xx[0]
                                + ', ' + author_3_abb + author_3_xx[0]
                                + ', ' + author_4_abb + author_4_xx[0]
                                + ', ' + author_5_abb + author_5_xx[0])
        # Варианты для единственного автора
        elif (not ';' in authors_str) and (',' in authors_str): # При наличии аббревиатуры
            argument_200 = ('^A' + title + '^F' + author_1_abb
                            + author_1_xx[0])
        else:                                                   # При отсутствии аббревиатуры
            argument_200 = ('^A' + title + '^F' + authors_str)
        field_200 = field_200 + argument_200 + '\n'

        # Аннотация (331)
        abstract = safe_get(df, idx, 'abstract')
        if abstract:
            field_331 += abstract + '\n'
        else:
            field_331 = '\n'

        # Рубрики (690)
        categories = []
        category = safe_get(df, idx, 'category') or ''
        if category and category.strip():
            if ';' in category:
                categories = category.split(' ; ')
                for cat in categories:
                    checker = cat_check(cat)
                    if checker == 1:
                        field_690 += '#690: ^L' + cat + '\n'
                    else:
                        field_690 += '\n'
                        wrong_categories.append(author_1 + '\n')
            else:
                checker = cat_check(category)
                if checker == 1:
                    field_690 += '#690: ^L' + category + '\n'
                else:
                    field_690 += '\n'
                    wrong_categories.append(author_1 + '\n')
        else:
            category = ''

        # Основной автор (700)
        argument_700 = ''
        if (not ';' in authors_str) and (',' in authors_str):                          # Если нет соавторов, но есть аббревиатура
            argument_700 = '^A' + author_1_xx[0] + '^B' + author_1_xx[1] + '\n'
        elif (not ';' in authors_str) and (not ',' in authors_str):                     # Если нет соавторов и аббревиатуры
            argument_700 = '^A' + authors_str + '\n'
        field_700 = field_700 + argument_700

        # Соавтор (701)
        if ';' in authors_str:
            if number_of_authors == 2:
                argument_701 = ('^A' + author_2_xx[0] + '^B'
                                + author_2_xx[1] + '\n')
                field_701 = (field_701 + argument_701 + '\n')
            elif number_of_authors == 3:
                argument_701 = ('^A' + author_2_xx[0] + '^B'
                                + author_2_xx[1] + '\n'
                                + '#701: ^A' + author_3_xx[0] + '^B'
                                + author_3_xx[1] + '\n' )
                field_701 = (field_701 + argument_701 + '\n')
            elif number_of_authors == 4:
                argument_701 = ('^A' + author_2_xx[0] + '^B'
                                + author_2_xx[1] + '\n'
                                + '#701: ^A' + author_3_xx[0] + '^B'
                                + author_3_xx[1] + '\n'
                                + '#701: ^A' + author_4_xx[0] + '^B'
                                + author_4_xx[1] + '\n')
                field_701 = (field_701 + argument_701 + '\n')
            elif number_of_authors == 5:
                argument_701 = ('^A' + author_2_xx[0] + '^B'
                                + author_2_xx[1] + '\n'
                                + '#701: ^A' + author_3_xx[0] + '^B'
                                + author_3_xx[1] + '\n'
                                + '#701: ^A' + author_4_xx[0] + '^B'
                                + author_4_xx[1] + '\n'
                                + '#701: ^A' + author_5_xx[0] + '^B'
                                + author_5_xx[1] + '\n')
                field_701 = (field_701 + argument_701 + '\n')
        else:
            field_701 = '\n'

        # URL (951)
        url = safe_get(df, idx, 'URL')
        if url:
            field_951 += '^I' + url + '^H05\n'
        else:
            field_951 = '\n'

        # ISSN и учредитель (963)
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
                        + field_200 + field_203 + field_331 + field_463 + field_690
                        + field_700 + field_701 + field_900 + FIELD_905
                        + FIELD_919 + FIELD_920 + field_951 + field_963 + field_965
                        + FIELD_999 + SEPARATOR)
        elif (review_marker == 1) and (document_type == 'online'):
            document = (field_19 + field_101 + FIELD_102 + FIELD_181 + FIELD_182
                        + field_200 + field_203 + field_331 + field_463 + field_470
                        + field_690 + field_700 + field_701 + field_900 + FIELD_905
                        + FIELD_919 + FIELD_920 + field_951 + field_963 + field_965
                        + FIELD_999 + SEPARATOR)
        else:
            document = (field_19 + field_101 + FIELD_102 + FIELD_181 + FIELD_182
                        + field_200 + field_203 + field_331 + field_463 + field_690
                        + field_700 + field_701 + field_900 + FIELD_905
                        + FIELD_919 + FIELD_920 + field_963 + field_965
                        + FIELD_999 + SEPARATOR)

        # Убираем двойные пустые строки
        document = document.replace('\n\n', '\n')
        documents.append(document)

    # Формирование данных о номере журнала
    field_903 += cipher + '\n'
    field_910 += actual_data + '\n'
    field_933 += serial + '\n'
    field_934 += year + '\n'
    field_935 += str(volume) + '\n'
    field_936 += issue + '\n'
    journal_issue = (FIELD_181 + FIELD_182 + field_203 + field_903 + FIELD_905_J + field_910 + FIELD_920_J + field_933 + field_934 + field_935 + field_936 + FIELD_999 + SEPARATOR)

    # Запись в файл
    try:
        with open(tgt, 'w', encoding='utf-8') as fout:
            fout.writelines(journal_issue)
            fout.writelines(documents)
        logger.info('Файл успешно создан: %s', tgt)
    except Exception as e:
        logger.exception('Ошибка при записи файла: %s', e)

    # Формирование файла ошибок в рубриках:
    if wrong_categories != []:
        with open(path_to_wrong_categories, 'w', encoding='utf-8') as wc:
            wc.writelines(f'Ошибки в рубриках допущены в статьях следующих авторов:\n\n')
            wc.writelines(wrong_categories)


if __name__ == '__main__':
    main()
