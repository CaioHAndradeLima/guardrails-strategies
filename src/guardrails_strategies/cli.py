import argparse
import json
import platform
import sys
from pathlib import Path

from .data import load_documents, load_golden, validate_golden
from .evaluation import evaluate
from .full_evaluation import run_full_evaluation
from .measure_profiles import evaluate_gates, load_measure_profiles
from .measurement_pipeline import run_measurement_pipeline
from .pipeline_evaluation import run_guardrails_pipeline_eval
from .scenario_evaluation import evaluate_test_use_cases, load_test_use_cases
from .strategies import select_strategies

ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = ROOT / "config" / "measure_profiles.json"


def _resolve_profile(name: str):
    profiles = load_measure_profiles(PROFILES_PATH)
    if name not in profiles:
        raise SystemExit(f"Unknown profile '{name}'. Choose from: {', '.join(sorted(profiles))}")
    return profiles[name]


def _environment_note() -> dict:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "note": "Synthetic regression fixtures; metrics score policy logic, not live cloud guardrail APIs.",
    }


def _run_evaluate(args: argparse.Namespace) -> dict:
    documents = load_documents(Path(args.documents))
    cases = load_golden(Path(args.golden))
    validate_golden(documents, cases)
    strategies = select_strategies([s.strip() for s in args.strategies.split(",") if s.strip()] or None)
    report = evaluate(cases, documents, strategies=strategies)
    report["environment"] = _environment_note()
    return report


def _run_evaluate_scenarios(args: argparse.Namespace) -> dict:
    documents = load_documents(Path(args.documents))
    scenarios = load_test_use_cases(Path(args.test_use_cases))
    return {
        "test_use_cases": evaluate_test_use_cases(scenarios, documents),
        "environment": _environment_note(),
    }


def _run_measure(args: argparse.Namespace) -> dict:
    documents = load_documents(Path(args.documents))
    cases = load_golden(Path(args.golden))
    validate_golden(documents, cases)
    profile = _resolve_profile(args.profile) if args.profile else None
    strategies = select_strategies(list(profile.strategies) if profile else None)
    report = run_measurement_pipeline(cases, documents, strategies=strategies)
    if profile:
        report["profile"] = {"name": profile.name, "description": profile.description}
    report["environment"] = _environment_note()
    return report


def _run_evaluate_pipeline(args: argparse.Namespace) -> dict:
    if not args.profile:
        raise SystemExit("evaluate-pipeline requires --profile (e.g. ci-guardrails-eval)")
    profile = _resolve_profile(args.profile)
    report = run_guardrails_pipeline_eval(ROOT, profile)
    report["environment"] = _environment_note()
    return report


def _run_check_measure(args: argparse.Namespace) -> dict:
    if not args.report or not args.profile:
        raise SystemExit("check-measure requires --profile and --report")
    report = json.loads(Path(args.report).read_text())
    profile = _resolve_profile(args.profile)
    return evaluate_gates(report, profile)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate layered guard-rails strategies")
    parser.add_argument(
        "command",
        choices=[
            "evaluate",
            "evaluate-scenarios",
            "evaluate-full",
            "evaluate-pipeline",
            "measure",
            "check-measure",
        ],
    )
    parser.add_argument("--documents", default=str(ROOT / "data/documents.json"))
    parser.add_argument("--golden", default=str(ROOT / "data/golden.json"))
    parser.add_argument("--test-use-cases", default=str(ROOT / "data/test_use_cases.json"))
    parser.add_argument("--output", default="")
    parser.add_argument("--strategies", default="", help="Comma-separated strategy names for evaluate/measure")
    parser.add_argument("--profile", default="", help="Measure profile from config/measure_profiles.json")
    parser.add_argument("--report", default="", help="JSON report for check-measure")
    args = parser.parse_args()

    if args.command == "evaluate":
        report = _run_evaluate(args)
    elif args.command == "evaluate-scenarios":
        report = _run_evaluate_scenarios(args)
    elif args.command == "measure":
        report = _run_measure(args)
    elif args.command == "evaluate-pipeline":
        report = _run_evaluate_pipeline(args)
    elif args.command == "check-measure":
        report = _run_check_measure(args)
    else:
        report = run_full_evaluation(ROOT)
        report["environment"] = _environment_note()

    serialized = json.dumps(report, indent=2, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(serialized + "\n")
    print(serialized)
    if args.command == "check-measure" and not report.get("passed", True):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
