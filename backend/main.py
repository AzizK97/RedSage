from dotenv import load_dotenv
import os

from fastapi import FastAPI
from routers.chat import router as chat_router

# Load .env from parent directory (backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = FastAPI()
app.include_router(chat_router)