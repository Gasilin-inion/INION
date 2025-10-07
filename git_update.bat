@echo off
REM Скрипт автоматической синхронизации Git

REM Переходим в директорию проекта
cd C:\Users\yotto\YandexDisk-gasilin@inion.ru\Developments\e-Library_to_IRBIS

REM Добавляем все изменения
git add .

REM Создаем коммит
git commit -m "Автоматическое обновление %date% %time%"

REM Загружаем изменения
git push origin main

REM Проверяем статус
git status
