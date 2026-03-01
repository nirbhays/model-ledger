"""Integration tests for ModelLedger CLI."""

from __future__ import annotations

from click.testing import CliRunner

from modelledger.cli import main


class TestCLIReportSample:
    """Test the `modelledger report --sample` command end-to-end."""

    def test_sample_report_exits_successfully(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert result.exit_code == 0, f"CLI failed with: {result.output}"

    def test_sample_report_contains_title(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert "Compliance Report" in result.output

    def test_sample_report_contains_models(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert "churn-predictor" in result.output
        assert "sentiment-analyzer" in result.output
        assert "demand-forecaster" in result.output

    def test_sample_report_contains_datasets(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert "customer-churn-v2" in result.output
        assert "product-reviews-nlp" in result.output

    def test_sample_report_contains_experiments(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert "exp-churn-baseline-001" in result.output
        assert "exp-sentiment-finetune-003" in result.output

    def test_sample_report_contains_risk_assessment(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert "Risk Assessment" in result.output

    def test_sample_report_contains_lineage(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample"])
        assert "Lineage" in result.output
        assert "nodes" in result.output

    def test_sample_report_markdown_format(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample", "--format", "markdown"])
        assert result.exit_code == 0
        assert "# " in result.output  # Markdown heading

    def test_sample_report_html_format(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample", "--format", "html"])
        assert result.exit_code == 0
        assert "<html" in result.output

    def test_sample_report_to_file(self, tmp_path) -> None:
        output_file = tmp_path / "report.md"
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample", "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "Compliance Report" in content

    def test_sample_report_custom_title(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--sample", "--title", "My Custom Audit"])
        assert result.exit_code == 0
        assert "My Custom Audit" in result.output


class TestCLIReportData:
    """Test the `modelledger report --data` command."""

    def test_report_from_data_file(self, tmp_path) -> None:
        """Generate data with init, then use it for a report."""
        data_file = tmp_path / "data.json"
        runner = CliRunner()

        # First generate sample data file
        result = runner.invoke(main, ["init", "--output", str(data_file)])
        assert result.exit_code == 0
        assert data_file.exists()

        # Then generate a report from it
        result = runner.invoke(main, ["report", "--data", str(data_file)])
        assert result.exit_code == 0
        assert "Compliance Report" in result.output

    def test_report_no_source_fails(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["report"])
        assert result.exit_code != 0


class TestCLIInit:
    """Test the `modelledger init` command."""

    def test_init_creates_file(self, tmp_path) -> None:
        output_file = tmp_path / "sample.json"
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()

    def test_init_output_contains_info(self, tmp_path) -> None:
        output_file = tmp_path / "sample.json"
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--output", str(output_file)])
        assert "Models:" in result.output
        assert "Datasets:" in result.output
        assert "Experiments:" in result.output


class TestCLIVersion:
    """Test the version option."""

    def test_version_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
