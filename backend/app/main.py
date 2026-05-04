import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import psycopg
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.admin_users import router as admin_users_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.dashboard import router as dashboard_router
from app.api.endpoints.monitoring import router as monitoring_router, monitoring_service
from app.api.endpoints.search import router as search_router
from app.core.settings import settings
from app.services.user_sync_service import UserSyncService

scheduler = AsyncIOScheduler()

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def _run_pm_sync_job() -> None:
    if not settings.PLATFORM_POSTGRES_URL:
        return
    try:
        with psycopg.connect(settings.PLATFORM_POSTGRES_URL) as conn:
            UserSyncService(conn).sync_project_managers()
            conn.commit()
    except Exception as exc:
        print(f"[PM_SYNC_JOB] failed: {exc}")


def _run_monitoring_job() -> None:
    try:
        monitoring_service.run_once()
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
        _run_monitoring_job()
    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="Redmine Chat Assist API",
    description="AI-powered project management chatbot backed by Redmine",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":    settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs"
    }
