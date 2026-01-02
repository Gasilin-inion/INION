# Анализ строки авторов. Возвращает словарь, состоящий из фамилий и аббревиатур авторов в двух форматах, без и с пробелом

def authors_process(authors_str: str):
    result = {}  # Словарь для результатов
    # Если авторов несколько 
    if ';' in authors_str:
        authors_list = authors_str.split(' ; ')
        number_of_authors = len(authors_list)
        result['number_of_authors'] = number_of_authors        
        for i, author in enumerate(authors_list, 1):
            key_base = f'author_{i}'            
            # Разделяем фамилию и инициалы
            if ',' in author:
                parts = author.split(', ')            
                result[f'{key_base}'] = parts[0]    # Фамилия
                result[f'{key_base}_xx'] = parts[1]     # Инициалы для полей 700 и 701                    
                abb = parts[1].replace('.', '. ')
                result[f'{key_base}_abb'] = abb         # Инициалы для поля 200
            else:
                result[f'{key_base}'] = author
                result[f'{key_base}_xx'] = ''
                result[f'{key_base}_abb'] = ''
    # Если автор один
    elif ',' in authors_str:
        result['number_of_authors'] = 1
        parts = authors_str.split(', ', 1)        
        if len(parts) > 1:
            result['author_1'] = parts[0]
            result['author_1_xx'] = parts[1]
            result['author_1_abb'] = parts[1].replace('.', '. ')
        else:
            result['author_1'] = parts[0]
            result['author_1_xx'] = ''
            result['author_1_abb'] = ''    
    # Исли у автора нет инициалов
    else:
        result['number_of_authors'] = 1
        result['author_1'] = authors_str
        result['author_1_xx'] = ''
        result['author_1_abb'] = ''
    
    return result

# Сборка поля 200

def build_argument_200(title: str, authors_dic: dict) -> str: # title - заголовок статьи, authors_dic - словарь с данными авторов

    if 'number_of_authors' not in authors_dic or authors_dic['number_of_authors'] == 0:
        return f'^A{title}^F'
    
    authors_parts = []
    
    for i in range(1, authors_dic['number_of_authors'] + 1):
        author_key = f'author_{i}'
        abb_key = f'{author_key}_abb'
        
        # Получаем данные автора (с обработкой отсутствующих полей)
        author_name = authors_dic.get(author_key, '')
        author_abb = authors_dic.get(abb_key, '')
        
        # Формируем часть для текущего автора
        if author_abb:
            author_part = f'{author_abb}{author_name}'
        else:
            author_part = author_name
        
        authors_parts.append(author_part)
    
    # Собираем всех авторов через запятую
    authors_str = ', '.join(authors_parts)
    
    return f'^A{title}^F{authors_str}'

# Сборка полей 700 и 701

def build_author_fields(authors_dic: dict, field_700: str = '', field_701: str = '') -> tuple:
    number_of_authors = authors_dic['number_of_authors']
    
    # Очищаем поля перед заполнением
    new_700 = field_700
    new_701 = field_701
    
    # Формирование поля 700 (основной автор)
    if number_of_authors == 1:
        author_1 = authors_dic.get('author_1', '')
        author_1_xx = authors_dic.get('author_1_xx', '')      
        if author_1_xx:
            new_700 += f'^A{author_1}^B{author_1_xx}\n'
        else:
            new_700 += f'^A{author_1}\n'    
    elif 1 < number_of_authors < 4:
        author_1 = authors_dic.get('author_1', '')
        author_1_xx = authors_dic.get('author_1_xx', '')
        
        if author_1_xx:
            new_700 += f'^A{author_1}^B{author_1_xx}\n'
        else:
            new_700 += f'^A{author_1}\n'
    else:
        new_700 = ''  # Для 4+ авторов поле 700 пустое

    # Формирование поля 701 (соавторы)
    if number_of_authors < 4:
        for i in range(number_of_authors):
            n = i + 1
            if i == 0:
                new_701 = ''
            else:
                author = authors_dic.get(f'author_{n}', '')
                author_xx = authors_dic.get(f'author_{n}_xx', '')
                new_701 += f'#701: ^A{author}^B{author_xx}\n'                                        
    else:
        for i in range(number_of_authors):
            n = i + 1
            author = authors_dic.get(f'author_{n}', '')
            author_xx = authors_dic.get(f'author_{n}_xx', '')
            if i == 0:
                new_701 += f'^A{author}^B{author_xx}\n'
            else:
                new_701 += f'#701: ^A{author}^B{author_xx}\n'
    
    return new_700, new_701

# Блок для отладки и тестирования
# names = 'Tadesse, A. ; Allen, W.R. ; Mitchell-Kernan, C.'
# print(f'{authors_process(names)}')
# print(f'{build_author_fields(authors_process(names))}')