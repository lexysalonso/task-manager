# Task Manager

A full-stack task management system where users can register, log in, create projects, assign tasks to members, and manage work collaboratively with role-based permissions. Built with Clean Architecture on the backend and feature-based Clean Architecture on the frontend.

---

## Quick Start

Elige la opcion que prefieras:

### Docker (recomendada)

**Requisito:** Docker Desktop (o Docker Engine + Docker Compose v2) y Git.

```bash
git clone https://github.com/lexysalonso/task-manager.git
cd task-manager
cp .env.example .env
docker compose up --build
```

| Servicio   | URL                              |
|------------|----------------------------------|
| Frontend   | http://localhost:5173            |
| API        | http://localhost:8000            |
| Health     | http://localhost:8000/api/v1/health |
| Swagger UI | http://localhost:8000/docs       |
| ReDoc      | http://localhost:8000/redoc      |

### Local Development (without Docker)

**Requisitos:** Node.js 20+, Python 3.12+, PostgreSQL 15+.

#### Backend

```bash
cd task-manager-api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Configura DATABASE_URL en .env con tu PostgreSQL local
alembic upgrade head
uvicorn src.main:app --reload
```

#### Frontend

```bash
cd task-manager-frontend
corepack enable && pnpm install
cp ../.env.example .env.local
pnpm dev
```

---

## Tech Stack

| Layer    | Technology                                                         |
|----------|--------------------------------------------------------------------|
| Backend  | Python 3.12 · FastAPI · SQLAlchemy async · PostgreSQL · Alembic · JWT |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS · shadcn/ui · TanStack Query · Zustand |
| Infra    | Docker · Docker Compose                                            |

---

## Repository Structure

```
task-manager/
├── task-manager-api/          # Backend — REST API
│   ├── src/
│   │   ├── domain/            # Entities, ports (abstract interfaces), exceptions
│   │   ├── application/       # Use cases, DTOs
│   │   ├── infrastructure/    # DB models, repositories, security adapters
│   │   └── presentation/      # FastAPI routers, Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── Dockerfile
│   └── README.md
│
├── task-manager-frontend/     # Frontend — React SPA
│   ├── src/
│   │   ├── domain/            # TypeScript interfaces and enums
│   │   ├── infrastructure/    # Axios client and API adapters
│   │   ├── application/       # Custom hooks (use cases) and Zustand store
│   │   └── presentation/      # React components and pages by feature
│   ├── Dockerfile
│   ├── vercel.json
│   └── README.md
│
├── docker-compose.yml         # Runs everything with a single command
├── .env.example               # All environment variables documented
├── .editorconfig
├── .gitignore
└── README.md                  ← this file
```

---

## Architecture

### Backend — Clean Architecture + Hexagonal Architecture

The backend is structured into four layers that follow the **dependency rule**: source code dependencies can only point inward. The **domain** layer (entities, port interfaces, exceptions) sits at the centre with zero external dependencies. The **application** layer (use cases, DTOs) depends only on the domain. The **infrastructure** layer (SQLAlchemy repositories, JWT, bcrypt) implements the port interfaces defined by the domain. The **presentation** layer (FastAPI routers, Pydantic schemas) depends on the application layer to invoke use cases.

This is also a **Hexagonal Architecture** (Ports & Adapters). The domain defines abstract **ports** — `UserRepository`, `ProjectRepository`, `TaskRepository` — and the infrastructure provides concrete **adapters** that implement those interfaces. FastAPI is just one adapter for the presentation port; the domain has zero knowledge of FastAPI, SQLAlchemy, or any framework. You could swap FastAPI for Django REST Framework, or SQLAlchemy for MongoDB, without touching a single line of domain or application code.

**SOLID** is applied throughout the backend. **SRP**: one use case per file, one router per resource. **OCP**: adding a feature means adding a new use case, not modifying existing ones. **LSP**: any concrete repository can substitute its abstract port without breaking callers. **ISP**: each port interface exposes only the methods its consumer actually needs. **DIP**: use cases depend on abstract ports that are injected via FastAPI `Depends`, never on SQLAlchemy or any concrete implementation.

This architecture makes the codebase **testable** (swap SQLAlchemy for an in-memory repository in tests), **swappable** (replace FastAPI with another framework without touching domain or application), and **scalable** (each layer evolves independently as the system grows).

```
┌─────────────────────────────────────────────────────┐
│                    Presentation                     │
│         FastAPI Routers · Pydantic Schemas          │
├─────────────────────────────────────────────────────┤
│                    Application                      │
│              Use Cases · DTOs                       │
├─────────────────────────────────────────────────────┤
│                      Domain                         │
│     Entities · Ports (interfaces) · Exceptions      │
├─────────────────────────────────────────────────────┤
│                  Infrastructure                     │
│   SQLAlchemy Repos · JWT · Bcrypt · Alembic         │
└─────────────────────────────────────────────────────┘
  ↑ Dependency rule: outer layers depend on inner layers.
    Inner layers know nothing about outer layers.
```

### Frontend — Feature-based Clean Architecture

Hexagonal Architecture does not map naturally to the React ecosystem — abstract ports and adapters for a UI framework create artificial indirection with no practical benefit. Instead, the frontend follows **Feature-based Clean Architecture**, which enforces the same dependency-inversion rule in a way that is idiomatic to React and immediately readable by any senior frontend engineer.

