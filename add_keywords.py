# Генерация нормализованных ключевых слов на основе СНЛ и списка персоналий
"""
Created on Mon Feb 17 16:46:54 2025
Changed on Tue Oct 07 2025 (json vers)
@author: Gasilin Andrey
"""

import json

def keys_from_text(text):
    # Явное объявление словарей и списка
    descriptors = {}
    persons = {}
    key_words = []
    text = text.lower()

    try:
        # Импорт списка дескрипторов
        with open('descriptors.json', 'r', encoding='utf-8') as file_1:
            descriptors = json.load(file_1)

        # Импорт списка персоналий
        with open('persons.json', 'r', encoding='utf-8') as file_2:
            persons = json.load(file_2)

    except FileNotFoundError:
        print("Ошибка: один из JSON-файлов не найден")
        return []
    except json.JSONDecodeError:
        print("Ошибка: проблема с форматом JSON")
        return []

    # Обработка персоналий
    for key, values in persons.items():  # Запускаем цикл перебора значений словаря персоналий
        if isinstance(values, list):  # Проверяем, что значения — список
            for value in values:
                if value.lower() in text:  # Приводим к нижнему регистру для сравнения
                    key_words.append(key)

    # Обработка дескрипторов
    for key, values in descriptors.items():  # Запускаем цикл перебора значений словаря дескрипторов
        if isinstance(values, list):  # Проверяем, что значения — список
            for value in values:
                if value.lower() in text:  # Приводим к нижнему регистру для сравнения
                    key = key.capitalize()
                    key_words.append(key)

    key_words = list(set(key_words))  # Удаляем из списка повторы
    return key_words
