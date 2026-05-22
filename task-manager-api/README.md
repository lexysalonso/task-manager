# Task Manager API

A RESTful task management API built with **FastAPI**, following **Clean Architecture**, **Hexagonal Architecture (Ports & Adapters)**, and **SOLID principles**.

## Architecture

```
src/
├── domain/                # Enterprise business rules
│   ├── entities/          # User, Project, Task dataclasses
│   ├── ports/             # Abstract repository interfaces
│   └── exceptions/        # Domain-specific exceptions
├── application/           # Application business rules
│   ├── use_cases/         # One interactor per business operation
│   └── dtos/              # Input/output data transfer objects
├── infrastructure/        # Frameworks, drivers, tooling
│   ├── db/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   └── repositories/  # Concrete implementations of ports
│   └── security/          # JWT, password hashing
├── presentation/          # Interface adapters
│   ├── api/v1/
│   │   ├── routers/       # FastAPI route handlers
│   │   └── schemas/       # Pydantic request/response schemas
│   └── dependencies.py    # FastAPI DI wiring
├── config.py              # Application settings
└── main.py                # FastAPI app factory
```

### Layer Dependencies

- **Domain** — no dependencies on any other layer
- **Application** — depends only on Domain (ports, entities)
- **Infrastructure** — implements Domain ports; depends on Domain + external libs
- **Presentation** — wires everything via dependency injection

## Business Rules

1. Any authenticated user can create a project and becomes its owner
2. Only the owner can edit/delete the project, manage members, or edit/delete any task
3. Regular members can view the project and its tasks, and manage only their own tasks
4. Tasks can only be assigned to project members
5. Archived projects make all tasks read-only (viewing still allowed)
6. Removing a member reassigns all their tasks to the project owner

## Tech Stack

| Component      | Library                     |
|----------------|-----------------------------|
| Framework      | FastAPI                     |
| ORM            | SQLAlchemy (async)          |
| Database       | PostgreSQL                  |
| Migrations     | Alembic                     |
| Validation     | Pydantic v2                 |
| Auth           | JWT (python-jose)           |
| Password hash  | passlib + bcrypt            |

## API Endpoints

### Authentication

| Method | Path              | Description          |
|--------|-------------------|----------------------|
| POST   | `/api/v1/auth/register` | Register a new user |
| POST   | `/api/v1/auth/login`    | Login, get JWT token |

### Projects

| Method | Path                         | Description               |
|--------|------------------------------|---------------------------|
| GET    | `/api/v1/projects`           | List user's projects      |
| POST   | `/api/v1/projects`           | Create a project          |
| GET    | `/api/v1/projects/{id}`      | Get project details       |
| PUT    | `/api/v1/projects/{id}`      | Update project (owner)    |
| DELETE | `/api/v1/projects/{id}`      | Delete project (owner)    |

### Project Members

| Method | Path                                  | Description                  |
|--------|---------------------------------------|------------------------------|
| POST   | `/api/v1/projects/{id}/members`       | Add member (owner)           |
| DELETE | `/api/v1/projects/{id}/members/{uid}` | Remove member, reassign tasks|

### Tasks

| Method | Path                                        | Description                     |
|--------|----------------------------------------------|---------------------------------|
| GET    | `/api/v1/projects/{id}/tasks`                | List tasks (members)            |
| POST   | `/api/v1/projects/{id}/tasks`                | Create task (members)           |
| PUT    | `/api/v1/projects/{id}/tasks/{task_id}`      | Update task                     |
| PATCH  | `/api/v1/projects/{id}/tasks/{task_id}/status` | Change status                 |
| PATCH  | `/api/v1/projects/{id}/tasks/{task_id}/priority` | Change priority             |
| DELETE | `/api/v1/projects/{id}/tasks/{task_id}`      | Delete task                     |

### Health

| Method | Path              | Description    |
|--------|-------------------|----------------|
| GET    | `/api/v1/health`  | Health check   |

Interactive docs at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Local Setup

### Prerequisites

- Python 3.12+
- PostgreSQL running locally

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd task-manager-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Create the database

```bash
createdb task_manager
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn src.main:app --reload
```

The API is now available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

## Environment Variables

| Variable          | Default                                              | Description                  |
|-------------------|------------------------------------------------------|------------------------------|
| `DATABASE_URL`    | `postgresql+asyncpg://postgres:postgres@localhost:5432/task_manager` | PostgreSQL connection string |
| `JWT_SECRET_KEY`  | `change-me-in-production`                            | Secret key for JWT signing   |
| `JWT_ALGORITHM`   | `HS256`                                              | JWT signing algorithm        |
| `JWT_EXPIRE_MINUTES` | `60`                                              | JWT token expiration         |
| `DEBUG`           | `false`                                              | Enable debug mode            |
| `ALLOWED_ORIGINS` | `http://localhost:3000`                              | CORS origins (comma-separated) |

## Deployment (Railway)

### Option 1: Connect GitHub repo

1. Push this repo to GitHub
2. Create a new project on [Railway](https://railway.app)
3. Select **Deploy from GitHub repo**
4. Railway auto-detects the `Dockerfile` and `railway.toml`
5. Add a PostgreSQL plugin — the `DATABASE_URL` is injected automatically
6. Set `JWT_SECRET_KEY` in Railway dashboard

### Option 2: Railway CLI

```bash
railway login
railway init
railway add postgresql
railway up
```

## Error Responses

All errors return a JSON body with `detail` and `code`:

```json
{
  "detail": "Only the project owner can perform this action",
  "code": "NOT_PROJECT_OWNER"
}
```

| HTTP Status | Code                  | Meaning                          |
|-------------|-----------------------|----------------------------------|
| 401         | `INVALID_CREDENTIALS` | Bad email or password            |
| 403         | `NOT_PROJECT_OWNER`   | Only the owner can do this       |
| 403         | `NOT_PROJECT_MEMBER`  | You are not in this project      |
| 403         | `ARCHIVED_PROJECT`    | Project is archived (read-only)  |
| 403         | `TASK_ACCESS_DENIED`  | Cannot modify another's task     |
| 404         | `PROJECT_NOT_FOUND`   | Project does not exist           |
| 404         | `TASK_NOT_FOUND`      | Task does not exist              |
| 409         | `DUPLICATE_EMAIL`     | Email already registered         |
| 422         | `VALIDATION_ERROR`    | Request body validation failed   |
| 422         | `INVALID_ASSIGNMENT`  | Cannot assign task to non-member |
