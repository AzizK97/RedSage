from benchmarks.runner import BenchmarkResult

def generate_report(results: list[BenchmarkResult]) -> str:
    """Generate summary report from benchmark results."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    avg_latency = sum(r.latency_ms for r in results) / total if total > 0 else 0
    
    # Group by agent
    by_agent = {}
    for r in results:
        if r.routed_agent not in by_agent:
            by_agent[r.routed_agent] = {"passed": 0, "failed": 0, "latencies": []}
        if r.passed:
            by_agent[r.routed_agent]["passed"] += 1
        else:
            by_agent[r.routed_agent]["failed"] += 1
        by_agent[r.routed_agent]["latencies"].append(r.latency_ms)
    
    report = f"""
╔════════════════════════════════════════╗
║     BENCHMARK REPORT                   ║
╚════════════════════════════════════════╝

OVERALL RESULTS:
  Total Cases:    {total}
  Passed:         {passed} ✅
  Failed:         {failed} ❌
  Pass Rate:      {pass_rate:.1f}%
  Avg Latency:    {avg_latency:.2f}ms

RESULTS BY AGENT:
"""
    
    for agent, stats in by_agent.items():
        agent_total = stats["passed"] + stats["failed"]
        agent_rate = (stats["passed"] / agent_total * 100) if agent_total > 0 else 0
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
        report += f"""
  {agent}:
    Pass Rate:    {agent_rate:.1f}% ({stats['passed']}/{agent_total})
    Avg Latency:  {avg_lat:.2f}ms
"""
    
    # Failures detail
    failures = [r for r in results if not r.passed]
    if failures:
        report += f"\nFAILED CASES:\n"
        for r in failures:
            report += f"  ❌ {r.case_id}: {r.error or 'Acceptance test failed'}\n"
    
    return report

def print_report(results: list[BenchmarkResult]):
    """Print formatted report to stdout."""
    print(generate_report(results))
    
    # Print individual failures for debugging
    failures = [r for r in results if not r.passed]
    if failures:
        print("\nDETAILED FAILURE LOGS:")
        print("-" * 64)
        for r in failures:
            print(f"\n[{r.case_id}]")
            if r.error:
                print(f"  Exception: {r.error}")
            if r.response:
                print(f"  Response: {r.response[:150]}...")
            else:
                print(f"  Response: (empty)")
        print("\n" + "-" * 64)