import pandas as pd
import json

# Чтение Excel файла
df = pd.read_excel('journal_list_25.07.xlsx')

# Преобразование DataFrame в список словарей
data = df.to_dict(orient='records')

# Сохранение с форматированием
with open('journal_list.json', 'w', encoding='utf-8') as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,  # корректное отображение кириллицы
        indent=4,           # отступы в 4 пробела
        sort_keys=True      # сортировка ключей
    )
