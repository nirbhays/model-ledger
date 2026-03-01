# ModelLedger Architecture

## Overview

ModelLedger is an MLOps compliance tool that tracks model lineage (model → dataset → experiment → deployment) and generates audit reports. It works entirely locally with JSON data files, with optional integrations planned for MLflow, DVC, and Langfuse.

## C4 Diagrams

### Level 1: System Context

```mermaid
graph TB
    User["ML/Platform Engineer"]
    ML["ModelLedger<br/>Compliance Dashboard"]
    Data["Model Metadata<br/>(JSON files)"]
    Reports["Compliance Reports<br/>(Markdown / HTML)"]
    Auditor["Auditor / Compliance Team"]

    User -->|"CLI"| ML
    Data -->|"import"| ML
    ML -->|"generate"| Reports
    Reports -->|"review"| Auditor

    style ML fill:#ef4444,stroke:#dc2626,color:#fff
```

### Level 2: Container Diagram

```mermaid
graph TB
    subgraph ModelLedger["ModelLedger"]
        CLI["CLI<br/>(click)"]
        Ledger["Ledger<br/>(in-memory store)"]
        Graph["Lineage Graph<br/>Builder"]
        Reporter["Report Generator<br/>(Jinja2)"]
        Sample["Sample Data<br/>Generator"]
    end

    CLI --> Ledger
    CLI --> Reporter
    CLI --> Sample
    Ledger --> Graph
    Graph --> Reporter

    style ModelLedger fill:#fef2f2,stroke:#ef4444
    style Ledger fill:#ef4444,color:#fff
    style Reporter fill:#f59e0b,color:#fff
```

### Sequence Diagram: Report Generation

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Sample as Sample Generator
    participant Ledger
    participant Reporter

    User->>CLI: modelledger report --sample
    CLI->>Sample: generate_sample_data()
    Sample-->>CLI: models, datasets, experiments

    CLI->>Ledger: add_model(), add_dataset(), add_experiment()
    CLI->>Ledger: build_graph()
    Ledger-->>CLI: LineageGraph

    CLI->>Reporter: generate_report(ledger, format="markdown")
    Reporter->>Reporter: render Jinja2 template
    Reporter-->>CLI: Markdown report string
    CLI-->>User: print report to stdout
```

## Design Decisions

### Local-First vs. Service-Based

**Chose:** CLI tool that works with local JSON files.

**Why:** Zero infrastructure requirements. Teams can start using it immediately by exporting their existing metadata to JSON. Service integrations (MLflow, DVC API) are planned as optional importers.

### Jinja2 Reports vs. Dashboard UI

**Chose:** Jinja2 template-based report generation (Markdown/HTML).

**Why:** Reports are portable, version-controllable, and can be generated in CI. A web dashboard adds deployment complexity inappropriate for v0.1.

## Extension Points

1. MLflow importer (API-based)
2. DVC importer (metadata parsing)
3. Langfuse importer (production traces)
4. Custom report templates
5. Risk scoring algorithms
