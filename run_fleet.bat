@echo off
echo Starting Fleet Management System...

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Start Flask server in a new CMD window
start cmd /k "python app.py"

:: Give server 5 seconds to start
timeout /t 5

:: Start simulator in a new CMD window
start cmd /k "python simulator.py"

echo Fleet system started!
pause