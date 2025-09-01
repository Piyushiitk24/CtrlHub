@echo off
REM CtrlHub Development Server Launcher for Windows
REM One command to rule them all! 🚀

echo 🎛️  Starting CtrlHub Development Environment...
echo ==============================================

REM Get current directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Colors don't work well in Windows CMD, so we'll use simple text
echo 🧹 Cleaning up existing processes...

REM Kill existing processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo 🐍 Setting up Python environment...

REM Check if virtual environment exists
if not exist "ctrlhub_env" (
    echo Creating virtual environment...
    python -m venv ctrlhub_env
)

REM Activate virtual environment
call ctrlhub_env\Scripts\activate.bat

echo 📦 Installing Python dependencies...
cd local_agent
pip install -q -r requirements.txt

echo 📦 Installing Node.js dependencies...
cd ..\frontend
if not exist "node_modules" npm install --silent

echo 🖥️  Starting CtrlHub Local Agent...
cd ..\local_agent
start "CtrlHub Local Agent" python main.py

echo    Waiting for local agent to initialize...
timeout /t 5 /nobreak >nul

echo 🌐 Starting React Development Server...
cd ..\frontend
start "CtrlHub Frontend" npm start

echo    Waiting for React server to initialize...
timeout /t 10 /nobreak >nul

echo 🌍 Opening CtrlHub in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000/components/dc-motor/parameter-extraction

echo.
echo 🎉 CtrlHub Development Environment Ready!
echo ==============================================
echo ✅ Local Agent:     http://localhost:8003
echo ✅ Web Interface:   http://localhost:3000
echo ✅ Parameter Page:  http://localhost:3000/components/dc-motor/parameter-extraction
echo.
echo 💡 Development Tips:
echo    • Both servers will auto-reload on file changes
echo    • Close this window to stop all servers
echo    • Check the opened terminal windows for any errors
echo.
echo Press any key to stop all servers...
pause >nul

REM Cleanup on exit
echo 🛑 Shutting down CtrlHub development servers...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo ✅ All servers stopped!
pause
