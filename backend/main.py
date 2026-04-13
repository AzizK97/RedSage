import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from agent.cache import close_redis   # We'll use it for pre-warm
from agent.tools.read import get_projects, get_members, get_versions  # your existing tools

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from routers.chat import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Redmine Agent...")
    print("🔥 Pre-warming Redmine cache...")

    # Pre-load common data into Redis
    await get_projects.ainvoke({})

    yield
    print("🛑 Shutting down...")
    await close_redis()

app = FastAPI(lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(chat_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name":    "Redmine Chat Assist API",
        "version": "1.0.0",
        "docs":    "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

