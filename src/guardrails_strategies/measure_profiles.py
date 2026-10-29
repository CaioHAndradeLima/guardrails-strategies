import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StrategyGate:
    min_attack_block_rate: float | None = None
    max_false_deny_rate: float | None = None
    max_false_allow_rate: float | None = None
    min_classification_accuracy: float | None = None
    max_policy_ms_p95: float | None = None


@dataclass(frozen=True)
class ScenarioGates:
    min_test_use_case_pass_rate: float | None = None
    min_tenant_scoped_match_rate: float | None = None
    max_shared_index_false_allow_rate: float | None = None


@dataclass(frozen=True)
class MeasureProfile:
    name: str
    description: str
    strategies: tuple[str, ...]
    gates: dict[str, StrategyGate]
    scenario_gates: ScenarioGates | None = None


def load_measure_profiles(path: Path) -> dict[str, MeasureProfile]:
    payload = json.loads(path.read_text())
    profiles = {}
    for name, row in payload.get("profiles", {}).items():
        gates = {}
        for strategy, gate_row in row.get("gates", {}).items():
            gates[strategy] = StrategyGate(
                min_attack_block_rate=gate_row.get("min_attack_block_rate"),
                max_false_deny_rate=gate_row.get("max_false_deny_rate"),
                max_false_allow_rate=gate_row.get("max_false_allow_rate"),
                min_classification_accuracy=gate_row.get("min_classification_accuracy"),
                max_policy_ms_p95=gate_row.get("max_policy_ms_p95"),
            )
        scenario_row = row.get("scenario_gates") or {}
        scenario_gates = ScenarioGates(
            min_test_use_case_pass_rate=scenario_row.get("min_test_use_case_pass_rate"),
            min_tenant_scoped_match_rate=scenario_row.get("min_tenant_scoped_match_rate"),
            max_shared_index_false_allow_rate=scenario_row.get("max_shared_index_false_allow_rate"),
        )
        if not any(
            v is not None
            for v in (
                scenario_gates.min_test_use_case_pass_rate,
                scenario_gates.min_tenant_scoped_match_rate,
                scenario_gates.max_shared_index_false_allow_rate,
            )
        ):
            scenario_gates = None
        profiles[name] = MeasureProfile(
            name=name,
            description=row.get("description", ""),
            strategies=tuple(row.get("strategies", ["layered_guardrails"])),
            gates=gates,
            scenario_gates=scenario_gates,
        )
    return profiles


def _check_min(values: dict, key: str, expected_min: float, strategy: str, failures: list, checks: list) -> None:
    actual = values.get(key, 0)
    ok = actual >= expected_min
    checks.append({"strategy": strategy, "metric": key, "expected_min": expected_min, "actual": actual, "passed": ok})
    if not ok:
        failures.append(f"{strategy} {key} {actual:.3f} < {expected_min}")


def _check_max(values: dict, key: str, expected_max: float, strategy: str, failures: list, checks: list) -> None:
    actual = values.get(key, 0)
    ok = actual <= expected_max
    checks.append({"strategy": strategy, "metric": key, "expected_max": expected_max, "actual": actual, "passed": ok})
    if not ok:
        failures.append(f"{strategy} {key} {actual:.3f} > {expected_max}")


def evaluate_gates(report: dict, profile: MeasureProfile) -> dict:
    summary = report.get("summary", {})
    failures: list[str] = []
    checks: list[dict] = []

    for strategy, gate in profile.gates.items():
        values = summary.get(strategy)
        if values is None and report.get("scorecard"):
            sc = report["scorecard"].get("core_quality", {})
            if strategy == report.get("scorecard", {}).get("primary_strategy"):
                values = sc
        if values is None:
            failures.append(f"missing strategy summary '{strategy}'")
            continue
        if gate.min_attack_block_rate is not None:
            _check_min(values, "attack_block_rate", gate.min_attack_block_rate, strategy, failures, checks)
        if gate.max_false_deny_rate is not None:
            _check_max(values, "false_deny_rate", gate.max_false_deny_rate, strategy, failures, checks)
        if gate.max_false_allow_rate is not None:
            _check_max(values, "false_allow_rate", gate.max_false_allow_rate, strategy, failures, checks)
        if gate.min_classification_accuracy is not None:
            _check_min(values, "classification_accuracy", gate.min_classification_accuracy, strategy, failures, checks)
        if gate.max_policy_ms_p95 is not None:
            _check_max(values, "policy_ms_p95", gate.max_policy_ms_p95, strategy, failures, checks)

    if profile.scenario_gates is not None:
        scenarios = report.get("scenarios", {})
        sg = profile.scenario_gates
        if sg.min_test_use_case_pass_rate is not None:
            actual = scenarios.get("test_use_cases", {}).get("summary", {}).get("pass_rate")
            if actual is None:
                failures.append("missing scenarios.test_use_cases")
            else:
                ok = actual >= sg.min_test_use_case_pass_rate
                checks.append(
                    {
                        "scope": "scenarios.test_use_cases",
                        "metric": "pass_rate",
                        "expected_min": sg.min_test_use_case_pass_rate,
                        "actual": actual,
                        "passed": ok,
                    }
                )
                if not ok:
                    failures.append(f"test_use_case pass_rate {actual:.3f} < {sg.min_test_use_case_pass_rate}")
        if sg.min_tenant_scoped_match_rate is not None:
            actual = scenarios.get("tenant_scoped_vs_shared", {}).get("tenant_scoped_match_rate")
            if actual is None:
                failures.append("missing scenarios.tenant_scoped_vs_shared")
            else:
                ok = actual >= sg.min_tenant_scoped_match_rate
                checks.append(
                    {
                        "scope": "scenarios.tenant_scoped_vs_shared",
                        "metric": "tenant_scoped_match_rate",
                        "expected_min": sg.min_tenant_scoped_match_rate,
                        "actual": actual,
                        "passed": ok,
                    }
                )
                if not ok:
                    failures.append(
                        f"tenant_scoped_match_rate {actual:.3f} < {sg.min_tenant_scoped_match_rate}"
                    )
        if sg.max_shared_index_false_allow_rate is not None:
            actual = scenarios.get("shared_index_antipattern", {}).get("false_allow_rate_shared_index")
            if actual is None:
                failures.append("missing scenarios.shared_index_antipattern")
            else:
                ok = actual <= sg.max_shared_index_false_allow_rate
                checks.append(
                    {
                        "scope": "scenarios.shared_index_antipattern",
                        "metric": "false_allow_rate_shared_index",
                        "expected_max": sg.max_shared_index_false_allow_rate,
                        "actual": actual,
                        "passed": ok,
                    }
                )
                if not ok:
                    failures.append(
                        f"shared_index false_allow {actual:.3f} > {sg.max_shared_index_false_allow_rate}"
                    )

    return {"profile": profile.name, "passed": not failures, "failures": failures, "checks": checks}
