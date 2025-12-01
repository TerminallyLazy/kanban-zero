#!/usr/bin/env bash
set -e

# Kanban Zero Development Startup Script
# Starts database, backend API, and frontend web server

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting Kanban Zero development environment..."
echo ""

# Check for required tools
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed. Please install uv first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install Node.js first."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    else
        echo "❌ No .env.example found. Please create .env manually."
        exit 1
    fi
fi

# Check for web/.env.local
if [ ! -f web/.env.local ]; then
    echo "⚠️  No web/.env.local file found. Creating..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > web/.env.local
fi

# Start PostgreSQL
echo "📦 Starting PostgreSQL..."
docker compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
max_attempts=30
attempt=0
until docker compose exec -T db pg_isready -U kz -d kanban_zero &> /dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Database failed to start after ${max_attempts} seconds"
        exit 1
    fi
    sleep 1
done
echo "✅ Database is ready"

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Start backend in background
echo "🔧 Starting backend API on http://localhost:8000..."
uv run uvicorn backend.kz.main:app --reload --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend on http://localhost:3000..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Services:"
echo "   Backend API:  http://localhost:8000"
echo "   Frontend Web: http://localhost:3000"
echo "   Database:     localhost:5432"
echo ""
echo "📚 Try the CLI:"
echo "   uv run kz add 'My first task'"
echo "   uv run kz list"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Trap Ctrl+C to kill all background processes
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    docker compose stop db
    echo "✅ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for background processes
wait
