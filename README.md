# Redmine Chat Assist

Redmine Chat Assist is a three-part system for AI-assisted Redmine workflows:

- a **backend** API that handles chat, monitoring, authentication, and Redmine integration
- a **frontend** web app for the chat and dashboard experience
- a **Redmine plugin** that embeds the assistant inside Redmine

This README focuses on the current architecture and the exact steps to clone and start each part.

## Architecture

### Backend

The backend lives in `backend/` and is a FastAPI application.

What it does:

- exposes chat, auth, dashboard, search, and monitoring endpoints
- talks to Redmine through the REST API
- runs background jobs for project-manager sync and monitoring
- provides CORS access for the frontend and the Redmine plugin

Main entry point:

- `backend/app/main.py`

Key configuration:

- `backend/.env` for backend runtime settings
- `JWT_SECRET`, `JWT_ISSUER`, `JWT_AUDIENCE`
- `CORS_ORIGINS_PLATFORM`
- `CORS_ORIGINS_PLUGIN`

### Frontend

The frontend lives in `frontend/redmineAgentUI/` and is a Vue 3 + Vite + TypeScript app.

What it does:

- provides the main user interface for chat, dashboard, and monitoring views
- calls the backend API over HTTP
- uses Vue Router so views survive refreshes

Main commands:

- `pnpm dev` for local development
- `pnpm build` for production build checks

### Redmine Plugin

The plugin lives in `plugins/redmine_ai_chat_widget/` and is installed inside a Redmine instance.

What it does:

- injects the assistant widget into Redmine pages
- passes user context and a signed widget token to the frontend
- reads its settings from Redmine's plugin settings page

Important plugin settings:

- `backend_url`
- `jwt_secret`
- `jwt_issuer`
- `jwt_audience`

The plugin does not run as a separate server. Redmine loads it as part of the Redmine application.

## Repository layout

```text
backend/                     FastAPI backend and agents
frontend/redmineAgentUI/     Vue frontend
plugins/redmine_ai_chat_widget/  Redmine plugin
scripts/                     Helper scripts
docker-compose.yml           Local full-stack setup
Dockerfile                   Container image for the backend stack
```

## Clone the repository

```bash
git clone <repo-url>
cd RedmineChatAssist_Test1
```

## Start the backend

The backend is the API that the frontend and plugin both depend on.

### 1) Configure environment variables

Create `backend/.env` from the sample file:

```bash
cp backend/.env.sample backend/.env
```

Fill in at least these values:

- `OPENROUTER_API_KEY`
- `REDMINE_URL`
- `REDMINE_API_KEY`
- `JWT_SECRET`
- `CORS_ORIGINS_PLATFORM`
- `CORS_ORIGINS_PLUGIN`

### 2) Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3) Start the backend server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API: `http://localhost:8000`
- docs: `http://localhost:8000/docs`

## Start the frontend

The frontend is the browser UI for the assistant.

### 1) Configure environment variables

Create `frontend/redmineAgentUI/.env` from the sample file:

```bash
cp frontend/redmineAgentUI/.env.sample frontend/redmineAgentUI/.env
```

The most important value is:

- `VITE_API_BASE_URL` — usually `http://localhost:8000`

### 2) Install dependencies

```bash
cd frontend/redmineAgentUI
pnpm install
```

### 3) Start the frontend dev server

```bash
pnpm dev
```

Frontend URL:

- `http://localhost:5173`

### 4) Optional production build check

```bash
pnpm build
```

## Install and start the Redmine plugin

The plugin is how the assistant appears inside Redmine.

### 1) Copy the plugin into Redmine

From your Redmine installation directory, copy the plugin folder into `plugins/`:

```bash
cp -R /path/to/RedmineChatAssist_Test1/plugins/redmine_ai_chat_widget /path/to/redmine/plugins/
```

You can also symlink it during development if that is easier.

### 2) Install plugin dependencies and migrate

From the Redmine root:

```bash
bundle install
bundle exec rake redmine:plugins:migrate RAILS_ENV=production
```

If you are developing locally, use the appropriate environment instead of `production`.

### 3) Restart Redmine

Restart the Redmine application so it loads the plugin.

### 4) Configure the plugin in Redmine

Open the Redmine plugin settings and set:

- `backend_url` to the backend address, usually `http://localhost:8000`
- `jwt_secret` to the same secret used by the backend
- `jwt_issuer` if you use issuer validation
- `jwt_audience` if you use audience validation

The plugin expects the backend to allow the Redmine origin through CORS.

## How the parts work together

1. The **backend** serves the API and generates/validates the assistant tokens.
2. The **frontend** provides the standalone web UI for the assistant.
3. The **Redmine plugin** embeds the assistant inside Redmine and points to the backend.

In practice, you usually start them in this order:

1. backend
2. frontend
3. Redmine with the plugin enabled

## Useful scripts

- `scripts/verify_env.sh` — checks common environment variables on Linux/macOS
- `scripts/verify_env.ps1` — checks common environment variables on Windows PowerShell

## Troubleshooting

- If the frontend cannot reach the backend, confirm `VITE_API_BASE_URL` and CORS settings.
- If the Redmine plugin cannot reach the backend, confirm `backend_url` and `CORS_ORIGINS_PLUGIN`.
- If authentication fails, confirm `JWT_SECRET`, `JWT_ISSUER`, and `JWT_AUDIENCE` match between backend and plugin.
