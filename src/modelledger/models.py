"""Pydantic models for ModelLedger compliance tracking."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel, Field


class ModelRecord(BaseModel):
    """A registered ML model with metadata for compliance tracking."""

    model_name: str = Field(..., description="Unique name of the model")
    model_version: str = Field(..., description="Semantic version string")
    framework: str = Field(..., description="ML framework used (e.g. pytorch, sklearn)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metrics: dict[str, float] = Field(default_factory=dict, description="Evaluation metrics")
    tags: list[str] = Field(default_factory=list, description="Freeform tags for categorization")
    git_commit: str | None = Field(default=None, description="Git commit SHA of training code")
    dataset_ref: str | None = Field(
        default=None, description="Reference to the dataset used for training"
    )
    description: str = Field(default="", description="Human-readable description of the model")

    @property
    def node_id(self) -> str:
        """Return a unique identifier for graph purposes."""
        return f"model:{self.model_name}:{self.model_version}"


class DatasetRecord(BaseModel):
    """A registered dataset with provenance information."""

    name: str = Field(..., description="Unique name of the dataset")
    version: str = Field(..., description="Dataset version string")
    path: str = Field(..., description="Storage path or URI")
    hash: str = Field(..., description="Content hash for integrity verification")
    num_samples: int = Field(..., ge=0, description="Number of samples in the dataset")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    description: str = Field(default="", description="Human-readable description")

    @property
    def node_id(self) -> str:
        """Return a unique identifier for graph purposes."""
        return f"dataset:{self.name}:{self.version}"


class ExperimentStatus(str, Enum):
    """Status of an experiment run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExperimentRecord(BaseModel):
    """A tracked experiment run linking a model to a dataset."""

    experiment_id: str = Field(..., description="Unique experiment identifier")
    model_ref: str = Field(..., description="Reference to the model used")
    dataset_ref: str = Field(..., description="Reference to the dataset used")
    metrics: dict[str, float] = Field(
        default_factory=dict, description="Metrics produced by the experiment"
    )
    params: dict[str, str | int | float | bool] = Field(
        default_factory=dict, description="Hyperparameters used"
    )
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Start timestamp")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")
    status: ExperimentStatus = Field(
        default=ExperimentStatus.COMPLETED, description="Experiment status"
    )

    @property
    def node_id(self) -> str:
        """Return a unique identifier for graph purposes."""
        return f"experiment:{self.experiment_id}"


class LineageEdge(BaseModel):
    """A directed edge in the lineage graph."""

    from_id: str = Field(..., description="Source node identifier")
    to_id: str = Field(..., description="Target node identifier")
    relation: str = Field(..., description="Relationship type (e.g. trained_on, produced_by)")


class LineageGraph(BaseModel):
    """A directed acyclic graph representing model lineage."""

    nodes: list[ModelRecord | DatasetRecord | ExperimentRecord] = Field(
        default_factory=list, description="All nodes in the lineage graph"
    )
    edges: list[LineageEdge] = Field(
        default_factory=list, description="Directed edges between nodes"
    )


class ComplianceReport(BaseModel):
    """A complete compliance report for audit purposes."""

    title: str = Field(..., description="Report title")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Report generation timestamp"
    )
    model_records: list[ModelRecord] = Field(
        default_factory=list, description="All registered models"
    )
    dataset_records: list[DatasetRecord] = Field(
        default_factory=list, description="All registered datasets"
    )
    experiments: list[ExperimentRecord] = Field(
        default_factory=list, description="All experiment runs"
    )
    lineage_summary: str = Field(default="", description="Human-readable lineage summary")
    risk_assessment: list[str] = Field(
        default_factory=list, description="List of identified risk flags"
    )
