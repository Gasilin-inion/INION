@echo off
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python excel_irbis.py
call myenv\Scripts\deactivate.bat
