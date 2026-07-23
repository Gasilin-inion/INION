"""
Конвертер библиографических записей из формата *.html в таблицу Excel

@author: Andrey Gasilin

Created: 03.01.2025
Last updated: 17.07.2026

"""
# Импорт внешних модулей

import sys
import json
import pandas as pd
import importlib.util
import xlsxwriter
from pathlib import Path
from datetime import datetime

# Импортируем файл конфигурации путей
from src.utils.config_path import set_config #type: ignore
config = set_config()

# Берём значение из словаря
EDITABLE_XLSX_DIR = config["files_to_edit"]

# Назначаем счётчики

counter = 1
index = 0
index_of_list = 0

# Назначаем переменные паттернов

author_pattern = '<b><font color=#00008f>'
author_start_shift = 23
author_end_pattern = '.</font></b>'
title_pattern = '<title>'
title_start_shift = 7
title_end_pattern = '</title>'
journal_pattern = 'Содержание выпусков этого журнала">'
journal_start_shift = 35
journal_end_pattern = '</a>'
year_pattern = 'Год:'
year_start_shift = 30
year_end_pattern = '</font>'
volume_pattern = 'Том:'
volume_start_shift = 30
volume_end_pattern = '</font>'
issue_pattern = 'Содержание выпуска">'
issue_start_shift = 20
issue_end_pattern = '</a>'
pages_pattern = 'Страницы:'
pages_start_shift = 35
pages_end_pattern = '</font>'
lang_pattern = 'Язык:'
lang_start_shift = 31
lang_end_pattern = '</font>'
abstract_pattern = '<div id="abstract1"'
abstract_start_shift = 133
abstract_end_pattern = '</div>'
keyword_pattern = '<a href="keyword_items.asp?id='
keyword_start_shift = 38
keyword_end_pattern ="</a>"
URL_pattern = 'meta property="og:url"'
URL_start_shift = 32
URL_end_pattern = '" />'
DOI_pattern = 'name="doi"'
DOI_start_shift = 20
DOI_end_pattern = '">'


# Назначаем технические переменные

title = ''
journal = ''
journal_ru = ''
journal_eng = ''
ISSN = ''
founder = ''
journal_keyword = ''
short_name = ''
elibrary_name = ''
rus_elibrary_name = ''
eng_elibrary_name = ''
founder_city = ''
journal_type = ''
serial_number = ''
journal_category = ''
volume = ''
abstract = ''
full_abstract = ''
optimized_abstract = ''
a_keywords_as_string = ''
file_name = ''

# Импортируем выходные данные журналов

journal_list_path = config["journal_list"]
journal_list_df = pd.read_json(journal_list_path)

