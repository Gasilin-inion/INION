# Функция для выделения ненормированных ключевых слов из файла в формате ИРБИС-64
# и добавления их в актуальную таблицу автозамены. Возвращает список терминов для проверки.
# @Author: Андрей Гасилин, 2026

import json
from pathlib import Path

# Читаем пути к папкам файлов в path_config
config_path = Path("data/config/path_config.json") # Путь к файлу конфигурации путей
with open(config_path, "r", encoding="utf-8") as f:
    config_paths = json.load(f) # Открываем файл в формате json, формируем массив данных
SNL_02 = config_paths["snl_02"] # Извлекаем путь к файлу актуального словника по специальности 02
SNL_04 = config_paths["snl_04"] # Извлекаем путь к файлу актуального словника по специальности 04
countries_04 = config_paths["countries_04"] # Извлекаем путь к файлу актуального фасета стран
persons_02 = config_paths["persons_02"] # Извлекаем путь к файлу актуального фасета персоналий

def key_extraction(file_path): # Функция извлечения ненормированных ключевых слов, на входе адрес целевого файла
    keywords = [] # Создаём список всех ключевых слов
    keywords_for_correction = [] # Создаём список ненормированных ключевых слов

    with open(file_path, 'r', encoding='utf-8') as f: # Открываем целевой файл
        strings = f.readlines() # Создаем на его основе список строк для обработки

    for string in strings: # Цикл перебора строк
        if '#610:' in string: # Выделение ненормированного ключевого слова
            topic_num = string[6:8] # Определение специальности
            break

    if topic_num == '02': # Если специальность - философия
        with open(SNL_02, 'r', encoding='utf-8') as f2: # Открываем файл с дескрипторами
            descriptors = f2.readlines() # Создаем на его основе список дескрипторов
            descriptors = [s.replace('\n', '') for s in descriptors] # Чистим дескрипторы от переносов в конце строки
            print(f'Нормированные ключи: {descriptors}')
    
        with open(persons_02, 'r', encoding='utf-8') as f3: # Открываем файл с персоналиями
            facet = f3.readlines() # Создаем на его основе нормализованный список стран
            facet = [s.replace('\n', '') for s in facet] # Чистим персоналии от переносов в конце строки

    elif topic_num == '04': # Если специальность - социология
        with open(SNL_04, 'r', encoding='utf-8') as f2: # Открываем файл с дескрипторами
            descriptors = f2.readlines() # Создаем на его основе список дескрипторов
            descriptors = [s.replace('\n', '') for s in descriptors] # Чистим дескрипторы от переносов в конце строки
    
        with open(countries_04, 'r', encoding='utf-8') as f3: # Открываем файл с фасетами стран
            facet = f3.readlines() # Создаем на его основе нормализованный список стран
            facet = [s.replace('\n', '') for s in facet] # Чистим страны от переносов в конце строки
    
    for string in strings: # Цикл перебора строк
        if '#965:' in string: # Выделение ключевых слов
            keyword = string[6:]
            keyword = keyword.rstrip()
            keywords.append(keyword) # Добавление выделенных ключей в список keywords
    keywords = list(set(keywords)) # Удаление дублей
    keywords = sorted(keywords) # Расстановка по алфавиту
    print(f'Ненормированные ключи: {keywords}')

    for keyword in keywords: # Перебор элементов полученного списка
        if (keyword not in descriptors) and (keyword not in facet): # Если элемент списка не совпадает с СНЛ или фасетом
            keywords_for_correction.append(keyword) # то он добавляется в список терминов для ручного редактирования
    return keywords_for_correction, topic_num # Функция возвращает список терминов для добавления в таблицу автокоррекции, а также номер специальности в виде строки 
