# Функция проверки корректности рубрик
"""
Created on Thu Feb 20 22:25:36 2025

@author: Gasilin Andrey
"""

def cat_check(category):
    write_categories = []
    fl = open('categories.txt', 'r', encoding= 'UTF-8')
    w_categories = fl.readlines()
    fl.close()
    for w_categorie in w_categories:
        w_categorie = w_categorie.replace('\n', '')
        write_categories.append(w_categorie)
    if category in write_categories:
        c_ok = 1
    else:
        c_ok = 0
    return c_ok
    