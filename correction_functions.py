# Функции для автоматической коррекции заголовков статей
"""
Created on Thu Jan 30 17:52:55 2025

@author: Гасилин Андрей
"""
# Функция коррекции имён собственных

def persons_correction(sentence):
    import pandas as pd
    a_facet = pd.read_excel('a_facet.xlsx')
    number_of_strings = len(a_facet)
    list_of_terms = a_facet['low_name'].tolist()
    list_of_corrected_terms = a_facet['up_name'].tolist()
    index = 0
    for counter in range(number_of_strings):
        low_name = str(list_of_terms[index])
        up_name = str(list_of_corrected_terms[index])
        if (low_name in sentence):
            sentence = sentence.replace(low_name, up_name)
        index += 1
    return sentence

# Исправление строчных букв на заглавные в начале предложений

def upper_sent(title):    
    if ('. ' in title):
        title = title.rstrip()
        start = 0
        end = len(title)
        number_of_points = title.count('. ')        
        for point_num in range(number_of_points):            
            point = title.find('. ', start, end)
            letter_point = point + 2
            letter = title[letter_point]
            letter = letter.upper()
            title = (title[:point + 2] + letter + title[(letter_point + 1):])
            start = letter_point
    if ('? ' in title):
        start = 0
        end = len(title)
        number_of_points = title.count('? ')
        for point_num in range(number_of_points):
            point = title.find('? ', start, end)
            letter_point = point + 2
            letter = title[letter_point]
            letter = letter.upper()
            title = (title[:point + 2] + letter + title[(letter_point + 1):])
            start = letter_point
            
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
    if (title[0] == '"'):    # Кавычки в начале заглавия  
        first_letter = title[1]
        first_letter = first_letter.upper()
        title = ('"' + first_letter + title[2:])
    if (' "' in title):     # Кавычки в середине заглавия
        start = 0
        end = len(title)
        count_of_commas = title.count(' "')
        for comma in range(count_of_commas):
            point = title.find(' "', start, end)
            next_point = point + 2
            letter = title[next_point]
            letter = letter.upper()
            title = title[:next_point] + letter + title[(next_point + 1):]
            start = next_point
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
    title = title.replace(u"\u0020\u002D\u0020", u"\u0020\u2014\u0020")
    return title

# Замена кавычек "лапок" на кавычки "ёлочки"

def change_quotation(title):
    title = title.replace(u"\u0020\u0022", u"\u0020\u00AB")
    title = title.replace(u"\u0022\u0020", u"\u00BB\u0020")
    title = title.replace(u"\u201C", u"\u00AB")
    title = title.replace(u"\u201D", u"\u00BB")
    return title
