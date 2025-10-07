# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import requests
import json

# Читаем IAM-токен
try:
    with open('iam.txt', 'r', encoding='UTF-8') as f:
        IAM_TOKEN = f.readline().strip()
except FileNotFoundError:
    raise Exception("Файл iam.txt не найден. Положите его рядом с ya_GPT.py")

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
                    "Одно-два предложения, максимум 100 слов, на русском. "
                    "Используй безличные конструкции. "
                    "Не пиши 'статья рассматривает', а 'в работе рассматриваются'."
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
