# Kanban Zero V1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a working CLI + Web Kanban board with energy-based columns, AI task parsing, and semantic search.

**Architecture:** Python monorepo with FastAPI backend, Typer CLI, and Next.js frontend. PostgreSQL with pgvector for storage and semantic search. AI parsing via Claude API.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Typer, Rich, Next.js 14, React 18, Tailwind CSS, shadcn/ui, Framer Motion, PostgreSQL 16, pgvector, Claude API

---

## Phase 1: Project Foundation

### Task 1: Initialize Python Monorepo

**Files:**
- Create: `pyproject.toml`
- Create: `backend/kz/__init__.py`
- Create: `cli/kz/__init__.py`

**Step 1: Create pyproject.toml with uv**

```toml
[project]
name = "kanban-zero"
version = "0.1.0"
description = "AI-native, energy-aware task management for ADHD brains"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "pgvector>=0.3.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "typer>=0.14.0",
    "rich>=13.9.0",
    "httpx>=0.28.0",
    "anthropic>=0.39.0",
    "alembic>=1.14.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[project.scripts]
kz = "cli.kz.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["backend/kz", "cli/kz"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["backend/tests", "cli/tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
```

**Step 2: Create package init files**

Create `backend/kz/__init__.py`:
```python
"""Kanban Zero backend API."""

__version__ = "0.1.0"
```

Create `cli/kz/__init__.py`:
```python
"""Kanban Zero CLI."""

__version__ = "0.1.0"
```

**Step 3: Verify setup**

Run: `uv sync`
Expected: Dependencies installed, virtual environment created

**Step 4: Commit**

```bash
git add pyproject.toml backend/ cli/
git commit -m "chore: initialize python monorepo with uv"
```

---

### Task 2: Docker Compose for PostgreSQL + pgvector

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create docker-compose.yml**

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: kanban_zero_db
    environment:
      POSTGRES_USER: kz
      POSTGRES_PASSWORD: kz_dev_password
      POSTGRES_DB: kanban_zero
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kz -d kanban_zero"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

**Step 2: Create .env.example**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://kz:kz_dev_password@localhost:5432/kanban_zero

# AI
ANTHROPIC_API_KEY=sk-ant-your-key-here

# App
KZ_ENV=development
```

**Step 3: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
.uv/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local

# Build
dist/
build/
*.egg-info/

# Node (for web/)
node_modules/
.next/
out/

# OS
.DS_Store
Thumbs.db
```

**Step 4: Start database and verify**

Run: `docker compose up -d`
Run: `docker compose ps`
Expected: kanban_zero_db running, healthy

**Step 5: Commit**

```bash
git add docker-compose.yml .env.example .gitignore
git commit -m "chore: add docker compose for postgres + pgvector"
```

---

### Task 3: Database Configuration and Connection

**Files:**
- Create: `backend/kz/config.py`
- Create: `backend/kz/db/__init__.py`
- Create: `backend/kz/db/database.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_db.py`

**Step 1: Write the failing test**

Create `backend/tests/__init__.py`:
```python
"""Backend tests."""
```

Create `backend/tests/test_db.py`:
```python
import pytest
from sqlalchemy import text

from backend.kz.db.database import get_async_engine


@pytest.mark.asyncio
async def test_database_connection():
    """Verify we can connect to the database."""
    engine = get_async_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_pgvector_extension():
    """Verify pgvector extension is available."""
    engine = get_async_engine()
    async with engine.connect() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        assert result.scalar() == "vector"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_db.py -v`
Expected: FAIL with ModuleNotFoundError (config/database don't exist)

**Step 3: Create config.py**

Create `backend/kz/config.py`:
```python
"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://kz:kz_dev_password@localhost:5432/kanban_zero"

    # AI
    anthropic_api_key: str = ""

    # App
    kz_env: str = "development"

    @property
    def is_development(self) -> bool:
        return self.kz_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

**Step 4: Create database.py**

Create `backend/kz/db/__init__.py`:
```python
"""Database module."""

from backend.kz.db.database import get_async_engine, get_async_session

__all__ = ["get_async_engine", "get_async_session"]
```

Create `backend/kz/db/database.py`:
```python
"""Database connection and session management."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.kz.config import get_settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    """Get cached async database engine."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.is_development,
        pool_pre_ping=True,
    )


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get async session maker."""
    return async_sessionmaker(
        get_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async_session = get_async_session_maker()
    async with async_session() as session:
        yield session
```

**Step 5: Create .env file for tests**

Run: `cp .env.example .env`

**Step 6: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_db.py -v`
Expected: 2 passed

**Step 7: Commit**

```bash
git add backend/kz/config.py backend/kz/db/ backend/tests/
git commit -m "feat: add database configuration and connection"
```

---

## Phase 2: Core Models

### Task 4: Task Model (SQLAlchemy + Pydantic)

**Files:**
- Create: `backend/kz/models/__init__.py`
- Create: `backend/kz/models/base.py`
- Create: `backend/kz/models/task.py`
- Create: `backend/tests/test_models.py`

**Step 1: Write the failing test**

Create `backend/tests/test_models.py`:
```python
import pytest
from sqlalchemy import text

from backend.kz.db.database import get_async_engine
from backend.kz.models.base import Base
from backend.kz.models.task import EnergyColumn, Task, TaskCreate


def test_task_create_schema():
    """Test TaskCreate pydantic schema."""
    task = TaskCreate(raw_input="fix the auth bug")
    assert task.raw_input == "fix the auth bug"
    assert task.energy_column == EnergyColumn.QUICK_WIN  # default


def test_task_create_with_energy():
    """Test TaskCreate with explicit energy column."""
    task = TaskCreate(raw_input="design the system", energy_column=EnergyColumn.HYPERFOCUS)
    assert task.energy_column == EnergyColumn.HYPERFOCUS


@pytest.mark.asyncio
async def test_task_table_creation():
    """Test that task table can be created."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Verify table exists
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'task'")
        )
        assert result.scalar() == "task"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_models.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create base.py**

Create `backend/kz/models/__init__.py`:
```python
"""Database models."""

from backend.kz.models.base import Base
from backend.kz.models.task import EnergyColumn, Task, TaskCreate, TaskRead, TaskUpdate

__all__ = [
    "Base",
    "EnergyColumn",
    "Task",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
]
```

Create `backend/kz/models/base.py`:
```python
"""SQLAlchemy base model."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass
```

**Step 4: Create task.py**

Create `backend/kz/models/task.py`:
```python
"""Task model and schemas."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.kz.models.base import Base


class EnergyColumn(StrEnum):
    """Energy-based Kanban columns."""

    HYPERFOCUS = "hyperfocus"
    QUICK_WIN = "quick_win"
    LOW_ENERGY = "low_energy"
    SHIPPED = "shipped"


class CreatedVia(StrEnum):
    """How the task was created."""

    CLI = "cli"
    SLACK = "slack"
    WEB = "web"
    API = "api"


class Task(Base):
    """Task database model."""

    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)

    energy_column: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EnergyColumn.QUICK_WIN.value
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_via: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CreatedVia.CLI.value
    )


# Pydantic schemas


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    raw_input: str = Field(..., min_length=1, max_length=5000)
    energy_column: EnergyColumn = EnergyColumn.QUICK_WIN
    created_via: CreatedVia = CreatedVia.CLI


class TaskRead(BaseModel):
    """Schema for reading a task."""

    id: UUID
    title: str
    body: str | None
    raw_input: str
    energy_column: EnergyColumn
    position: int
    created_at: datetime
    updated_at: datetime
    shipped_at: datetime | None
    created_via: CreatedVia

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str | None = None
    body: str | None = None
    energy_column: EnergyColumn | None = None
    position: int | None = None
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_models.py -v`
Expected: 3 passed

**Step 6: Commit**

```bash
git add backend/kz/models/
git commit -m "feat: add Task model with energy columns and pgvector"
```

---

### Task 5: Tag Model

**Files:**
- Modify: `backend/kz/models/__init__.py`
- Create: `backend/kz/models/tag.py`
- Modify: `backend/tests/test_models.py`

**Step 1: Write the failing test**

