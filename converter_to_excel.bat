@echo off
cd /d "%~dp0"
call myenv\Scripts\activate.bat
python elibrary_excel.py
call myenv\Scripts\deactivate.bat
