"""Возвращает список файлов в указанной папке"""

import os
from pathlib import Path
import glob

def get_files_in_folder(folder_path, extensions=None):

    file_list = []

    try:
        # Проверяем, существует ли папка
        if not os.path.isdir(folder_path):
            raise ValueError("Указанный путь не является папкой")

        # Получаем список элементов в папке
        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file():
                    # Фильтрация по расширениям
                    if extensions:
                        _, file_ext = os.path.splitext(entry.name)
                        if file_ext.lower() in extensions:
                            file_list.append(entry.path)
                    else:
                        file_list.append(entry.path)

    except Exception as e:
        print(f"Ошибка: {e}")
        return []

    return file_list

""" Создаёт XLSX-таблицу из HTML-файлов в указанной папке. """

def create_xlsx_from_folder(folder_path, output_dir):
    """    
    Args:
        folder_path: путь к папке с HTML-файлами
        output_dir: директория для сохранения XLSX (если None — сохраняет в той же папке)
    
    Returns:
        Путь к созданному XLSX-файлу
    """
    # Находим все HTML-файлы в папке (включая подпапки текущего уровня)
    html_files = glob.glob(os.path.join(folder_path, '*.html'))
    
    if not html_files:
        print(f"Нет HTML-файлов в папке: {folder_path}")
        return None
   
    # Определяем путь для сохранения
    output_path = Path(output_dir) / f"{Path(folder_path).name}.xlsx"
   
    return str(output_path)

""" Рекурсивно обрабатывает директорию и все её подпапки """
""""
def process_directory_recursive(root_dir, output_dir, include_root=True):
    
    xlsx_files = []    
    # Преобразуем в Path для удобства
    root_path = Path(root_dir)

    # Если нужно обработать корневую папку как отдельную
    if include_root:
        xlsx_path = create_xlsx_from_folder(root_path, output_dir)
        if xlsx_path:
            xlsx_files.append(xlsx_path)
    
    # Рекурсивно обходим все подпапки
    for subfolder in root_path.rglob('*'):
        if subfolder.is_dir():
            xlsx_path = create_xlsx_from_folder(subfolder, output_dir)
            if xlsx_path:
                xlsx_files.append(xlsx_path)
    
    return xlsx_files

# Пример использования
if __name__ == "__main__":

    current_dir = os.getcwd()
    root_directory = os.path.join(current_dir, 'files_to_process')
    output_directory = os.path.join(current_dir, 'files_to_edit')

    # Запускаем обработку
    result_files = process_directory_recursive(
        root_directory,
        output_directory,
        include_root=True  # обрабатывать ли корневую папку
    )
    print(result_files)
"""