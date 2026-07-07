# Функция для добавления ненормированных ключей в
# таблицу автозамены, представленную в формате excel.
# Таблица используется для промежуточного редактирования.

import pandas as pd
import numpy as np

def add_keys(upload_file_path, result_file_path, data_list):
    # Проверка входных данных
    if not data_list:
        print("Предупреждение: data_list пуст")
        return

    # Читаем существующий файл таблицы автозамены
    df = pd.read_json(upload_file_path)

    # Удаляем все значения "nan"
    df = df.replace("nan", np.nan)

    # Генерируем дата-фрейм на основе списка ненормализованных ключевых слов
    new_rows = pd.DataFrame({df.columns[0]: data_list})

    # Записываем ненормированные ключи после нормализованных
    new_df = pd.concat([df, new_rows], ignore_index=True)

    # Очищаем все пустые ячейки
    new_df = new_df.where(pd.notnull(new_df), None)

    # Записываем обратно в файл с обработкой ошибок
    with pd.ExcelWriter(result_file_path, engine='openpyxl', mode='w') as writer:
        new_df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        worksheet.column_dimensions['A'].width = 100
        worksheet.column_dimensions['B'].width = 100
    print(f"Файл успешно сохранён: {result_file_path}")