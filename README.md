# TaskPilot

A production-grade **Project Management SaaS** built with FastAPI and React.

TaskPilot helps teams organize projects, track tasks, collaborate with comments, and stay on top of deadlines — all through a clean, modern interface and a well-architected API.

---

## Features

- **JWT Authentication** with access + refresh tokens
- **Role-Based Access Control** (Admin, Manager, Member)
- **Email verification** and **password reset** flows
- **Avatar upload** for user profiles
- **Projects** with members, status, deadlines, and archiving
- **Tasks** with priorities, statuses, due dates, labels, and assignment
- **Comments** on tasks
- **Labels** scoped to projects
- **Notifications** for task assignment, mentions, deadlines, and invitations
- **Activity logging** for key events
- **Dashboard** with project and task statistics
- **CSV export** for projects and tasks
- **Security headers** and **rate limiting**
- **Soft delete** everywhere — data is never permanently removed
- **Modern React frontend** with dark mode, responsive layout, and SaaS styling

---

## Architecture

```
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # API layer: routers, dependencies
│   │   ├── core/         # Config, security, DB engine, middleware
│   │   ├── crud/         # Data access layer (generic + specific)
│   │   ├── models/       # SQLModel domain models
│   │   ├── schemas/      # Request/response schemas
│   │   ├── services/     # Business logic: auth, notifications, CSV
│   │   ├── email-templates/
│   │   ├── alembic/      # Database migrations
│   │   └── tests/        # Backend tests
│   └── pyproject.toml
├── frontend/             # React (Vite + TanStack Router + shadcn/ui)
│   └── src/
│       ├── client/       # Auto-generated API client
│       ├── components/   # UI components
│       ├── routes/       # Pages
│       └── hooks/        # Auth, theme, toast hooks
├── compose.yml           # Docker Compose (Postgres, backend, frontend)
├── openapi.json          # Generated OpenAPI spec
└── .env                  # Environment configuration
```

---

## Tech Stack

**Backend:** FastAPI · SQLModel · SQLAlchemy · Alembic · PostgreSQL · Pydantic · PyJWT · Argon2/bCrypt

**Frontend:** React 19 · Vite · TanStack Router · TanStack Query · shadcn/ui · Tailwind CSS · Zod · Axios

**Infrastructure:** Docker · Docker Compose · Traefik · GitHub Actions · pre-commit

---

## Installation

### Prerequisites

- Docker & Docker Compose, **or**
- Python 3.14+, Node 20+, PostgreSQL 16+

### Quick Start with Docker

```bash
cp .env.example .env   # adjust values as needed
docker compose up -d
```

The frontend is available at `http://localhost` and the API docs at `http://localhost/api/v1/docs`.

### Local Development

**Backend:**

```bash
cd backend
pip install -r requirements.txt  # or use uv sync
alembic upgrade head
python app/initial_data.py
fastapi run app/main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Generate the frontend API client after backend changes:

```bash
./scripts/generate-client.sh
```

---

## API Documentation

Interactive docs are available at `/api/v1/docs` (Swagger UI) and `/api/v1/redoc`.

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/access-token` | Login, returns access + refresh tokens |
| POST | `/api/v1/auth/refresh-token` | Exchange refresh token for a new pair |
| POST | `/api/v1/auth/register` | Register a new account |
| GET | `/api/v1/auth/verify-email` | Verify email with token |
| POST | `/api/v1/auth/password-recovery/{email}` | Request password reset |
| POST | `/api/v1/auth/reset-password/` | Reset password with token |

### Projects & Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/v1/projects/` | List / create projects |
| GET/PATCH/DELETE | `/api/v1/projects/{id}` | Read / update / delete a project |
| GET/POST | `/api/v1/projects/{id}/members` | List / add members |
| GET/POST | `/api/v1/projects/{id}/labels` | List / create labels |
| GET/POST | `/api/v1/tasks/` | List / create tasks |
| GET/PATCH/DELETE | `/api/v1/tasks/{id}` | Read / update / delete a task |
| GET/POST | `/api/v1/tasks/{id}/comments` | List / add comments |

### Other

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/dashboard/` | Dashboard statistics |
| GET | `/api/v1/notifications/` | List notifications |
| GET | `/api/v1/activity/` | Activity log |
| GET | `/api/v1/exports/projects.csv` | Export projects |
| GET | `/api/v1/exports/tasks.csv` | Export tasks |

All list endpoints support pagination (`skip`, `limit`), filtering, sorting, and search.

---

## Screenshots

![Dashboard](./img/dashboard.png)
*Dashboard with project and task statistics*

![Projects](./img/dashboard-projects.png)
*Projects overview*

---

## Folder Structure

```
backend/app/
├── api/
│   ├── deps.py           # Dependencies (auth, RBAC, DB)
│   ├── main.py           # API router registration
│   └── routes/           # Feature routers
├── core/
│   ├── config.py         # Pydantic settings
│   ├── security.py       # JWT, password hashing
│   └── db.py             # Engine & init
├── crud/                 # CRUD operations
├── models/               # SQLModel models
├── schemas/              # API schemas
├── services/             # Business logic
├── alembic/              # Migrations
└── tests/                # Tests

frontend/src/
├── client/               # Generated API client
├── components/           # Reusable UI components
├── routes/               # Page routes
├── hooks/                # React hooks
└── lib/                  # Utilities
```

---

## Future Roadmap

- [ ] Real-time updates via WebSockets
- [ ] File attachments on tasks
- [ ] Advanced filtering and saved views
- [ ] Kanban board view
- [ ] Time tracking
- [ ] Team workspaces & organizations
- [ ] Webhook integrations
- [ ] Mobile app

---

## License

This project is licensed under the MIT License.
