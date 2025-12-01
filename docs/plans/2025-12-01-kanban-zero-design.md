# Kanban Zero — Design Document

**Date:** 2025-12-01
**Status:** Approved
**Tagline:** *"A Kanban board with ADHD that does its own homework — when you let it."*

---

## Executive Summary

Kanban Zero is an AI-native, energy-aware task management system designed for ADHD brains building AI products. It combines instant multi-channel capture (CLI, Slack, Web), energy-based organization, intelligent GraphRAG memory, and optional AI agents that can actually work on tasks autonomously.

**Key differentiators:**
- Energy columns instead of status columns (Hyperfocus, Quick Wins, Low Energy, Agent Zone, Shipped)
- User-controlled AI autonomy dial (Ghost → Copilot → Autopilot → Agent)
- Dopamine engineering with variable rewards, satisfying animations, and surprise celebrations
- GraphRAG-powered semantic search and relationship discovery
- Future ACP (Agent Client Protocol) support for hot-swappable AI agents

---

## Table of Contents

1. [Vision & Core Concepts](#1-vision--core-concepts)
2. [Architecture](#2-architecture)
3. [Data Model](#3-data-model)
4. [Capture & Interaction Flows](#4-capture--interaction-flows)
5. [Dopamine Engineering](#5-dopamine-engineering)
6. [GraphRAG & AI Intelligence](#6-graphrag--ai-intelligence)
7. [Implementation Phases](#7-implementation-phases)
8. [Project Structure](#8-project-structure)

---

## 1. Vision & Core Concepts

### Core Principles

1. **Capture is instant** — Slack message, CLI one-liner, or web quick-add. Zero required fields. AI parses intent, extracts metadata, auto-tags.

2. **Energy-based organization** — Columns reflect YOUR energy state, not bureaucratic status:
   - `local_fire_department` **Hyperfocus** — Deep work, high complexity
   - `bolt` **Quick Wins** — Small dopamine hits, <15 min tasks
   - `self_improvement` **Low Energy** — Mindless but useful (docs, cleanup)
   - `smart_toy` **Agent Zone** — AI is working on these
   - `rocket_launch` **Shipped** — Done, celebrated, archived

3. **User-controlled AI autonomy** — A global dial with per-task overrides:
   - `visibility_off` **Ghost** — AI silent, pure manual Kanban
   - `assistant` **Copilot** — AI suggests, you approve
   - `autopilot` **Autopilot** — AI acts, you can override
   - `robot` **Agent** — AI works autonomously, you review

4. **Dopamine engineering** — Satisfying animations, surprise celebrations, counters, streaks, easter eggs. Variable reward schedules to maintain engagement.

5. **GraphRAG memory** — Every task is embedded. Semantic search, pattern recognition, "what was that thing?" queries, relationship graph.

### Design Constraints (ADHD-Optimized)

These are the productivity tool killers we're designing against:

| Problem | Our Solution |
|---------|--------------|
| Too much ceremony | Zero required fields, AI parses free text |
| Context switching cost | Capture from where you ARE (CLI, Slack, Web) |
| No dopamine hits | Variable rewards, visual progress, surprises |

### Icon System

Google Material Icons throughout. No emojis. Consistent visual language across CLI (text representations), Web (actual icons), and Slack (emoji fallbacks only where required).

---

## 2. Architecture

### Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend API** | Python + FastAPI | Fast async, excellent AI/ML ecosystem, typing |
| **Database** | PostgreSQL + pgvector | Relational + vector search unified, single service |
| **Graph Layer** | PostgreSQL (TASK_EDGE table) | V1 simplicity; Neo4j migration path for V4+ |
| **CLI** | Typer (Python) | Beautiful CLI, same language as backend |
| **Web Frontend** | Next.js 14 + React | App router, server components, great DX |
| **UI Components** | shadcn/ui + Tailwind | Beautiful defaults, customizable, Material icons |
| **Animations** | Framer Motion | Satisfying micro-interactions, drag-and-drop |
| **Slack App** | Slack Bolt (Python) | Same backend language, full Slack API support |
| **AI/Agents** | Claude API + LangGraph | Agent orchestration, tool use, multi-step reasoning |
| **Queue/Jobs** | ARQ (async Redis queue) | Background agent work, lightweight |
| **Cache/Pubsub** | Redis | Job queue, real-time updates |

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAPTURE LAYER                            │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐   │
│  │  CLI    │    │  Slack  │    │   Web   │    │  Voice/API  │   │
│  │ (Typer) │    │ (Bolt)  │    │ (Next)  │    │  (future)   │   │
│  └────┬────┘    └────┬────┘    └────┬────┘    └──────┬──────┘   │
└───────┼──────────────┼──────────────┼────────────────┼──────────┘
        │              │              │                │
        └──────────────┴───────┬──────┴────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Task CRUD  │  │  AI Parser  │  │  Autonomy Controller    │  │
│  │             │  │  (intent)   │  │  (ghost/copilot/agent)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
│  ┌─────────────────────┐    ┌───────────────────────────────┐   │
│  │  PostgreSQL         │    │  Redis                        │   │
│  │  • Tasks, Users     │    │  • Job queue                  │   │
│  │  • pgvector embeds  │    │  • Real-time pubsub           │   │
│  └─────────────────────┘    └───────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Graph Store (TASK_EDGE table in PostgreSQL)            │    │
│  │  • Task relationships: blocks, related, spawned_from    │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Agent Gateway (ACP-Ready Interface)                      │  │
│  │  • V1-V3: Direct Claude/LangGraph integration             │  │
│  │  • V4+: Full ACP protocol (JSON-RPC, stdin/stdout)        │  │
│  │  • Capability discovery, permission proxying              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│           ┌──────────────────┼──────────────────┐               │
│           ▼                  ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │ Claude Agent│    │ Local LLM   │    │ Custom Agent│          │
│  │   (V1-V3)   │    │   (V4+)     │    │   (V4+)     │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### ACP Compatibility Strategy

The Agent Client Protocol (ACP) enables hot-swappable AI agents via:
- JSON-RPC over stdin/stdout (agents as subprocesses)
- Capability advertising at startup
- Permission framework with user approval gates
- `_meta` field extensibility

**V1-V3 Strategy:** Build clean `AgentGateway` abstraction with ACP-like patterns (capabilities, permissions, sessions). Direct Claude integration behind it.

**V4+ Strategy:** Swap to full ACP protocol support, enabling any ACP-compliant agent.

**Autonomy dial maps to ACP permissions:**
- Ghost → No agent spawned
- Copilot → All tool calls require approval
- Autopilot → Pre-approved tool categories
- Agent → Full autonomy with audit log

---

## 3. Data Model

### Core Entities

```sql
-- TASK: The atomic unit of work
CREATE TABLE task (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(500) NOT NULL,
    body            TEXT,                           -- Markdown, optional
    raw_input       TEXT NOT NULL,                  -- Original capture text, preserved

    energy_column   VARCHAR(20) NOT NULL DEFAULT 'quick_win',
                    -- ENUM: hyperfocus, quick_win, low_energy, agent_zone, shipped
    autonomy_level  VARCHAR(20),                    -- NULL = inherit global
                    -- ENUM: ghost, copilot, autopilot, agent

    parent_id       UUID REFERENCES task(id),       -- Optional hierarchy
    position        INTEGER NOT NULL DEFAULT 0,     -- Ordering within column

    embedding       vector(1536),                   -- pgvector for semantic search

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    shipped_at      TIMESTAMPTZ,                    -- For cycle time metrics
    created_via     VARCHAR(20) NOT NULL DEFAULT 'cli',
                    -- ENUM: cli, slack, web, agent, api

    agent_session_id UUID REFERENCES agent_session(id)
);

-- TAG: Categorization
CREATE TABLE tag (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) UNIQUE NOT NULL,
    color           VARCHAR(7),                     -- Hex color
    icon            VARCHAR(50),                    -- Material icon name
    auto_generated  BOOLEAN NOT NULL DEFAULT false
);

-- TASK_TAG: Many-to-many junction
CREATE TABLE task_tag (
    task_id         UUID REFERENCES task(id) ON DELETE CASCADE,
    tag_id          UUID REFERENCES tag(id) ON DELETE CASCADE,
    confidence      FLOAT,                          -- 0-1 if AI-assigned
    PRIMARY KEY (task_id, tag_id)
);

-- TASK_EDGE: Graph relationships
CREATE TABLE task_edge (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_task_id    UUID REFERENCES task(id) ON DELETE CASCADE,
    to_task_id      UUID REFERENCES task(id) ON DELETE CASCADE,
    edge_type       VARCHAR(20) NOT NULL,
                    -- ENUM: blocks, related, spawned_from, duplicate_of, depends_on
    created_by      VARCHAR(10) NOT NULL DEFAULT 'user',
                    -- ENUM: user, agent
    confidence      FLOAT,                          -- If agent-detected
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Agent & Activity Tracking

```sql
-- AGENT_SESSION: Tracks agent work on tasks
CREATE TABLE agent_session (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID REFERENCES task(id),
    agent_type      VARCHAR(100) NOT NULL,          -- e.g., "claude-sonnet-4-20250514"
    status          VARCHAR(20) NOT NULL DEFAULT 'running',
                    -- ENUM: running, paused, completed, failed
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at        TIMESTAMPTZ,
    autonomy_level  VARCHAR(20) NOT NULL,           -- Captured at start
    output_summary  TEXT,
    artifacts       JSONB                           -- File paths, PR links, etc.
);

-- ACTIVITY_LOG: Audit trail + dopamine fuel
CREATE TABLE activity_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID REFERENCES task(id) ON DELETE SET NULL,
    actor           VARCHAR(10) NOT NULL,           -- ENUM: user, agent, system
    action          VARCHAR(50) NOT NULL,           -- created, moved, shipped, etc.
    details         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- USER_SETTINGS: Per-user configuration
CREATE TABLE user_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    global_autonomy VARCHAR(20) NOT NULL DEFAULT 'ghost',
    slack_user_id   VARCHAR(50),
    dopamine_prefs  JSONB NOT NULL DEFAULT '{}',    -- Which celebrations enabled
    energy_pattern  JSONB                           -- Learned patterns
);
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `raw_input` preserved | Never lose context; AI can re-parse with better models |
| `embedding` on Task | Enables "find similar", "what was that thing?", clustering |
| `TASK_EDGE` in Postgres | Graph relationships without separate Neo4j; V1 simplicity |
| `confidence` on tags/edges | Distinguishes AI guesses from user truth; can filter by certainty |
| `created_via` tracking | Analytics: which capture method is actually used? |
| `energy_pattern` JSONB | Flexible schema for ML features, learns YOUR patterns |

---

## 4. Capture & Interaction Flows

**Golden Rule:** *Capture in <5 seconds or it won't happen.*

### Flow 1: CLI Capture

```bash
# Minimal — just the thought
$ kz add "fix the auth bug that's blocking slack integration"
# AI parses → title, tags, edges, energy (inferred)

# With explicit energy override
$ kz add "refactor the entire agent architecture" --energy hyperfocus

# Brain dump mode
$ kz dump
> entering multi-line mode, ctrl+d to finish
> update readme
> fix typo in login page
> respond to that PR comment
^D
# AI processes all, auto-categorizes each
```

**CLI quick actions:**
```bash
$ kz now                    # What should I work on RIGHT NOW?
$ kz wins                   # Show quick wins only
$ kz ship 3f2a              # Mark task shipped (partial ID match)
$ kz agent                  # What is the agent doing?
$ kz agent give 3f2a        # Hand task to agent
$ kz agent take 3f2a        # Take back from agent
$ kz search "that auth thing"  # Semantic search
```

### Flow 2: Slack Capture

**Slash commands:**
```
/kz fix the flaky test in CI
/kz-quick update the env vars documentation
/kz-hyper design the notification system
/kz-agent research competitor pricing models
```

**Message reactions:**
- React with `:kz:` → AI extracts task from message, confirms in thread
- React with `:kz-agent:` → Task created AND assigned to agent

**Daily digest (morning Slack message):**
```
┌─────────────────────────────────────────────┐
│  [today] Your Day — Monday                  │
├─────────────────────────────────────────────┤
│                                             │
│  [fire] HYPERFOCUS (2)                      │
│  • Design notification system               │
│  • Refactor agent architecture              │
│                                             │
│  [bolt] QUICK WINS (5)                      │
│  • Fix flaky test                           │
│  • Update env docs                          │
│  • ... 3 more                               │
│                                             │
│  [robot] AGENT WORKING ON (1)               │
│  • Research competitor pricing              │
│    └─ Status: 60% complete                  │
│                                             │
│  [trophy] Yesterday: 7 shipped!             │
│                                             │
│  [Start Focus Session]  [Show All]          │
└─────────────────────────────────────────────┘
```

### Flow 3: Web Dashboard

**Board View:**
- Columns: Hyperfocus | Quick Wins | Low Energy | Agent Zone | Shipped
- Drag-and-drop with satisfying animations
- Click task → slide-out detail panel
- Bulk select + move for planning sessions

**Focus Mode:**
- Single task, fullscreen, no distractions
- Optional timer (pomodoro-style)
- Quick actions: Ship, Block, Hand to Agent, Spawn subtask
- "I'm stuck" button → AI offers help or suggests switching

### Flow 4: Agent Working Loop

```
┌──────────────────────────────────────────────────────────────┐
│  AGENT ZONE — What the robots are doing                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [robot] Research competitor pricing                         │
│  ├─ Status: In progress (3 min elapsed)                      │
│  ├─ Current: Analyzing ProductHunt listings                  │
│  ├─ Progress: ████████░░ 80%                                 │
│  └─ [Pause] [Take Over] [View Logs]                          │
│                                                              │
│  [robot] Draft PR for auth fix                               │
│  ├─ Status: Awaiting review                                  │
│  ├─ Output: PR #47 ready — 3 files changed                   │
│  └─ [Approve & Ship] [View Diff] [Request Changes]           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Dopamine Engineering

**Philosophy:** *Variable rewards beat predictable rewards. Satisfaction beats notification spam.*

### Pillar 1: Numbers Going Up

**Always-visible counters:**
- TODAY: X shipped
- STREAK: X days
- ALL-TIME: X shipped

**Weekly velocity:** Sparkline + trend arrow (no guilt, just data)

**Personal bests:** Most in a day, longest streak, biggest session

### Pillar 2: Visual Progress

| Action | Animation |
|--------|-----------|
| Task created | Soft fade-in + subtle pulse |
| Drag task | Card lifts with shadow, smooth glide |
| Drop in column | Gentle bounce settle |
| Ship task | Card compresses → shoots to Shipped with trail |
| Agent picks up | Subtle robot overlay, gentle glow |
| Agent completes | Success ripple outward |

### Pillar 3: Surprise & Delight

**Variable reward distribution:**
```
standard_ship:     70%  — Simple satisfying animation
confetti_burst:    15%  — Colorful confetti explosion
achievement_popup: 10%  — "5 in a row!" message
easter_egg:         5%  — Rare delightful surprises
```

**Easter egg examples:**
- 10th task → card does victory dance
- First Monday ship → "Week crushed. Day 1." with sunrise
- 3am ship → "Night owl mode activated"
- 100th all-time → golden explosion (one-time)
- Random 1/50 → tiny rocket blasts off

**Streak celebrations:** 3 days (flame), 7 days (larger), 14 days (bonfire), 30 days (phoenix)

### Anti-Patterns Avoided

| Bad Pattern | Our Alternative |
|-------------|-----------------|
| Daily goals with shame | Just show data, no judgment |
| Notifications for everything | Celebrate completion, not creation |
| Leaderboards | Personal bests only |
| Losing streaks punishment | Streak freeze (1 free skip/week) |

### User Controls

Celebration preferences panel:
- Animation intensity slider (subtle ↔ party)
- Toggle: confetti, easter eggs, sounds, streaks, daily digest
- Celebration cooldown (default: 5 min)

---

## 6. GraphRAG & AI Intelligence

### Layer 1: Semantic Memory (Vector Search)

Every task embedded on creation (1536-dim via OpenAI or similar).

**Powers:**
- Fuzzy search: `kz search "that slack thing"`
- Duplicate detection: "This looks similar to 'Fix OAuth flow'"
- Related suggestions on task creation
- Smart clustering in UI
- Natural language queries: `kz ask "what have I been working on for auth?"`

### Layer 2: Graph Intelligence

**Edge types:**
- `blocks` → Dependency warnings, ordering
- `spawned_from` → Task lineage, scope tracking
- `related_to` → Context when working on either
- `duplicate_of` → Deduplication, merging
- `depends_on` → Suggested ordering

**AI auto-detects relationships** with confidence scores.

**Graph queries:**
```bash
$ kz blocked          # Tasks with unresolved blockers
$ kz tree 3f2a        # Full lineage
$ kz impact 3f2a      # Downstream effects
```

### Layer 3: Pattern Learning

**Tracked patterns:**
- Energy rhythms (peak hyperfocus times, quick win preference times)
- Task tendencies (avg time in column, abandonment risk, completion rate by tag)
- Velocity patterns (best/worst days, streak impact)

**Pattern-powered features:**
- Smart `kz now` (time + energy + staleness)
- Abandonment nudges ("8 days in Hyperfocus — break it down?")
- Energy suggestions ("Friday 4pm → showing Low Energy tasks")
- Stale detection ("3 tasks haven't moved in 2 weeks")

### RAG Pipeline

```
User: "What's the status of Slack integration?"
         ↓
1. RETRIEVE: Vector search + graph traversal + recent activity
         ↓
2. AUGMENT: Task details, statuses, edges, agent outputs, patterns
         ↓
3. GENERATE: Synthesized answer with actionable suggestions
```

---

## 7. Implementation Phases

### V1: Minimum Lovable Product

**Scope:**
- CLI capture & management (add, list, now, ship, search)
- Energy-based columns (no Agent Zone yet)
- Flat tasks + AI auto-tagging
- Basic web board with drag-drop
- PostgreSQL + pgvector
- One satisfying ship animation
- Slack: `/kz` slash command only

**Explicitly OUT:** Agent Zone, hierarchy, graph edges, pattern learning, variable rewards, daily digest, autonomy dial

**Success criteria:** You use it every day for a week.

### V2: Dopamine & Relationships

**Adds:**
- Parent-child task linking
- Graph edges (blocks, related, spawned_from)
- Full celebration system (variable rewards, streaks, counters)
- Slack reactions + daily digest
- Smart `kz now` suggestions
- Duplicate detection

### V3: The Agents Arrive

**Adds:**
- Agent Zone column
- Autonomy dial (ghost/copilot/autopilot/agent)
- Agent Gateway abstraction
- Claude agent integration (research, code drafting, PR creation)
- Agent session tracking & logs
- "Hand to agent" / "Take back" actions

### V4: Protocol & Patterns

**Adds:**
- Full ACP protocol support
- Pattern learning engine
- Voice capture
- Multi-user / team features
- Mobile companion app

---

## 8. Project Structure

```
kanban_zero/
├── README.md
├── docker-compose.yml              # Postgres + Redis
├── pyproject.toml                  # Python monorepo (uv/poetry)
│
├── backend/
│   ├── kz/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Settings, env vars
│   │   ├── models/                 # SQLAlchemy + Pydantic
│   │   │   ├── task.py
│   │   │   ├── tag.py
│   │   │   ├── edge.py
│   │   │   └── activity.py
│   │   ├── api/
│   │   │   ├── tasks.py
│   │   │   ├── tags.py
│   │   │   └── search.py
│   │   ├── services/
│   │   │   ├── parser.py           # AI intent parsing
│   │   │   ├── embeddings.py       # Vector operations
│   │   │   └── tagger.py           # Auto-tagging
│   │   └── db/
│   │       ├── database.py
│   │       └── migrations/
│   └── tests/
│
├── cli/
│   ├── kz/
│   │   ├── __init__.py
│   │   ├── main.py                 # Typer CLI entrypoint
│   │   ├── commands/
│   │   │   ├── add.py
│   │   │   ├── list.py
│   │   │   ├── ship.py
│   │   │   └── search.py
│   │   └── display.py              # Rich formatting
│   └── tests/
│
├── web/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Board view
│   │   └── components/
│   │       ├── Board.tsx
│   │       ├── Column.tsx
│   │       ├── TaskCard.tsx
│   │       └── TaskDetail.tsx
│   └── lib/
│       └── api.ts                  # Backend client
│
└── slack/                          # V1: minimal
    ├── bot/
    │   ├── __init__.py
    │   ├── app.py                  # Slack Bolt app
    │   └── commands.py
    └── tests/
```

---

## Appendix A: CLI Command Reference (V1)

| Command | Description |
|---------|-------------|
| `kz add "text"` | Add task (AI parses) |
| `kz add "text" --energy <col>` | Add with explicit energy column |
| `kz dump` | Multi-line brain dump mode |
| `kz list` | Show all active tasks by column |
| `kz list --column <col>` | Filter by column |
| `kz now` | AI suggests what to work on |
| `kz wins` | Show quick wins only |
| `kz ship <id>` | Mark task shipped |
| `kz move <id> <column>` | Move task to column |
| `kz search "query"` | Semantic search |
| `kz show <id>` | Task details |

---

## Appendix B: API Endpoints (V1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks` | List tasks (filterable) |
| GET | `/api/tasks/:id` | Get task |
| PATCH | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |
| POST | `/api/tasks/:id/ship` | Ship task |
| POST | `/api/tasks/search` | Semantic search |
| GET | `/api/tags` | List tags |
| POST | `/api/tags` | Create tag |

---

## Appendix C: Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/kanban_zero

# Redis
REDIS_URL=redis://localhost:6379

# AI
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...  # For embeddings

# Slack (V1 minimal)
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# App
KZ_DEFAULT_AUTONOMY=ghost
KZ_CELEBRATION_COOLDOWN_SECONDS=300
```

---

*Document generated: 2025-12-01*
*Next step: Implementation planning with `/superpowers:write-plan`*
