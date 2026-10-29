import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestCliSmoke(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "guardrails_strategies.cli", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_evaluate_full(self):
        out = ROOT / "reports" / "test-full-smoke.json"
        proc = self._run("evaluate-full", "--output", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(out.read_text())
        self.assertEqual(payload["coverage"]["lab_coverage_percent"], 100)

    def test_evaluate_pipeline(self):
        out = ROOT / "reports" / "test-pipeline-smoke.json"
        proc = self._run(
            "evaluate-pipeline",
            "--profile",
            "ci-guardrails-eval",
            "--output",
            str(out),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_check_measure(self):
        out = ROOT / "reports" / "test-pipeline-smoke.json"
        if not out.exists():
            self.test_evaluate_pipeline()
        proc = self._run(
            "check-measure",
            "--profile",
            "ci-guardrails-eval",
            "--report",
            str(out),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
