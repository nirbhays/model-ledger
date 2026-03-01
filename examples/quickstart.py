"""Quickstart example: using ModelLedger as a Python library.

This script demonstrates how to:
1. Create a Ledger and register models, datasets, and experiments
2. Build a lineage graph
3. Generate a compliance report programmatically
"""

from __future__ import annotations

from datetime import datetime

from modelledger.core import Ledger, ReportGenerator, SampleDataGenerator
from modelledger.models import (
    DatasetRecord,
    ExperimentRecord,
    ExperimentStatus,
    ModelRecord,
)


def main() -> None:
    # -----------------------------------------------------------------------
    # Option A: Use built-in sample data
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Option A: Generating a report from built-in sample data")
    print("=" * 70)

    ledger = Ledger()
    SampleDataGenerator().populate(ledger)

    generator = ReportGenerator(ledger)
    report = generator.generate_report(title="Sample Compliance Report")
    print(report[:500])
    print("... (truncated for brevity)\n")

    # -----------------------------------------------------------------------
    # Option B: Register your own records
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Option B: Registering custom records")
    print("=" * 70)

    ledger = Ledger()

    # Register a dataset
    ledger.add_dataset(
        DatasetRecord(
            name="fraud-transactions",
            version="1.0.0",
            path="/data/fraud/v1/",
            hash="abc123def456",
            num_samples=50_000,
            created_at=datetime(2025, 3, 1),
            description="Labeled fraud transaction dataset.",
        )
    )

    # Register a model
    ledger.add_model(
        ModelRecord(
            model_name="fraud-detector",
            model_version="1.0.0",
            framework="xgboost",
            created_at=datetime(2025, 3, 10),
            metrics={"auc_roc": 0.9823, "precision": 0.9512, "recall": 0.9301},
            tags=["production", "fraud", "finance"],
            git_commit="1a2b3c4d5e6f7890abcdef1234567890abcdef12",
            dataset_ref="fraud-transactions",
            description="XGBoost fraud detection model.",
        )
    )

    # Register an experiment
    ledger.add_experiment(
        ExperimentRecord(
            experiment_id="exp-fraud-001",
            model_ref="fraud-detector",
            dataset_ref="fraud-transactions",
            metrics={"auc_roc": 0.9823, "precision": 0.9512, "recall": 0.9301},
            params={"n_estimators": 300, "max_depth": 6, "learning_rate": 0.05},
            started_at=datetime(2025, 3, 10, 14, 0),
            completed_at=datetime(2025, 3, 10, 15, 30),
            status=ExperimentStatus.COMPLETED,
        )
    )

    # Inspect the data
    print(f"Models:      {len(ledger.models)}")
    print(f"Datasets:    {len(ledger.datasets)}")
    print(f"Experiments: {len(ledger.experiments)}")

    # Build lineage for a model
    lineage = ledger.get_lineage("fraud-detector")
    print(f"\nLineage for 'fraud-detector': {len(lineage.nodes)} nodes, {len(lineage.edges)} edges")
    for edge in lineage.edges:
        print(f"  {edge.from_id} --[{edge.relation}]--> {edge.to_id}")

    # Generate and print a compliance report
    generator = ReportGenerator(ledger)
    report = generator.generate_report(title="Fraud Detection Compliance Report")
    print("\n" + report)

    # -----------------------------------------------------------------------
    # Option C: Export to JSON and re-import
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Option C: JSON round-trip")
    print("=" * 70)

    json_str = ledger.export_json()
    print(f"Exported JSON ({len(json_str)} bytes)")

    # You could also write to a file:
    # ledger.export_json(path="my_data.json")
    # And later re-import:
    # new_ledger = Ledger()
    # new_ledger.import_json("my_data.json")


if __name__ == "__main__":
    main()
