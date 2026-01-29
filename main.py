import subprocess
import sys

def run_script(script_path):
    result = subprocess.run([
        sys.executable,  # путь к текущему Python
        script_path,     # путь к скрипту 
    ], capture_output=True, text=True)
    if result.returncode == 0:
        print("Запуск скрипта прошёл успешно")
        print(result.stdout)
    else:
        print("Ошибка при выполнении скрипта:")
        print(result.stderr)

# Запуск скрипта из вложенной папки
print("Программа двухступенчатой конвертации библиографических метаданных из e-Library в ИРБИС 64")
k = input("Введите номер этапа конвертации: [1] - e-Library-Excel / [2] - Excel-IRBIS) ")
if k == '1':
    run_script("src/converters/elibrary_excel.py")
    print('Задание выполнено. Результат см. в папке /resources/files_to_edit')
elif k == '2':
    run_script("src/converters/excel_irbis.py")
    print('Задание выполнено. Результат см. в папке /resources/files_to_import_to_IRBIS')
else:
    print("Введёно некорректное значение, попробуйте ещё раз")