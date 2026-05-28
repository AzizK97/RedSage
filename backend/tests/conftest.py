# backend/tests/conftest.py - Shared fixtures

import pytest
from pytest_asyncio import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg

@pytest.fixture
def db_engine():
    """Test database (in-memory SQLite or test Postgres)"""
    engine = create_engine("sqlite:///:memory:")
    # Create all tables from models
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
async def app_client(db_engine):
    """FastAPI test client with mocked database"""
    from app.main import app
    from app.dependencies.db import get_db
    
    def override_get_db():
        SessionLocal = sessionmaker(bind=db_engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def mock_redmine_api(monkeypatch):
    """Mock Redmine API responses"""
    def mock_post(url, **kwargs):
        class MockResponse:
            status_code = 201
            def json(self):
                if "issues" in url:
                    return {"issue": {"id": 123}}
                return {}
        return MockResponse()
    
    monkeypatch.setattr("requests.post", mock_post)

@pytest.fixture
def mock_llm(monkeypatch):
    """Mock LLM responses"""
    def mock_invoke(messages, **kwargs):
        class MockMessage:
            content = "I'll create an issue for you."
        return MockMessage()
    
    monkeypatch.setattr("langchain_openai.ChatOpenAI.invoke", mock_invoke)