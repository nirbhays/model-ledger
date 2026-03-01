"""Core logic for ModelLedger: Ledger, ReportGenerator, and SampleDataGenerator."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import structlog
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from modelledger import __version__
from modelledger.models import (
    ComplianceReport,
    DatasetRecord,
    ExperimentRecord,
    ExperimentStatus,
    LineageEdge,
    LineageGraph,
    ModelRecord,
)

logger = structlog.get_logger(__name__)


class Ledger:
    """In-memory store for ML compliance records.

    Provides methods to add, retrieve, and query ModelRecord, DatasetRecord,
    and ExperimentRecord instances. Supports import from JSON files.
    """

    def __init__(self) -> None:
        self._models: list[ModelRecord] = []
        self._datasets: list[DatasetRecord] = []
        self._experiments: list[ExperimentRecord] = []

    @property
    def models(self) -> list[ModelRecord]:
        """Return all registered models."""
        return list(self._models)

    @property
    def datasets(self) -> list[DatasetRecord]:
        """Return all registered datasets."""
        return list(self._datasets)

    @property
    def experiments(self) -> list[ExperimentRecord]:
        """Return all registered experiments."""
        return list(self._experiments)

    def add_model(self, record: ModelRecord) -> None:
        """Register a model record."""
        logger.info("model_added", model_name=record.model_name, version=record.model_version)
        self._models.append(record)

    def add_dataset(self, record: DatasetRecord) -> None:
        """Register a dataset record."""
        logger.info("dataset_added", name=record.name, version=record.version)
        self._datasets.append(record)

    def add_experiment(self, record: ExperimentRecord) -> None:
        """Register an experiment record."""
        logger.info("experiment_added", experiment_id=record.experiment_id, status=record.status)
        self._experiments.append(record)

    def get_model(self, model_name: str, version: str | None = None) -> ModelRecord | None:
        """Look up a model by name and optionally version. Returns the latest if no version."""
        matches = [m for m in self._models if m.model_name == model_name]
        if version:
            matches = [m for m in matches if m.model_version == version]
        if not matches:
            return None
        return sorted(matches, key=lambda m: m.created_at, reverse=True)[0]

    def get_dataset(self, name: str, version: str | None = None) -> DatasetRecord | None:
        """Look up a dataset by name and optionally version."""
        matches = [d for d in self._datasets if d.name == name]
        if version:
            matches = [d for d in matches if d.version == version]
        if not matches:
            return None
        return sorted(matches, key=lambda d: d.created_at, reverse=True)[0]

    def get_lineage(self, model_name: str) -> LineageGraph:
        """Build a lineage graph for a specific model, tracing its data and experiment history."""
        graph = LineageGraph()
        nodes_seen: set[str] = set()
        edges: list[LineageEdge] = []

        target_models = [m for m in self._models if m.model_name == model_name]
        for model in target_models:
            if model.node_id not in nodes_seen:
                graph.nodes.append(model)
                nodes_seen.add(model.node_id)

            if model.dataset_ref:
                dataset = self.get_dataset(model.dataset_ref)
                if dataset and dataset.node_id not in nodes_seen:
                    graph.nodes.append(dataset)
                    nodes_seen.add(dataset.node_id)
                if dataset:
                    edges.append(
                        LineageEdge(
                            from_id=dataset.node_id,
                            to_id=model.node_id,
                            relation="trained_on",
                        )
                    )

            related_experiments = [
                e for e in self._experiments if e.model_ref == model.model_name
            ]
            for exp in related_experiments:
                if exp.node_id not in nodes_seen:
                    graph.nodes.append(exp)
                    nodes_seen.add(exp.node_id)
                edges.append(
                    LineageEdge(
                        from_id=model.node_id,
                        to_id=exp.node_id,
                        relation="evaluated_in",
                    )
                )

                if exp.dataset_ref:
                    exp_dataset = self.get_dataset(exp.dataset_ref)
                    if exp_dataset and exp_dataset.node_id not in nodes_seen:
                        graph.nodes.append(exp_dataset)
                        nodes_seen.add(exp_dataset.node_id)
                    if exp_dataset:
                        edges.append(
                            LineageEdge(
                                from_id=exp_dataset.node_id,
                                to_id=exp.node_id,
                                relation="used_in",
                            )
                        )

        graph.edges = edges
        return graph

    def build_graph(self) -> LineageGraph:
        """Build a complete lineage graph covering all registered records."""
        graph = LineageGraph()
        edges: list[LineageEdge] = []

        for model in self._models:
            graph.nodes.append(model)
        for dataset in self._datasets:
            graph.nodes.append(dataset)
        for exp in self._experiments:
            graph.nodes.append(exp)

        for model in self._models:
            if model.dataset_ref:
                dataset = self.get_dataset(model.dataset_ref)
                if dataset:
                    edges.append(
                        LineageEdge(
                            from_id=dataset.node_id,
                            to_id=model.node_id,
                            relation="trained_on",
                        )
                    )

        for exp in self._experiments:
            model = self.get_model(exp.model_ref)
            if model:
                edges.append(
                    LineageEdge(
                        from_id=model.node_id,
                        to_id=exp.node_id,
                        relation="evaluated_in",
                    )
                )
            if exp.dataset_ref:
                dataset = self.get_dataset(exp.dataset_ref)
                if dataset:
                    edges.append(
                        LineageEdge(
                            from_id=dataset.node_id,
                            to_id=exp.node_id,
                            relation="used_in",
                        )
                    )

        graph.edges = edges
        return graph

    def import_json(self, path: str | Path) -> None:
        """Import records from a JSON file.

        Expected format:
        {
            "models": [...],
            "datasets": [...],
            "experiments": [...]
        }
        """
        path = Path(path)
        logger.info("importing_json", path=str(path))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for model_data in data.get("models", []):
            self.add_model(ModelRecord(**model_data))
        for dataset_data in data.get("datasets", []):
            self.add_dataset(DatasetRecord(**dataset_data))
        for exp_data in data.get("experiments", []):
            self.add_experiment(ExperimentRecord(**exp_data))

        logger.info(
            "import_complete",
            models=len(self._models),
            datasets=len(self._datasets),
            experiments=len(self._experiments),
        )

    def export_json(self, path: str | Path | None = None) -> str:
        """Export all records to JSON. If path is given, writes to file and returns the JSON."""
        data = {
            "models": [m.model_dump(mode="json") for m in self._models],
            "datasets": [d.model_dump(mode="json") for d in self._datasets],
            "experiments": [e.model_dump(mode="json") for e in self._experiments],
        }
        json_str = json.dumps(data, indent=2, default=str)
        if path:
            path = Path(path)
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info("exported_json", path=str(path))
        return json_str


class ReportGenerator:
    """Generates compliance reports from a Ledger.

    Uses Jinja2 templates to render reports in Markdown or HTML format.
    """

    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger
        templates_dir = Path(__file__).parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _assess_risks(self) -> list[str]:
        """Identify compliance risks in the current ledger data."""
        risks: list[str] = []

        # Flag models without dataset references
        for model in self.ledger.models:
            if not model.dataset_ref:
                risks.append(
                    f"Model '{model.model_name}' v{model.model_version} has no dataset reference "
                    f"-- training data provenance is unknown."
                )

        # Flag models without git commits
        for model in self.ledger.models:
            if not model.git_commit:
                risks.append(
                    f"Model '{model.model_name}' v{model.model_version} has no git commit "
                    f"-- code provenance cannot be verified."
                )

        # Flag experiments without metrics
        for exp in self.ledger.experiments:
            if not exp.metrics:
                risks.append(
                    f"Experiment '{exp.experiment_id}' has no metrics recorded "
                    f"-- evaluation results are missing."
                )

        # Flag failed experiments
        for exp in self.ledger.experiments:
            if exp.status == ExperimentStatus.FAILED:
                risks.append(
                    f"Experiment '{exp.experiment_id}' has status FAILED "
                    f"-- investigate failure cause."
                )

        # Flag models without any experiments
        model_names_with_experiments = {e.model_ref for e in self.ledger.experiments}
        for model in self.ledger.models:
            if model.model_name not in model_names_with_experiments:
                risks.append(
                    f"Model '{model.model_name}' v{model.model_version} has no associated "
                    f"experiments -- model has not been evaluated."
                )

        return risks

    def _build_lineage_summary(self) -> str:
        """Build a human-readable lineage summary."""
        graph = self.ledger.build_graph()
        if not graph.nodes:
            return "No lineage information available."

        lines: list[str] = []
        lines.append(
            f"The lineage graph contains **{len(graph.nodes)} nodes** "
            f"and **{len(graph.edges)} edges**."
        )
        lines.append("")

        model_count = sum(1 for n in graph.nodes if isinstance(n, ModelRecord))
        dataset_count = sum(1 for n in graph.nodes if isinstance(n, DatasetRecord))
        experiment_count = sum(1 for n in graph.nodes if isinstance(n, ExperimentRecord))

        lines.append(f"- Models: {model_count}")
        lines.append(f"- Datasets: {dataset_count}")
        lines.append(f"- Experiments: {experiment_count}")
        lines.append("")

        if graph.edges:
            lines.append("Key relationships:")
            for edge in graph.edges:
                lines.append(f"- `{edge.from_id}` --[{edge.relation}]--> `{edge.to_id}`")

        return "\n".join(lines)

    def generate_report(
        self,
        format: str = "markdown",
        title: str = "ModelLedger Compliance Report",
    ) -> str:
        """Generate a compliance report.

        Args:
            format: Output format, either 'markdown' or 'html'.
            title: Report title.

        Returns:
            Rendered report as a string.
        """
        risks = self._assess_risks()
        lineage_summary = self._build_lineage_summary()

        report = ComplianceReport(
            title=title,
            model_records=self.ledger.models,
            dataset_records=self.ledger.datasets,
            experiments=self.ledger.experiments,
            lineage_summary=lineage_summary,
            risk_assessment=risks,
        )

        template = self._env.get_template("report.md.j2")
        rendered = template.render(
            title=report.title,
            generated_at=report.generated_at,
            model_records=report.model_records,
            dataset_records=report.dataset_records,
            experiments=report.experiments,
            lineage_summary=report.lineage_summary,
            risk_assessment=report.risk_assessment,
            version=__version__,
        )

        if format == "html":
            rendered = self._markdown_to_html(rendered)

        return rendered

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to a basic HTML document.

        This is a lightweight conversion that wraps the markdown in HTML tags.
        For production use, consider integrating a full markdown-to-HTML library.
        """
        html_lines: list[str] = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "  <title>ModelLedger Compliance Report</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', "
            "Roboto, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; "
            "line-height: 1.6; color: #333; }",
            "    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }",
            "    th, td { border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }",
            "    th { background: #f5f5f5; font-weight: 600; }",
            "    tr:nth-child(even) { background: #fafafa; }",
            "    code { background: #f0f0f0; padding: 0.15rem 0.35rem; border-radius: 3px; "
            "font-size: 0.9em; }",
            "    h1 { border-bottom: 2px solid #333; padding-bottom: 0.5rem; }",
            "    h2 { border-bottom: 1px solid #ccc; padding-bottom: 0.3rem; margin-top: 2rem; }",
            "    hr { border: none; border-top: 1px solid #eee; margin: 2rem 0; }",
            "  </style>",
            "</head>",
            "<body>",
            f"<pre>{_escape_html(markdown_text)}</pre>",
            "</body>",
            "</html>",
        ]
        return "\n".join(html_lines)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class SampleDataGenerator:
    """Generates realistic sample data for demos and testing."""

    def __init__(self) -> None:
        self._base_time = datetime(2025, 1, 15, 10, 0, 0)

    def populate(self, ledger: Ledger) -> Ledger:
        """Populate a ledger with realistic sample data.

        Creates 3 models, 2 datasets, and 5 experiments with realistic
        metrics and parameters.
        """
        self._add_datasets(ledger)
        self._add_models(ledger)
        self._add_experiments(ledger)
        return ledger

    def _add_datasets(self, ledger: Ledger) -> None:
        """Add sample datasets."""
        ledger.add_dataset(
            DatasetRecord(
                name="customer-churn-v2",
                version="2.1.0",
                path="s3://ml-data/customer-churn/v2.1/",
                hash="a3f2b8c91d4e5f6071829384756abcde",
                num_samples=45_230,
                created_at=self._base_time - timedelta(days=30),
                description="Customer churn prediction dataset with behavioral features.",
            )
        )
        ledger.add_dataset(
            DatasetRecord(
                name="product-reviews-nlp",
                version="1.3.0",
                path="s3://ml-data/product-reviews/v1.3/",
                hash="b7e4d2f189ca3b56e0712938475d6ecf",
                num_samples=128_500,
                created_at=self._base_time - timedelta(days=15),
                description="Product review sentiment analysis corpus, preprocessed and labeled.",
            )
        )

    def _add_models(self, ledger: Ledger) -> None:
        """Add sample models."""
        ledger.add_model(
            ModelRecord(
                model_name="churn-predictor",
                model_version="1.0.0",
                framework="scikit-learn",
                created_at=self._base_time,
                metrics={"accuracy": 0.8734, "precision": 0.8521, "recall": 0.8912, "f1": 0.8712},
                tags=["production", "classification", "customer-analytics"],
                git_commit="a1b2c3d4e5f6789012345678abcdef01fedcba98",
                dataset_ref="customer-churn-v2",
                description="Gradient-boosted tree model for customer churn prediction.",
            )
        )
        ledger.add_model(
            ModelRecord(
                model_name="sentiment-analyzer",
                model_version="2.1.0",
                framework="pytorch",
                created_at=self._base_time + timedelta(days=5),
                metrics={"accuracy": 0.9215, "f1_macro": 0.9102, "auc_roc": 0.9567},
                tags=["nlp", "sentiment", "transformer"],
                git_commit="f9e8d7c6b5a4321098765432fedcba0123456789",
                dataset_ref="product-reviews-nlp",
                description="Fine-tuned DistilBERT model for product review sentiment.",
            )
        )
        ledger.add_model(
            ModelRecord(
                model_name="demand-forecaster",
                model_version="0.3.0",
                framework="tensorflow",
                created_at=self._base_time + timedelta(days=10),
                metrics={"mae": 12.45, "rmse": 18.92, "mape": 0.0834},
                tags=["forecasting", "time-series", "staging"],
                git_commit=None,  # Intentionally missing for risk assessment demo
                dataset_ref=None,  # Intentionally missing for risk assessment demo
                description="LSTM-based demand forecasting model (experimental).",
            )
        )

    def _add_experiments(self, ledger: Ledger) -> None:
        """Add sample experiments."""
        ledger.add_experiment(
            ExperimentRecord(
                experiment_id="exp-churn-baseline-001",
                model_ref="churn-predictor",
                dataset_ref="customer-churn-v2",
                metrics={"accuracy": 0.8734, "precision": 0.8521, "recall": 0.8912, "f1": 0.8712},
                params={
                    "n_estimators": 200,
                    "max_depth": 8,
                    "learning_rate": 0.05,
                    "subsample": 0.8,
                },
                started_at=self._base_time + timedelta(hours=1),
                completed_at=self._base_time + timedelta(hours=1, minutes=45),
                status=ExperimentStatus.COMPLETED,
            )
        )
        ledger.add_experiment(
            ExperimentRecord(
                experiment_id="exp-churn-tuned-002",
                model_ref="churn-predictor",
                dataset_ref="customer-churn-v2",
                metrics={"accuracy": 0.8891, "precision": 0.8702, "recall": 0.8998, "f1": 0.8847},
                params={
                    "n_estimators": 500,
                    "max_depth": 10,
                    "learning_rate": 0.02,
                    "subsample": 0.9,
                    "min_child_weight": 3,
                },
                started_at=self._base_time + timedelta(days=2),
                completed_at=self._base_time + timedelta(days=2, hours=3),
                status=ExperimentStatus.COMPLETED,
            )
        )
        ledger.add_experiment(
            ExperimentRecord(
                experiment_id="exp-sentiment-finetune-003",
                model_ref="sentiment-analyzer",
                dataset_ref="product-reviews-nlp",
                metrics={
                    "accuracy": 0.9215,
                    "f1_macro": 0.9102,
                    "auc_roc": 0.9567,
                    "loss": 0.2134,
                },
                params={
                    "epochs": 5,
                    "batch_size": 32,
                    "learning_rate": 2e-5,
                    "warmup_steps": 500,
                    "weight_decay": 0.01,
                },
                started_at=self._base_time + timedelta(days=5, hours=2),
                completed_at=self._base_time + timedelta(days=5, hours=8),
                status=ExperimentStatus.COMPLETED,
            )
        )
        ledger.add_experiment(
            ExperimentRecord(
                experiment_id="exp-demand-lstm-004",
                model_ref="demand-forecaster",
                dataset_ref="customer-churn-v2",
                metrics={},  # Intentionally empty for risk assessment demo
                params={
                    "hidden_size": 128,
                    "num_layers": 2,
                    "dropout": 0.3,
                    "sequence_length": 30,
                },
                started_at=self._base_time + timedelta(days=10, hours=1),
                completed_at=self._base_time + timedelta(days=10, hours=6),
                status=ExperimentStatus.COMPLETED,
            )
        )
        ledger.add_experiment(
            ExperimentRecord(
                experiment_id="exp-demand-failed-005",
                model_ref="demand-forecaster",
                dataset_ref="customer-churn-v2",
                metrics={},
                params={"hidden_size": 512, "num_layers": 4, "dropout": 0.1},
                started_at=self._base_time + timedelta(days=11),
                completed_at=None,
                status=ExperimentStatus.FAILED,
            )
        )
