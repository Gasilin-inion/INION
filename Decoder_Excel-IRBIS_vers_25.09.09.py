# -*- coding: utf-8 -*-

# Декодер библиографических записей из таблицы Excel в формат ИРБИС 64
# ! Адаптировано под Linux !
# Версия с автоматической генерацией шифра хранения на основе данных об электронном журнале.
# 02/05/25 - В версию добавлена поддержка автоматического распознавания и индексации рецензий
"""
Created on Fri Jan 10 10:44:19 2025

@author: Gasilin Andrey
"""

# Задаём неизменяемые строковые "переменные"
field_102 = '#102: RU\n'
field_181 = '#181: ^Ai\n'
field_182 = '#182: ^An\n'
field_610 = '#610: '
field_905 = '#905: ^22^B1^D3^M1^S1\n'
field_919 = '#919: ^rus^N02^KPSBO\n'
field_920 = '#920: ASP\n'
field_999 = '#999: 0000000\n'
separator = '*****\n'
list_of_documents = ''
path_to_the_source_file = '/home/user/Desktop/eLibrary_IRBIS/files_for_editing/Вопросы_философии/Вопросы_философии_2024_8.xlsx'
path_to_the_target_file = '/home/user/Desktop/eLibrary_IRBIS/files_for_import_in_IRBIS/Вопросы_философии/Вопросы_философии_2024_8.txt'

# Импортируем модуль даты и времени
import datetime
# Выводим теущую дату и переворачиваем её от года к числу
current_date = datetime.date.today().isoformat()
# Превращаем дату в строку и удаляем лишние дефисы
date = str(current_date)
date = date.replace('-', '')

