# Функция считывает данные из таблицы автозамены и генерирует на их основе 
# список заданий для глобальной корректировки в формате .gbl
# @Author: Andrey Gasilin, 2026

import pandas as pd

def key_decoder(file_path): # На входе - адрес файла для обработки
    counter = 0
    file_lines = [] # Список строк    
    file_lines.append('0\n') # Первая строка в виде ноля
    df = pd.read_excel(file_path) # Чтение данных из таблицы Excel
    while counter < len(df):        # Цикл работает до последней строки
        synonym = str(df.at[counter, 'synonym'])    # Извлечение синонимов
        synonym = synonym.rstrip()
        keyword = str(df.at[counter, 'keyword'])    # Извлечение ключевых слов
        keyword = keyword.rstrip()
        if keyword == 'nan':
            task = f"REP\n965\nF\n(if v965= '{synonym}' then # else v965 fi/)\n" # Если термину не соответствует ни одно ключевое слово
        else:
            task = f"REP\n965\nF\n(if v965= '{synonym}' then '{keyword}' else v965 fi/)\n" # Если пара для термина есть

        file_lines.append(task) # Добавление новой строки в список строк
        counter += 1
    return file_lines