Each layer maps directly to a React concept. **`domain/`** contains pure TypeScript interfaces and enums with zero React imports and zero logic — the only layer that could be copied unchanged into a React Native project. **`infrastructure/`** holds the Axios instance (with JWT interceptor) and one API adapter file per resource; no component ever imports Axios directly. **`application/`** provides custom hooks that act as use cases (`useProjects`, `useTasks`, `useMembers`), a Zustand store for global auth state, and TanStack Query for all server-state management. **`presentation/`** organises React components by feature (`auth/`, `projects/`, `tasks/`, `members/`). Components depend on hooks, never on API adapters.

**SOLID** on the frontend. **SRP**: each component has one responsibility — `TaskCard` renders, `TaskForm` collects input, `useTask` fetches and mutates. **OCP**: features extend via composition (slot pattern, compound components) without modifying existing components. **DIP**: components depend on custom hooks (abstractions), never on Axios (concrete detail) — the same principle as backend ports and adapters. **ISP**: each hook exposes only the interface its feature needs.

State management follows a three-layer strategy. **TanStack Query** owns all server state — caching, loading indicators, error handling, background refetching, and optimistic updates. **Zustand** owns only client-side global state — the auth token and current user. **Local `useState`** handles ephemeral UI state such as modal open/close and form dirty flags. This prevents over-fetching, eliminates prop drilling, and keeps every component lean.

```
┌─────────────────────────────────────────────────────┐
│                   Presentation                      │
│       React Components · Pages (by feature)         │
├─────────────────────────────────────────────────────┤
│                   Application                       │
│       Custom Hooks (use cases) · Zustand            │
├─────────────────────────────────────────────────────┤
│                  Infrastructure                     │
│          Axios Client · API Adapters                │
├─────────────────────────────────────────────────────┤
│                     Domain                          │
│       TypeScript Interfaces · Enums (pure)          │
└─────────────────────────────────────────────────────┘
  ↑ Dependency rule: outer layers depend on inner layers.
    Domain has zero framework imports.
```

---

## Business Rules

1. Any authenticated user can create a project. The creator becomes the owner.
2. Only the owner can edit or delete the project.
3. Only the owner can add or remove members.
4. Only the owner can edit or delete tasks created by any member.
5. Members can create, edit, and delete only their own tasks.
6. Tasks can only be assigned to current members of the project.
7. When a member is removed, all their tasks are reassigned to the owner.
8. Archived projects are fully read-only for tasks (no create/edit/delete). Viewing tasks of archived projects is allowed for all members.

---

## Environment Variables

| Variable                     | Used by  | Description                              | Example                          |
|------------------------------|----------|------------------------------------------|----------------------------------|
| DATABASE_URL                 | Backend  | PostgreSQL async connection string       | postgresql+asyncpg://...         |
| SECRET_KEY                   | Backend  | JWT signing secret (min 32 chars)        | change-me-in-production          |
| ALGORITHM                    | Backend  | JWT algorithm                            | HS256                            |
| ACCESS_TOKEN_EXPIRE_MINUTES  | Backend  | Token TTL                                | 60                               |
| ALLOWED_ORIGINS              | Backend  | CORS allowed origins (comma-separated)   | http://localhost:5173            |
| POSTGRES_USER                | Docker   | PostgreSQL username                      | postgres                         |
| POSTGRES_PASSWORD            | Docker   | PostgreSQL password                      | postgres                         |
| POSTGRES_DB                  | Docker   | PostgreSQL database name                 | taskmanager                      |
| VITE_API_URL                 | Frontend | Backend base URL                         | http://localhost:8000            |

---

## API Reference

Full interactive documentation is available at http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc (ReDoc).

```
POST   /auth/register                        Register a new user
POST   /auth/login                           Authenticate and get JWT

GET    /api/v1/health                         Health check

GET    /projects                             List user's projects
POST   /projects                             Create a project
GET    /projects/{id}                        Get project details
PUT    /projects/{id}                        Update project (owner only)
DELETE /projects/{id}                        Delete project (owner only)

POST   /projects/{id}/members                Add member (owner only)
DELETE /projects/{id}/members/{user_id}      Remove member (owner only)

GET    /projects/{id}/tasks                  List project tasks
POST   /projects/{id}/tasks                  Create task
PUT    /projects/{id}/tasks/{task_id}        Update task
PATCH  /projects/{id}/tasks/{task_id}/status Change task status
PATCH  /projects/{id}/tasks/{task_id}/priority Change task priority
DELETE /projects/{id}/tasks/{task_id}        Delete task
```

---

## Git Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/).

```
<type>(<scope>): <description>
```

| Type       | Usage                                       |
|------------|---------------------------------------------|
| `feat`     | A new feature                               |
| `fix`      | A bug fix                                   |
| `refactor` | Code change that neither fixes nor adds     |
| `chore`    | Build, CI, dependencies, tooling            |
| `docs`     | Documentation only                          |
| `test`     | Adding or updating tests                    |
| `style`    | Formatting, missing semi-colons, etc.       |

Examples:

```
feat(api): add task reassignment on member removal
fix(frontend): prevent dropdown from rendering behind header
refactor(api): extract member validation into domain service
docs: add architecture diagram to README
chore: configure docker compose healthcheck for postgres
```

---

## License

MIT