def convert_html_to_excel(files):

    # Формируем списки

    author_list = []
    category_list = []
    title_list = []
    journal_list = []
    journal_eng_list = []
    year_list = []
    volume_list = []
    issue_list = []
    pages_list = []
    abstract_list = []
    keys_from_title = []
    keys_from_a_keys = []
    keys_from_abstract = []
    a_keywords = []
    keywords_list = []
    additional_keywords = []
    URL_list = []
    DOI_list = []
    ISSN_list = []
    lang_list = []
    founder_list = []
    short_name_list = []
    journal_type_list = []
    serial_number_list = []

    # Определяем количество загруженных файлов
    number_of_files = len(files)

    # Перебираем файлы из списка

    for idx in range(number_of_files):
        with open(files[idx], 'r', encoding='UTF-8') as fl:
            strings = fl.readlines()

        # Блок автора
        authors = []
        counter = 1
        for string in strings:
            if author_pattern in string:
                authors_num = string.count(author_pattern)
                while counter <= authors_num:
                    first_point = string.find(author_pattern)
                    second_point = string.find(author_end_pattern)
                    start = first_point + author_start_shift
                    end = second_point + 1
                    full_name = string[start:end]
                    author = full_name.replace('&nbsp;', ', ')
                    author = author.title()
                    authors.append(author)
                    string = string[(end + 12):]
                    counter += 1
        authors_str = ' ; '.join(authors)

        # Блок заголовка
        for string in strings:
            if title_pattern in string:
                first_word = string.find(title_pattern)
                second_word = string.find(title_end_pattern)
                start = first_word + title_start_shift
                title = string[start:second_word]
                
                # Выделяем ключевые слова
                add_keywords = config["add_keywords"]
                spec = importlib.util.spec_from_file_location("add_keywords", add_keywords)
                module = importlib.util.module_from_spec(spec)
                sys.modules["add_keywords"] = module
                spec.loader.exec_module(module)
                keys_from_title = module.keys_from_text(title)
                title = title.capitalize()

                # Импортируем модуль автокоррекции
                corrections = config["correction"]
                spec = importlib.util.spec_from_file_location("correction_functions", corrections)
                module = importlib.util.module_from_spec(spec)
                sys.modules["correction_functions"] = module
                spec.loader.exec_module(module)

                # Запускаем функции модуля автокоррекции
                title = module.persons_correction(title)
                title = module.upper_sent(title)
                title = module.upper_review(title)
                title = module.upper_abb(title)
                title = module.upper_comma(title)
                title = module.delete_tag(title)
                title = module.change_hyphen(title)
                title = module.change_quotation(title)

        # Блок названия журнала
        for string in strings:
            if journal_pattern in string:
                first_word = string.find(journal_pattern)
                second_word = string.find(journal_end_pattern)
                start = first_word + journal_start_shift
                journal = string[start:second_word]

        # Загрузка данных журнала из journal_list
        rows_count = len(journal_list_df)
        for row in range(rows_count):
            if ((journal == journal_list_df.at[row, 'e-library_name']) or
                (journal == journal_list_df.at[row, 'journal']) or
                (journal == journal_list_df.at[row, 'journal_eng']) or
                (journal == journal_list_df.at[row, 'journal_eng_2'])):
                journal_ru = journal_list_df.at[row, 'journal']
                journal_eng = journal_list_df.at[row, 'journal_eng']            
                founder = journal_list_df.at[row, 'founder']
                ISSN = journal_list_df.at[row, 'ISSN']
                journal_keyword = journal_list_df.at[row, 'journal_keyword']
                short_name = journal_list_df.at[row, 'short_name']
                founder_city =  journal_list_df.at[row, 'city']
                journal_type =  journal_list_df.at[row, 'type']
                serial_number = journal_list_df.at[row, 'serial_number']
                journal_category = journal_list_df.at[row, 'journal_category']
                if journal_ru == journal_eng:
                    journal_eng = ''
                break              
        # Блок года
        year = ''
        for string in strings:
            if year_pattern in string:
                first_word = string.find(year_pattern)
                second_word = string.find(year_end_pattern)
                year = string[first_word + year_start_shift:second_word]

        # Блок тома
        volume = ''
        for string in strings:
            if volume_pattern in string:
                first_word = string.find(volume_pattern)
                second_word = string.find(volume_end_pattern)
                volume = string[first_word + volume_start_shift:second_word]

        # Блок номера
        issue = ''
        for string in strings:
            if issue_pattern in string:
                first_word = string.find(issue_pattern)
                second_word = string.find(issue_end_pattern)
                issue = string[first_word + issue_start_shift:second_word]
                issue = issue.replace('&nbsp;', ' ')

        # Блок диапазона страниц
        pages = ''
        for string in strings:
            if pages_pattern in string:
                first_word = string.find(pages_pattern)
                second_word = string.find(pages_end_pattern)
                pages = string[first_word + pages_start_shift:second_word]

        # Блок языка
        lang = ''
        for string in strings:
            if lang_pattern in string:
                first_word = string.find(lang_pattern)
                second_word = string.find(lang_end_pattern)
                lang = string[first_word + lang_start_shift:second_word]

        # Блок аннотации
        abstract = ''
        optimized_abstract = ''
        if journal_category == 'A02':
            for string in strings:
                if abstract_pattern in string:
                    first_word = string.find(abstract_pattern)
                    second_word = string.find(abstract_end_pattern)
                    if first_word != -1 and second_word != -1:
                        start = first_word + abstract_start_shift
                        abstract = string[start:second_word]
                        
                        # Переводим аннотацию, если она не на русском

                        if lang in ['английский', 'французский', 'немецкий']:
                            abstracts_translator = config["translation"]
                            spec = importlib.util.spec_from_file_location("ya_trans", abstracts_translator)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules["ya_trans"] = module
                            spec.loader.exec_module(module)
                            abstract = module.abstracts_translator(abstract)
                        
                        # Подбираем ключи на основе аннотации

                        add_keywords = config["add_keywords"]
                        spec = importlib.util.spec_from_file_location("add_keywords", add_keywords)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules["add_keywords"] = module
                        spec.loader.exec_module(module)
                        keys_from_abstract = module.keys_from_text(abstract)
                        
                        if abstract:
                            # Импортируем модуль оптимизации аннотации посредством YandexGPT 
                            translation = config["AI_processing"]
                            spec = importlib.util.spec_from_file_location("ya_GPT", translation)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules["ya_GPT"] = module
                            spec.loader.exec_module(module)
                            optimized_abstract = module.abstract_optimization_with_gpt(abstract) or ''
                            if 'Я не могу обсуждать эту тему' in optimized_abstract:
                                optimized_abstract = ''
                        
        # Усеченный вариант обработки для специальностей 04, 10 и 13
        elif (journal_category == 'A04') or (journal_category == 'A10') or (journal_category == 'A13'):
            for string in strings:
                if abstract_pattern in string:
                    first_word = string.find(abstract_pattern)
                    second_word = string.find(abstract_end_pattern)
                    if first_word != -1 and second_word != -1:
                        start = first_word + abstract_start_shift
                        abstract = string[start:second_word]
                        optimized_abstract = abstract[:500]
                        last_point = optimized_abstract.rfind('.')
                        optimized_abstract = optimized_abstract[:(last_point + 1)]
        else:
            optimized_abstract = ''

        # Блок URL
        URL = ''
        for string in strings:
            if URL_pattern in string:
                first_word = string.find(URL_pattern)
                second_word = string.find(URL_end_pattern)
                if first_word != -1 and second_word != -1:
                    URL = string[first_word + URL_start_shift:second_word]

        # Блок DOI
        DOI = ''
        for string in strings:
            if DOI_pattern in string:
                first_word = string.find(DOI_pattern)
                second_word = string.find(DOI_end_pattern)
                if first_word != -1 and second_word != -1:
                    DOI = string[first_word + DOI_start_shift:second_word]

        # Блок анализа авторских ключевых слов
        final_keywords = []
        a_keywords = []  # Инициализация списка ключевых слов

        if journal_category == 'A02':
            for string in strings:
                if keyword_pattern in string:
                    first_word = string.find(keyword_pattern)
                    second_word = string.find(keyword_end_pattern)
                    if first_word != -1 and second_word != -1:
                        a_keyword = string[first_word + keyword_start_shift:second_word]
                        a_keyword = a_keyword.replace('>', '')
                        a_keyword = a_keyword.replace('"', '')
                        a_keyword = a_keyword.lower()
                        a_keywords.append(a_keyword)

            # Формируем строку из ключевых слов только если они есть
            if a_keywords:
                a_keywords_as_string = ", ".join(a_keywords)
            else:
                a_keywords_as_string = ""  # Значение по умолчанию при отсутствии ключевых слов

            # Отсеиваем ненормированные ключевые слова
            try:
                add_keywords = config["add_keywords"]
                spec = importlib.util.spec_from_file_location("add_keywords", add_keywords)
                module = importlib.util.module_from_spec(spec)
                sys.modules["add_keywords"] = module
                spec.loader.exec_module(module)

                # Проверяем наличие функции keys_from_text
                if hasattr(module, 'keys_from_text'):
                    keys_from_a_keys = module.keys_from_text(a_keywords_as_string)
                else:
                    keys_from_a_keys = []  # Значение по умолчанию, если функция отсутствует
            except (FileNotFoundError, ImportError) as e:
                print(f"Ошибка при импорте модуля add_keywords: {e}")
                keys_from_a_keys = []  # Значение по умолчанию при ошибке импорта

            # Объединяем ключевые слова, сохраняем порядок и убираем дубликаты
            final_keywords = list(dict.fromkeys(keys_from_title + keys_from_a_keys + keys_from_abstract))
        else:
            final_keywords.append(journal_keyword)


        # Подбор рубрики по философии (эксперементальная функция)
        if journal_category == 'A02':
            add_category = config["add_categories"]
            spec = importlib.util.spec_from_file_location("add_categories", add_category)
            module = importlib.util.module_from_spec(spec)
            sys.modules["add_categories"] = module
            spec.loader.exec_module(module)
            journal_category = module.add_main_category(final_keywords)

        # Преобразование ключей в строки
        final_keywords = final_keywords[:10]
        keyword_string = ', '.join(final_keywords)
        if journal_keyword in final_keywords:
            keyword_string = journal_keyword

        # Добавление всех параметров в списки
        author_list.append(authors_str)
        category_list.append(journal_category)
        title_list.append(title)
        journal_list.append(journal_ru)
        journal_eng_list.append(journal_eng)
        year_list.append(year)
        volume_list.append(volume)
        issue_list.append(issue)
        pages_list.append(pages)
        abstract_list.append(optimized_abstract)
        URL_list.append(URL)
        DOI_list.append(DOI)
        ISSN_list.append(ISSN)
        lang_list.append(lang)
        founder_list.append(founder)
        keywords_list.append(keyword_string)
        short_name_list.append(short_name)
        journal_type_list.append(journal_type)
        serial_number_list.append(serial_number)

    # Формирование дата-фрейма
    articles_pd = pd.DataFrame({
    'author': author_list,
    'category': category_list,
    'title': title_list,
    'keywords': keywords_list,
    'abstract': abstract_list,
    'journal': journal_list,
    'journal_eng': journal_eng_list,
    'short_name': short_name_list,
    'year': year_list,
    'volume': volume_list,
    'issue': issue_list,
    'pages': pages_list,    
    'URL': URL_list,
    'DOI': DOI_list,
    'ISSN': ISSN_list,
    'lang': lang_list,
    'founder': founder_list,
    'type': journal_type_list,
    'serial': serial_number_list
    })

    return articles_pd

