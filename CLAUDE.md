# ModelLedger — Claude Code Context

## What This Project Is

ModelLedger is an MLOps compliance dashboard that tracks model lineage and generates structured audit reports. It is fully local (no cloud, no database) and works with a single `pip install -e .` followed by `modelledger report --sample`.

This project belongs to Nirbhay Singh and is a core part of his $800K career strategy targeting AI Infra Architect / Staff+ MLOps roles. AI governance and model compliance are among the highest-paid MLOps competencies right now. Related projects in the portfolio:

- **tune-forge** — trains and fine-tunes the models whose records ModelLedger tracks
- **data-mint** — generates the synthetic test data that feeds those training runs
- **agent-loom** — the agent orchestration layer that consumes production models

## Project Layout

```
src/modelledger/
  __init__.py          # package version
  models.py            # Pydantic data models (ModelRecord, DatasetRecord, etc.)
  core.py              # Ledger, ReportGenerator, SampleDataGenerator
  cli.py               # Click CLI (report, inspect, init commands)
  templates/
    report.md.j2       # Jinja2 template for Markdown report output
examples/
  quickstart.py        # Python API usage example
  sample_data.json     # Sample JSON data file
tests/
  test_core.py         # 48 unit tests
  test_integration.py  # end-to-end CLI tests
docs/
  architecture.md      # Internal design notes
```

## Compliance Frameworks Supported

ModelLedger is designed to produce audit-ready records for:

| Framework | What ModelLedger addresses |
|---|---|
| **EU AI Act** | Training data provenance, model versioning, risk documentation |
| **NIST AI RMF** | Model inventory, experiment traceability, risk assessment flags |
| **SOC 2** | Immutable lineage records, hash-verified dataset integrity |

The compliance posture comes from the combination of: git commit tracking on every model, SHA-256 hashing on every dataset, and full experiment history linking models to their training runs.

## Data Model (JSON Schema)

Records are stored as JSON and loaded into Pydantic models. The top-level structure:

```json
{
  "models": [
    {
      "model_name": "my-model",
      "model_version": "1.0.0",
      "framework": "pytorch",
      "metrics": {"accuracy": 0.95, "f1": 0.93},
      "tags": ["production", "classification"],
      "git_commit": "abc123def456",
      "dataset_ref": "my-dataset",
      "description": "Optional human-readable description"
    }
  ],
  "datasets": [
    {
      "name": "my-dataset",
      "version": "1.0.0",
      "path": "/data/my-dataset/",
      "hash": "sha256:e3b0c44298fc...",
      "num_samples": 10000,
      "description": "Optional description"
    }
  ],
  "experiments": [
    {
      "experiment_id": "exp-001",
      "model_ref": "my-model",
      "dataset_ref": "my-dataset",
      "metrics": {"accuracy": 0.95},
      "params": {"learning_rate": 0.001, "epochs": 10},
      "status": "completed"
    }
  ]
}
```

The Pydantic models live in `src/modelledger/models.py`:
- `ModelRecord` — a trained model with version, metrics, git ref, and dataset reference
- `DatasetRecord` — a dataset with path, SHA-256 hash, and sample count
- `ExperimentRecord` — a training run linking a model to a dataset, with status (`pending | running | completed | failed`)
- `LineageEdge` — a directed edge `(from_id, relation, to_id)` in the lineage DAG
- `LineageGraph` — the full DAG of nodes and edges
- `ComplianceReport` — the final report model containing all of the above plus risk flags

## Key Commands

```bash
# Instant demo report — no data file needed
modelledger report --sample

# Generate report from your own data
modelledger report --data my_data.json

# HTML output, written to a file
modelledger report --data my_data.json --format html --output report.html

# Inspect data in rich terminal tables
modelledger inspect --data my_data.json

# Generate a starter data file to edit
modelledger init --output my_data.json
```

## Lineage Tracking Mechanism

The lineage graph is built inside `Ledger.get_lineage()` and `Ledger.build_graph()` in `core.py`:

1. Each `ModelRecord` carries a `dataset_ref` (foreign key to a dataset name) and optionally a `git_commit`.
2. Each `ExperimentRecord` carries both a `model_ref` and a `dataset_ref`.
3. When building the graph, the ledger walks all models, finds their referenced datasets and experiments, and creates `LineageEdge` objects with relation types: `trained_on`, `produced_by`, `evaluated_on`.
4. The result is a `LineageGraph` (DAG) where nodes are `model:name:version`, `dataset:name:version`, and `experiment:id`.
5. Risk flags are generated automatically: missing `dataset_ref`, missing `git_commit`, failed experiments, models never evaluated, experiments without metrics.

## Development Setup

```bash
pip install -e ".[dev]"
pytest                        # 48 tests
ruff check src/ tests/
mypy src/
```

## How to Add a New Compliance Framework

1. Open `src/modelledger/models.py`. The `ComplianceReport` model has a `risk_assessment: list[str]` field. Add any new framework-specific fields here if needed (e.g., `eu_ai_act_tier: str`).
2. Open `src/modelledger/core.py`. In `ReportGenerator._assess_risks()`, add new risk-check logic that inspects records and appends flags.
3. Open `src/modelledger/templates/report.md.j2`. Add a new section to the report template that renders the framework-specific data.
4. Add tests in `tests/test_core.py` covering the new risk flags.

No configuration file or plugin system is needed — the compliance logic is all in `_assess_risks()`.

## How to Add a New Report Output Format

Currently `report --format markdown` and `report --format html` are supported. To add a new format (e.g., PDF or JSON):

1. In `src/modelledger/core.py`, find `ReportGenerator.generate_report()`. It dispatches on a `format` string.
2. Add a new branch: `elif format == "pdf": return self._render_pdf()`.
3. Implement `_render_pdf()` using whichever library fits (e.g., `weasyprint` from the HTML render, or `reportlab`).
4. Add the new format choice to the `click.Choice(["markdown", "html", "pdf"])` list in `src/modelledger/cli.py`.
5. Add tests in `tests/test_integration.py`.

## Python API

```python
from modelledger.core import Ledger, ReportGenerator
from modelledger.models import ModelRecord, DatasetRecord, ExperimentRecord

ledger = Ledger()
ledger.add_model(ModelRecord(
    model_name="fraud-detector",
    model_version="2.1.0",
    framework="xgboost",
    git_commit="abc123",
    dataset_ref="fraud-training-v3",
    metrics={"auc": 0.97},
    tags=["production", "finance"],
))
ledger.add_dataset(DatasetRecord(
    name="fraud-training-v3",
    version="3.0.0",
    path="s3://my-bucket/fraud/v3/",
    hash="sha256:e3b0c44298fc...",
    num_samples=500000,
))
report = ReportGenerator(ledger).generate_report()
print(report)
```
