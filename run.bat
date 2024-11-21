@echo off
call venv\Scripts\activate.bat
uvicorn app.app:app --reload
