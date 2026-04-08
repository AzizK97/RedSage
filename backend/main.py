import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from routers.chat import router as chat_router

app = FastAPI(
    title="Redmine Chat Assist API",
    description="AI-powered project management chatbot backed by Redmine",
    version="1.0.0",
)

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