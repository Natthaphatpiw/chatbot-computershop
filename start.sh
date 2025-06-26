#!/bin/bash

# Chatbot Computer Shop Backend Startup Script

echo "🚀 Starting Chatbot Computer Shop Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    exit 1
fi

# Load environment variables
echo "🔐 Loading environment variables..."
source .env

# Check if MongoDB is running (optional)
if command -v mongod &> /dev/null; then
    if ! pgrep -x "mongod" > /dev/null; then
        echo "⚠️  MongoDB is not running. Please start MongoDB first."
        echo "   You can start MongoDB with: brew services start mongodb-community"
    fi
fi

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 ReDoc will be available at: http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 