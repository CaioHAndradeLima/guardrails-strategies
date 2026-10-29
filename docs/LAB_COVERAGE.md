# Guard-rails docs → reference implementation coverage

Maps each guide under [AI-System-Architecturing-Engineering/guard-rails](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/tree/main/guard-rails) to code and CLI output.

| Guide | Module / command | `evaluate-full` key |
| --- | --- | --- |
| [guardrails-strategy.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guardrails-strategy.md) | `policy_pipeline.py`, `strategies.py` | `guardrails_strategy`, `strategy_comparison` |
| [guard-rails-category.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-category.md) | `policy_categories.py` | `guard_rails_category` |
| [guardrails-cloud-architecture.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guardrails-cloud-architecture.md) | `cloud_architecture_checklist.py` | `guardrails_cloud_architecture` |
| [guard-rails-cloud-comparison.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-cloud-comparison.md) | `cloud_guardrail_map.py` | `guard_rails_cloud_comparison` |
| [ai-specific-controls-amazon-bedrock-guardrails.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/ai-specific-controls-amazon-bedrock-guardrails.md) | `cloud_adapters.py` (AWS slot) | `amazon_bedrock_guardrails` |
| [ai-specific-controls-google-model-armor.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/ai-specific-controls-google-model-armor.md) | `cloud_adapters.py` (GCP slot) | `google_model_armor` |
| [ai-specific-controls-azure-content-safety-prompt-shields.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/ai-specific-controls-azure-content-safety-prompt-shields.md) | `cloud_adapters.py` (Azure slot) | `azure_content_safety` |
| [wrong-architecture-shared-retrieval.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/wrong-architecture-shared-retrieval.md) | `shared_index_simulation.py` | `wrong_architecture_shared_retrieval`, `scenarios.shared_index_antipattern` |
| [safer-architecture-tenant-scoped-retrieval.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/safer-architecture-tenant-scoped-retrieval.md) | `tenant_scoped_retrieval.py` | `safer_architecture_tenant_scoped_retrieval` |
| [guardrails-data-isolation.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guardrails-data-isolation.md) | `data_isolation.py` | `guardrails_data_isolation` |
| [guardrails-aws-services.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guardrails-aws-services.md) | `aws_services_complement.py` | `guardrails_aws_services` |
| [guard-rails-test-use-cases.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-test-use-cases.md) | `scenario_evaluation.py`, `data/test_use_cases.json` | `guard_rails_test_use_cases`, `scenarios.test_use_cases` |
| [guard-rails-robust-cloud-rules-implementation.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-robust-cloud-rules-implementation.md) | `implementation_flow.py` | `guard_rails_robust_implementation`, `implementation_checklist` |
| [guard-rails-decision-architecturing-assistance.md](https://github.com/CaioHAndradeLima/AI-System-Architecturing-Engineering/blob/main/guard-rails/guard-rails-decision-architecturing-assistance.md) | `maturity.py` | `guard_rails_decision_assistance`, `maturity` |

**Coverage:** 14/14 guides — `evaluate-full` → `coverage.lab_coverage_percent` is **100** (regression syllabus; live Bedrock/Model Armor/Azure APIs, org IAM, and WAF deploy are listed under `maturity.production_deployment_only`).

Run everything:

```bash
python -m guardrails_strategies.cli evaluate-full --output reports/full.json
```

Recommended PR gate:

```bash
python -m guardrails_strategies.cli evaluate-pipeline --profile ci-guardrails-eval --output reports/pipeline-eval.json
python -m guardrails_strategies.cli check-measure --profile ci-guardrails-eval --report reports/pipeline-eval.json
```
