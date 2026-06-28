@echo off
echo =========================================
echo  OsuCollector Downloader Builder
echo =========================================
echo.

echo [1/3] Установка PyInstaller...
pip install pyinstaller

echo.
echo [2/3] Компиляция проекта в .exe...
pyinstaller --onefile --name "OsuCollectorDownloader" main.py

echo.
echo =========================================
echo [3/3] Сборка завершена! 
echo Исполняемый файл OsuCollectorDownloader.exe находится в папке 'dist'.
echo =========================================
pause
