"""
Main Entry Point
Can be used to run the system or evaluation.

Usage:
  python main.py --mode cli           # Run CLI interface
  python main.py --mode web           # Run web interface
  python main.py --mode evaluate      # Run evaluation
"""

import argparse
import asyncio
import sys
from pathlib import Path


def run_cli():
    """Run CLI interface."""
    from src.ui.cli import main as cli_main
    cli_main()


def run_web():
    """Run web interface."""
    import subprocess
    print("Starting Streamlit web interface...")
    subprocess.run(["streamlit", "run", "src/ui/streamlit_app.py"])


async def run_evaluation():
    """Run system evaluation using LLM-as-a-Judge."""
    import yaml
    from dotenv import load_dotenv
    from src.autogen_orchestrator import AutoGenOrchestrator
    from src.evaluation.evaluator import SystemEvaluator

    # Load environment variables
    load_dotenv()

    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    print("=" * 70)
    print("MULTI-AGENT RESEARCH SYSTEM - EVALUATION MODE")
    print("=" * 70)

    # Initialize AutoGen orchestrator
    print("\nInitializing AutoGen orchestrator...")
    orchestrator = AutoGenOrchestrator(config)
    print("✓ Orchestrator initialized")

    # Initialize system evaluator
    print("Initializing system evaluator...")
    evaluator = SystemEvaluator(config, orchestrator=orchestrator)
    print("✓ Evaluator initialized")

    # Run full evaluation
    print("\n" + "=" * 70)
    print("RUNNING FULL SYSTEM EVALUATION")
    print("=" * 70)
    print(f"\nTest queries file: data/example_queries.json")
    print(f"Max queries: {config.get('evaluation', {}).get('num_test_queries', 'All')}")
    print("\nThis may take several minutes...\n")

    # Run evaluation
    report = await evaluator.evaluate_system("data/example_queries.json")

    # Display results
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)

    summary = report.get("summary", {})
    scores = report.get("scores", {})

    print(f"\nTotal Queries: {summary.get('total_queries', 0)}")
    print(f"Successful: {summary.get('successful', 0)}")
    print(f"Failed: {summary.get('failed', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0.0):.1%}")

    print(f"\nOverall Average Score: {scores.get('overall_average', 0.0):.3f}")

    print("\nScores by Criterion:")
    for criterion, score in scores.get("by_criterion", {}).items():
        print(f"  • {criterion}: {score:.3f}")

    # Show best and worst performing queries
    best = report.get("best_result")
    worst = report.get("worst_result")

    if best:
        print(f"\n✓ Best Performing Query (Score: {best.get('score', 0.0):.3f}):")
        print(f"  {best.get('query', '')[:80]}...")

    if worst:
        print(f"\n⚠ Lowest Performing Query (Score: {worst.get('score', 0.0):.3f}):")
        print(f"  {worst.get('query', '')[:80]}...")

    print("\n" + "=" * 70)
    print("RESULTS SAVED")
    print("=" * 70)
    print("\nDetailed results and summary have been saved to outputs/")
    print("Check outputs/ directory for:")
    print("  • evaluation_YYYYMMDD_HHMMSS.json (full results)")
    print("  • evaluation_summary_YYYYMMDD_HHMMSS.txt (summary report)")
    print("=" * 70 + "\n")


def run_autogen():
    """Run AutoGen example."""
    import subprocess
    print("Running AutoGen example...")
    subprocess.run([sys.executable, "example_autogen.py"])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research Assistant"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "web", "evaluate", "autogen"],
        default="autogen",
        help="Mode to run: cli, web, evaluate, or autogen (default)"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    elif args.mode == "web":
        run_web()
    elif args.mode == "evaluate":
        asyncio.run(run_evaluation())
    elif args.mode == "autogen":
        run_autogen()


if __name__ == "__main__":
    main()
