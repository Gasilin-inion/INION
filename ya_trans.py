def abstracts_translator(texts):
    import requests
    import json

    # Читаем токен из файла
    with open('iam.txt', 'r', encoding='UTF-8') as file:
        IAM_TOKEN = file.readline().strip()

    folder_id = "b1g33b2g1d47guea42co"
    target_language = "ru"
    texts = texts

    body = {
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(IAM_TOKEN)
    }

    response = requests.post(
        "https://translate.api.cloud.yandex.net/translate/v2/translate",
        json=body,
        headers=headers,
    )

    data = response.json()
    translated_text = data['translations'][0]['text']

    return translated_text
