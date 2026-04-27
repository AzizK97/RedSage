import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.admin_users import router as admin_users_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.monitoring import router as monitoring_router, service as monitoring_service
from app.core.config import settings

scheduler = AsyncIOScheduler()

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENABLE_MONITORING:
        scheduler.add_job(
            monitoring_service.run_once,
            trigger=IntervalTrigger(seconds=settings.MONITORING_INTERVAL_SECONDS),
            id="monitoring_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()

    yield

    if settings.ENABLE_MONITORING and scheduler.running:
        scheduler.shutdown(wait=False)

    await monitoring_service.close()

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
app.include_router(monitoring_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":    settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs"
    }