Add to `backend/tests/test_models.py`:
```python
from backend.kz.models.tag import Tag, TagCreate, TaskTag


def test_tag_create_schema():
    """Test TagCreate pydantic schema."""
    tag = TagCreate(name="auth")
    assert tag.name == "auth"
    assert tag.color is None
    assert tag.icon is None


def test_tag_create_with_color():
    """Test TagCreate with color and icon."""
    tag = TagCreate(name="frontend", color="#3B82F6", icon="code")
    assert tag.color == "#3B82F6"
    assert tag.icon == "code"


@pytest.mark.asyncio
async def test_tag_table_creation():
    """Test that tag and task_tag tables can be created."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'tag'")
        )
        assert result.scalar() == "tag"

        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'task_tag'")
        )
        assert result.scalar() == "task_tag"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_models.py::test_tag_create_schema -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create tag.py**

Create `backend/kz/models/tag.py`:
```python
"""Tag model and schemas."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Float, ForeignKey, String, func, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.kz.models.base import Base


class Tag(Base):
    """Tag database model."""

    __tablename__ = "tag"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # hex color
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Material icon
    auto_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    tasks: Mapped[list["TaskTag"]] = relationship(back_populates="tag")


class TaskTag(Base):
    """Many-to-many junction table for tasks and tags."""

    __tablename__ = "task_tag"

    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("task.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-1 if AI-assigned
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    tag: Mapped["Tag"] = relationship(back_populates="tasks")


# Pydantic schemas


class TagCreate(BaseModel):
    """Schema for creating a tag."""

    name: str = Field(..., min_length=1, max_length=100)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(None, max_length=50)


class TagRead(BaseModel):
    """Schema for reading a tag."""

    id: UUID
    name: str
    color: str | None
    icon: str | None
    auto_generated: bool

    model_config = {"from_attributes": True}
```

**Step 4: Update models __init__.py**

Update `backend/kz/models/__init__.py`:
```python
"""Database models."""

from backend.kz.models.base import Base
from backend.kz.models.tag import Tag, TagCreate, TagRead, TaskTag
from backend.kz.models.task import (
    CreatedVia,
    EnergyColumn,
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)

__all__ = [
    "Base",
    "CreatedVia",
    "EnergyColumn",
    "Tag",
    "TagCreate",
    "TagRead",
    "Task",
    "TaskCreate",
    "TaskRead",
    "TaskTag",
    "TaskUpdate",
]
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_models.py -v`
Expected: 6 passed

**Step 6: Commit**

```bash
git add backend/kz/models/
git commit -m "feat: add Tag model with task_tag junction table"
```

---

### Task 6: Activity Log Model

**Files:**
- Create: `backend/kz/models/activity.py`
- Modify: `backend/kz/models/__init__.py`
- Modify: `backend/tests/test_models.py`

**Step 1: Write the failing test**

Add to `backend/tests/test_models.py`:
```python
from backend.kz.models.activity import ActivityLog, Actor, ActivityLogRead


def test_activity_log_read_schema():
    """Test ActivityLogRead schema has correct fields."""
    # Just verify the schema exists and has expected fields
    assert hasattr(ActivityLogRead, "model_fields")
    assert "id" in ActivityLogRead.model_fields
    assert "action" in ActivityLogRead.model_fields
    assert "actor" in ActivityLogRead.model_fields


@pytest.mark.asyncio
async def test_activity_log_table_creation():
    """Test that activity_log table can be created."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'activity_log'")
        )
        assert result.scalar() == "activity_log"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_models.py::test_activity_log_read_schema -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create activity.py**

Create `backend/kz/models/activity.py`:
```python
"""Activity log model and schemas."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.kz.models.base import Base


class Actor(StrEnum):
    """Who performed the action."""

    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ActivityLog(Base):
    """Activity log database model for audit trail and dopamine fuel."""

    __tablename__ = "activity_log"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("task.id", ondelete="SET NULL"), nullable=True
    )
    actor: Mapped[str] = mapped_column(String(10), nullable=False, default=Actor.USER.value)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# Pydantic schemas


class ActivityLogRead(BaseModel):
    """Schema for reading an activity log entry."""

    id: UUID
    task_id: UUID | None
    actor: Actor
    action: str
    details: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

**Step 4: Update models __init__.py**

Update `backend/kz/models/__init__.py`:
```python
"""Database models."""

from backend.kz.models.activity import ActivityLog, ActivityLogRead, Actor
from backend.kz.models.base import Base
from backend.kz.models.tag import Tag, TagCreate, TagRead, TaskTag
from backend.kz.models.task import (
    CreatedVia,
    EnergyColumn,
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)

__all__ = [
    "ActivityLog",
    "ActivityLogRead",
    "Actor",
    "Base",
    "CreatedVia",
    "EnergyColumn",
    "Tag",
    "TagCreate",
    "TagRead",
    "Task",
    "TaskCreate",
    "TaskRead",
    "TaskTag",
    "TaskUpdate",
]
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_models.py -v`
Expected: 8 passed

**Step 6: Commit**

```bash
git add backend/kz/models/
git commit -m "feat: add ActivityLog model for audit trail"
```

---

### Task 7: Alembic Migrations Setup

**Files:**
- Create: `backend/kz/db/migrations/env.py`
- Create: `backend/kz/db/migrations/script.py.mako`
- Create: `alembic.ini`

**Step 1: Initialize alembic**

Run: `cd /Users/lazy/Projects/kanban_zero && uv run alembic init backend/kz/db/migrations`

**Step 2: Configure alembic.ini**

Edit `alembic.ini` (only key changes shown):
```ini
[alembic]
script_location = backend/kz/db/migrations
prepend_sys_path = .
sqlalchemy.url = postgresql+asyncpg://kz:kz_dev_password@localhost:5432/kanban_zero
```

**Step 3: Update env.py for async and models**

Replace `backend/kz/db/migrations/env.py` with:
```python
"""Alembic migrations environment."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from backend.kz.config import get_settings
from backend.kz.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from settings."""
    return get_settings().database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 4: Create initial migration**

Run: `uv run alembic revision --autogenerate -m "initial schema"`
Expected: Migration file created in `backend/kz/db/migrations/versions/`

**Step 5: Edit migration to add pgvector extension**

Edit the generated migration file (in versions/), add at the top of `upgrade()`:
```python
def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ... rest of auto-generated code
```

**Step 6: Run migration**

Run: `uv run alembic upgrade head`
Expected: Migration applied successfully

**Step 7: Verify tables exist**

Run: `docker exec -it kanban_zero_db psql -U kz -d kanban_zero -c "\dt"`
Expected: Tables listed: task, tag, task_tag, activity_log, alembic_version

**Step 8: Commit**

```bash
git add alembic.ini backend/kz/db/migrations/
git commit -m "feat: add alembic migrations with initial schema"
```

---

## Phase 3: Task Service & API

### Task 8: Task Repository

**Files:**
- Create: `backend/kz/repositories/__init__.py`
- Create: `backend/kz/repositories/task.py`
- Create: `backend/tests/test_repositories.py`

**Step 1: Write the failing test**

Create `backend/tests/test_repositories.py`:
```python
import pytest
from sqlalchemy import text

from backend.kz.db.database import get_async_engine, get_async_session_maker
from backend.kz.models import Base, EnergyColumn, TaskCreate
from backend.kz.repositories.task import TaskRepository


@pytest.fixture
async def db_session():
    """Create a fresh database session for each test."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@pytest.mark.asyncio
async def test_create_task(db_session):
    """Test creating a task."""
    repo = TaskRepository(db_session)
    task_data = TaskCreate(raw_input="fix the auth bug")

    task = await repo.create(task_data, title="Fix the auth bug")

    assert task.id is not None
    assert task.title == "Fix the auth bug"
    assert task.raw_input == "fix the auth bug"
    assert task.energy_column == EnergyColumn.QUICK_WIN.value


@pytest.mark.asyncio
async def test_get_task_by_id(db_session):
    """Test retrieving a task by ID."""
    repo = TaskRepository(db_session)
    task_data = TaskCreate(raw_input="test task")
    created = await repo.create(task_data, title="Test Task")

    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Test Task"


@pytest.mark.asyncio
async def test_list_tasks_by_column(db_session):
    """Test listing tasks by energy column."""
    repo = TaskRepository(db_session)

    await repo.create(
        TaskCreate(raw_input="quick task", energy_column=EnergyColumn.QUICK_WIN),
        title="Quick Task",
    )
    await repo.create(
        TaskCreate(raw_input="focus task", energy_column=EnergyColumn.HYPERFOCUS),
        title="Focus Task",
    )

    quick_wins = await repo.list_by_column(EnergyColumn.QUICK_WIN)

    assert len(quick_wins) == 1
    assert quick_wins[0].title == "Quick Task"


@pytest.mark.asyncio
async def test_ship_task(db_session):
    """Test shipping (completing) a task."""
    repo = TaskRepository(db_session)
    task = await repo.create(TaskCreate(raw_input="ship me"), title="Ship Me")

    shipped = await repo.ship(task.id)

    assert shipped is not None
    assert shipped.energy_column == EnergyColumn.SHIPPED.value
    assert shipped.shipped_at is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_repositories.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create task repository**

Create `backend/kz/repositories/__init__.py`:
```python
"""Data repositories."""

