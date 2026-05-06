# Redmine Chat Assistant

A multi-agent AI system for intelligent Redmine project management. Route natural language queries to specialized agents that handle tasks, planning, overview, and reporting.

## 🎯 Overview

**Redmine Chat Assistant** uses a supervisor agent pattern to delegate user queries to four specialized agents:

- **Overview Agent** — Project summaries, team info, general status
- **Tasks Agent** — Task listing, filtering, creation, updates, time logging
- **Planning Agent** — Sprint management, milestone tracking, risk analysis
- **Report Agent** — Complete project health reports with metrics

Each agent has read tools (query Redmine) and write tools (create/modify items). Write operations require human approval via HITL (Human-in-the-Loop) middleware.

## 🚀 Quick Start

This project has 3 parts:

- `backend/` — FastAPI service and AI orchestration
- `frontend/redmineAgentUI/` — Vue UI used to interact with the assistant
- `plugins/redmine_ai_chat_widget/` — Redmine plugin that embeds the widget inside Redmine

For the smoothest setup, start the backend first, then the frontend, then install the plugin into Redmine.

### Option 1: Docker Compose (Recommended)

**One command to run everything:**

```bash
# Clone the repo
git clone <repo-url>
cd RedmineChatAssist_Test1

# Copy environment template
cp .env.example .env

# Edit .env and set your API keys
OPENROUTER_API_KEY=sk-or-v1-...
REDMINE_API_KEY=your-redmine-api-key

# Start all services (backend, Redmine, MySQL)
docker compose up -d

# Services are now running:
# - Backend API: http://localhost:8000
# - Redmine: http://localhost:3000
# - API Docs: http://localhost:8000/docs
```

See [DOCKER_README.md](DOCKER_README.md) for full Docker guide, custom ports, external Redmine setup, and troubleshooting.

### Option 2: Run locally in development

#### 1) Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API:

- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

#### 2) Start the frontend

```bash
cd frontend/redmineAgentUI
pnpm install
pnpm dev
```

Frontend dev server:

- `http://localhost:5173`

#### 3) Install the Redmine plugin

The plugin lives in `plugins/redmine_ai_chat_widget/`. Copy or symlink it into your Redmine installation's `plugins/` folder.

Example:

```bash
# from your Redmine install directory
cp -R /path/to/RedmineChatAssist_Test1/plugins/redmine_ai_chat_widget plugins/
bundle install
bundle exec rake redmine:plugins:migrate RAILS_ENV=production
```

Then restart Redmine.

#### 4) Configure the plugin

Open the Redmine plugin settings and set:

- `backend_url` → URL of the backend API, usually `http://localhost:8000`
- `jwt_secret` → same secret used by the backend
- `jwt_issuer` → optional issuer value, must match the backend if set
- `jwt_audience` → optional audience value, must match the backend if set

The backend must also allow the Redmine origin in CORS. The default CORS variables are:

- `CORS_ORIGINS_PLATFORM` for the frontend app
- `CORS_ORIGINS_PLUGIN` for the Redmine plugin host

If you run Redmine on a different port or host, add that origin to `CORS_ORIGINS_PLUGIN`.


### Start the CLI assistant

If you want the command-line assistant instead of the web UI:

```bash
cd backend
python -m agent.supervisor
```

## 📚 Usage

### CLI Interactive Mode

```bash
cd backend
python -m agent.supervisor
```

Example conversation:
```
You : What projects do we have?
Agent: [routing] Delegating to overview_agent
[tool] Calling tool: get_projects
Final: We have 3 projects: ai-platform-project, e-commerce-platform, internal-tools

You : List open issues in ai-platform-project
Agent: [tool] Calling tool: get_issues
Final: Found 12 open issues...

You : exit
Bye!
```

### API Endpoint

**Chat endpoint:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What projects do we have?",
    "thread_id": "session-1"
  }'
```

**Response:**
```json
{
  "response": "We have 3 projects...",
  "requires_human": false,
  "interrupts": {}
}
```

**Write operations (require approval):**

```bash
# Step 1: Request write action (returns pending)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create sprint Sprint 5 in ai-platform-project due 2026-06-01",
    "thread_id": "session-1"
  }'

# Response: requires_human=true, with action details

# Step 2: Approve
curl -X POST http://localhost:8000/approve/session-1?decision_type=approve

