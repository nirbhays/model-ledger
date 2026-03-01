"""Unit tests for ModelLedger core logic."""

from __future__ import annotations

from datetime import datetime

import pytest

from modelledger.core import Ledger, ReportGenerator, SampleDataGenerator
from modelledger.models import (
    DatasetRecord,
    ExperimentRecord,
    ExperimentStatus,
    ModelRecord,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_ledger() -> Ledger:
    """Return a fresh empty Ledger."""
    return Ledger()


@pytest.fixture
def sample_model() -> ModelRecord:
    """Return a sample ModelRecord."""
    return ModelRecord(
        model_name="test-model",
        model_version="1.0.0",
        framework="scikit-learn",
        created_at=datetime(2025, 1, 1),
        metrics={"accuracy": 0.95, "f1": 0.93},
        tags=["test", "classification"],
        git_commit="abc123def456",
        dataset_ref="test-dataset",
        description="A test model.",
    )


@pytest.fixture
def sample_dataset() -> DatasetRecord:
    """Return a sample DatasetRecord."""
    return DatasetRecord(
        name="test-dataset",
        version="1.0.0",
        path="/data/test-dataset/v1",
        hash="deadbeef12345678",
        num_samples=1000,
        created_at=datetime(2025, 1, 1),
        description="A test dataset.",
    )


@pytest.fixture
def sample_experiment() -> ExperimentRecord:
    """Return a sample ExperimentRecord."""
    return ExperimentRecord(
        experiment_id="exp-test-001",
        model_ref="test-model",
        dataset_ref="test-dataset",
        metrics={"accuracy": 0.95},
        params={"n_estimators": 100, "max_depth": 5},
        started_at=datetime(2025, 1, 2, 10, 0),
        completed_at=datetime(2025, 1, 2, 11, 0),
        status=ExperimentStatus.COMPLETED,
    )


@pytest.fixture
def populated_ledger(
    empty_ledger: Ledger,
    sample_model: ModelRecord,
    sample_dataset: DatasetRecord,
    sample_experiment: ExperimentRecord,
) -> Ledger:
    """Return a ledger with one model, one dataset, one experiment."""
    empty_ledger.add_model(sample_model)
    empty_ledger.add_dataset(sample_dataset)
    empty_ledger.add_experiment(sample_experiment)
    return empty_ledger


# ---------------------------------------------------------------------------
# Ledger add / get tests
# ---------------------------------------------------------------------------

class TestLedgerAddGet:
    """Tests for Ledger add and get operations."""

    def test_add_model(self, empty_ledger: Ledger, sample_model: ModelRecord) -> None:
        empty_ledger.add_model(sample_model)
        assert len(empty_ledger.models) == 1
        assert empty_ledger.models[0].model_name == "test-model"

    def test_add_dataset(self, empty_ledger: Ledger, sample_dataset: DatasetRecord) -> None:
        empty_ledger.add_dataset(sample_dataset)
        assert len(empty_ledger.datasets) == 1
        assert empty_ledger.datasets[0].name == "test-dataset"

    def test_add_experiment(
        self, empty_ledger: Ledger, sample_experiment: ExperimentRecord
    ) -> None:
        empty_ledger.add_experiment(sample_experiment)
        assert len(empty_ledger.experiments) == 1
        assert empty_ledger.experiments[0].experiment_id == "exp-test-001"

    def test_get_model_by_name(self, populated_ledger: Ledger) -> None:
        model = populated_ledger.get_model("test-model")
        assert model is not None
        assert model.model_name == "test-model"

    def test_get_model_by_name_and_version(self, populated_ledger: Ledger) -> None:
        model = populated_ledger.get_model("test-model", version="1.0.0")
        assert model is not None
        assert model.model_version == "1.0.0"

    def test_get_model_not_found(self, populated_ledger: Ledger) -> None:
        model = populated_ledger.get_model("nonexistent")
        assert model is None

    def test_get_dataset_by_name(self, populated_ledger: Ledger) -> None:
        dataset = populated_ledger.get_dataset("test-dataset")
        assert dataset is not None
        assert dataset.name == "test-dataset"

    def test_get_dataset_not_found(self, populated_ledger: Ledger) -> None:
        dataset = populated_ledger.get_dataset("nonexistent")
        assert dataset is None

    def test_models_returns_copy(self, populated_ledger: Ledger) -> None:
        """Ensure the models property returns a copy, not the internal list."""
        models = populated_ledger.models
        models.clear()
        assert len(populated_ledger.models) == 1


# ---------------------------------------------------------------------------
# Lineage graph tests
# ---------------------------------------------------------------------------

class TestLineageGraph:
    """Tests for lineage graph building."""

    def test_build_graph_nodes(self, populated_ledger: Ledger) -> None:
        graph = populated_ledger.build_graph()
        assert len(graph.nodes) == 3  # 1 model + 1 dataset + 1 experiment

    def test_build_graph_edges(self, populated_ledger: Ledger) -> None:
        graph = populated_ledger.build_graph()
        assert len(graph.edges) >= 2  # dataset->model (trained_on), model->exp (evaluated_in)

    def test_build_graph_edge_relations(self, populated_ledger: Ledger) -> None:
        graph = populated_ledger.build_graph()
        relations = {e.relation for e in graph.edges}
        assert "trained_on" in relations
        assert "evaluated_in" in relations

    def test_get_lineage_for_model(self, populated_ledger: Ledger) -> None:
        graph = populated_ledger.get_lineage("test-model")
        node_types = {type(n).__name__ for n in graph.nodes}
        assert "ModelRecord" in node_types
        assert "DatasetRecord" in node_types
        assert "ExperimentRecord" in node_types

    def test_get_lineage_empty_for_unknown_model(self, populated_ledger: Ledger) -> None:
        graph = populated_ledger.get_lineage("nonexistent")
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_empty_ledger_graph(self, empty_ledger: Ledger) -> None:
        graph = empty_ledger.build_graph()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


# ---------------------------------------------------------------------------
# SampleDataGenerator tests
# ---------------------------------------------------------------------------

class TestSampleDataGenerator:
    """Tests for the SampleDataGenerator."""

    def test_populate_creates_models(self, empty_ledger: Ledger) -> None:
        SampleDataGenerator().populate(empty_ledger)
        assert len(empty_ledger.models) == 3

    def test_populate_creates_datasets(self, empty_ledger: Ledger) -> None:
        SampleDataGenerator().populate(empty_ledger)
        assert len(empty_ledger.datasets) == 2

    def test_populate_creates_experiments(self, empty_ledger: Ledger) -> None:
        SampleDataGenerator().populate(empty_ledger)
        assert len(empty_ledger.experiments) == 5

    def test_sample_models_are_valid(self, empty_ledger: Ledger) -> None:
        SampleDataGenerator().populate(empty_ledger)
        for model in empty_ledger.models:
            assert model.model_name
            assert model.model_version
            assert model.framework

    def test_sample_datasets_are_valid(self, empty_ledger: Ledger) -> None:
        SampleDataGenerator().populate(empty_ledger)
        for dataset in empty_ledger.datasets:
            assert dataset.name
            assert dataset.version
            assert dataset.path
            assert dataset.hash
            assert dataset.num_samples > 0

    def test_sample_experiments_are_valid(self, empty_ledger: Ledger) -> None:
        SampleDataGenerator().populate(empty_ledger)
        for exp in empty_ledger.experiments:
            assert exp.experiment_id
            assert exp.model_ref
            assert exp.dataset_ref

    def test_sample_data_has_risk_flags(self, empty_ledger: Ledger) -> None:
        """The sample data should include records that trigger risk assessment flags."""
        SampleDataGenerator().populate(empty_ledger)
        # At least one model should lack a git_commit
        models_without_commit = [m for m in empty_ledger.models if m.git_commit is None]
        assert len(models_without_commit) >= 1

        # At least one experiment should have empty metrics
        exps_without_metrics = [e for e in empty_ledger.experiments if not e.metrics]
        assert len(exps_without_metrics) >= 1


# ---------------------------------------------------------------------------
# ReportGenerator tests
# ---------------------------------------------------------------------------

class TestReportGenerator:
    """Tests for the ReportGenerator."""

    def test_generate_markdown_report(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report(format="markdown")
        assert isinstance(report, str)
        assert len(report) > 100

    def test_report_contains_title(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report(title="Test Report")
        assert "Test Report" in report

    def test_report_contains_model_info(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report()
        assert "test-model" in report
        assert "scikit-learn" in report

    def test_report_contains_dataset_info(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report()
        assert "test-dataset" in report

    def test_report_contains_experiment_info(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report()
        assert "exp-test-001" in report

    def test_report_contains_lineage_summary(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report()
        assert "Lineage" in report
        assert "nodes" in report

    def test_report_contains_risk_assessment(self) -> None:
        """A ledger with sample data should produce risk flags."""
        ledger = Ledger()
        SampleDataGenerator().populate(ledger)
        generator = ReportGenerator(ledger)
        report = generator.generate_report()
        assert "Risk Assessment" in report
        # Sample data has a model without git_commit
        assert "git commit" in report.lower() or "provenance" in report.lower()

    def test_html_format(self, populated_ledger: Ledger) -> None:
        generator = ReportGenerator(populated_ledger)
        report = generator.generate_report(format="html")
        assert "<html" in report
        assert "</html>" in report

    def test_empty_ledger_report(self, empty_ledger: Ledger) -> None:
        generator = ReportGenerator(empty_ledger)
        report = generator.generate_report()
        assert "No models registered" in report or "Model Inventory" in report


# ---------------------------------------------------------------------------
# JSON import/export round-trip
# ---------------------------------------------------------------------------

class TestJsonRoundTrip:
    """Tests for JSON import and export."""

    def test_export_and_import(self, populated_ledger: Ledger, tmp_path) -> None:
        export_path = tmp_path / "export.json"
        populated_ledger.export_json(path=export_path)

        new_ledger = Ledger()
        new_ledger.import_json(export_path)

        assert len(new_ledger.models) == len(populated_ledger.models)
        assert len(new_ledger.datasets) == len(populated_ledger.datasets)
        assert len(new_ledger.experiments) == len(populated_ledger.experiments)
        assert new_ledger.models[0].model_name == populated_ledger.models[0].model_name
