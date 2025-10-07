"""
Декодер библиографических записей из html страниц e-Library в таблицу Excel

@author: Andrey Gasilin

Created: 03.01.2025
Last updated: 23.09.2025

"""
# Импорт внешних модулей

import time
import pandas as pd
import xlsxwriter
from ya_trans import abstracts_translator
from ya_GPT import abstract_optimization_with_gpt
from add_keywords_new import keys_from_text
from multifile_import import get_files_in_folder
from correction_functions import (
    persons_correction,
    upper_sent,
    upper_review,
    upper_comma,
    upper_abb,
    delete_tag,
    change_hyphen,
    change_quotation)
from add_categories import add_main_category

# Счётчики

counter = 1
index = 0
index_of_list = 0

# Списки

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

# Переменные паттернов

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


# Тех. переменные

title = ''
journal = ''
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
optimized_abstract = ''
a_keywords_as_string = ''
path_to_the_source_file = 'files_to_proceed/Sociological_review/2020/2'
path_to_the_target_file = 'files_for_editing/Sociological_review/Sociological_review_2020_2.xlsx'

# Импортируем данные из таблицы журналов

journal_list_df = pd.read_excel('journal_list_25.07.xlsx')

# Импортируем файлы из исходной папки

files = get_files_in_folder(path_to_the_source_file)
number_of_files = len(files)

print(f"Подождите, идёт обработка!")
start_time = time.time() # Включение таймера

# Цикл перебора файлов

for idx in range(number_of_files):
    with open(files[idx], 'r', encoding='UTF-8') as fl:
        strings = fl.readlines()

    # Авторы статьи
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

    # Заголовок статьи
    keys_from_title = []
    for string in strings:
        if title_pattern in string:
            first_word = string.find(title_pattern)
            second_word = string.find(title_end_pattern)
            start = first_word + title_start_shift
            title = string[start:second_word]
            keys_from_title = keys_from_text(title)
            title = title.capitalize()
            title = persons_correction(title)
            title = upper_sent(title)
            title = upper_review(title)
            title = upper_abb(title)
            title = upper_comma(title)
            title = delete_tag(title)
            title = change_hyphen(title)
            title = change_quotation(title)

    # Название журнала
    for string in strings:
        if journal_pattern in string:
            first_word = string.find(journal_pattern)
            second_word = string.find(journal_end_pattern)
            start = first_word + journal_start_shift
            journal = string[start:second_word]

    # Данные журнала
    rows_count = len(journal_list_df)
    for row in range(rows_count):
        elibrary_name = journal_list_df.at[row, 'e-library_name']
        if '/' in elibrary_name:
            splitter_position = elibrary_name.find('/')
            rus_elibrary_name = elibrary_name[:splitter_position]
            eng_elibrary_name = elibrary_name[(splitter_position + 1):]
        else:
            rus_elibrary_name = elibrary_name
            eng_elibrary_name = elibrary_name
        if ((journal == rus_elibrary_name) or
            (journal == eng_elibrary_name) or
            (journal == journal_list_df.at[row, 'journal']) or
            (journal == journal_list_df.at[row, 'journal_eng'])):
            journal = journal_list_df.at[row, 'journal']
            journal_eng = journal_list_df.at[row, 'journal_eng']
            founder = journal_list_df.at[row, 'founder']
            ISSN = journal_list_df.at[row, 'ISSN']
            journal_keyword = journal_list_df.at[row, 'journal_keyword']
            short_name = journal_list_df.at[row, 'short_name']
            founder_city =  journal_list_df.at[row, 'city']
            journal_type =  journal_list_df.at[row, 'type']
            serial_number = journal_list_df.at[row, 'serial_number']
            journal_category = journal_list_df.at[row, 'journal_category']
            break
    if journal == journal_eng:
        journal_eng = ''

    # Год
    year = ''
    for string in strings:
        if year_pattern in string:
            first_word = string.find(year_pattern)
            second_word = string.find(year_end_pattern)
            year = string[first_word + year_start_shift:second_word]

    # Том
    volume = ''
    for string in strings:
        if volume_pattern in string:
            first_word = string.find(volume_pattern)
            second_word = string.find(volume_end_pattern)
            volume = string[first_word + volume_start_shift:second_word]

    # Номер
    issue = ''
    for string in strings:
        if issue_pattern in string:
            first_word = string.find(issue_pattern)
            second_word = string.find(issue_end_pattern)
            issue = string[first_word + issue_start_shift:second_word]
            issue = issue.replace('&nbsp;', ' ')

    # Страницы
    pages = ''
    for string in strings:
        if pages_pattern in string:
            first_word = string.find(pages_pattern)
            second_word = string.find(pages_end_pattern)
            pages = string[first_word + pages_start_shift:second_word]

    # Язык
    lang = ''
    for string in strings:
        if lang_pattern in string:
            first_word = string.find(lang_pattern)
            second_word = string.find(lang_end_pattern)
            lang = string[first_word + lang_start_shift:second_word]

    # Аннотация
    abstract = ''
    optimized_abstract = ''
    keys_from_abstract = []
    for string in strings:
        if abstract_pattern in string:
            first_word = string.find(abstract_pattern)
            second_word = string.find(abstract_end_pattern)
            if first_word != -1 and second_word != -1:
                start = first_word + abstract_start_shift
                abstract = string[start:second_word]
                if lang in ['английский', 'французский', 'немецкий']:
                    abstract = abstracts_translator(abstract)
                keys_from_abstract = keys_from_text(abstract)
                if abstract:
                    optimized_abstract = abstract_optimization_with_gpt(abstract) or ''

    # URL
    URL = ''
    for string in strings:
        if URL_pattern in string:
            first_word = string.find(URL_pattern)
            second_word = string.find(URL_end_pattern)
            if first_word != -1 and second_word != -1:
                URL = string[first_word + URL_start_shift:second_word]

    # DOI
    DOI = ''
    for string in strings:
        if DOI_pattern in string:
            first_word = string.find(DOI_pattern)
            second_word = string.find(DOI_end_pattern)
            if first_word != -1 and second_word != -1:
                DOI = string[first_word + DOI_start_shift:second_word]

    # Авторские ключевые слова
    keys_from_a_keys = []
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
    a_keywords_as_string = ", ".join(a_keywords)

    # Нормализация ключевых слов
    keys_from_a_keys = keys_from_text(a_keywords_as_string)

    # Объединяем ключевые слова, сохраняем порядок и убираем дубликаты
    final_keywords = list(dict.fromkeys(keys_from_title + keys_from_a_keys + keys_from_abstract))

    # Рубрика
    if journal_category == 'A02':
        journal_category = add_main_category(final_keywords)

    # Преобразование ключей в строки
    final_keywords = final_keywords[:10]
    keyword_string = ', '.join(final_keywords)
    if journal_keyword in final_keywords:
        keyword_string = journal_keyword

    # Добавление в списки
    author_list.append(authors_str)
    category_list.append(journal_category)
    title_list.append(title)
    journal_list.append(journal)
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

