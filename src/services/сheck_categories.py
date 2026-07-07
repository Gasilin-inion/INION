# Проверка документов, представленных в формате ИРБИС-64, 
# по полю 690 (рубрики АИСОН) на соответствие рубрикатору
# NB!: Эта версия функции адаптировано только под использование с одной рубрикой.
# NB!: Если в одном документе указано несколько рубрик, все, кроме первой будут проигнорированы
# NB!: Функция нуждается в доработке (06.07.2026) 

import json
import pandas as pd
from pathlib import Path

# Читаем пути к папкам файлов в path_config
#config_path = Path("data/config/path_config.json")
config_path = Path("C:/Users/yotto/CONVERTERS/INION/data/config/path_config.json")

try:
    with open(config_path, "r", encoding="utf-8") as f:
        config_paths = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("Файл конфигурации path_config.json не найден.")
except ValueError as e:
    raise ValueError("Ошибка в файле конфигурации path_config.json: {}".format(e))

rubricator_fl = config_paths.get("rubricator")
if not rubricator_fl:
    raise ValueError("В конфигурации path_config.json отсутствует ключ 'rubricator'.")


def check_cat(file_path, spec):
    """
    Проверяет категории из списка строк на соответствие рубрикатору для заданной специальности.
    
    Особенности:
        - #903: (номер) и #690: (категория) всегда находятся в разных строках.
        - Связь между номером и категорией устанавливается по порядку появления:
          первый номер -> первая категория, второй номер -> вторая категория и т.д.
    
    Параметры:
        strings — список строк (каждая строка может содержать либо #903:, либо #690:, либо другие значения).
        spec — код специальности (например, '02').
        rubricator_path — путь к JSON-файлу рубрикатора.
    
    Возвращает:
        pd.DataFrame с колонками ['category', 'identifier'] — только строки с некорректными категориями.
        Если ошибок нет — пустой DataFrame с этими колонками.
    """
    specifications = {
        "philosophy": "02",
        "history": "03",
        "sociology": "04",
        "economics": "06",
        "law": "10",
        "politics": "11",
        "science": "12",
        "cultural_studies": "13",
        "language": "16",
        "literature": "17",
        "religion": "21"
    }
    
    # 0. Читаем файл, загруженный пользователем
    with open(file_path, 'r', encoding='UTF-8') as file:
        strings = file.readlines()
    
    # 1. Читаем рубрикатор и делаем DataFrame
    try:
        with open(rubricator_fl, "r", encoding="utf-8") as f:
            rubricator_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Файл рубрикатора не найден: {}".format(rubricator_fl))
    except ValueError as e:
        raise ValueError("Ошибка в JSON-файле рубрикатора: {}".format(e))

    rubricator_df = pd.DataFrame(rubricator_data)

    # 2. Фильтруем рубрикатор через pandas и получаем множество разрешённых категорий
    filtered_df = rubricator_df[rubricator_df["specialization"] == spec]
    allowed_categories = set(filtered_df["category"].astype(str).tolist())

    # 3. Проходим по строкам и собираем номера и категории в отдельные списки,
    #    сохраняя порядок их появления.
    identifiers = []
    categories = []

    for line in strings:
        line = line.strip()
        if not line:
            continue

        idx_903 = line.find("#903:")
        if idx_903 != -1:
            unique_number = line[idx_903 + 7:].strip()
            identifiers.append(unique_number)

        idx_690 = line.find("#690:")
        if idx_690 != -1:
            category = line[idx_690 + 8:].strip()
            categories.append(category)

    # 4. Связываем номера и категории по порядку (по индексу в собранных списках)
    rows = []
    max_len = min(len(identifiers), len(categories))

    for i in range(max_len):
        category = categories[i]
        identifier = identifiers[i]

        if category not in allowed_categories:
            rows.append({
                "identifier": identifier,
                "category": category                
            })

    # Если категорий больше, чем номеров (или наоборот), «лишние» элементы просто игнорируются.
    # При необходимости можно добавить предупреждение, если len(identifiers) != len(categories).

    return pd.DataFrame(rows, columns=["identifier", "category"])


# Тестовое задание

file_path = 'C:/Users/yotto/Downloads/02_files_to_process_test_vers.txt'
spec = '02'

result_df = check_cat(file_path, spec)
if result_df.empty:
    print("Ошибок не найдено: все рубрики соответствуют рубрикатору.")
else:
    print("Найдены некорректные рубрики:")
    print(result_df)