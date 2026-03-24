"""Entry point for running benchmarks as a module."""

from benchmarks.cases import CASES
from benchmarks.runner import run_all
from benchmarks.report import print_report


def main():
    """Run all benchmarks and print report."""
    print("=" * 64)
    print("SUPERVISOR AGENT BENCHMARK SUITE")
    print("=" * 64)
    print(f"\nRunning {len(CASES)} benchmark cases...\n")
    
    results = run_all(CASES)
    
    print("\n")
    print_report(results)


if __name__ == "__main__":
    main()
