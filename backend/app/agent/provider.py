from __future__ import annotations

import threading
from typing import ClassVar

from langchain_ollama import ChatOllama
from app.core.settings import Settings, get_settings

# ---------------------------------------------------------------------------
# ModelProvider — thread-safe singleton + DI boundary
# ---------------------------------------------------------------------------

class ModelProvider:
    """Singleton that builds LangChain ChatOllama model instances.

    Production:
        provider = ModelProvider.instance()
        llm = provider.build()

    Tests:
        ModelProvider._set_instance(FakeProvider(...))
        ModelProvider.reset()
    """

    _instance: ClassVar[ModelProvider | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, app_settings: Settings) -> None:
        self._settings = app_settings

    # ------------------------------------------------------------------
    # Singleton lifecycle
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls) -> ModelProvider:
        """Get or create the singleton ModelProvider."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(get_settings())
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton — test teardown only."""
        with cls._lock:
            cls._instance = None

    @classmethod
    def _set_instance(cls, provider: ModelProvider) -> None:
        """Inject a custom provider — test setup only."""
        with cls._lock:
            cls._instance = provider

    # ------------------------------------------------------------------
    # Model factory
    # ------------------------------------------------------------------

    def build(self) -> ChatOllama:
        """Build and return a ChatOllama model instance configured from settings.

        Returns:
            ChatOllama: Configured language model instance for Ollama.

        Raises:
            ValueError: If Ollama base URL is not configured.
        """
        base_url = self._settings.LLM_BASE_URL
        if not base_url:
            raise ValueError(
                "LLM_BASE_URL is required for Ollama model usage. "
                "Set LLM_BASE_URL environment variable or provide it in settings."
            )

        return ChatOllama(
            model=self._settings.LLM_MODEL,
            base_url=base_url,
            temperature=self._settings.LLM_TEMPERATURE,
            top_p=self._settings.LLM_TOP_P,
            top_k=self._settings.LLM_TOP_K,
        )