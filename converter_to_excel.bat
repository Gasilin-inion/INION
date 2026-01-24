@echo off
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python ..\scr\converters\elibrary_excel.py
call myenv\Scripts\deactivate.bat
