# Функция добавляет рубрики на основе ключевых слов
"""
Created on Sat Mar  1 18:11:50 2025

@author: yotto
"""

def add_main_category(keywords):
    # Объявляем переменные
    descriptors = []
    categories = []
    cat_list = []
    separator = ', '
    final_category = 'A02'
    # Импортируем таблицу соответветствия рубрик дескрипторам
    import pandas as pd
    df = pd.read_excel('descriptors_categories.xlsx')
    descriptors = df['descriptors'].tolist()
    categories = df['categories'].tolist()
    # Цикл перебора ключевых слов
    for keyword in keywords:
        k = 0
        for descriptor in descriptors:
            cat_number = 0
            # Сравнение ключевых слов со списком дескрипторов
            if keyword == descriptor:
                list_of_categories = str(categories[k])  
                list_of_categories = list_of_categories.rstrip()
                cat_number = list_of_categories.count(separator)
                # Извлечение рубрик и составление списка рубрик
                if cat_number == 0:
                    cat_list.append(list_of_categories)
                if cat_number >= 1:
                    local_cat_list = list_of_categories.split(separator)
                    for item in local_cat_list:
                        cat_list.append(item)
            k += 1
    # Вычисление дублирующихся рубрик (простое дублирование), 
    # определение на их основе основной рубрики
    for item in cat_list:        
        number_of_doubles = cat_list.count(item)
        if number_of_doubles >= 2:
            final_category = item
            break
    return final_category


                
                