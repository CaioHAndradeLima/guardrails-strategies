import unittest
from pathlib import Path

from guardrails_strategies.full_evaluation import run_full_evaluation

ROOT = Path(__file__).resolve().parents[1]


class TestFullEvaluation(unittest.TestCase):
    def test_coverage_100(self):
        report = run_full_evaluation(ROOT)
        self.assertEqual(report["coverage"]["lab_coverage_percent"], 100)
        self.assertEqual(report["coverage"]["guard_rails_guides"], "14/14")

    def test_all_guide_keys_present(self):
        report = run_full_evaluation(ROOT)
        keys = [
            "guardrails_strategy",
            "guard_rails_category",
            "guardrails_cloud_architecture",
            "guard_rails_cloud_comparison",
            "amazon_bedrock_guardrails",
            "google_model_armor",
            "azure_content_safety",
            "wrong_architecture_shared_retrieval",
            "safer_architecture_tenant_scoped_retrieval",
            "guardrails_data_isolation",
            "guardrails_aws_services",
            "guard_rails_test_use_cases",
            "guard_rails_robust_implementation",
            "guard_rails_decision_assistance",
        ]
        for key in keys:
            self.assertIn(key, report)


if __name__ == "__main__":
    unittest.main()
