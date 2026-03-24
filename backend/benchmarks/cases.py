from dataclasses import dataclass, field
from typing import Optional, Callable, Any

@dataclass
class BenchmarkCase:
    """A single test case for the supervisor."""
    id: str
    query: str
    expected_agent: str
    accept_fn: Callable[[Any], bool]  # returns True if result passes
    description: str = ""
    tags: list[str] = field(default_factory=list)  # e.g., ["read", "overview", "tools"]

# Example test cases
CASES = [
    BenchmarkCase(
        id="overview-1",
        query="What projects do we have?",
        expected_agent="overview_agent",
        accept_fn=lambda result: "project" in result.lower(),
        description="List all projects",
        tags=["read", "overview"]
    ),
    BenchmarkCase(
        id="planning-write-1",
        query="Create a new sprint called Sprint 5 for ai-platform-project due 2026-05-01",
        expected_agent="planning_agent",
        accept_fn=lambda result: "created" in result.lower() or "sprint" in result.lower(),
        description="Create sprint (write operation)",
        tags=["write", "planning"]
    ),
    BenchmarkCase(
        id="tasks-read-1",
        query="List open issues in the ai-platform-project",
        expected_agent="tasks_agent",
        accept_fn=lambda result: len(result) > 10,  # non-trivial response
        description="List tasks",
        tags=["read", "tasks"]
    ),
]