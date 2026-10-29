# Guard-rails pipeline evaluation (`evaluate-pipeline`)

`evaluate-pipeline --profile ci-guardrails-eval` produces a **three-layer scorecard** on bundled fixtures:

1. **Core policy** (`scorecard.core_quality`) — attack block rate, false deny/allow, classification accuracy, policy latency.
2. **Scenarios** (`scenarios`) — all rows from [guard-rails-test-use-cases.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-test-use-cases.md), tenant-scoped vs shared retrieval, shared-index anti-pattern metrics.
3. **Optional live cloud AI safety** — documented in `cloud_adapters.py`; CI uses offline stubs unless `AWS_BEDROCK_GUARDRAIL_ID`, `GCP_MODEL_ARMOR_TEMPLATE`, or `AZURE_CONTENT_SAFETY_ENDPOINT` is set.

## Scorecard fields

| Field | Meaning |
| --- | --- |
| `attack_block_rate` | Adversarial / cross-tenant cases correctly denied |
| `false_deny_rate` | Legitimate requests incorrectly denied |
| `false_allow_rate` | Attacks incorrectly allowed |
| `classification_accuracy` | `expected_allow` matches policy decision |
| `policy_ms_p95` | End-to-end policy evaluation latency |

## Scenario gates (`ci-guardrails-eval`)

| Gate | Source |
| --- | --- |
| `min_test_use_case_pass_rate` | `scenarios.test_use_cases.summary.pass_rate` |
| `min_tenant_scoped_match_rate` | `scenarios.tenant_scoped_vs_shared.tenant_scoped_match_rate` |
| `max_shared_index_false_allow_rate` | `scenarios.shared_index_antipattern.false_allow_rate_shared_index` (anti-pattern baseline; should stay high to prove risk) |

Thresholds live in [config/measure_profiles.json](../config/measure_profiles.json).

## Related docs

- [guard-rails-test-use-cases.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-test-use-cases.md)
- [LAB_COVERAGE.md](./LAB_COVERAGE.md)