# Функция преобразует дата-фрейм в таблицу в формате *.xlsx
def data_frame_to_workbook(data_frame):
    
    # Формируем название файла
    journal_name = data_frame.at[1, 'short_name']
    year = data_frame.at[1, 'year']
    volume = data_frame.at[1, 'volume']
    issue = data_frame.at[1, 'issue']
    datestamp = datetime.now().strftime("gen_%Y.%m.%d") # Маркер времени формирования
    if (volume != '') and (volume != 'NaN') and (volume != 'none'):
        file_name = f'{EDITABLE_XLSX_DIR}{journal_name}_{year}_{volume}_{issue}_{datestamp}.xlsx'
    else:
        file_name = f'{EDITABLE_XLSX_DIR}{journal_name}_{year}_{issue}_{datestamp}.xlsx'

    # Формируем выходной файл в формате *.xlsx

    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    data_frame.to_excel(writer, sheet_name='List of articles', index=False)

    # Форматируем таблицу
    workbook = writer.book
    worksheet = writer.sheets['List of articles']
    text_format = workbook.add_format({"text_wrap": True})

    worksheet.set_column('A:A', None, text_format)
    worksheet.set_column('C:C', None, text_format)
    worksheet.set_column('D:D', None, text_format)
    worksheet.set_column('E:E', None, text_format)
    worksheet.set_column('P:P', None, text_format)

    # Назначаем названия колонкам таблицы
    worksheet.write(0, 0, 'author')
    worksheet.write(0, 1, 'category')
    worksheet.write(0, 2, 'title')
    worksheet.write(0, 3, 'keywords')
    worksheet.write(0, 4, 'abstract')
    worksheet.write(0, 5, 'journal')
    worksheet.write(0, 6, 'journal_eng')
    worksheet.write(0, 7, 'short_name')
    worksheet.write(0, 8, 'year')
    worksheet.write(0, 9, 'volume')
    worksheet.write(0, 10, 'issue')
    worksheet.write(0, 11, 'pages')
    worksheet.write(0, 12, 'URL')
    worksheet.write(0, 13, 'DOI')
    worksheet.write(0, 14, 'ISSN')
    worksheet.write(0, 15, 'lang')
    worksheet.write(0, 16, 'founder')
    worksheet.write(0, 17, 'type')
    worksheet.write(0, 18, 'serial')
    worksheet.write(0, 19, 'review_author')
    worksheet.write(0, 20, 'review_title')
    worksheet.write(0, 21, 'review_output_data')

    # Регулируем ширину колонок
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(1, 1, 20)
    worksheet.set_column(2, 2, 70)
    worksheet.set_column(3, 3, 20)
    worksheet.set_column(4, 4, 70)
    worksheet.set_column(5, 5, 30)
    worksheet.set_column(6, 6, 30)
    worksheet.set_column(7, 7, 30)
    worksheet.set_column(8, 8, 5)
    worksheet.set_column(9, 9, 5)
    worksheet.set_column(10, 10, 5)
    worksheet.set_column(11, 11, 8)
    worksheet.set_column(12, 12, 22)
    worksheet.set_column(13, 13, 35)
    worksheet.set_column(14, 14, 10)
    worksheet.set_column(15, 15, 10)
    worksheet.set_column(16, 16, 30)
    worksheet.set_column(17, 17, 20)
    worksheet.set_column(18, 18, 20)
    worksheet.set_column(19, 19, 20)
    worksheet.set_column(20, 20, 50)
    worksheet.set_column(21, 21, 50)

    workbook.close()