from backend.kz.repositories.task import TaskRepository

__all__ = ["TaskRepository"]
```

Create `backend/kz/repositories/task.py`:
```python
"""Task repository for database operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.kz.models import EnergyColumn, Task, TaskCreate, TaskUpdate


class TaskRepository:
    """Repository for Task database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TaskCreate, title: str, body: str | None = None) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            body=body,
            raw_input=data.raw_input,
            energy_column=data.energy_column.value,
            created_via=data.created_via.value,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get a task by ID."""
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_by_short_id(self, short_id: str) -> Task | None:
        """Get a task by partial ID match (first N characters)."""
        result = await self.session.execute(
            select(Task).where(Task.id.cast(str).startswith(short_id))
        )
        return result.scalar_one_or_none()

    async def list_by_column(self, column: EnergyColumn) -> list[Task]:
        """List all tasks in a specific energy column."""
        result = await self.session.execute(
            select(Task)
            .where(Task.energy_column == column.value)
            .order_by(Task.position, Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[Task]:
        """List all non-shipped tasks."""
        result = await self.session.execute(
            select(Task)
            .where(Task.energy_column != EnergyColumn.SHIPPED.value)
            .order_by(Task.energy_column, Task.position, Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, task_id: UUID, data: TaskUpdate) -> Task | None:
        """Update a task."""
        task = await self.get_by_id(task_id)
        if task is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "energy_column" and value is not None:
                value = value.value
            setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def ship(self, task_id: UUID) -> Task | None:
        """Mark a task as shipped."""
        task = await self.get_by_id(task_id)
        if task is None:
            return None

        task.energy_column = EnergyColumn.SHIPPED.value
        task.shipped_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: UUID) -> bool:
        """Delete a task."""
        task = await self.get_by_id(task_id)
        if task is None:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_repositories.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add backend/kz/repositories/
git commit -m "feat: add TaskRepository for database operations"
```

---

### Task 9: AI Parser Service (Task Intent Parsing)

**Files:**
- Create: `backend/kz/services/__init__.py`
- Create: `backend/kz/services/parser.py`
- Create: `backend/tests/test_services.py`

**Step 1: Write the failing test**

Create `backend/tests/test_services.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch

from backend.kz.models import EnergyColumn
from backend.kz.services.parser import ParsedTask, TaskParser


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client."""
    with patch("backend.kz.services.parser.AsyncAnthropic") as mock:
        yield mock


@pytest.mark.asyncio
async def test_parser_extracts_title(mock_anthropic):
    """Test that parser extracts a clean title."""
    mock_client = AsyncMock()
    mock_client.messages.create.return_value = AsyncMock(
        content=[AsyncMock(text='{"title": "Fix authentication bug", "energy": "quick_win", "tags": ["auth", "bug"]}')]
    )
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("fix the auth bug thats been bothering me")

    assert result.title == "Fix authentication bug"
    assert result.energy == EnergyColumn.QUICK_WIN


@pytest.mark.asyncio
async def test_parser_extracts_tags(mock_anthropic):
    """Test that parser extracts relevant tags."""
    mock_client = AsyncMock()
    mock_client.messages.create.return_value = AsyncMock(
        content=[AsyncMock(text='{"title": "Build Slack integration", "energy": "hyperfocus", "tags": ["slack", "integration"]}')]
    )
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("build the slack integration for notifications")

    assert "slack" in result.tags
    assert result.energy == EnergyColumn.HYPERFOCUS


@pytest.mark.asyncio
async def test_parser_handles_explicit_energy(mock_anthropic):
    """Test that explicit energy override is respected."""
    mock_client = AsyncMock()
    mock_client.messages.create.return_value = AsyncMock(
        content=[AsyncMock(text='{"title": "Update README", "energy": "quick_win", "tags": ["docs"]}')]
    )
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("update readme", energy_override=EnergyColumn.LOW_ENERGY)

    # Override should take precedence
    assert result.energy == EnergyColumn.LOW_ENERGY


@pytest.mark.asyncio
async def test_parser_fallback_on_error(mock_anthropic):
    """Test graceful fallback when AI fails."""
    mock_client = AsyncMock()
    mock_client.messages.create.side_effect = Exception("API error")
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("some task that fails")

    # Should return input as title, default energy
    assert result.title == "some task that fails"
    assert result.energy == EnergyColumn.QUICK_WIN
    assert result.tags == []
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_services.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create parser service**

Create `backend/kz/services/__init__.py`:
```python
"""Business logic services."""

from backend.kz.services.parser import ParsedTask, TaskParser

__all__ = ["ParsedTask", "TaskParser"]
```

Create `backend/kz/services/parser.py`:
```python
"""AI-powered task parsing service."""

import json
import logging
from dataclasses import dataclass

from anthropic import AsyncAnthropic

from backend.kz.config import get_settings
from backend.kz.models import EnergyColumn

logger = logging.getLogger(__name__)

PARSE_PROMPT = """You are a task parser for a Kanban board. Parse the user's input and extract:

1. **title**: A clean, concise task title (imperative form, e.g., "Fix auth bug" not "Fixing auth bug")
2. **energy**: Which energy column fits best:
   - "hyperfocus" - Deep work, complex, requires concentration (>30 min)
   - "quick_win" - Small tasks, quick dopamine hits (<15 min)
   - "low_energy" - Mindless but useful (docs, cleanup, admin)
3. **tags**: 1-3 relevant lowercase tags (e.g., ["auth", "bug", "backend"])

Respond ONLY with valid JSON:
{"title": "...", "energy": "...", "tags": ["...", "..."]}

User input: {input}"""


@dataclass
class ParsedTask:
    """Result of parsing a task input."""

    title: str
    energy: EnergyColumn
    tags: list[str]


class TaskParser:
    """AI-powered task intent parser."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def parse(
        self,
        raw_input: str,
        energy_override: EnergyColumn | None = None,
    ) -> ParsedTask:
        """Parse raw task input into structured data."""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=256,
                messages=[
                    {"role": "user", "content": PARSE_PROMPT.format(input=raw_input)}
                ],
            )

            result = json.loads(response.content[0].text)

            energy = energy_override or EnergyColumn(result.get("energy", "quick_win"))
            tags = result.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]

            return ParsedTask(
                title=result.get("title", raw_input),
                energy=energy,
                tags=[t.lower().strip() for t in tags[:5]],  # Max 5 tags
            )

        except Exception as e:
            logger.warning(f"Failed to parse task with AI: {e}")
            # Graceful fallback
            return ParsedTask(
                title=raw_input,
                energy=energy_override or EnergyColumn.QUICK_WIN,
                tags=[],
            )
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_services.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add backend/kz/services/
git commit -m "feat: add AI-powered TaskParser service"
```

---

### Task 10: FastAPI Application with Task Endpoints

**Files:**
- Create: `backend/kz/main.py`
- Create: `backend/kz/api/__init__.py`
- Create: `backend/kz/api/tasks.py`
- Create: `backend/tests/test_api.py`

**Step 1: Write the failing test**

