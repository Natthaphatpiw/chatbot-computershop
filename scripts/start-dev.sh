#!/bin/bash

# Development startup script for separated frontend/backend

echo "🚀 Starting IT Store Chatbot Development Environment"
echo "=================================================="

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please ensure you're in the project root."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
echo "🔍 Checking ports..."
check_port 8000 || echo "  Backend port 8000 may be in use"
check_port 3000 || echo "  Frontend port 3000 may be in use"

# Start backend
echo ""
echo "🐍 Starting Python Backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/pyvenv.cfg" ] || [ "requirements.txt" -nt "venv/pyvenv.cfg" ]; then
    echo "📚 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check environment file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found in backend. Please copy .env.example to .env and configure it."
    echo "  Continuing anyway, but you may encounter connection errors."
fi

# Start backend in background
echo "🚀 Starting FastAPI server..."
python start.py &
BACKEND_PID=$!

# Return to root directory
cd ..

# Wait a moment for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start. Check the logs above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Check frontend environment
if [ ! -f ".env.local" ]; then
    echo "⚠️  No .env.local file found for frontend. Please copy .env.local.example to .env.local"
    echo "  Continuing anyway, but API calls may fail."
fi

# Start frontend
echo ""
echo "⚛️  Starting Next.js Frontend..."
echo "🚀 Starting development server..."

# Install frontend dependencies if needed
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "📚 Installing Node.js dependencies..."
    npm install
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 5

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend failed to start. Check the logs above."
fi

echo ""
echo "🎉 Development environment is ready!"
echo "=================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🐍 Backend:  http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "👋 Goodbye!"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait