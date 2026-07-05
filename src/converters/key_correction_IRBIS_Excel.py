# Функция для выделения ненормированных ключевых слов из файла в формате ИРБИС-64
# и добавления их в актуальную таблицу автозамены. Возвращает список терминов для проверки.
# @Author: Андрей Гасилин, 2026

import json
from pathlib import Path

from src.services.read_actual_file import read_actual  # type: ignore

# Читаем пути к папкам файлов в path_config
config_path = Path("data/config/path_config.json") # Путь к файлу конфигурации путей
with open(config_path, "r", encoding="utf-8") as f:
    config_paths = json.load(f) # Открываем файл в формате json, формируем массив данных
SNL_02 = config_paths["SNL_02"] # Задаем путь к папке с версиями словника по философии
SNL_04 = config_paths["SNL_04"] # Задаем путь к папке с версиями словника по социологии

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
        actual_path = read_actual(SNL_02) # Определяем путь до наиболее актуальной версии СНЛ
        with open(actual_path, 'r', encoding='utf-8') as f2: # Открываем файл с дескрипторами
            descriptors = f2.readlines() # Создаем на его основе список дескрипторов
            descriptors = [s.replace('\n', '') for s in descriptors] # Чистим дескрипторы от переносов в конце строки

    elif topic_num == '04': # Если специальность - социология
        actual_path = read_actual(SNL_04) # Определяем путь до наиболее актуальной версии СНЛ
        with open(actual_path, 'r', encoding='utf-8') as f2: # Открываем файл с дескрипторами
            descriptors = f2.readlines() # Создаем на его основе список дескрипторов
            descriptors = [s.replace('\n', '') for s in descriptors] # Чистим дескрипторы от переносов в конце строки
    
    for string in strings: # Цикл перебора строк
        if '#965:' in string: # Выделение ключевых слов
            keyword = string[6:]
            keyword = keyword.rstrip()
            keywords.append(keyword) # Добавление выделенных ключей в список keywords
    keywords = list(set(keywords)) # Удаление дублей
    keywords = sorted(keywords) # Расстановка по алфавиту
    print(f'Ненормированные ключи: {keywords}')

    for keyword in keywords: # Перебор элементов полученного списка
        if (keyword not in descriptors): # Если элемент списка не совпадает с СНЛ
            keywords_for_correction.append(keyword) # то он добавляется в список терминов для ручного редактирования
    return keywords_for_correction, topic_num # Функция возвращает список терминов для добавления в таблицу автокоррекции, а также номер специальности в виде строки 