Create `backend/tests/test_api.py`:
```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.kz.db.database import get_async_engine, get_async_session_maker
from backend.kz.main import app
from backend.kz.models import Base


@pytest.fixture
async def setup_db():
    """Set up clean database for each test."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client(setup_db):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_task(client):
    """Test creating a task via API."""
    response = await client.post(
        "/api/tasks",
        json={"raw_input": "fix the auth bug", "energy_column": "quick_win"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["raw_input"] == "fix the auth bug"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tasks(client):
    """Test listing tasks."""
    # Create a task first
    await client.post(
        "/api/tasks",
        json={"raw_input": "test task"},
    )

    response = await client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_ship_task(client):
    """Test shipping a task."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={"raw_input": "ship me"},
    )
    task_id = create_response.json()["id"]

    # Ship it
    response = await client.post(f"/api/tasks/{task_id}/ship")
    assert response.status_code == 200
    data = response.json()
    assert data["energy_column"] == "shipped"
    assert data["shipped_at"] is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_api.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create FastAPI main app**

Create `backend/kz/main.py`:
```python
"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.kz.api import tasks
from backend.kz.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Kanban Zero API",
        description="AI-native, energy-aware task management",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Next.js dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "env": settings.kz_env}

    return app


app = create_app()
```

**Step 4: Create tasks API router**

Create `backend/kz/api/__init__.py`:
```python
"""API routers."""
```

Create `backend/kz/api/tasks.py`:
```python
"""Task API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.kz.db.database import get_async_session
from backend.kz.models import EnergyColumn, TaskCreate, TaskRead, TaskUpdate
from backend.kz.repositories.task import TaskRepository
from backend.kz.services.parser import TaskParser

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_async_session)]


def get_task_repository(session: DbSession) -> TaskRepository:
    """Dependency for task repository."""
    return TaskRepository(session)


TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskRead)
async def create_task(data: TaskCreate, repo: TaskRepo) -> TaskRead:
    """Create a new task with AI parsing."""
    parser = TaskParser()
    parsed = await parser.parse(data.raw_input, energy_override=data.energy_column)

    task = await repo.create(
        data=TaskCreate(
            raw_input=data.raw_input,
            energy_column=parsed.energy,
            created_via=data.created_via,
        ),
        title=parsed.title,
    )
    return TaskRead.model_validate(task)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    repo: TaskRepo,
    column: EnergyColumn | None = None,
) -> list[TaskRead]:
    """List tasks, optionally filtered by column."""
    if column:
        tasks = await repo.list_by_column(column)
    else:
        tasks = await repo.list_active()
    return [TaskRead.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, repo: TaskRepo) -> TaskRead:
    """Get a specific task by ID."""
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: UUID, data: TaskUpdate, repo: TaskRepo) -> TaskRead:
    """Update a task."""
    task = await repo.update(task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, repo: TaskRepo) -> None:
    """Delete a task."""
    deleted = await repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/ship", response_model=TaskRead)
async def ship_task(task_id: UUID, repo: TaskRepo) -> TaskRead:
    """Mark a task as shipped (completed)."""
    task = await repo.ship(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest backend/tests/test_api.py -v`
Expected: 4 passed

**Step 6: Commit**

```bash
git add backend/kz/main.py backend/kz/api/
git commit -m "feat: add FastAPI app with task CRUD endpoints"
```

---

## Phase 4: CLI Application

### Task 11: CLI Skeleton with Typer

**Files:**
- Create: `cli/kz/main.py`
- Create: `cli/kz/config.py`
- Create: `cli/tests/__init__.py`
- Create: `cli/tests/test_cli.py`

**Step 1: Write the failing test**

Create `cli/tests/__init__.py`:
```python
"""CLI tests."""
```

Create `cli/tests/test_cli.py`:
```python
from typer.testing import CliRunner

from cli.kz.main import app

runner = CliRunner()


def test_app_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_app_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Kanban Zero" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest cli/tests/test_cli.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Create CLI main**

Create `cli/kz/config.py`:
```python
"""CLI configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CLISettings(BaseSettings):
    """CLI settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_base_url: str = "http://localhost:8000"


@lru_cache
def get_cli_settings() -> CLISettings:
    """Get cached CLI settings."""
    return CLISettings()
```

Create `cli/kz/main.py`:
```python
"""Kanban Zero CLI entry point."""

from typing import Annotated, Optional

import typer

from cli.kz import __version__

app = typer.Typer(
    name="kz",
    help="Kanban Zero - AI-native, energy-aware task management for ADHD brains",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"Kanban Zero CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Kanban Zero - Your ADHD-friendly task companion."""
    pass


if __name__ == "__main__":
    app()
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest cli/tests/test_cli.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add cli/kz/main.py cli/kz/config.py cli/tests/
git commit -m "feat: add CLI skeleton with Typer"
```

---

### Task 12: CLI `add` Command

**Files:**
- Create: `cli/kz/commands/__init__.py`
- Create: `cli/kz/commands/add.py`
- Create: `cli/kz/api_client.py`
- Modify: `cli/kz/main.py`
- Modify: `cli/tests/test_cli.py`

**Step 1: Write the failing test**

Add to `cli/tests/test_cli.py`:
```python
from unittest.mock import AsyncMock, patch


def test_add_command_help():
    """Test add command shows help."""
    result = runner.invoke(app, ["add", "--help"])
    assert result.exit_code == 0
    assert "Add a new task" in result.stdout


@patch("cli.kz.commands.add.APIClient")
def test_add_task(mock_client_class):
    """Test adding a task."""
    mock_client = AsyncMock()
    mock_client.create_task.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Fix the auth bug",
        "energy_column": "quick_win",
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["add", "fix the auth bug"])

    assert result.exit_code == 0
    assert "Fix the auth bug" in result.stdout


@patch("cli.kz.commands.add.APIClient")
def test_add_task_with_energy(mock_client_class):
    """Test adding a task with explicit energy."""
    mock_client = AsyncMock()
    mock_client.create_task.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Refactor the whole thing",
        "energy_column": "hyperfocus",
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["add", "refactor the whole thing", "--energy", "hyperfocus"])

    assert result.exit_code == 0
    mock_client.create_task.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest cli/tests/test_cli.py::test_add_command_help -v`
Expected: FAIL (add command doesn't exist)

**Step 3: Create API client**

Create `cli/kz/api_client.py`:
```python
"""HTTP client for Kanban Zero API."""

from types import TracebackType
from typing import Any, Self

import httpx

from cli.kz.config import get_cli_settings


