# Changelog

All notable changes to ModelLedger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-15

### Added

- Ledger for tracking models, datasets, and experiments
- Lineage graph construction with directed edges
- Jinja2-based compliance report generation (Markdown and HTML)
- Automated risk assessment (missing provenance, failed experiments)
- JSON import/export for ledger data
- CLI commands: `report`, `inspect`, `init`
- Sample data generator for instant demos
- Rich terminal tables for data inspection
