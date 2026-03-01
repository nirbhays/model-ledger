"""Click CLI for ModelLedger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
import structlog
from rich.console import Console
from rich.table import Table

from modelledger import __version__
from modelledger.core import Ledger, ReportGenerator, SampleDataGenerator

# Configure structlog to suppress log output during normal CLI use.
# structlog.make_filtering_bound_logger accepts a minimum log level (int).
# logging.WARNING == 30, which suppresses INFO/DEBUG messages from the Ledger.
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(30),
)

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="modelledger")
def main() -> None:
    """ModelLedger -- MLOps compliance dashboard for lineage tracking and audit reports."""


@main.command()
@click.option(
    "--sample",
    is_flag=True,
    default=False,
    help="Generate a report using built-in sample data.",
)
@click.option(
    "--data",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a JSON data file to generate a report from.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "html"], case_sensitive=False),
    default="markdown",
    help="Output format (default: markdown).",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write report to a file instead of stdout.",
)
@click.option(
    "--title",
    type=str,
    default="ModelLedger Compliance Report",
    help="Custom report title.",
)
def report(
    sample: bool,
    data: Path | None,
    output_format: str,
    output: Path | None,
    title: str,
) -> None:
    """Generate a compliance report."""
    if not sample and data is None:
        click.echo(
            "Error: Provide either --sample for demo data or --data PATH for a JSON file.",
            err=True,
        )
        raise SystemExit(1)

    ledger = Ledger()

    if sample:
        SampleDataGenerator().populate(ledger)
    elif data is not None:
        try:
            ledger.import_json(data)
        except (json.JSONDecodeError, FileNotFoundError) as exc:
            click.echo(f"Error loading data file: {exc}", err=True)
            raise SystemExit(1) from exc

    generator = ReportGenerator(ledger)
    rendered = generator.generate_report(format=output_format, title=title)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        click.echo(f"Report written to {output}")
    else:
        click.echo(rendered)


@main.command()
@click.option(
    "--data",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to a JSON data file to inspect.",
)
def inspect(data: Path) -> None:
    """Inspect imported data with rich terminal tables."""
    ledger = Ledger()
    try:
        ledger.import_json(data)
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        click.echo(f"Error loading data file: {exc}", err=True)
        raise SystemExit(1) from exc

    # Summary
    console.print()
    console.print(f"[bold cyan]ModelLedger Data Summary[/bold cyan]  --  {data}")
    console.print(
        f"  Models: [green]{len(ledger.models)}[/green]  |  "
        f"Datasets: [green]{len(ledger.datasets)}[/green]  |  "
        f"Experiments: [green]{len(ledger.experiments)}[/green]"
    )
    console.print()

    # Models table
    if ledger.models:
        model_table = Table(title="Models", show_lines=True)
        model_table.add_column("Name", style="bold")
        model_table.add_column("Version")
        model_table.add_column("Framework")
        model_table.add_column("Git Commit")
        model_table.add_column("Dataset Ref")
        model_table.add_column("Tags")
        model_table.add_column("Metrics")

        for m in ledger.models:
            metrics_str = ", ".join(f"{k}={v:.4f}" for k, v in m.metrics.items())
            model_table.add_row(
                m.model_name,
                m.model_version,
                m.framework,
                (m.git_commit[:12] + "...") if m.git_commit else "[red]N/A[/red]",
                m.dataset_ref or "[red]N/A[/red]",
                ", ".join(m.tags) if m.tags else "none",
                metrics_str or "none",
            )
        console.print(model_table)
        console.print()

    # Datasets table
    if ledger.datasets:
        dataset_table = Table(title="Datasets", show_lines=True)
        dataset_table.add_column("Name", style="bold")
        dataset_table.add_column("Version")
        dataset_table.add_column("Path")
        dataset_table.add_column("Hash")
        dataset_table.add_column("Samples", justify="right")

        for d in ledger.datasets:
            dataset_table.add_row(
                d.name,
                d.version,
                d.path,
                d.hash[:12] + "...",
                f"{d.num_samples:,}",
            )
        console.print(dataset_table)
        console.print()

    # Experiments table
    if ledger.experiments:
        exp_table = Table(title="Experiments", show_lines=True)
        exp_table.add_column("ID", style="bold")
        exp_table.add_column("Model Ref")
        exp_table.add_column("Dataset Ref")
        exp_table.add_column("Status")
        exp_table.add_column("Metrics")
        exp_table.add_column("Params")

        for e in ledger.experiments:
            status_style = {
                "completed": "green",
                "running": "yellow",
                "pending": "blue",
                "failed": "red",
            }.get(e.status.value, "white")
            metrics_str = ", ".join(f"{k}={v:.4f}" for k, v in e.metrics.items()) or "none"
            params_str = ", ".join(f"{k}={v}" for k, v in e.params.items()) or "none"
            exp_table.add_row(
                e.experiment_id,
                e.model_ref,
                e.dataset_ref,
                f"[{status_style}]{e.status.value}[/{status_style}]",
                metrics_str,
                params_str,
            )
        console.print(exp_table)
        console.print()

    # Lineage graph summary
    graph = ledger.build_graph()
    console.print(f"[bold cyan]Lineage Graph:[/bold cyan] {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    for edge in graph.edges:
        console.print(f"  {edge.from_id} --[{edge.relation}]--> {edge.to_id}")
    console.print()


@main.command()
@click.option(
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("modelledger_data.json"),
    help="Output path for the generated sample JSON file.",
)
def init(output: Path) -> None:
    """Generate a sample data JSON file as a starting point."""
    ledger = Ledger()
    SampleDataGenerator().populate(ledger)
    json_str = ledger.export_json(path=output)
    click.echo(f"Sample data file written to {output}")
    click.echo(f"  Models: {len(ledger.models)}")
    click.echo(f"  Datasets: {len(ledger.datasets)}")
    click.echo(f"  Experiments: {len(ledger.experiments)}")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  modelledger inspect --data {output}")
    click.echo(f"  modelledger report --data {output}")


if __name__ == "__main__":
    main()