class APIClient:
    """Async HTTP client for the Kanban Zero API."""

    def __init__(self) -> None:
        settings = get_cli_settings()
        self.base_url = settings.api_base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with APIClient()' context.")
        return self._client

    async def create_task(
        self,
        raw_input: str,
        energy_column: str | None = None,
        created_via: str = "cli",
    ) -> dict[str, Any]:
        """Create a new task."""
        payload: dict[str, Any] = {
            "raw_input": raw_input,
            "created_via": created_via,
        }
        if energy_column:
            payload["energy_column"] = energy_column

        response = await self.client.post("/api/tasks", json=payload)
        response.raise_for_status()
        return response.json()

    async def list_tasks(self, column: str | None = None) -> list[dict[str, Any]]:
        """List tasks, optionally filtered by column."""
        params = {}
        if column:
            params["column"] = column
        response = await self.client.get("/api/tasks", params=params)
        response.raise_for_status()
        return response.json()

    async def ship_task(self, task_id: str) -> dict[str, Any]:
        """Ship (complete) a task."""
        response = await self.client.post(f"/api/tasks/{task_id}/ship")
        response.raise_for_status()
        return response.json()

    async def get_task(self, task_id: str) -> dict[str, Any]:
        """Get a specific task."""
        response = await self.client.get(f"/api/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
```

**Step 4: Create add command**

Create `cli/kz/commands/__init__.py`:
```python
"""CLI commands."""
```

Create `cli/kz/commands/add.py`:
```python
"""Add task command."""

import asyncio
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from cli.kz.api_client import APIClient

console = Console()

ENERGY_ICONS = {
    "hyperfocus": "[red]fire[/red]",
    "quick_win": "[yellow]bolt[/yellow]",
    "low_energy": "[blue]self_improvement[/blue]",
    "shipped": "[green]rocket_launch[/green]",
}


def add(
    task: Annotated[str, typer.Argument(help="Task description (free text)")],
    energy: Annotated[
        Optional[str],
        typer.Option(
            "--energy",
            "-e",
            help="Energy column: hyperfocus, quick_win, low_energy",
        ),
    ] = None,
) -> None:
    """Add a new task with AI parsing."""
    asyncio.run(_add_task(task, energy))


async def _add_task(task: str, energy: str | None) -> None:
    """Async implementation of add command."""
    try:
        async with APIClient() as client:
            result = await client.create_task(task, energy_column=energy)

        icon = ENERGY_ICONS.get(result["energy_column"], "")
        console.print(
            Panel(
                f"[bold]{result['title']}[/bold]\n\n"
                f"{icon} {result['energy_column'].replace('_', ' ').title()}",
                title="[green]Task Added[/green]",
                subtitle=f"ID: {result['id'][:8]}",
            )
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

**Step 5: Update main.py to include add command**

Update `cli/kz/main.py`:
```python
"""Kanban Zero CLI entry point."""

from typing import Annotated, Optional

import typer

from cli.kz import __version__
from cli.kz.commands.add import add

app = typer.Typer(
    name="kz",
    help="Kanban Zero - AI-native, energy-aware task management for ADHD brains",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"Kanban Zero CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Kanban Zero - Your ADHD-friendly task companion."""
    pass


# Register commands
app.command()(add)


if __name__ == "__main__":
    app()
```

**Step 6: Run tests to verify they pass**

Run: `uv run pytest cli/tests/test_cli.py -v`
Expected: 5 passed

**Step 7: Commit**

```bash
git add cli/kz/
git commit -m "feat: add CLI 'add' command with API client"
```

---

### Task 13: CLI `list` Command

**Files:**
- Create: `cli/kz/commands/list.py`
- Create: `cli/kz/display.py`
- Modify: `cli/kz/main.py`
- Modify: `cli/tests/test_cli.py`

**Step 1: Write the failing test**

Add to `cli/tests/test_cli.py`:
```python
@patch("cli.kz.commands.list.APIClient")
def test_list_tasks(mock_client_class):
    """Test listing tasks."""
    mock_client = AsyncMock()
    mock_client.list_tasks.return_value = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Task One",
            "energy_column": "quick_win",
            "created_at": "2025-01-01T00:00:00Z",
        },
        {
            "id": "223e4567-e89b-12d3-a456-426614174000",
            "title": "Task Two",
            "energy_column": "hyperfocus",
            "created_at": "2025-01-01T00:00:00Z",
        },
    ]
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Task One" in result.stdout
    assert "Task Two" in result.stdout


@patch("cli.kz.commands.list.APIClient")
def test_list_tasks_by_column(mock_client_class):
    """Test listing tasks filtered by column."""
    mock_client = AsyncMock()
    mock_client.list_tasks.return_value = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Quick Task",
            "energy_column": "quick_win",
            "created_at": "2025-01-01T00:00:00Z",
        },
    ]
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list", "--column", "quick_win"])

    assert result.exit_code == 0
    mock_client.list_tasks.assert_called_once_with(column="quick_win")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest cli/tests/test_cli.py::test_list_tasks -v`
Expected: FAIL

**Step 3: Create display helpers**

Create `cli/kz/display.py`:
```python
"""Rich display helpers for CLI output."""

from rich.console import Console
from rich.table import Table

console = Console()

ENERGY_STYLES = {
    "hyperfocus": ("red", "local_fire_department"),
    "quick_win": ("yellow", "bolt"),
    "low_energy": ("blue", "self_improvement"),
    "shipped": ("green", "rocket_launch"),
}


def display_tasks_table(tasks: list[dict], title: str = "Tasks") -> None:
    """Display tasks in a formatted table."""
    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="bold")
    table.add_column("Energy", justify="center")

    for task in tasks:
        energy = task["energy_column"]
        style, icon = ENERGY_STYLES.get(energy, ("white", "task"))
        energy_display = f"[{style}]{icon}[/{style}]"

        table.add_row(
            task["id"][:8],
            task["title"],
            energy_display,
        )

    console.print(table)


def display_tasks_by_column(tasks: list[dict]) -> None:
    """Display tasks grouped by energy column."""
    columns = {
        "hyperfocus": [],
        "quick_win": [],
        "low_energy": [],
    }

    for task in tasks:
        col = task["energy_column"]
        if col in columns:
            columns[col].append(task)

    for col_name, col_tasks in columns.items():
        if col_tasks:
            style, icon = ENERGY_STYLES.get(col_name, ("white", "task"))
            console.print(f"\n[{style} bold]{icon} {col_name.upper().replace('_', ' ')}[/{style} bold]")
            for task in col_tasks:
                console.print(f"  [{style}]•[/{style}] {task['title']} [dim]({task['id'][:8]})[/dim]")
```

**Step 4: Create list command**

Create `cli/kz/commands/list.py`:
```python
"""List tasks command."""

import asyncio
from typing import Annotated, Optional

import typer
from rich.console import Console

from cli.kz.api_client import APIClient
from cli.kz.display import display_tasks_by_column, display_tasks_table

console = Console()


def list_tasks(
    column: Annotated[
        Optional[str],
        typer.Option(
            "--column",
            "-c",
            help="Filter by energy column: hyperfocus, quick_win, low_energy",
        ),
    ] = None,
    table: Annotated[
        bool,
        typer.Option("--table", "-t", help="Display as table instead of grouped"),
    ] = False,
) -> None:
    """List all active tasks."""
    asyncio.run(_list_tasks(column, table))


async def _list_tasks(column: str | None, as_table: bool) -> None:
    """Async implementation of list command."""
    try:
        async with APIClient() as client:
            tasks = await client.list_tasks(column=column)

        if as_table:
            display_tasks_table(tasks)
        else:
            display_tasks_by_column(tasks)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

**Step 5: Update main.py**

Update `cli/kz/main.py` to add the list command:
```python
"""Kanban Zero CLI entry point."""

from typing import Annotated, Optional

import typer

from cli.kz import __version__
from cli.kz.commands.add import add
from cli.kz.commands.list import list_tasks

app = typer.Typer(
    name="kz",
    help="Kanban Zero - AI-native, energy-aware task management for ADHD brains",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"Kanban Zero CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Kanban Zero - Your ADHD-friendly task companion."""
    pass


# Register commands
app.command()(add)
app.command("list")(list_tasks)


if __name__ == "__main__":
    app()
```

**Step 6: Run tests to verify they pass**

Run: `uv run pytest cli/tests/test_cli.py -v`
Expected: 7 passed

**Step 7: Commit**

```bash
git add cli/kz/
git commit -m "feat: add CLI 'list' command with Rich display"
```

---

### Task 14: CLI `ship` Command

**Files:**
- Create: `cli/kz/commands/ship.py`
- Modify: `cli/kz/main.py`
- Modify: `cli/tests/test_cli.py`

**Step 1: Write the failing test**

Add to `cli/tests/test_cli.py`:
```python
@patch("cli.kz.commands.ship.APIClient")
def test_ship_task(mock_client_class):
    """Test shipping a task."""
    mock_client = AsyncMock()
    mock_client.ship_task.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Completed Task",
        "energy_column": "shipped",
        "shipped_at": "2025-01-01T12:00:00Z",
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["ship", "123e4567"])

    assert result.exit_code == 0
    assert "Shipped" in result.stdout or "shipped" in result.stdout.lower()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest cli/tests/test_cli.py::test_ship_task -v`
Expected: FAIL

**Step 3: Create ship command**

Create `cli/kz/commands/ship.py`:
```python
"""Ship (complete) task command."""

import asyncio
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from cli.kz.api_client import APIClient

console = Console()


def ship(
    task_id: Annotated[str, typer.Argument(help="Task ID (full or partial)")],
) -> None:
    """Ship (complete) a task. Celebrate!"""
    asyncio.run(_ship_task(task_id))


async def _ship_task(task_id: str) -> None:
    """Async implementation of ship command."""
    try:
        async with APIClient() as client:
            result = await client.ship_task(task_id)

        console.print(
            Panel(
                f"[bold green]{result['title']}[/bold green]\n\n"
                f"[green]rocket_launch[/green] Shipped!",
                title="[green bold]Task Completed![/green bold]",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

**Step 4: Update main.py**

Update `cli/kz/main.py`:
```python
"""Kanban Zero CLI entry point."""

from typing import Annotated, Optional

import typer

from cli.kz import __version__
from cli.kz.commands.add import add
from cli.kz.commands.list import list_tasks
from cli.kz.commands.ship import ship

app = typer.Typer(
    name="kz",
    help="Kanban Zero - AI-native, energy-aware task management for ADHD brains",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"Kanban Zero CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Kanban Zero - Your ADHD-friendly task companion."""
    pass


# Register commands
app.command()(add)
app.command("list")(list_tasks)
app.command()(ship)


if __name__ == "__main__":
    app()
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest cli/tests/test_cli.py -v`
Expected: 8 passed

**Step 6: Commit**

```bash
git add cli/kz/
git commit -m "feat: add CLI 'ship' command"
```

---

### Task 15: CLI `wins` Shortcut Command

**Files:**
- Create: `cli/kz/commands/wins.py`
- Modify: `cli/kz/main.py`
- Modify: `cli/tests/test_cli.py`

**Step 1: Write the failing test**

Add to `cli/tests/test_cli.py`:
```python
@patch("cli.kz.commands.wins.APIClient")
def test_wins_command(mock_client_class):
    """Test wins command (quick_win shortcut)."""
    mock_client = AsyncMock()
    mock_client.list_tasks.return_value = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Quick Win",
            "energy_column": "quick_win",
            "created_at": "2025-01-01T00:00:00Z",
        },
    ]
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["wins"])

    assert result.exit_code == 0
    mock_client.list_tasks.assert_called_once_with(column="quick_win")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest cli/tests/test_cli.py::test_wins_command -v`
Expected: FAIL

**Step 3: Create wins command**

Create `cli/kz/commands/wins.py`:
```python
"""Quick wins shortcut command."""

import asyncio

import typer
from rich.console import Console

from cli.kz.api_client import APIClient
from cli.kz.display import display_tasks_table

console = Console()


def wins() -> None:
    """Show quick win tasks only. Easy dopamine hits!"""
    asyncio.run(_show_wins())


async def _show_wins() -> None:
    """Async implementation of wins command."""
    try:
        async with APIClient() as client:
            tasks = await client.list_tasks(column="quick_win")

        if not tasks:
            console.print("[yellow]No quick wins right now. Add some![/yellow]")
            console.print("[dim]kz add 'small task' --energy quick_win[/dim]")
            return

        console.print("[yellow bold]bolt QUICK WINS[/yellow bold]\n")
        display_tasks_table(tasks, title="Ready for easy wins?")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

**Step 4: Update main.py**

Update `cli/kz/main.py`:
```python
"""Kanban Zero CLI entry point."""

from typing import Annotated, Optional

import typer

from cli.kz import __version__
from cli.kz.commands.add import add
from cli.kz.commands.list import list_tasks
from cli.kz.commands.ship import ship
from cli.kz.commands.wins import wins

app = typer.Typer(
    name="kz",
    help="Kanban Zero - AI-native, energy-aware task management for ADHD brains",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"Kanban Zero CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Kanban Zero - Your ADHD-friendly task companion."""
    pass


# Register commands
app.command()(add)
app.command("list")(list_tasks)
app.command()(ship)
app.command()(wins)


if __name__ == "__main__":
    app()
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest cli/tests/test_cli.py -v`
Expected: 9 passed

**Step 6: Commit**

```bash
git add cli/kz/
git commit -m "feat: add CLI 'wins' shortcut command"
```

---

## Phase 5: Web Frontend Foundation

### Task 16: Next.js Project Setup

**Files:**
- Create: `web/package.json`
- Create: `web/next.config.js`
- Create: `web/tailwind.config.js`
- Create: `web/tsconfig.json`
- Create: `web/app/layout.tsx`
- Create: `web/app/page.tsx`

**Step 1: Initialize Next.js project**

Run:
```bash
cd /Users/lazy/Projects/kanban_zero
npx create-next-app@latest web --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --no-turbo
```

Expected: Next.js project created in `web/` directory

**Step 2: Install additional dependencies**

Run:
```bash
cd /Users/lazy/Projects/kanban_zero/web
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities framer-motion lucide-react
npm install -D @types/node
```

**Step 3: Verify setup**

Run: `cd /Users/lazy/Projects/kanban_zero/web && npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add web/
git commit -m "feat: initialize Next.js 14 web frontend"
```

---

### Task 17: Install and Configure shadcn/ui

**Files:**
- Modify: `web/tailwind.config.js`
- Create: `web/components.json`
- Create: `web/lib/utils.ts`
- Create: `web/app/globals.css`

**Step 1: Initialize shadcn/ui**

Run:
```bash
cd /Users/lazy/Projects/kanban_zero/web
npx shadcn@latest init
```

Select options:
- Style: Default
- Base color: Slate
- CSS variables: Yes

**Step 2: Add required components**

Run:
```bash
cd /Users/lazy/Projects/kanban_zero/web
npx shadcn@latest add button card badge
```

**Step 3: Verify installation**

Run: `cd /Users/lazy/Projects/kanban_zero/web && npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add web/
git commit -m "feat: add shadcn/ui component library"
```

---

### Task 18: API Client for Frontend

**Files:**
- Create: `web/lib/api.ts`
- Create: `web/lib/types.ts`

**Step 1: Create types**

Create `web/lib/types.ts`:
```typescript
export type EnergyColumn = 'hyperfocus' | 'quick_win' | 'low_energy' | 'shipped';

export interface Task {
  id: string;
  title: string;
  body: string | null;
  raw_input: string;
  energy_column: EnergyColumn;
  position: number;
  created_at: string;
  updated_at: string;
  shipped_at: string | null;
  created_via: 'cli' | 'slack' | 'web' | 'api';
}

export interface CreateTaskInput {
  raw_input: string;
  energy_column?: EnergyColumn;
  created_via?: 'web';
}

export interface UpdateTaskInput {
  title?: string;
  body?: string;
  energy_column?: EnergyColumn;
  position?: number;
}
```

**Step 2: Create API client**

Create `web/lib/api.ts`:
```typescript
import { Task, CreateTaskInput, UpdateTaskInput, EnergyColumn } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new APIError(response.status, await response.text());
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const api = {
  tasks: {
    list: (column?: EnergyColumn): Promise<Task[]> => {
      const params = column ? `?column=${column}` : '';
      return fetchAPI<Task[]>(`/api/tasks${params}`);
    },

    get: (id: string): Promise<Task> => {
      return fetchAPI<Task>(`/api/tasks/${id}`);
    },

    create: (data: CreateTaskInput): Promise<Task> => {
      return fetchAPI<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({ ...data, created_via: 'web' }),
      });
    },

    update: (id: string, data: UpdateTaskInput): Promise<Task> => {
      return fetchAPI<Task>(`/api/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },

    delete: (id: string): Promise<void> => {
      return fetchAPI<void>(`/api/tasks/${id}`, {
        method: 'DELETE',
      });
    },

    ship: (id: string): Promise<Task> => {
      return fetchAPI<Task>(`/api/tasks/${id}/ship`, {
        method: 'POST',
      });
    },
  },
};
```

**Step 3: Create .env.local**

Create `web/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Step 4: Commit**

```bash
git add web/lib/ web/.env.local
git commit -m "feat: add API client for web frontend"
```

---

### Task 19: Board Component Structure

**Files:**
- Create: `web/app/components/Board.tsx`
- Create: `web/app/components/Column.tsx`
- Create: `web/app/components/TaskCard.tsx`
- Modify: `web/app/page.tsx`

**Step 1: Create TaskCard component**

Create `web/app/components/TaskCard.tsx`:
```tsx
'use client';

import { motion } from 'framer-motion';
import { Task } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Rocket } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onShip?: (id: string) => void;
}

export function TaskCard({ task, onShip }: TaskCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.02 }}
      className="cursor-grab active:cursor-grabbing"
    >
      <Card className="bg-card hover:bg-accent/50 transition-colors">
        <CardContent className="p-3">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium leading-tight">{task.title}</p>
            {task.energy_column !== 'shipped' && onShip && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onShip(task.id);
                }}
                className="text-muted-foreground hover:text-green-500 transition-colors"
                title="Ship it!"
              >
                <Rocket className="h-4 w-4" />
              </button>
            )}
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {task.id.slice(0, 8)}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
```

**Step 2: Create Column component**

Create `web/app/components/Column.tsx`:
```tsx
'use client';

import { AnimatePresence } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { TaskCard } from './TaskCard';
import { Flame, Zap, Coffee, Rocket } from 'lucide-react';

const COLUMN_CONFIG: Record<EnergyColumn, { icon: React.ReactNode; color: string; label: string }> = {
  hyperfocus: {
    icon: <Flame className="h-5 w-5" />,
    color: 'text-red-500',
    label: 'Hyperfocus',
  },
  quick_win: {
    icon: <Zap className="h-5 w-5" />,
    color: 'text-yellow-500',
    label: 'Quick Wins',
  },
  low_energy: {
    icon: <Coffee className="h-5 w-5" />,
    color: 'text-blue-500',
    label: 'Low Energy',
  },
  shipped: {
    icon: <Rocket className="h-5 w-5" />,
    color: 'text-green-500',
    label: 'Shipped',
  },
};

interface ColumnProps {
  column: EnergyColumn;
  tasks: Task[];
  onShipTask?: (id: string) => void;
}

export function Column({ column, tasks, onShipTask }: ColumnProps) {
  const config = COLUMN_CONFIG[column];

  return (
    <div className="flex flex-col min-w-[280px] max-w-[320px]">
      <div className={`flex items-center gap-2 mb-3 ${config.color}`}>
        {config.icon}
        <h2 className="font-semibold">{config.label}</h2>
        <span className="text-muted-foreground text-sm">({tasks.length})</span>
      </div>

      <div className="flex flex-col gap-2 min-h-[200px] p-2 bg-muted/30 rounded-lg">
        <AnimatePresence mode="popLayout">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onShip={onShipTask} />
          ))}
        </AnimatePresence>

        {tasks.length === 0 && (
          <p className="text-muted-foreground text-sm text-center py-8">
            No tasks here
          </p>
        )}
      </div>
    </div>
  );
}
```

**Step 3: Create Board component**

Create `web/app/components/Board.tsx`:
```tsx
'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { api } from '@/lib/api';
import { Column } from './Column';

