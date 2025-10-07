"""Возвращает список файлов в указанной папке"""

import os

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

# Пример использования
if __name__ == "__main__":
    target_folder = input("Введите путь к папке: ").strip()

    # Получаем список файлов
    files = get_files_in_folder(target_folder)

    # Выводим результат
    if files:
        print(f"Найдено файлов: {len(files)}")
        for idx, file in enumerate(files, 1):
            print(f"{idx}. {os.path.basename(file)}")

        # Сохраняем в файл
        with open("file_list.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(files))
        print("Список сохранён в file_list.txt")
    else:
        print("Файлы не найдены или произошла ошибка")
