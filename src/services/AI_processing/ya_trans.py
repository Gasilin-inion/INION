def abstracts_translator(texts):
    import requests
    import json

    # Чтение IAM-токена
    try:
        with open('purple.json', 'r', encoding='UTF-8') as file:
            data = json.load(file)
            IAM_TOKEN = data.get("key")
            if not IAM_TOKEN:
                raise ValueError("В файле purple.json отсутствует ключ 'key'.")
    except FileNotFoundError:
        raise Exception("Файл purple.json не найден. Положите его в каталог с программой.")
    except json.JSONDecodeError:
        raise Exception("Файл purple.json содержит некорректный JSON.")

    folder_id = "b1g33b2g1d47guea42co"
    target_language = "ru"

    # Приведение входа к списку
    input_is_string = False
    if isinstance(texts, str):
        texts = [texts]
        input_is_string = True
    elif not isinstance(texts, (list, tuple)):
        raise TypeError("Параметр 'texts' должен быть строкой или списком/кортежем строк.")

    body = {
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IAM_TOKEN}",
    }

    # Выполнение запроса
    try:
        response = requests.post(
            "https://translate.api.cloud.yandex.net/translate/v2/translate",
            json=body,
            headers=headers,
            timeout=20
        )
    except requests.RequestException as e:
        raise Exception(f"Ошибка сети при обращении к сервису перевода: {e}")

    # Проверка статуса
    if response.status_code != 200:
        raise Exception(f"Ошибка API перевода: HTTP {response.status_code}, тело: {response.text}")

    # Парсинг результата
    data = response.json()

    if "translations" not in data:
        raise Exception(f"Ответ API не содержит ключ 'translations': {data}")

    translations = [item.get("text", "") for item in data["translations"]]

    # Возвращаем строку, если вход был строкой
    if input_is_string:
        return translations[0] if translations else ""

    # Иначе возвращаем список переводов
    return translations