# Название выходного файла
workbook = xlsxwriter.Workbook(path_to_the_target_file)

# Формат переноса текста
text_format = workbook.add_format({"text_wrap": True})
worksheet = workbook.add_worksheet()

# Названия колонок таблицы
worksheet.write(0, 0, 'author')
worksheet.write(0, 1, 'category')
worksheet.write(0, 2, 'title')
worksheet.write(0, 3, 'keywords')
worksheet.write(0, 4, 'abstract')
worksheet.write(0, 5, 'journal')
worksheet.write(0, 6, 'journal_eng')
worksheet.write(0, 7, 'year')
worksheet.write(0, 8, 'volume')
worksheet.write(0, 9, 'issue')
worksheet.write(0, 10, 'pages')
worksheet.write(0, 11, 'URL')
worksheet.write(0, 12, 'DOI')
worksheet.write(0, 13, 'ISSN')
worksheet.write(0, 14, 'lang')
worksheet.write(0, 15, 'founder')
worksheet.write(0, 16, 'type')
worksheet.write(0, 17, 'serial')
worksheet.write(0, 18, 'review_author')
worksheet.write(0, 19, 'review_title')
worksheet.write(0, 20, 'review_output_data')

# Регулировка ширины колонок
worksheet.set_column(0, 0, 20)
worksheet.set_column(1, 1, 20)
worksheet.set_column(2, 2, 70)
worksheet.set_column(3, 3, 20)
worksheet.set_column(4, 4, 70)
worksheet.set_column(5, 5, 30)
worksheet.set_column(6, 6, 30)
worksheet.set_column(7, 7, 5)
worksheet.set_column(8, 8, 5)
worksheet.set_column(9, 9, 5)
worksheet.set_column(10, 10, 8)
worksheet.set_column(11, 11, 22)
worksheet.set_column(12, 12, 35)
worksheet.set_column(13, 13, 10)
worksheet.set_column(14, 14, 10)
worksheet.set_column(15, 15, 30)
worksheet.set_column(16, 16, 20)
worksheet.set_column(17, 17, 20)
worksheet.set_column(18, 18, 20)
worksheet.set_column(19, 19, 50)
worksheet.set_column(20, 20, 50)

# Заполнение таблицы
for i in range(number_of_files):
    worksheet.write(i+1, 0, author_list[i], text_format)
    worksheet.write(i+1, 1, category_list[i])
    worksheet.write(i+1, 2, title_list[i], text_format)
    worksheet.write(i+1, 3, keywords_list[i], text_format)
    worksheet.write(i+1, 4, abstract_list[i], text_format)
    worksheet.write(i+1, 5, journal_list[i])
    worksheet.write(i+1, 6, journal_eng_list[i])
    worksheet.write(i+1, 7, year_list[i])
    worksheet.write(i+1, 8, volume_list[i])
    worksheet.write(i+1, 9, issue_list[i])
    worksheet.write(i+1, 10, pages_list[i])
    worksheet.write(i+1, 11, URL_list[i])
    worksheet.write(i+1, 12, DOI_list[i])
    worksheet.write(i+1, 13, ISSN_list[i])
    worksheet.write(i+1, 14, lang_list[i])
    worksheet.write(i+1, 15, founder_list[i], text_format)
    worksheet.write(i+1, 16, journal_type_list[i])
    worksheet.write(i+1, 17, serial_number_list[i])

workbook.close()

# Таймер
end_time = time.time()
period = end_time - start_time
minutes = int(period // 60)
seconds = int(period - minutes * 60)

print(f"Спасибо за ожидание!")
print(f"Количество обработанных документов: {number_of_files}, время исполнения: {minutes}:{seconds}")
print(f"Результат обработки см. по адресу: {path_to_the_target_file}")
