# Kanban Zero

AI-native, energy-aware task management for ADHD brains.

## Overview

Kanban Zero is a task management system designed specifically for ADHD brains, using AI to automatically parse and categorize tasks by energy level. Tasks flow through three energy-aware columns (High, Medium, Low) and get "shipped" when complete.

## Features

- **AI-Powered Task Parsing**: Natural language task input with automatic title extraction
- **Energy-Aware Columns**: High/Medium/Low energy categorization for better task selection
- **Three Interfaces**: REST API, CLI, and Web UI
- **Ship It**: Complete tasks with a satisfying "ship" action
- **ADHD-Friendly**: Designed to reduce friction and cognitive load

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd kanban_zero

# 2. Install dependencies
uv sync

# 3. Start all services (database, API, web)
./scripts/dev.sh

# 4. Run migrations
uv run alembic upgrade head

# 5. Try the CLI
uv run kz add "Write documentation for the API"
uv run kz list
uv run kz ship <task-id>
```

## Architecture

### Backend (`backend/kz/`)
FastAPI application with PostgreSQL + pgvector for task storage.

**Structure:**
- `api/` - FastAPI route handlers
- `db/` - Database connection and migrations
- `models/` - SQLAlchemy models and Pydantic schemas
- `repositories/` - Data access layer
- `services/` - Business logic (AI parsing, etc.)
- `config.py` - Application configuration

**Key Components:**
- `TaskParser` - Uses Claude to parse natural language into structured tasks
- `TaskRepository` - CRUD operations for tasks
- `tasks.py` - REST API endpoints

### CLI (`cli/kz/`)
Typer-based command-line interface.

**Commands:**
- `kz add <text>` - Add a new task
- `kz list [--column high|medium|low]` - List tasks
- `kz ship <task-id>` - Mark task as complete
- `kz wins` - Show completed tasks

### Web (`web/`)
Next.js 15 application with React 19 and Tailwind CSS.

**Features:**
- Drag-and-drop Kanban board using @dnd-kit
- Real-time task management
- Energy-aware column visualization
- Responsive design

## Project Structure

```
kanban_zero/
├── backend/
│   ├── kz/
│   │   ├── api/          # REST API endpoints
│   │   ├── db/           # Database setup and migrations
│   │   ├── models/       # Data models and schemas
│   │   ├── repositories/ # Data access layer
│   │   ├── services/     # Business logic
│   │   ├── config.py     # Configuration
│   │   └── main.py       # FastAPI app
│   └── tests/            # Backend tests
├── cli/
│   └── kz/
│       ├── commands/     # CLI commands
│       └── main.py       # CLI entry point
├── web/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   └── lib/              # Utilities and API client
├── scripts/
│   └── dev.sh            # Development startup script
├── docs/                 # Documentation
├── alembic.ini           # Database migration config
├── docker-compose.yml    # PostgreSQL setup
└── pyproject.toml        # Python dependencies
```

## Development

### Requirements
- Python 3.12+
- Node.js 18+
- PostgreSQL 16 with pgvector
- Claude API key (for AI parsing)

### Environment Setup

Create `.env` in project root:
```bash
DATABASE_URL=postgresql+asyncpg://kz:kz_dev_password@localhost:5432/kanban_zero
ANTHROPIC_API_KEY=your_api_key_here
KZ_ENV=development
```

Create `web/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development Commands

```bash
# Start all services
./scripts/dev.sh

# Run backend only
uv run uvicorn backend.kz.main:app --reload --port 8000

# Run frontend only
cd web && npm run dev

# Run CLI
uv run kz --help

# Database migrations
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head

# Testing
uv run pytest                    # Run all tests
uv run pytest backend/tests/ -v  # Verbose backend tests
uv run pytest --cov=backend.kz   # With coverage

# Code quality
uv run ruff check .              # Linting
uv run mypy backend/ cli/        # Type checking
```

### API Endpoints

**Base URL:** `http://localhost:8000`

```
GET    /health              # Health check
POST   /api/tasks           # Create task
GET    /api/tasks           # List tasks (?column=high|medium|low)
GET    /api/tasks/{id}      # Get task
PATCH  /api/tasks/{id}      # Update task
DELETE /api/tasks/{id}      # Delete task
POST   /api/tasks/{id}/ship # Ship task
```

### Database Schema

**Tasks Table:**
- `id` (UUID) - Primary key
- `raw_input` (TEXT) - Original user input
- `title` (TEXT) - Parsed task title
- `energy_column` (ENUM) - high/medium/low
- `shipped_at` (TIMESTAMP) - Completion time
- `created_via` (TEXT) - cli/api/web
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Testing

```bash
# Run all tests
uv run pytest -v

# Run specific test suites
uv run pytest backend/tests/test_api.py -v
uv run pytest backend/tests/test_integration.py -v

# With coverage
uv run pytest --cov=backend.kz --cov-report=html
```

## Deployment

1. Set production environment variables
2. Run database migrations
3. Build frontend: `cd web && npm run build`
4. Start backend: `uvicorn backend.kz.main:app --host 0.0.0.0 --port 8000`
5. Start frontend: `cd web && npm start`

## License

MIT

## Version

0.1.0 - V1 Release
