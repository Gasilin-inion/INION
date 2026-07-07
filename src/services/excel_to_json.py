# Функция переводит таблицу в формате excel в формат json

import pandas as pd
import json

# Загрузка конфигурации, извлечение путей к авторитетным файлам
with open("C:/Users/yotto/CONVERTERS/INION/data/config/path_config.json", "r", encoding="utf-8") as pathfile:
    config_paths = json.load(pathfile)
    
path_to_facet = config_paths["facet"]

def to_json(input_file):
    # Создаём дата-фрейм на основе таблицы excel
    a_facet = pd.read_excel(input_file)
    # Меняем имя файла
    a_facet_json = path_to_facet.replace('.xlsx', '.json')
    a_facet.to_json(a_facet_json, orient="records", force_ascii=False, indent=2)
    return a_facet_json

print(f'Фасет в формате .json: \n{to_json(path_to_facet)}')