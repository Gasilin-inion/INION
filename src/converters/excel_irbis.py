# -*- coding: utf-8 -*-
"""
Конвертер библиографических данных из формата Excel в формат ИРБИС 64

Автор: Gasilin Andrey
Дата последнего обновления: 17.12.25
"""

import os
import sys
import datetime
import json
import logging
import pandas as pd
from typing import List
import importlib.util

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Импорт файла конфигурации путей

with open("./data/config/path_config.json", "r", encoding="utf-8") as pathfile:
    config_paths = json.load(pathfile)

# Параметры и шаблоны
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
input_files = []
output_files = []
authors_dic = {}
indx = 0

# Импорт данных из DataFrame

def safe_get(df: pd.DataFrame, idx: int, col: str):
    try:
        val = df.at[idx, col]
    except Exception:
        return None
    if pd.isna(val):
        return None
    return str(val)

# Импорт рубрикатора

rubricator_path = config_paths["rubricator"]
rubricator = pd.read_json(rubricator_path)

def cat_check(category):
    return rubricator['category'].str.contains(category, na=False).any()

# Анализируем содержимое папки 'files_to_edit'

get_files = config_paths["multifile"]
spec = importlib.util.spec_from_file_location("get_files_in_folder", get_files)
module = importlib.util.module_from_spec(spec)
sys.modules["get_files_in_folder"] = module
spec.loader.exec_module(module)
path_to_income_files = config_paths["files_to_edit"]
input_files = module.get_files_in_folder(path_to_income_files)
for source in input_files:
    line = source.replace('files_to_edit', 'files_to_import_to_IRBIS')
    line = line.replace('.xlsx', '.txt')
    output_files.append(line)
number_of_files = len(input_files)

# Основная логика

def main(src: str = input_files[indx], tgt: str = output_files[indx]):
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
        field_701 = '#701: '
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

        # DOI (поле 19)
        doi = safe_get(df, idx, 'DOI')
        if doi:
            field_19 += doi + '\n'
        else:
            field_19 = '\n'

        # Язык (поле 101)
        lang = safe_get(df, idx, 'lang')
        if lang and 'англий' in lang.lower():
            argument_101 = 'eng'
        else:
            argument_101 = 'rus'
        field_101 += argument_101 + '\n'

        # Автор(ы)
        authors_str = safe_get(df, idx, 'author')
        authors_funct = config_paths["authors"]
        spec = importlib.util.spec_from_file_location("authors_functions", authors_funct)
        module = importlib.util.module_from_spec(spec)
        sys.modules["authors_functions"] = module
        spec.loader.exec_module(module)
        authors_dic = module.authors_process(authors_str)
        
        # Заголовок (поле 200)
        title = safe_get(df, idx, 'title')
        argument_200 = module.build_argument_200(title, authors_dic)       
        field_200 = field_200 + argument_200 + '\n'     

        # Аннотация (поле 331)
        abstract = safe_get(df, idx, 'abstract')
        if abstract:
            field_331 += abstract + '\n'
        else:
            field_331 = '\n'

        # Рубрики АИСОН (поле 690)
        categories = []
        category = safe_get(df, idx, 'category') or ''
        if category and category.strip():
            if ',' in category:
                categories = category.split(', ')
                for cat in categories:
                    checker = cat_check(cat)
                    if checker == True:
                        field_690 += '#690: ^L' + cat + '\n'
                    else:
                        field_690 += '\n'
                        wrong_categories.append(title + '\n\n')
            else:
                checker = cat_check(category)
                if checker == True:
                    field_690 += '#690: ^L' + category + '\n'
                else:
                    field_690 += '\n'
                    wrong_categories.append(title + '\n\n')
        else:
            category = ''

        # Автор и соавторы (поля 700 и 701)
        field_700, field_701 = module.build_author_fields(authors_dic, field_700, field_701)
                
        # URL (поле 951)
        url = safe_get(df, idx, 'URL')
        if url:
            field_951 += '^I' + url + '^H05\n'
        else:
            field_951 = '\n'

        # ISSN и учредитель (поле 963)
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

        # Год, том, номер, диапазон страниц, шифр
        year = safe_get(df, idx, 'year') or ''
        volume = safe_get(df, idx, 'volume') or ''
        issue = safe_get(df, idx, 'issue') or ''
        pages = safe_get(df, idx, 'pages') or ''
        serial = safe_get(df, idx, 'serial') or ''

        # Основные выходные данные (поле 463)
        if volume:
            cipher = f"{serial}/{year}/{volume}/{issue}"
            argument_463 = (f"^C{journal}^J{year}^VТ. {volume}^H№ {issue}^S{pages}^X{journal_eng}^W{cipher}\n")
        else:
            cipher = f"{serial}/{year}/{issue}"
            argument_463 = (f"^C{journal}^J{year}^H{issue}^S{pages}^X{journal_eng}^W{cipher}\n")
        field_463 += argument_463

        # Рецензия (при наличии)
        review_author = safe_get(df, idx, 'review_author')
        review_marker = 1 if review_author else 0
        if review_marker:
            review_title = safe_get(df, idx, 'review_title') or ''
            review_output_data = safe_get(df, idx, 'review_output_data') or ''
            argument_470 = '^C' + review_title + '^D' + review_output_data + '^F' + review_author
            field_470 += argument_470 + '\n'
        else:
            field_470 = '\n'

        # Тип документа (непосредственный/электронный)
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

        # Ключевые слова (поле 965)
        keywords_str = safe_get(df, idx, 'keywords')
        if keywords_str and keywords_str.strip():
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            for kw in keywords:
                field_965 += '#965: ' + kw + '\n'
        else:
            field_965 = '\n'

        # Сборка документа по вариантам
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
                        + FIELD_919 + FIELD_920 + field_951 + field_963
                        + field_965 + FIELD_999 + SEPARATOR)
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
    field_936 += issue + '\n'
    if volume:
        field_935 += str(volume) + '\n'
        journal_issue = (FIELD_181 + FIELD_182 + field_203 + field_903 + FIELD_905_J
                    + field_910 + FIELD_920_J + field_933 + field_934 + field_935
                    + field_936 + FIELD_999 + SEPARATOR)
    else:
        journal_issue = (FIELD_181 + FIELD_182 + field_203 + field_903 + FIELD_905_J
                    + field_910 + FIELD_920_J + field_933 + field_934
                    + field_936 + FIELD_999 + SEPARATOR)

    # Запись в файл
    try:
        with open(tgt, 'w', encoding='utf-8') as fout:
            fout.writelines(journal_issue)
            fout.writelines(documents)
        logger.info('Файл успешно создан: %s', tgt)
    except Exception as e:
        logger.exception('Ошибка при записи файла: %s', e)

    # Файл ошибок в рубриках (при наличии)
    if (wrong_categories != []):
        wct = tgt.replace('.txt', '_wrong_cat.txt')
        try:
            with open(wct, 'w', encoding='utf-8') as wrong:
                wrong.writelines(f'Внимание! В статьях со следующеми заголовками допущены ошибки в рубриках:\n\n')
                wrong.writelines(wrong_categories)
                wrong.writelines(f'Исправьте ошибки в исходном файле и запустите конвертер заново\n')
            logger.info('Файл успешно создан: %s')
        except Exception as e:
            logger.exception('Ошибка при записи файла: %s', e)
if __name__ == '__main__':
    for indx in range(number_of_files):
        main(src=input_files[indx], tgt=output_files[indx])
