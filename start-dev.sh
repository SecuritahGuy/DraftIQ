#!/bin/bash

# DraftIQ Development Server Startup Script
# This script starts both the FastAPI backend and React frontend development servers

set -e

echo "🚀 Starting DraftIQ Development Environment..."
echo "=============================================="

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "   ✅ Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "   ✅ Frontend server stopped"
    fi
    echo "   🎯 All servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if node_modules exists in web directory
if [ ! -d "web/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Please run: cd web && npm install"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating Python virtual environment..."
source .venv/bin/activate

# Start backend server
echo "🔧 Starting FastAPI backend server on http://localhost:8000..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "⚛️  Starting React frontend server on http://localhost:5173..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ Development servers started successfully!"
echo "=============================================="
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "⚛️  Frontend:     http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop servers
wait
