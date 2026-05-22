# Task Manager — Frontend

A React + TypeScript SPA for managing projects and tasks, consuming the Task Manager REST API.

Built with **Feature-based Clean Architecture** adapted for frontend: domain types, infrastructure adapters, application hooks/store, and presentation components.

## Architecture

```
src/
├── domain/               # TypeScript interfaces and enums (no logic)
│   └── types/
├── infrastructure/        # HTTP adapters (Axios, never imported by components)
│   └── api/
├── application/           # Custom hooks + Zustand store
│   ├── hooks/
│   └── store/
└── presentation/          # React components organized by feature
    ├── components/
    │   ├── ui/            # shadcn/ui wrappers
    │   └── common/        # Navbar, ProtectedRoute, ErrorBoundary
    ├── features/
    │   ├── auth/          # Login, Register
    │   ├── projects/      # List, Create, Edit, Detail
    │   ├── tasks/         # List, Form, Badges
    │   └── members/       # List, Add/Remove
    └── layouts/
```

### Layer Responsibilities

| Layer | Responsibility | Depends on |
|-------|---------------|------------|
| **domain** | TypeScript interfaces & enums | Nothing |
| **infrastructure** | Axios client, API adapters | Domain |
| **application** | TanStack Query hooks, Zustand store | Domain, Infrastructure |
| **presentation** | React components, pages, layouts | Application |

## Tech Stack

| Component | Library |
|-----------|---------|
| Framework | React 18 + TypeScript (strict) |
| Build tool | Vite |
| Routing | React Router v6 |
| Styling | Tailwind CSS v3 + shadcn/ui |
| Server state | TanStack Query v5 |
| Global state | Zustand |
| Forms | React Hook Form + Zod |
| HTTP | Axios |

## Local Setup

### Prerequisites

- Node.js 18+
- The Task Manager API running (see backend README)

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit VITE_API_URL to point to your backend (default: http://localhost:8000/api/v1)
```

### 3. Start dev server

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

### Build for production

```bash
npm run build
npm run preview
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

## Features

- **Auth**: Register and login with JWT, persisted to localStorage
- **Projects**: CRUD with role-based actions (owner vs member), archive toggle
- **Tasks**: CRUD with status/priority filters, inline updates, archived read-only mode
- **Members**: Add/remove members, task reassignment warning on removal
- **UI**: Responsive design, loading skeletons, toast notifications, error boundaries

## Deploy to Vercel

1. Push the repo to GitHub
2. Import the project on [Vercel](https://vercel.com)
3. Set `VITE_API_URL` environment variable to your backend URL
4. Deploy — Vercel auto-detects the Vite configuration

The `vercel.json` rewrites all routes to `index.html` for SPA routing.

## Screenshots

*(Add screenshots here)*

## Live Demo

*(Add link to live deployment)*