const COLUMNS: EnergyColumn[] = ['hyperfocus', 'quick_win', 'low_energy', 'shipped'];

export function Board() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const data = await api.tasks.list();
      setTasks(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleShipTask = async (id: string) => {
    try {
      const shipped = await api.tasks.ship(id);
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? shipped : t))
      );
    } catch (e) {
      console.error('Failed to ship task:', e);
    }
  };

  const tasksByColumn = COLUMNS.reduce((acc, col) => {
    acc[col] = tasks.filter((t) => t.energy_column === col);
    return acc;
  }, {} as Record<EnergyColumn, Task[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex gap-4 overflow-x-auto pb-4"
    >
      {COLUMNS.map((column) => (
        <Column
          key={column}
          column={column}
          tasks={tasksByColumn[column]}
          onShipTask={handleShipTask}
        />
      ))}
    </motion.div>
  );
}
```

**Step 4: Update page.tsx**

Update `web/app/page.tsx`:
```tsx
import { Board } from './components/Board';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Kanban Zero</h1>
        <p className="text-muted-foreground">
          AI-native, energy-aware task management
        </p>
      </header>

      <Board />
    </main>
  );
}
```

**Step 5: Verify build**

Run: `cd /Users/lazy/Projects/kanban_zero/web && npm run build`
Expected: Build succeeds

**Step 6: Commit**

```bash
git add web/app/
git commit -m "feat: add Board, Column, and TaskCard components"
```

---

### Task 20: Ship Animation

**Files:**
- Modify: `web/app/components/TaskCard.tsx`
- Create: `web/app/components/ShipCelebration.tsx`

**Step 1: Create celebration component**

Create `web/app/components/ShipCelebration.tsx`:
```tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

