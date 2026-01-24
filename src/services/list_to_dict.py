# Скрипт, предназначенный для склонения терминов в пяти падежах
# и составления на их основе словаря теримнов

lnv = open('heads.txt', 'r', encoding='UTF-8')
heads = lnv.readlines()
lnv.close()

fl = open('normalized_personalities.txt', 'r', encoding='UTF-8')
persons = fl.readlines()
fl.close()

list_of_heads = []
list_of_persons = []
list_of_morphed_persons = []  # Добавляем определение списка

# Чистка дескрипторов
for person in persons:
    person = person.replace('\n', '')
    list_of_persons.append(person)

for head in heads:
    head = head.replace('\n', '')
    list_of_heads.append(head)  # Исправляем heads на head

import pymorphy2
morph = pymorphy2.MorphAnalyzer()
def safe_decline(word, case):
    try:
        parsed_word = morph.parse(word)[0]
        declined = parsed_word.inflect({case})
        if declined:
            return declined.word
        else:
            print(f"Не удалось просклонять слово: {word} в падеже {case}")
            return word
    except Exception as e:
        print(f"Ошибка при склонении слова {word}: {e}")
        return word

for word in list_of_heads:
    # Анализируем слово с обработкой ошибок
    n_w = safe_decline(word, 'nomn')
    g_w = safe_decline(word, 'gent')
    d_w = safe_decline(word, 'datv')
    a_w = safe_decline(word, 'ablt')
    l_w = safe_decline(word, 'loct')
    
    names_list = [n_w, g_w, d_w, a_w, l_w]
    list_of_morphed_persons.append(names_list)

persons_dict = dict(zip(list_of_persons, list_of_morphed_persons))

print(persons_dict)