# Импорт таблицы
import pandas as pd
data_frame = pd.read_excel(path_to_the_source_file)
number_of_strings = len(data_frame)
counter = 1
index = 0
for counter in range(number_of_strings):
    # Задаём изменяемые строковые переменные
    field_19 = '#19: ^X0^A6 DOI^B' # Поле DOI
    field_101 = '#101: ' # Поле языка публикации
    field_200 = '#200: ' # Поле заголовка и автора публикации
    field_203 = '#203: ' # Поле типа доступа
    field_331 = '#331: ' # Поле аннотации
    field_463 = '#463: ' # Поле сведений об издании (название журнала, год, номер, диапазон страниц)
    field_470 = '#470: ^0Рец. на кн.'
    field_690 = '#690: ^L' # Поле рубрикатора АИСОН
    field_700 = '#700: ' # Поле первого/основного автора
    field_701 = '#701: ' # Поле соавтора
    field_900 = '#900: ' # Поле вида документа
    field_951 = '#951: ' # Поле ссылки на внешний объект
    field_963 = '#963: ' # Поле сведений об ответственности    
    field_964 = '#964: ' # Поле индекса ГРНТИ
    field_965 = '' # Поле дескрипторов
    review_marker = 0
    review_author = 'nan'
    # Извлекаем DOI статьи и записываем в аргумент
    argument_19 = str(data_frame.at[index, 'DOI'])
    if (argument_19 != 'nan'):
        field_19 = field_19 + argument_19 + '\n'
    else:
        field_19 = '\n'
    # Извлекаем язык публикации. Если язык английский, передаём аргументу значение
    # 'eng', в остальных случаях - 'rus'
    lang = data_frame.at[index, 'lang']
    if lang == 'английский':
        argument_101 = 'eng'
    else:
        argument_101 = 'rus'
    field_101 = field_101 + argument_101 + '\n'

    # Извлекаем автора(ов) публикации
    authors_str = str(data_frame.at[index, 'author'])
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
    # Извлекаем заголовок
    title = data_frame.at[index, 'title']   
    # Формируем аргумент поля 200 из заголовка и авторов
    # Прописываем разные варианты для нескольких авторов
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
    # Извлекаем аннотацию и записываем в аргумент
    argument_331 = str(data_frame.at[index, 'abstract'])
    if (argument_331 != 'nan') and (argument_331 != 'None'):
        field_331 = field_331 + argument_331 + '\n'
    else:
        field_331 = '\n'
    # Извлекаем рубрику АИСОН и записываем в аргумент
    category = str(data_frame.at[index, 'category'])
    # Проверка на соответствие формату
    from check_functions import cat_check
    write_cat = cat_check(category)
    if write_cat != 1:
        print(category + ' is wrong category!')
        category = input('Input write one: ')
        print('Now ' + category + ' is write!')    
    field_690 = field_690 + category + '\n'
    # Задаём ключ для сборки БУ (поле 610)
    if ('A02' in category): # В случае философской специальности
        current_date = datetime.date.today()
        if current_date.month == 6 and current_date.day <= 15:
            BU_number = '02 #07 2025'
        if current_date.month == 7 and current_date.day <= 15:
            BU_number = '02 #08 2025'
        if (current_date.month == 8 and current_date.day <= 15) or (current_date.month == 7 and current_date.day > 15):
            BU_number = '02 #09 2025'
        if (current_date.month == 9 and current_date.day <= 20) or (current_date.month == 8 and current_date.day > 15):
            BU_number = '02 #10 2025'
        if (current_date.month == 10 and current_date.day <= 20) or (current_date.month == 9 and current_date.day > 20):
            BU_number = '02 #11 2025'
        if (current_date.month == 11 and current_date.day <= 20) or (current_date.month == 10 and current_date.day > 20):
            BU_number = '02 #12 2025'
        if (current_date.month == 12 and current_date.day <= 20) or (current_date.month == 11 and current_date.day > 20):
            BU_number = '02 #01 2026'
    else:                   # В случае нефилософской специальности
        BU_number = 'online_journals_archive'
    field_610 = '#610: ' + BU_number + '\n'

    # Формируем аргумент поля 700 (основной автор)
    argument_700 = ''
    if (not ';' in authors_str) and (',' in authors_str):                          # Если нет соавторов, но есть аббревиатура
        argument_700 = '^A' + author_1_xx[0] + '^B' + author_1_xx[1] + '\n'
    elif (not ';' in authors_str) and (not ',' in authors_str):                     # Если нет соавторов и аббревиатуры
        argument_700 = '^A' + authors_str + '\n'
    field_700 = field_700 + argument_700

    # Формируем аргумент поля 701 (соавтор), в случае наличия второго автора
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
    # Извлекаем URL и записываем в аргумент
    argument_951 = str(data_frame.at[index, 'URL'])
    field_951 = field_951 + '^I' + argument_951 + '^H05\n'
    # Извлекаем ISSN журнала и записываем в аргумент
    ISSN_num = str(data_frame.at[index, 'ISSN'])
    # Извлекаем сведения об учредителе
    founder = str(data_frame.at[index, 'founder'])
    # Формируем аргумент поля 963
    argument_963 = '^F' + founder + '^I' + ISSN_num
    field_963 = field_963 + argument_963 + '\n'
    # Извлекаем заглавие журнала
    journal = str(data_frame.at[index, 'journal'])
    # Извлекаем параллельное заглавие журнала
    journal_eng = str(data_frame.at[index, 'journal_eng'])
    if journal_eng == 'nan':
        journal_eng = ''
    # Извлекаем год публикации
    year = str(data_frame.at[index, 'year'])
    # Извлекаем том журнала
    volume = str(data_frame.at[index, 'volume'])
    # Извлекаем номер журнала
    issue = str(data_frame.at[index, 'issue'])
    # Извлекаем диапазон страниц
    pages = str(data_frame.at[index, 'pages'])
   # Извлекаем шифр хранения
    serial = str(data_frame.at[index, 'serial'])
    # Формируем шифр публикации при наличии метки тома
    if (volume != 'nan'):
        cipher = (serial + '/' + year + '/' + volume + '/' + issue)
        argument_463 = ('^C' + journal + '^J' + year + '^VТ. ' + volume + '^H№ ' + issue
                    + '^S' + pages + '^X' + journal_eng + '^W' + cipher + '\n')
    # Или при его отсутствии
    elif (volume == 'nan'):
        cipher = (serial + '/' + year + '/' + issue)
        argument_463 = ('^C' + journal + '^J' + year + '^H' + issue
                    + '^S' + pages + '^X' + journal_eng + '^W' + cipher + '\n')
    # Записываем все данные о выпуске в аргумент при наличии тома
    field_463 = field_463 + argument_463
    # Проверяем, не является ли статья рецензией на книгу,
    # при положительном результате проверки извлекаем сведения об ответственности и
    # выходные данные
    review_author =  str(data_frame.at[index, 'review_author'])
    if (review_author != 'nan'):
        review_marker = 1
    if (review_marker == 1):
        review_title = str(data_frame.at[index, 'review_title'])
        review_output_data = str(data_frame.at[index, 'review_output_data'])
    # Извлечённые аргументы записываются в соответствующие подполя поля 470
        argument_470 = '^C' + review_title + '^D' + review_output_data + '^F' + review_author
        field_470 = field_470 + argument_470 + '\n'
    # Извлекаем тип публикации
    document_type = str(data_frame.at[index, 'type'])
    if (document_type == 'online') and (review_marker == 0): # Происываем тип доступа и тип публикации
        argument_203 = '^AТекст^Cэлектронный\n'
        argument_900 = '^Tl2\n'
    elif (document_type == 'online') and (review_marker == 1): # Вариант рецензии
        argument_203 = '^AТекст^Cэлектронный\n'
        argument_900 = '^Cd2^Tl2\n'
    else:                                                      # Вариант бумажной публикации
        argument_203 = '^AТекст^Cнепосредственный\n'
        argument_900 = '^B08\n'
    field_203 = field_203 + argument_203
    field_900 = field_900 + argument_900
    # Формируем индекс ГРНТИ на основе рубрики АИСОН
    argument_964 = category[1:6]
    field_964 = field_964 + argument_964 + '\n'
    # Извлекаем ключи
    keywords_str = str(data_frame.at[index, 'keywords'])
    keywords = keywords_str.split(', ')
    # Записываем повторения поля 965 при условии наличия ключей
    for keyword in keywords:
        field_965 = field_965 + '#965: ' + keyword + '\n'
    if (keywords_str == ''):
        field_965 = '\n'
    # Записываем все поля в одну переменную
    if (review_marker == 0) and (document_type == 'online'):                        # Вариант электронного журнала без признака рецензии
        document = (field_19 + field_101 + field_102 + field_181 + field_182 
          + field_200 + field_203 + field_331 + field_463 + field_610 + field_690
          + field_700 + field_701 + field_900 + field_905
          + field_919 + field_920 + field_951 + field_963 + field_964 + field_965
          + field_999 + separator)
    elif (review_marker == 1) and (document_type == 'online'):                      # Вариант электронного журнала с признаком рецензии
        document = (field_19 + field_101 + field_102 + field_181 + field_182
          + field_200 + field_203 + field_331 + field_463 + field_470 + field_610
          + field_690 + field_700 + field_701 + field_900 + field_905
          + field_919 + field_920 + field_951 + field_963 + field_964 + field_965
          + field_999 + separator)
    else:                                                                           # Вариант бумажного журнала
        document = (field_19 + field_101 + field_102 + field_181 + field_182 
          + field_200 + field_203 + field_331 + field_463 + field_610 + field_690
          + field_700 + field_701 + field_900 + field_905
          + field_919 + field_920 + field_963 + field_964 + field_965
          + field_999 + separator)
    document = document.replace('\n\n','\n')
    list_of_documents = list_of_documents + document
    counter += 1
    index += 1

# Создаём файл для записи результатов
file = open(path_to_the_target_file, 'w', encoding='utf-8')
file.writelines(list_of_documents)
file.close()

print('Файл успешно создан!')
print('Результат см. по адресу:')
print(path_to_the_target_file)
