import pandas as pd
import os
from openpyxl.utils import get_column_letter

def append_with_pandas(file_path, sheet_name, column_name, data_list):
    # Проверка входных данных
    if not data_list:
        print("Предупреждение: data_list пуст, операция пропущена.")
        return

    # Читаем существующий файл или создаём новый DataFrame
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except ValueError:  # Лист не найден
            df = pd.DataFrame(columns=[column_name])
    else:
        df = pd.DataFrame(columns=[column_name])

    # Находим индекс первой пустой ячейки после последней заполненной в колонке
    if df.empty or column_name not in df.columns:
        # Если DataFrame пустой или колонки нет, начинаем с первой строки
        start_idx = 0
    else:
        col_data = df[column_name]
        # Ищем последнюю не-NaN ячейку
        non_null_mask = col_data.notna()
        if non_null_mask.any():
            last_non_null_idx = non_null_mask[::-1].idxmax()  # Последний индекс с данными
            start_idx = last_non_null_idx + 1  # Следующая строка — первая пустая
        else:
            start_idx = 0  # Все ячейки пустые

    # Создаём DataFrame для новых данных
    new_data = pd.DataFrame({column_name: data_list})

    # Определяем, куда добавлять новые данные
    if start_idx == 0:
        # Колонка полностью пустая или DataFrame новый
        result_df = new_data
    elif start_idx < len(df):
        # Новые данные вписываются в существующие строки (заполняем пропуски)
        df_copy = df.copy()
        for i, value in enumerate(data_list):
            row_idx = start_idx + i
            if row_idx < len(df_copy):
                df_copy.at[row_idx, column_name] = value
            else:
                # Если вышли за пределы, добавляем новую строку
                new_row = pd.Series({col: None for col in df_copy.columns})
                new_row[column_name] = value
                df_copy = pd.concat([df_copy, new_row.to_frame().T], ignore_index=True)
        result_df = df_copy
    else:
        # Добавляем новые строки в конец
        result_df = pd.concat([df, new_data], ignore_index=True)

    # Записываем обратно в файл с установкой ширины столбцов
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
        result_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Получаем workbook и worksheet
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Устанавливаем ширину первых двух столбцов в 60 единиц
        worksheet.column_dimensions['A'].width = 60
        worksheet.column_dimensions['B'].width = 60