import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.admin_users import router as admin_users_router
from app.core.config import settings

# from monitoring.config import settings
# from monitoring.service import MonitoringService
# from routers.monitoring import router as monitoring_router

#scheduler = AsyncIOScheduler()
#monitoring_service = MonitoringService()

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# @asynccontextmanager
# async def lifespan(app):
#     if settings.ENABLE_MONITORING:
#         scheduler.add_job(
#             monitoring_service.run_once,
#             "interval",
#             seconds=settings.MONITORING_INTERVAL_SECONDS,
#             id="monitoring_job",
#             replace_existing=True,
#             max_instances=1,
#             coalesce=True,
#         )
#         scheduler.start()
    
#     yield

#     if settings.ENABLE_MONITORING:
#         scheduler.shutdown()

app = FastAPI(
    title="Redmine Chat Assist API",
    description="AI-powered project management chatbot backed by Redmine",
    version="1.0.0"
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
#app.include_router(monitoring_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":    settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs"
    }