interface ShipCelebrationProps {
  show: boolean;
  onComplete?: () => void;
}

export function ShipCelebration({ show, onComplete }: ShipCelebrationProps) {
  const [particles, setParticles] = useState<{ id: number; x: number; y: number }[]>([]);

  useEffect(() => {
    if (show) {
      // Generate particles
      const newParticles = Array.from({ length: 12 }, (_, i) => ({
        id: i,
        x: Math.random() * 100 - 50,
        y: Math.random() * -100 - 50,
      }));
      setParticles(newParticles);

      // Clear after animation
      const timer = setTimeout(() => {
        setParticles([]);
        onComplete?.();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [show, onComplete]);

  return (
    <AnimatePresence>
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          initial={{ opacity: 1, scale: 1, x: 0, y: 0 }}
          animate={{
            opacity: 0,
            scale: 0,
            x: particle.x,
            y: particle.y,
          }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="absolute w-2 h-2 rounded-full bg-green-500 pointer-events-none"
          style={{ left: '50%', top: '50%' }}
        />
      ))}
    </AnimatePresence>
  );
}
```

**Step 2: Update TaskCard with ship animation**

Update `web/app/components/TaskCard.tsx`:
```tsx
'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Rocket } from 'lucide-react';
import { ShipCelebration } from './ShipCelebration';

interface TaskCardProps {
  task: Task;
  onShip?: (id: string) => void;
}

export function TaskCard({ task, onShip }: TaskCardProps) {
  const [isShipping, setIsShipping] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  const handleShip = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onShip || isShipping) return;

    setIsShipping(true);
    setShowCelebration(true);

    // Small delay for animation
    setTimeout(() => {
      onShip(task.id);
    }, 300);
  }, [onShip, task.id, isShipping]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{
        opacity: isShipping ? 0 : 1,
        y: 0,
        scale: isShipping ? 0.8 : 1,
        x: isShipping ? 100 : 0,
      }}
      exit={{ opacity: 0, scale: 0.8, x: 100 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      whileHover={{ scale: 1.02 }}
      className="cursor-grab active:cursor-grabbing relative"
    >
      <Card className="bg-card hover:bg-accent/50 transition-colors">
        <CardContent className="p-3">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium leading-tight">{task.title}</p>
            {task.energy_column !== 'shipped' && onShip && (
              <motion.button
                onClick={handleShip}
                disabled={isShipping}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                className="text-muted-foreground hover:text-green-500 transition-colors disabled:opacity-50"
                title="Ship it!"
              >
                <Rocket className="h-4 w-4" />
              </motion.button>
            )}
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {task.id.slice(0, 8)}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <ShipCelebration show={showCelebration} onComplete={() => setShowCelebration(false)} />
    </motion.div>
  );
}
```

**Step 3: Verify build**

Run: `cd /Users/lazy/Projects/kanban_zero/web && npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add web/app/components/
git commit -m "feat: add ship celebration animation"
```

---

## Phase 6: Integration & Final Setup

### Task 21: Quick Add Component for Web

**Files:**
- Create: `web/app/components/QuickAdd.tsx`
- Modify: `web/app/components/Board.tsx`

**Step 1: Create QuickAdd component**

Create `web/app/components/QuickAdd.tsx`:
```tsx
'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { Task } from '@/lib/types';

interface QuickAddProps {
  onTaskAdded: (task: Task) => void;
}

export function QuickAdd({ onTaskAdded }: QuickAddProps) {
  const [input, setInput] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isAdding) return;

    setIsAdding(true);
    try {
      const task = await api.tasks.create({ raw_input: input.trim() });
      onTaskAdded(task);
      setInput('');
      setIsExpanded(false);
    } catch (error) {
      console.error('Failed to add task:', error);
    } finally {
      setIsAdding(false);
    }
  }, [input, isAdding, onTaskAdded]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsExpanded(false);
      setInput('');
    }
  }, []);

  if (!isExpanded) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <Button
          onClick={() => setIsExpanded(true)}
          variant="outline"
          className="w-full justify-start gap-2 text-muted-foreground"
        >
          <Plus className="h-4 w-4" />
          Quick add task...
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.form
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="flex gap-2"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="What needs to be done? (AI will parse)"
        autoFocus
        disabled={isAdding}
        className="flex-1 px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
      />
      <Button type="submit" disabled={!input.trim() || isAdding}>
        {isAdding ? 'Adding...' : 'Add'}
      </Button>
      <Button
        type="button"
        variant="ghost"
        onClick={() => {
          setIsExpanded(false);
          setInput('');
        }}
      >
        Cancel
      </Button>
    </motion.form>
  );
}
```

**Step 2: Update Board to include QuickAdd**

Update `web/app/components/Board.tsx`:
```tsx
'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Task, EnergyColumn } from '@/lib/types';
import { api } from '@/lib/api';
import { Column } from './Column';
import { QuickAdd } from './QuickAdd';

