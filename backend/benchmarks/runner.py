import time
from dataclasses import dataclass
from typing import Any

from agent.supervisor import get_app
from benchmarks.cases import BenchmarkCase

@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    case_id: str
    passed: bool
    response: str
    latency_ms: float
    routed_agent: str
    error: str = None

def run_case(case: BenchmarkCase) -> BenchmarkResult:
    """Execute a single benchmark case and return result."""
    from langchain_core.messages import HumanMessage
    
    app = get_app()
    config = {"configurable": {"thread_id": f"bench-{case.id}"}}
    
    start = time.time()
    try:
        result = app.invoke(
            {"messages": [HumanMessage(content=case.query)]},
            config=config
        )
        latency_ms = (time.time() - start) * 1000
        
        # Extract final response
        response_text = ""
        routed_agent = "unknown"
        
        # Check messages in result for routing + final answer
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            # Find last AI message with content
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content and isinstance(msg.content, str):
                    response_text = msg.content
                    break
        
        # Run acceptance test
        passed = case.accept_fn(response_text)
        
        return BenchmarkResult(
            case_id=case.id,
            passed=passed,
            response=response_text[:200],  # truncate for logging
            latency_ms=latency_ms,
            routed_agent=routed_agent,
            error=None
        )
    
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return BenchmarkResult(
            case_id=case.id,
            passed=False,
            response="",
            latency_ms=latency_ms,
            routed_agent="error",
            error=str(e)
        )

def run_all(cases: list[BenchmarkCase]) -> list[BenchmarkResult]:
    """Run all benchmark cases sequentially."""
    results = []
    for i, case in enumerate(cases, 1):
        print(f"  [{i:2d}/{len(cases)}] {case.id:25s}", end=" ", flush=True)
        result = run_case(case)
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.latency_ms:7.2f}ms")
        results.append(result)
    return results