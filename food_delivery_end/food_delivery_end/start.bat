@echo off
echo ========================================
echo  🚀 ЗАПУСК МАГАЗИНА
echo ========================================
echo.

echo 📂 Активация виртуального окружения...
call venv\Scripts\activate

echo 🚀 Запуск Django сервера...
start python manage.py runserver 0.0.0.0:8000

echo 🌐 Запуск xTunnel...
start xtunnel http 8000

echo.
echo ========================================
echo ✅ Сервер запущен!
echo 📱 Открой в MAX: https://твой-адрес.xtunnel.ru
echo ========================================
echo.
echo Нажми любую клавишу для выхода...
pause > nul