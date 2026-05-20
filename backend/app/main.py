from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env before any app imports that read os.environ (e.g. app.core.config).
_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(_backend_root / ".env")
load_dotenv(_backend_root / "app" / ".env", override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import psycopg
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.admin_users import router as admin_users_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.dashboard import router as dashboard_router
from app.api.endpoints.monitoring import router as monitoring_router, monitoring_data_service
from app.api.endpoints.search import router as search_router
from app.api.endpoints.redmine_widget_gate import router as redmine_widget_gate_router
from app.api.endpoints.redmine_metadata import router as redmine_metadata_router
from app.core.settings import settings
from app.services.user_sync_service import UserSyncService

scheduler = AsyncIOScheduler()


def _run_pm_sync_job() -> None:
    if not settings.PLATFORM_POSTGRES_URL:
        return
    try:
        with psycopg.connect(settings.PLATFORM_POSTGRES_URL) as conn:
            UserSyncService(conn).sync_project_managers()
            conn.commit()
    except Exception as exc:
        print(f"[PM_SYNC_JOB] failed: {exc}")


async def _run_monitoring_job() -> None:
    try:
        await monitoring_data_service.run_once()
    except Exception as exc:
        print(f"[MONITORING_JOB] failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.PM_SYNC_ENABLED and settings.PM_SYNC_INTERVAL_MINUTES > 0:
        scheduler.add_job(
            _run_pm_sync_job,
            "interval",
            minutes=settings.PM_SYNC_INTERVAL_MINUTES,
            id="pm_sync_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
        _run_pm_sync_job()

    if settings.ENABLE_MONITORING and settings.MONITORING_INTERVAL_SECONDS > 0:
        scheduler.add_job(
            _run_monitoring_job,
            "interval",
            seconds=settings.MONITORING_INTERVAL_SECONDS,
            id="monitoring_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        if not scheduler.running:
            scheduler.start()
        await _run_monitoring_job()
    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="Redmine Chat Assist API",
    description="AI-powered project management chatbot backed by Redmine",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Mount the built Vue widget ────────────────────────────────────────────────

from pathlib import Path
import os

# Get absolute path to the widget build folder
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "redmineAgentUI" / "dist-widget"

if not frontend_dist.exists():
    print(f"⚠️  Vue dist folder not found at {frontend_dist}")
    print("⚠️  Run: cd frontend/redmineAgentUI && pnpm build:widget")

app.mount(
    "/api/static",
    StaticFiles(directory=str(frontend_dist), check_dir=False),
    name="static",
)

if frontend_dist.exists():
    print(f"✓ Serving Vue widget from {frontend_dist}")

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_PLATFORM + settings.CORS_ORIGINS_PLUGIN,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(chat_router)
app.include_router(admin_users_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(monitoring_router)
app.include_router(search_router)
app.include_router(redmine_widget_gate_router)
app.include_router(redmine_metadata_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":    settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs"
    }
