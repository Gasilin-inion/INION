# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import requests
import json

# Импорт файла конфигурации путей

with open("./data/config/path_config.json", "r", encoding="utf-8") as pathfile:
    config_paths = json.load(pathfile)
token_path = config_paths["yandex_cloud"]

# Чтение IAM-токена
try:
    with open(token_path, 'r', encoding='UTF-8') as file:
        data = json.load(file)
        IAM_TOKEN = data.get("key")
        if not IAM_TOKEN:
            raise ValueError("В файле конфигурации отсутствует ключ 'key'.")
except FileNotFoundError:
    raise Exception("Файл конфигурации не найден.")
except json.JSONDecodeError:
    raise Exception("Файл конфигурации содержит некорректный JSON.")

FOLDER_ID = "b1g33b2g1d47guea42co"

def abstract_optimization_with_gpt(input_text: str) -> str:
    """
    Преобразует текст в научную аннотацию через прямой вызов Yandex GPT API.
    """
    if not input_text.strip():
        return "Аннотация отсутствует."

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "temperature": 0.3,
            "maxTokens": "500"
        },
        "messages": [
            {
                "role": "system",
                "text": (
                    "Преобразуй текст в аннотацию для научной статьи. "
                    "Объем текста - не больше 200 знаков с пробелами. "
                    "Отдавай предпочтение безличным вводным конструкциям, вроде 'Анализ', 'Сравнительный анализ', 'Обзор', 'Авторская концепция', 'Исследование посвящено' ."
                    "Если в исходном тексте речь идёт об авторе, то начинай аннотацию с 'Автор рассматривает', 'Автор анализирует', 'Автор сравнивает', 'Автор исследует'."
                )
            },
            {
                "role": "user",
                "text": input_text
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # Извлекаем ответ
        text = result["result"]["alternatives"][0]["message"]["text"].strip()
        return text

    except Exception as e:
        return f"Ошибка GPT: {str(e)}"


def error_correction(input_text: str) -> str:
    """
    Исправляет ошибки в тексте.
    """
    if not input_text.strip():
        return input_text

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "temperature": 0.1,
            "maxTokens": "500"
        },
        "messages": [
            {
                "role": "system",
                "text": "Исправь орфографические, грамматические и пунктуационные ошибки."
            },
            {
                "role": "user",
                "text": input_text
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        text = result["result"]["alternatives"][0]["message"]["text"].strip()
        return text

    except Exception as e:
        return f"Ошибка исправления: {str(e)}"
