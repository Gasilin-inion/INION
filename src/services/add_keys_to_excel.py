import pandas as pd
import os

def append_with_pandas(upload_file_path, result_file_path, sheet_name, column_name, data_list):
    # Проверка входных данных
    if not data_list:
        print("Предупреждение: data_list пуст, операция пропущена.")
        return

    # Получаем директорию из пути к результату
    result_dir = os.path.dirname(result_file_path)

    # Проверяем существование директории и создаём, если нужно
    if not os.path.exists(result_dir):
        try:
            os.makedirs(result_dir, exist_ok=True)
            print(f"Создана директория: {result_dir}")
        except PermissionError:
            raise PermissionError(f"Нет прав для создания директории: {result_dir}")

    # Проверяем права на запись
    if not os.access(result_dir, os.W_OK):
        raise PermissionError(f"Нет прав записи в директорию: {result_dir}")

    # Читаем существующий файл или создаём новый DataFrame
    if os.path.exists(upload_file_path):
        try:
            df = pd.read_excel(upload_file_path, sheet_name=sheet_name)
        except ValueError:  # Лист не найден
            df = pd.DataFrame(columns=[column_name])
    else:
        df = pd.DataFrame(columns=[column_name])

    # Находим индекс первой пустой ячейки после последней заполненной в колонке
    if df.empty or column_name not in df.columns:
        start_idx = 0
    else:
        col_data = df[column_name]
        non_null_mask = col_data.notna()
        if non_null_mask.any():
            last_non_null_idx = non_null_mask[::-1].idxmax()
            start_idx = last_non_null_idx + 1
        else:
            start_idx = 0

    # Создаём DataFrame для новых данных
    new_data = pd.DataFrame({column_name: data_list})

    # Определяем, куда добавлять новые данные
    if start_idx == 0:
        result_df = new_data
    elif start_idx < len(df):
        df_copy = df.copy()
        for i, value in enumerate(data_list):
            row_idx = start_idx + i
            if row_idx < len(df_copy):
                df_copy.at[row_idx, column_name] = value
            else:
                new_row = pd.Series({col: None for col in df_copy.columns})
                new_row[column_name] = value
                df_copy = pd.concat([df_copy, new_row.to_frame().T], ignore_index=True)
        result_df = df_copy
    else:
        result_df = pd.concat([df, new_data], ignore_index=True)

    # Записываем обратно в файл с обработкой ошибок
    try:
        with pd.ExcelWriter(result_file_path, engine='openpyxl', mode='w') as writer:
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            worksheet.column_dimensions['A'].width = 60
            worksheet.column_dimensions['B'].width = 60
        print(f"Файл успешно сохранён: {result_file_path}")
    except PermissionError as e:
        raise PermissionError(f"Ошибка прав доступа при записи файла: {e}")
    except Exception as e:
        raise Exception(f"Ошибка при записи файла Excel: {e}")
