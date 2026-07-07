"""
@name Модуль функций для автоматической коррекции заголовков

@author: Гасилин Андрей

Created on 30.01.2025
Updated on 24.01.2026

"""
import pandas as pd
import json

# Загрузка конфигурации, извлечение путей к авторитетным файлам
with open("./data/config/path_config.json", "r", encoding="utf-8") as pathfile:
    config_paths = json.load(pathfile)
    
path_to_facet = config_paths["facet"]

# Функция коррекции имён собственных

def persons_correction(sentence):


    a_facet = pd.read_json(path_to_facet)
    
    # Извлекаем столбцы как списки, приводим к строке и фильтруем NaN/None
    list_of_terms = [
        str(term) for term in a_facet['low_name'].dropna().tolist()
    ]
    list_of_corrected_terms = [
        str(corr) for corr in a_facet['up_name'].dropna().tolist()
    ]

    # Применяем замены: перебираем пары (low_name, up_name)
    for low_name, up_name in zip(list_of_terms, list_of_corrected_terms):
        if low_name in sentence:
            sentence = sentence.replace(low_name, up_name)

    return sentence

# Исправление строчных букв на заглавные в начале предложений

def upper_sent(title):
    if not title:
        return title

    # Список разделителей, после которых нужно капитализировать следующую букву
    delimiters = ['. ', '? ']
    
    for delimiter in delimiters:
        start = 0
        while True:
            # Ищем следующий разделитель начиная с позиции start
            pos = title.find(delimiter, start)
            if pos == -1:  # разделитель не найден
                break
            
            # Позиция буквы после разделителя (пропускаем пробел)
            letter_pos = pos + len(delimiter)
            
            
            # Проверяем, что буква существует (не выход за границы строки)
            if letter_pos < len(title):
                # Заменяем букву на заглавную
                title = (title[:letter_pos] + 
                        title[letter_pos].upper() +
                        title[letter_pos + 1:])
            
            # Сдвигаем начало поиска после обработанной буквы
            start = letter_pos + 1

    return title


# Перевод первой буквы слова "рецензия" в верхний регистр 
   
def upper_review(title):
    if (' рецензия' in title):
        title = title.replace(' рецензия', '. Рецензия')
        title = title.replace('..', '.')
        title = title.replace(':.', ':')
    if (' review' in title):
        title = title.replace(' review', '. Review')
        title = title.replace('..', '.')
        title = title.replace(':.', ':')
    return title

# Замена первой буквы заковыченной фразы на заглавную

def upper_comma(title):
    if not title:
        return title

    # Обработка кавычки в начале строки
    if title.startswith('"'):
        title = '"' + title[1].upper() + title[2:]

    # Обработка кавычек в середине строки (шаблон ' "')
    start = 0
    while True:
        pos = title.find(' "', start)
        if pos == -1:  # больше нет вхождений
            break
        
        letter_pos = pos + 2  # позиция буквы после ' "'
        
        # Проверяем, что буква существует (не выход за границы)
        if letter_pos < len(title):
            title = (title[:letter_pos] +
                   title[letter_pos].upper() +
                   title[letter_pos + 1:])
        
        start = letter_pos + 1  # продолжаем поиск после обработанной буквы

    return title
            
# Перевод аббревиатур в верхний регистр

def upper_abb(title):    
    start = 0
    end = len(title)
    number_of_points = title.count('.')
    for point_num in range(number_of_points):
        point = title.find('.', start, end)
        next_point = point + 1
        next_2_point = point + 2
        prew_2_point = point - 2
        letter_point = point - 1
        if point <= (end - 3):
            if (((title[next_point] == ' ') and (title[prew_2_point] == ' ')) or
                ((title[next_point] == ' ') and (title[prew_2_point] == '.')) or
                ((title[next_point] == ',') and (title[prew_2_point] == ' ')) or
                ((title[next_point] == '-') and (title[prew_2_point] == ' ')) or
                ((title[next_point] == ' ') and (title[prew_2_point] == '-')) or                 
                ((title[next_2_point] == '.') and (title[prew_2_point] == ' ')) or
                ((title[next_point] == ';') and (title[prew_2_point] == ' '))):
                letter = title[letter_point]
                letter = letter.upper()
                title = title[:letter_point] + letter + title[point:]
        start = next_point
    return title

# Удаление тега курсива <i> и </i>

def delete_tag(title):
    if ('<i>' in title):
        title = title.replace('<i>', '')
    if ('</i>' in title):
        title = title.replace('</i>', '')
    return title

# Замена дефиса на большое тире

def change_hyphen(title):
    title = title.replace("\u0020\u002D\u0020", "\u0020\u2014\u0020")
    return title

def change_quotation(title):
    if not title:  # Защита от пустой строки
        return title

    # 1. Заменяем «умные» кавычки (если есть)
    title = title.replace("\u201C", "\u00AB")  # “ → «
    title = title.replace("\u201D", "\u00BB")  # ” → »

    # 2. Заменяем сочетания с пробелом
    while "\u0022\u0020" in title:
        title = title.replace("\u0022\u0020", "\u00BB\u0020")  # " + пробел → » + пробел
    while "\u0020\u0022" in title:
        title = title.replace("\u0020\u0022", "\u0020\u00AB")  # пробел + " → пробел + «

    # 3. Заменяем специальные сочетания: ", → »,,  и ": → »:
    title = title.replace("\u0022,", "\u00BB,")  # ", → »,
    title = title.replace("\u0022:", "\u00BB:")  # ": → »:

    # 4. Обрабатываем одиночные кавычки в начале/конце строки
    if title.startswith("\u0022"):
        title = "\u00AB" + title[1:]  # "текст → «текст
    if title.endswith("\u0022"):
        title = title[:-1] + "\u00BB"  # текст" → текст»

    # 5. Дополнительная проверка внутренних " перед пробелом (через разбиение)
    parts = title.split("\u0020")
    for i in range(1, len(parts)):  # Пропускаем первый элемент
        if parts[i].startswith("\u0022"):
            parts[i] = "\u00BB" + parts[i][1:]
    title = "\u0020".join(parts)

    return title