# Or reject
curl -X POST "http://localhost:8000/approve/session-1?decision_type=reject&message=Not ready yet"
```

### API Documentation

Interactive API docs available at: **http://localhost:8000/docs**

## 🧪 Testing

### Run Benchmarks

Validate agent routing, latency, and accuracy:

```bash
cd backend
python -m benchmarks
```

Output:
```
================================================================================
                    SUPERVISOR AGENT BENCHMARK REPORT
================================================================================

OVERALL RESULTS:
  Total Cases:              9
  Passed:                   8 ✅
  Failed:                   1 ❌
  Pass Rate:                88.9%

LATENCY STATISTICS:
  Average:                  2341.50ms
  Min:                      1245.23ms
  Max:                      4123.67ms

RESULTS BY AGENT TYPE:
  overview_agent:
    Pass Rate:              100.0% (2/2)
    Avg Latency:            1523.45ms
  tasks_agent:
    Pass Rate:              83.3% (5/6)
    Avg Latency:            2341.50ms
  planning_agent:
    Pass Rate:              100.0% (2/2)
    Avg Latency:            2789.12ms
...
```

Add test cases in `backend/benchmarks/cases.py`.

## 🏗️ Architecture

```
backend/
├── agent/
│   ├── supervisor.py          # Multi-agent orchestrator
│   ├── agents/
│   │   ├── overview.py        # Project overview agent
│   │   ├── tasks.py           # Task management agent
│   │   ├── planning.py        # Sprint planning agent
│   │   └── report.py          # Report generation agent
│   └── tools/
│       ├── read.py            # Redmine read operations (GET)
│       └── write.py           # Redmine write operations (POST/PUT)
├── routers/
│   └── chat.py                # FastAPI endpoints
├── benchmarks/
│   ├── cases.py               # Test case definitions
│   ├── runner.py              # Benchmark execution
│   └── report.py              # Results aggregation
└── main.py                    # App entry (optional)

Dockerfile                      # Container build
docker-compose.yml             # Local stack (backend + Redmine + MySQL)
.env.example                   # Environment template
requirements.txt               # Python dependencies
```

## 🔌 Integration with Redmine

The agents connect to Redmine via REST API using an API key.

**Setup required in Redmine:**

1. Create a Redmine user account
2. Enable API access (Administration → Settings → Enable REST API)
3. Generate API key (My Account → API access key)
4. Set in `.env`:
   ```
   REDMINE_URL=http://your-redmine-instance.com
   REDMINE_API_KEY=your-api-key
   ```

## 🤖 Agent Routing Rules

The supervisor uses these rules to delegate queries:

| Intent | Agent | Example |
|--------|-------|---------|
| General project info | `overview_agent` | "What projects exist?" |
| Task listing & filtering | `tasks_agent` | "List open issues" |
| Task creation/modification | `tasks_agent` | "Create ticket 'Bug fix'" |
| Sprint management | `planning_agent` | "Create sprint", "Analyze sprint 2" |
| Full project report | `report_agent` | "Generate health report" |

## 🛡️ Human-in-the-Loop (HITL)

Write operations are suspended for approval before execution:

**Write tools that trigger HITL:**
- `create_issue`
- `update_issue_status`
- `reassign_issue`
- `add_comment_to_issue`
- `update_issue_dates`
- `log_time`
- `create_version`
- `update_version_dates`

**Workflow:**
1. User requests write → API returns `requires_human=true`
2. Human reviews action details
3. Human approves/rejects via `/approve/{thread_id}`
4. On approval: tool executes; on reject: operation cancelled

## 🔐 Environment Variables

Create a `.env` file (copy from `.env.example`):

```
# OpenRouter (LLM provider)
OPENROUTER_API_KEY=sk-or-v1-...

# Redmine connection
REDMINE_URL=http://localhost:3000
REDMINE_API_KEY=your-api-key

