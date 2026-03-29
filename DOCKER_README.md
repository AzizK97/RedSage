# Docker Setup Guide

This project includes a complete Docker Compose setup for easy deployment.

## Quick Start

### 1. Clone the repository (if not already done)
```bash
git clone <repo-url>
cd RedmineChatAssist_Test1
```

### 2. Configure environment variables
```bash
cp .env.example .env
```

Then edit `.env` and set your API keys:
```
OPENROUTER_API_KEY=your-actual-key-here
REDMINE_API_KEY=your-redmine-api-key
```

### 3. Start the services
```bash
docker compose up -d
```

This will:
- Build the backend Docker image
- Start the backend service (accessible at http://localhost:8000)
- Start a Redmine instance (accessible at http://localhost:3000)
- Start a MySQL database for Redmine

### 4. Verify services are running
```bash
docker compose ps
```

You should see three containers:
- `redmine-chat-assist-backend` (Python backend)
- `redmine-server` (Redmine)
- `redmine-mysql` (MySQL database)

### 5. Access the services

**Backend API**: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Chat endpoint: POST http://localhost:8000/chat

**Redmine**: http://localhost:3000
- Default login: admin / admin (first time setup required)

## Common Commands

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f redmine
```

### Stop services
```bash
docker compose down
```

### Stop and remove all data (volumes)
```bash
docker compose down -v
```

### Rebuild images
```bash
docker compose up --build
```

### Run commands in container
```bash
# Run benchmarks
docker compose exec backend python -m benchmarks

# Run CLI agent
docker compose exec backend python -m agent.supervisor

# Access shell
docker compose exec backend /bin/bash
```

## Configuration

### Using external Redmine
If you want to use an external Redmine instance instead of the Docker one:

1. Edit `.env`:
```
REDMINE_URL=https://your-redmine-instance.com
REDMINE_API_KEY=your-api-key
```

2. Modify `docker-compose.yml` and remove/comment out the `redmine` and `mysql` services

3. Run:
```bash
docker compose up -d backend
```

### Custom ports
Edit `.env` to change ports:
```
BACKEND_PORT=8080
REDMINE_PORT=3001
```

## Troubleshooting

### Backend can't connect to Redmine
- Ensure both services are running: `docker compose ps`
- Check backend logs: `docker compose logs backend`
- Verify REDMINE_URL and REDMINE_API_KEY in `.env`

### MySQL connection errors
```bash
# Check MySQL is healthy
docker compose logs mysql

# Restart MySQL
docker compose restart mysql
```

### Port already in use
Change the port in `.env`:
```
BACKEND_PORT=8080   # Instead of 8000
REDMINE_PORT=3001   # Instead of 3000
```

### Permission denied (Linux)
May need `sudo`:
```bash
sudo docker compose up
```

Or add your user to docker group:
```bash
sudo usermod -aG docker $USER
```

## Development Workflow

### Hot reload (backend updates)
The backend service automatically reloads when code changes:
```bash
# Make changes to backend/
# uvicorn will auto-reload
docker compose logs -f backend
```

### Execute benchmarks
```bash
docker compose exec backend python -m benchmarks
```

### Run CLI interactive agent
```bash
docker compose exec -it backend python -m agent.supervisor
```

## Next Steps

1. Set up your OpenRouter API key in `.env`
2. Configure Redmine projects and API access
3. Test the agent routing with the CLI
4. Run benchmarks to validate agent behavior

For more details, see the main README.md
