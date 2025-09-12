#!/bin/bash

# Start development servers for HackGenix

echo "🚀 Starting HackGenix development servers..."

# Function to kill background processes on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start the FastAPI backend server
echo "📡 Starting FastAPI backend server..."
cd server
source venv/bin/activate
python agentic_rag.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the SvelteKit frontend server
echo "🎨 Starting SvelteKit frontend server..."
cd ..
npm run dev &
FRONTEND_PID=$!

echo "✅ Both servers are starting up..."
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
