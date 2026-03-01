# ModelLedger

**MLOps compliance dashboard -- model lineage tracking and audit report generation in one command.**

[![CI](https://github.com/YOUR_ORG/modelledger/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/modelledger/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/modelledger.svg)](https://pypi.org/project/modelledger/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Tests](https://img.shields.io/badge/tests-48%20passing-brightgreen)
![No External Services](https://img.shields.io/badge/runs-100%25%20local-orange)

> `modelledger report --sample` -- instant compliance report. No database, no cloud, no setup.

---

## The Problem

AI regulations (EU AI Act, NIST AI RMF) require auditable records of:
- What data trained each model
- Which code version produced it
- How it was evaluated
- What risks were identified

Most teams track this in spreadsheets, wikis, or not at all.

## The Fix

ModelLedger generates structured compliance reports from simple JSON data:

```bash
modelledger report --sample
```

Output: a complete Markdown report with model inventory, dataset provenance, experiment history, lineage graph, and automated risk assessment.

## Quickstart

```bash
pip install -e .

# Instant demo -- no files needed
modelledger report --sample

# Create your own data file
modelledger init --output my_data.json
# Edit my_data.json with your models/datasets/experiments
modelledger report --data my_data.json
```

## Why ModelLedger?

| Approach | Setup | Cost | Offline | Audit-Ready |
|----------|-------|------|:-------:|:-----------:|
| MLflow | Server + DB | Free/Paid | No | Partial |
| Weights & Biases | Cloud account | $$ | No | Partial |
| DVC | Git-based | Free | Yes | No |
| **ModelLedger** | **`pip install`** | **Free** | **Yes** | **Yes** |

## CLI Reference

### `modelledger report`

```bash
modelledger report --sample                    # Built-in sample data
modelledger report --data my_data.json         # Your data
modelledger report --data d.json --format html # HTML output
modelledger report --data d.json --output r.md # Write to file
```

| Flag | Description |
|------|-------------|
| `--sample` | Generate report from built-in sample data |
| `--data PATH` | Path to JSON data file |
| `--format` | `markdown` (default) or `html` |
| `--output FILE` | Write to file instead of stdout |
| `--title TEXT` | Custom report title |

### `modelledger inspect`

```bash
modelledger inspect --data my_data.json
```

Rich terminal tables showing all models, datasets, and experiments.

### `modelledger init`

```bash
modelledger init --output my_data.json
```

Generate a sample JSON data file as a starting point.

## Report Contents

A generated report includes:

1. **Model Inventory** -- all registered models with version, framework, metrics, tags
2. **Dataset Registry** -- datasets with provenance (path, hash, sample count)
3. **Experiment History** -- runs with hyperparameters, metrics, and status
4. **Lineage Graph** -- relationships between models, datasets, and experiments
5. **Risk Assessment** -- automatic flags for:
   - Models missing dataset references (unknown training data)
   - Models missing git commits (unverifiable code)
   - Experiments without metrics (unevaluated models)
   - Failed experiments (investigate cause)
   - Models with no experiments (never evaluated)

## Data Format

```json
{
  "models": [{
    "model_name": "my-model",
    "model_version": "1.0.0",
    "framework": "pytorch",
    "metrics": {"accuracy": 0.95},
    "tags": ["production"],
    "git_commit": "abc123",
    "dataset_ref": "my-dataset"
  }],
  "datasets": [{
    "name": "my-dataset",
    "version": "1.0.0",
    "path": "/data/my-dataset/",
    "hash": "sha256...",
    "num_samples": 10000
  }],
  "experiments": [{
    "experiment_id": "exp-001",
    "model_ref": "my-model",
    "dataset_ref": "my-dataset",
    "metrics": {"accuracy": 0.95},
    "params": {"learning_rate": 0.001},
    "status": "completed"
  }]
}
```

## Library API

```python
from modelledger.core import Ledger, ReportGenerator
from modelledger.models import ModelRecord, DatasetRecord

ledger = Ledger()
ledger.add_model(ModelRecord(
    model_name="my-model",
    model_version="1.0.0",
    framework="pytorch",
    dataset_ref="my-dataset",
))

generator = ReportGenerator(ledger)
report = generator.generate_report()
print(report)
```

## Use Cases

### EU AI Act Compliance
Maintain auditable records of training data, model performance, and decision-making processes as required by emerging AI regulations.

### Model Auditing
Trace any model back to its training data, code version, and evaluation experiments through the lineage graph.

### Team Onboarding
New team members run `modelledger inspect --data project_data.json` for an instant overview of all models, datasets, and experiments.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/ tests/
mypy src/
```

## License

MIT. See [LICENSE](LICENSE).
