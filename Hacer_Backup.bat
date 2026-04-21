@echo off
echo Iniciando copia de seguridad del Taller...

:: 1. Verificamos si la carpeta existe
if not exist "C:\Backups_Taller" mkdir "C:\Backups_Taller"

:: 2. Magia pura: Obtenemos fecha y hora seguras usando PowerShell
for /f %%I in ('powershell -Command "Get-Date -Format 'yyyyMMdd_HHmm'"') do set FECHA=%%I

:: 3. Armamos el nombre del archivo final
set ARCHIVO=C:\Backups_Taller\GestionTaller_%FECHA%.bak

echo Intentando guardar backup en: %ARCHIVO%
echo.

:: 4. Ejecutamos el comando de SQL Server
sqlcmd -S localhost -E -Q "BACKUP DATABASE GestionTallerDB TO DISK='%ARCHIVO%'"

echo.
echo ===============================================
echo LIMPIEZA DE BACKUPS VIEJOS
echo ===============================================
echo Buscando archivos con mas de 30 dias de antiguedad...

:: 5. La rotacion: Borramos archivos .bak de mas de 30 dias
forfiles /p "C:\Backups_Taller" /m *.bak /d -30 /c "cmd /c del @file" 2>nul

if %errorlevel% equ 0 (
    echo Se encontraron y eliminaron backups antiguos.
) else (
    echo No hay backups tan viejos para borrar todavia.
)

echo.
echo ===============================================
echo PROCESO TOTALMENTE TERMINADO.
echo ===============================================
:: Usamos timeout en vez de pause para que se cierre solo a los 5 segundos
timeout /t 5