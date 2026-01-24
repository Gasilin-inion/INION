import subprocess
import sys

def run_script(script_path):
    result = subprocess.run([
        sys.executable,  # путь к текущему Python
        script_path,     # путь к скрипту (например, "src/modules/my_script.py")
    ], capture_output=True, text=True)


    if result.returncode == 0:
        print("Скрипт выполнен успешно:")
        print(result.stdout)
    else:
        print("Ошибка при выполнении скрипта:")
        print(result.stderr)

# Запуск скрипта из вложенной папки
run_script("src/converters/elibrary_excel.py")
