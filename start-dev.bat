@echo off
REM DraftIQ Development Server Startup Script for Windows
REM This script starts both the FastAPI backend and React frontend development servers

echo 🚀 Starting DraftIQ Development Environment...
echo ==============================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if node_modules exists in web directory
if not exist "web\node_modules" (
    echo ❌ Frontend dependencies not found. Please run: cd web ^&^& npm install
    pause
    exit /b 1
)

REM Activate virtual environment
echo 📦 Activating Python virtual environment...
call .venv\Scripts\activate.bat

REM Start backend server
echo 🔧 Starting FastAPI backend server on http://localhost:8000...
start "DraftIQ Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo ⚛️  Starting React frontend server on http://localhost:5173...
cd web
start "DraftIQ Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ✅ Development servers started successfully!
echo ==============================================
echo 🔧 Backend API:  http://localhost:8000
echo 📚 API Docs:     http://localhost:8000/docs
echo ⚛️  Frontend:     http://localhost:5173
echo.
echo Both servers are running in separate windows.
echo Close the windows to stop the servers.
echo.
pause