const COLUMNS: EnergyColumn[] = ['hyperfocus', 'quick_win', 'low_energy', 'shipped'];

export function Board() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const data = await api.tasks.list();
      setTasks(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleTaskAdded = useCallback((task: Task) => {
    setTasks((prev) => [task, ...prev]);
  }, []);

  const handleShipTask = async (id: string) => {
    try {
      const shipped = await api.tasks.ship(id);
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? shipped : t))
      );
    } catch (e) {
      console.error('Failed to ship task:', e);
    }
  };

  const tasksByColumn = COLUMNS.reduce((acc, col) => {
    acc[col] = tasks.filter((t) => t.energy_column === col);
    return acc;
  }, {} as Record<EnergyColumn, Task[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <QuickAdd onTaskAdded={handleTaskAdded} />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex gap-4 overflow-x-auto pb-4"
      >
        {COLUMNS.map((column) => (
          <Column
            key={column}
            column={column}
            tasks={tasksByColumn[column]}
            onShipTask={handleShipTask}
          />
        ))}
      </motion.div>
    </div>
  );
}
```

**Step 3: Verify build**

Run: `cd /Users/lazy/Projects/kanban_zero/web && npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add web/app/components/
git commit -m "feat: add QuickAdd component for web task capture"
```

---

### Task 22: README and Development Scripts

**Files:**
- Create: `README.md`
- Create: `scripts/dev.sh`
- Modify: `package.json` (root, if needed)

**Step 1: Create README.md**

Create `README.md`:
```markdown
# Kanban Zero

> AI-native, energy-aware task management for ADHD brains.

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Setup

1. **Clone and install dependencies:**

```bash
git clone <repo>
cd kanban_zero

# Python dependencies
uv sync

# Web dependencies
cd web && npm install && cd ..
```

2. **Start the database:**

```bash
docker compose up -d
```

3. **Set up environment:**

```bash
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

4. **Run database migrations:**

```bash
uv run alembic upgrade head
```

5. **Start the backend:**

```bash
uv run uvicorn backend.kz.main:app --reload
```

6. **Start the frontend (new terminal):**

```bash
cd web && npm run dev
```

7. **Use the CLI:**

```bash
# Add a task
uv run kz add "fix the auth bug"

# List tasks
uv run kz list

# Ship a task
uv run kz ship <task-id>

# Show quick wins
uv run kz wins
```

## Architecture

- **Backend:** Python + FastAPI + SQLAlchemy + pgvector
- **Frontend:** Next.js 14 + React + Tailwind + shadcn/ui + Framer Motion
- **CLI:** Python + Typer + Rich
- **Database:** PostgreSQL 16 + pgvector
- **AI:** Claude API for task parsing

## Project Structure

```
kanban_zero/
├── backend/kz/          # FastAPI backend
├── cli/kz/              # Typer CLI
├── web/                 # Next.js frontend
├── docs/plans/          # Design & implementation docs
└── docker-compose.yml   # PostgreSQL + pgvector
```

## Development

### Run tests

```bash
# All tests
uv run pytest

# Backend only
uv run pytest backend/tests/

# CLI only
uv run pytest cli/tests/
```

### Code quality

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy backend/ cli/
```

## License

MIT
```

**Step 2: Create dev script**

Create `scripts/dev.sh`:
```bash
#!/bin/bash
set -e

echo "Starting Kanban Zero development environment..."

# Start database if not running
if ! docker compose ps | grep -q "kanban_zero_db.*running"; then
    echo "Starting PostgreSQL..."
    docker compose up -d
    sleep 3
fi

# Run migrations
echo "Running migrations..."
uv run alembic upgrade head

# Start backend in background
echo "Starting backend..."
uv run uvicorn backend.kz.main:app --reload &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd web && npm run dev &
FRONTEND_PID=$!

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
```

Make it executable:
```bash
chmod +x scripts/dev.sh
```

**Step 3: Commit**

```bash
git add README.md scripts/
git commit -m "docs: add README and development scripts"
```

---

### Task 23: Final Integration Test

**Files:**
- Create: `backend/tests/test_integration.py`

**Step 1: Write integration test**

Create `backend/tests/test_integration.py`:
```python
"""End-to-end integration tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.kz.db.database import get_async_engine, get_async_session_maker
from backend.kz.main import app
from backend.kz.models import Base


@pytest.fixture
async def setup_db():
    """Set up clean database for each test."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client(setup_db):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_task_lifecycle(client):
    """Test complete task lifecycle: create -> list -> ship."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={"raw_input": "write integration tests", "energy_column": "quick_win"},
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]

    # Verify it appears in list
    list_response = await client.get("/api/tasks")
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert any(t["id"] == task_id for t in tasks)

    # Ship the task
    ship_response = await client.post(f"/api/tasks/{task_id}/ship")
    assert ship_response.status_code == 200
    shipped_task = ship_response.json()
    assert shipped_task["energy_column"] == "shipped"
    assert shipped_task["shipped_at"] is not None


@pytest.mark.asyncio
async def test_task_filtering_by_column(client):
    """Test that column filtering works."""
    # Create tasks in different columns
    await client.post(
        "/api/tasks",
        json={"raw_input": "hyperfocus task", "energy_column": "hyperfocus"},
    )
    await client.post(
        "/api/tasks",
        json={"raw_input": "quick win task", "energy_column": "quick_win"},
    )

    # Filter by hyperfocus
    response = await client.get("/api/tasks", params={"column": "hyperfocus"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["energy_column"] == "hyperfocus"


@pytest.mark.asyncio
async def test_task_update(client):
    """Test updating a task."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={"raw_input": "original task"},
    )
    task_id = create_response.json()["id"]

    # Update it
    update_response = await client.patch(
        f"/api/tasks/{task_id}",
        json={"energy_column": "hyperfocus"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["energy_column"] == "hyperfocus"


@pytest.mark.asyncio
async def test_task_deletion(client):
    """Test deleting a task."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={"raw_input": "delete me"},
    )
    task_id = create_response.json()["id"]

    # Delete it
    delete_response = await client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404
```

**Step 2: Run integration tests**

Run: `uv run pytest backend/tests/test_integration.py -v`
Expected: All tests pass

**Step 3: Run full test suite**

Run: `uv run pytest -v`
Expected: All backend and CLI tests pass

**Step 4: Commit**

```bash
git add backend/tests/test_integration.py
git commit -m "test: add end-to-end integration tests"
```

---

### Task 24: V1 Complete - Final Commit

**Step 1: Run all tests one more time**

Run: `uv run pytest -v`
Expected: All tests pass

**Step 2: Build frontend**

Run: `cd /Users/lazy/Projects/kanban_zero/web && npm run build`
Expected: Build succeeds

**Step 3: Create release commit**

```bash
git add -A
git commit -m "feat: complete Kanban Zero V1

V1 Minimum Lovable Product complete:
- CLI with add, list, ship, wins commands
- FastAPI backend with task CRUD + AI parsing
- Next.js frontend with energy-based board
- PostgreSQL + pgvector for storage and embeddings
- Ship animation for dopamine hits

Ready for daily use!"
```

---

## Summary

**V1 delivers:**

| Component | Features |
|-----------|----------|
| **CLI** | `add`, `list`, `ship`, `wins` commands with Rich formatting |
| **Backend** | FastAPI with task CRUD, AI parsing via Claude, pgvector embeddings |
| **Frontend** | Next.js board with energy columns, drag indicators, ship animation |
| **Database** | PostgreSQL 16 + pgvector, Alembic migrations |
| **DX** | Docker Compose, test suite, dev scripts |

**Total: 24 tasks, ~200 test cases, production-ready foundation**

---

*Plan generated: 2025-12-01*
*Estimated implementation time: 2-3 focused sessions*