# Docker Compose
BACKEND_PORT=8000
REDMINE_PORT=3000
MYSQL_ROOT_PASSWORD=redmine
```

### Verify your environment quickly

Use the included verifier to check that essential environment variables are set. Make the script executable and run it from the repo root:

```bash
chmod +x scripts/verify_env.sh
bash scripts/verify_env.sh
```

If the script reports missing variables, copy the sample files and fill them in:

```bash
cp backend/.env.sample backend/.env
cp frontend/redmineAgentUI/.env.sample frontend/redmineAgentUI/.env
# or copy root-level .env from .env.example
```

### Windows (PowerShell) notes

If your colleagues use Windows, the steps below work in PowerShell (Developer PowerShell / PowerShell Core):

- Create and activate Python venv (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Create `.env` files by copying the samples:

```powershell
Copy-Item backend\.env.sample backend\.env
Copy-Item frontend\redmineAgentUI\.env.sample frontend\redmineAgentUI\.env
```

- Set environment variables for the current PowerShell session (non-persistent):

```powershell
$env:REDMINE_URL = 'http://localhost:3000'
$env:REDMINE_API_KEY = 'your-api-key'
$env:OPENROUTER_API_KEY = 'sk-or-...'
```

- To persist variables for your user account (Windows), use `setx`:

```powershell
setx REDMINE_URL "http://localhost:3000"
setx REDMINE_API_KEY "your-api-key"
setx OPENROUTER_API_KEY "sk-or-..."
```

- Verify env with the PowerShell verifier:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_env.ps1
```

Note: `verify_env.ps1` will also load values from `.env` files if present, and returns a non-zero exit code when variables are missing.

## 📦 Dependencies

- **LLM**: OpenRouter (OpenAI-compatible API)
- **Agents**: LangChain + LangGraph
- **API**: FastAPI + Uvicorn
- **Redmine Client**: requests
- **Other**: pydantic, python-dotenv

See `backend/requirements.txt` for pinned versions.

## 🐳 Docker

Full Docker Compose setup included:

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f

# Run benchmarks inside container
docker compose exec backend python -m benchmarks

# Interactive CLI
docker compose exec -it backend python -m agent.supervisor

# Stop all
docker compose down
```

See [DOCKER_README.md](DOCKER_README.md) for advanced Docker usage.

## 🧑‍💻 Development

### Add a New Test Case

Edit `backend/benchmarks/cases.py`:

```python
CASES = [
    # ... existing cases
    BenchmarkCase(
        id="my-test",
        query="Your test question here",
        expected_agent="tasks_agent",
        accept_fn=lambda result: "expected_word" in result.lower(),
        description="Test description",
        tags=["read", "tasks"]
    ),
]
```

Run: `python -m benchmarks`

### Modify Agent Prompt

Edit the corresponding agent in `backend/agent/agents/`:

```python
# E.g., backend/agent/agents/tasks.py
TASKS_PROMPT = """
Your updated prompt here...
"""
```

Changes auto-reload in development mode.

### Add a New Tool

1. Define tool function in `backend/agent/tools/read.py` or `write.py`
2. Add `@tool` decorator
3. Include in agent's `tools` list
4. Update agent prompt with tool description

## 🐛 Troubleshooting

### Backend can't connect to Redmine
```bash
# Check REDMINE_URL and REDMINE_API_KEY in .env
# Verify Redmine is accessible
curl -I http://localhost:3000
```

### "User not found" from OpenRouter
```bash
# Verify API key is correct
# Check OPENROUTER_API_KEY in .env
# Regenerate key if needed
```

### Port already in use
```bash
# Change port in .env or docker-compose
BACKEND_PORT=8080
REDMINE_PORT=3001
```

### Benchmark tests failing
```bash
# Check Redmine has data (projects, issues, sprints)
# View detailed logs: docker compose logs backend
# Run single case for debugging
```

## 📖 Documentation

- [DOCKER_README.md](DOCKER_README.md) — Complete Docker guide
- [Architecture diagram](k3s/namespace.yaml) — K3s deployment reference
- Agent prompts — See `backend/agent/agents/*.py`
- API docs — Hosted at http://localhost:8000/docs

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes focus on one agent or tool
4. Run benchmarks to validate
5. Commit + push
6. Submit PR

## 📄 License

[Add your license here]

## 🙋 Support

For issues or questions:
- Check [DOCKER_README.md](DOCKER_README.md) for Docker problems
- Review agent prompts in `backend/agent/agents/`
- Check Redmine API key and connectivity
- Review logs: `docker compose logs -f` or `python -m agent.supervisor`

---

**Happy project managing! 🚀**
