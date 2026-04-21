@echo off
:: Este comando hace que el script se ubique en la carpeta actual automáticamente
cd /d "%~dp0"

:: Activamos tu entorno virtual
call .venv\Scripts\activate

:: Levantamos Waitress
waitress-serve --listen=*:8000 nucleo.wsgi:application