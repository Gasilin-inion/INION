@echo off
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python ..\scr\converters\excel_irbis.py
call myenv\Scripts\deactivate.bat
