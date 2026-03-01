# AI Regulation Is Coming. Your ML Pipeline Isn't Ready. Mine Wasn't Either.

*How I built a single-command compliance dashboard after realizing my team couldn't answer basic audit questions about our own models.*

---

The EU AI Act entered into force in August 2024. By August 2026, organizations deploying high-risk AI systems need to demonstrate full traceability: what data trained the model, what code produced it, how it was evaluated, and whether it passed. If you can't answer those questions with documentation, you have a compliance problem.

I spent a Tuesday afternoon trying to answer them for my own team's models. It did not go well.

> **TL;DR -- Why You Should Keep Reading**
> - The EU AI Act high-risk deadline lands in **6 months** (August 2026). Most ML teams cannot produce a single compliance artifact today.
> - **ModelLedger** is a local-first, zero-infrastructure CLI that turns simple JSON metadata into auditable compliance reports with one command.
> - It auto-detects 5 categories of risk, builds a full lineage graph, and outputs Markdown or HTML reports an auditor can actually read.
> - It is open source, installs in seconds, and you can see a full sample report before touching your own data.

Which dataset version trained our production recommender? "The big one, I think." What commit hash corresponds to the model checkpoint we shipped in January? Silence. Did we ever actually evaluate the fallback model, or did we just... deploy it? Nervous laughter.

We had MLflow running. We had experiment logs somewhere. We even had a shared spreadsheet that someone started maintaining in Q3 and abandoned by Q4. None of it amounted to an audit trail. None of it could produce a compliance report. And none of it could tell us, at a glance, which models were risky and why.

So I built ModelLedger.

---

## By the Numbers

| | |
|---|---|
| **48** | tests passing across the entire suite |
| **5** | risk categories auto-detected per report |
| **1** | command to generate a full compliance report |
| **0** | infrastructure required -- no server, no database, no cloud account |
| **< 1 s** | report generation time for typical projects |
| **6 months** | until the EU AI Act high-risk compliance deadline |

---

## The Compliance Gap Nobody Talks About

Here is the dirty secret of most ML teams: the gap between "we track experiments" and "we can prove compliance" is enormous. Tracking metrics in a dashboard is not the same as maintaining an auditable lineage graph. Logging hyperparameters is not the same as linking a model to its training data provenance, its code version, and its evaluation results in a single, reviewable document.

**If an auditor walked into your office tomorrow and asked "show me every dataset that touched your production model," could you answer in under five minutes?**

Most teams I've talked to fall into one of three buckets:

1. **No tracking at all.** Models are trained in notebooks, checkpointed to a shared drive, and deployed via Slack message. God help them.
2. **Partial tracking with tools.** They use MLflow or Weights & Biases for experiment logging but have no systematic way to connect models to datasets to code to evaluation. The information exists but is scattered across dashboards, Git repos, and someone's memory.
3. **Over-engineered tracking.** They stood up a metadata store, a feature platform, a model registry, and a lineage service -- but the complexity means half the team bypasses it and the other half doesn't trust it.

ModelLedger targets the gap between bucket 2 and actual compliance readiness. It is a local-first, file-based MLOps compliance tool that tracks model lineage and generates audit reports. One command, one report, zero infrastructure.

## One Command to Compliance

Here is the entire workflow:

```bash
pip install modelledger
modelledger report --sample
```

That's it. The `--sample` flag generates a complete compliance report using built-in sample data so you can see exactly what the output looks like before you plug in your own metadata. The report lands as a Markdown file (or HTML, if you prefer) with every section an auditor would ask for.

For real usage, you maintain simple JSON files that describe your models, datasets, and experiments. No database. No server. No API keys. No cloud account. Just JSON files in your repo, versioned alongside your code.

```bash
modelledger report --data ./ml-metadata/ --format html
```

The tool reads your metadata, constructs a lineage graph, runs automated risk assessment, and generates a formatted report. The whole process takes under a second for typical project sizes.

You can also inspect your metadata interactively before generating a report:

```bash
modelledger models list
modelledger datasets list
modelledger experiments list
```

These commands render rich terminal tables using the Rich library, giving you a quick visual overview of what's tracked and what's missing.

## The 10-Minute Compliance Audit

Let's walk through a realistic scenario. Your team has three models in production. You have never generated a compliance report. You have 10 minutes before a standup where your lead is going to ask about EU AI Act readiness. Go.

**Minute 0-1: Install and see the sample.**

```bash
pip install modelledger
modelledger report --sample
```

You now have a Markdown report showing exactly what the output looks like. You understand the format.

**Minute 1-4: Describe your models.**

Create `ml-metadata/models.json`. For each production model, write a simple entry: name, version, framework, git commit (grab it from your deploy log or `git log`), and a reference to the dataset it was trained on. This is not boilerplate -- it is the minimum an auditor needs.

**Minute 4-6: Describe your datasets.**

Create `ml-metadata/datasets.json`. Name, version, sample count, and a SHA-256 hash if you have one. If you do not have a hash, leave it out -- ModelLedger will flag it as a risk, which is exactly what you want. Honest gaps are better than hidden ones.

**Minute 6-8: Describe your experiments and link the edges.**

Create `ml-metadata/experiments.json` with your evaluation runs: which model, which metrics, pass or fail. Then create `ml-metadata/edges.json` to connect models to datasets (`trained_on`) and models to experiments (`evaluated_in`).

**Minute 8-9: Generate the real report.**

```bash
modelledger report --data ./ml-metadata/ --format html
```

Open the HTML file. You now have a model inventory, a dataset registry, a lineage graph, and a risk assessment. The risks are color-coded. The gaps are explicit.

**Minute 9-10: Read the risk section.**

Every missing link, every unevaluated model, every absent git commit is flagged with a severity level. You now know exactly where your compliance gaps are -- and you have a document to prove you identified them.

That is 10 minutes from zero to a compliance artifact. Not perfect compliance -- but a concrete, reviewable starting point that puts you ahead of most teams in the industry.

## What's Actually in a Report

The generated report is not a vanity dashboard. It is structured for auditability. Here is a condensed snippet from a real ModelLedger report:

```markdown
# ML Compliance Report
Generated: 2026-02-15T10:30:00Z

## Model Inventory
| Model              | Version | Framework  | Git Commit | Dataset Ref       |
|--------------------|---------|------------|------------|-------------------|
| fraud-detector     | 2.1.0   | pytorch    | a3f8c91    | transactions-v3   |
| churn-predictor    | 1.4.0   | sklearn    | (missing)  | customer-data-v2  |
| fallback-ranker    | 0.9.0   | tensorflow | b7e2d44    | (missing)         |

## Risk Assessment
[HIGH] churn-predictor v1.4.0: Missing git commit -- code provenance unverifiable
[HIGH] fallback-ranker v0.9.0: Missing dataset reference -- training data unknown
[WARN] fallback-ranker v0.9.0: No experiments found -- model never evaluated
[WARN] experiment-042: Status FAILED -- results should not be used

## Dataset Registry
| Dataset            | Version | Samples  | Hash (SHA256)               |
|--------------------|---------|----------|-----------------------------|
| transactions-v3    | 3.0.0   | 1245890  | 9f86d08...                  |
| customer-data-v2   | 2.1.0   | 58340    | a591a6d...                  |

## Lineage Graph
fraud-detector v2.1.0
  -- trained_on --> transactions-v3
  -- evaluated_in --> experiment-038 (accuracy: 0.94, status: SUCCESS)
  -- evaluated_in --> experiment-041 (accuracy: 0.96, status: SUCCESS)

churn-predictor v1.4.0
  -- trained_on --> customer-data-v2
  -- evaluated_in --> experiment-039 (f1: 0.87, status: SUCCESS)

fallback-ranker v0.9.0
  -- (no lineage edges recorded)
```

The risk assessment section is the part that actually matters for compliance. ModelLedger automatically flags five categories of risk:

- **Models missing dataset references** -- if you can't trace a model back to its training data, you cannot demonstrate data governance compliance.
- **Models missing git commits** -- if you can't link a model to a specific code version, you cannot reproduce it or verify what logic produced it.
- **Experiments without metrics** -- if an experiment ran but recorded no metrics, the evaluation is meaningless.
- **Failed experiments** -- explicit flags to prevent anyone from accidentally treating failed runs as valid.
- **Models with no experiments** -- a model that was never formally evaluated is a model you cannot vouch for.

An auditor does not need to understand your ML stack. They need to read this report and see either green or red.

## What Auditors Actually Ask (And How ModelLedger Answers)

Compliance is not abstract. Auditors show up with specific questions. Here are the ones I've encountered most often, and exactly how ModelLedger addresses each:

| Auditor's Question | Where ModelLedger Answers It |
|---|---|
| "Can you list every ML model currently in production?" | **Model Inventory** table -- name, version, framework, and git commit for every registered model. |
| "What data was used to train this model?" | **Lineage Graph** -- follow the `trained_on` edge from any model to its dataset, including version and hash. |
| "How was this model evaluated, and did it pass?" | **Lineage Graph** + **Experiment section** -- every `evaluated_in` edge links to an experiment with recorded metrics and a pass/fail status. |
| "Can you reproduce this model from source?" | **Git commit** field in the Model Inventory + **dataset hash** in the Dataset Registry. If either is missing, the Risk Assessment flags it as HIGH. |
| "Are there any known risks or gaps in your documentation?" | **Risk Assessment** section -- every gap is auto-detected and categorized by severity. Nothing is hidden. |
| "When was this documentation last generated?" | **Report header** -- every report is timestamped. Because the JSON lives in Git, you also have a full change history. |

**The most dangerous compliance position is not having gaps -- it is not knowing where your gaps are.**

## The Lineage Graph, Explained

The core data structure in ModelLedger is a directed graph. Nodes are models, datasets, and experiments. Edges represent relationships: `trained_on`, `evaluated_in`, `used_in`.

Think of it like a supply chain for your ML artifacts. A model was trained on a dataset. That training produced an experiment. The experiment recorded metrics and a pass/fail status. If you pull any thread, you should be able to trace it all the way back to the source data and the source code.

Here is what a more realistic lineage graph looks like for a team with shared datasets and multiple model versions:

```
                        ┌─────────────────────┐
                        │  raw-clickstream-v2  │
                        │     (dataset)        │
                        └────────┬─────────────┘
                                 │ trained_on
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌────────▼───────┐
            │ recommender    │       │ click-predictor │
            │   v3.1.0       │       │   v1.2.0        │
            │  (pytorch)     │       │  (sklearn)      │
            └───┬────────┬───┘       └────┬────────────┘
                │        │                │
      evaluated_in  evaluated_in    evaluated_in
                │        │                │
        ┌───────▼──┐  ┌──▼────────┐  ┌───▼──────────┐
        │ exp-051  │  │ exp-054   │  │ exp-055      │
        │ ndcg:0.71│  │ ndcg:0.74 │  │ auc: 0.89   │
        │ SUCCESS  │  │ SUCCESS   │  │ SUCCESS      │
        └──────────┘  └───────────┘  └──────────────┘

  ┌─────────────────────┐
  │ customer-segments-v4 │
  │     (dataset)        │
  └────────┬─────────────┘
           │ trained_on
    ┌──────▼──────────┐
    │ churn-model      │
    │   v2.0.0         │
    │  (xgboost)       │
    └──────┬──────────┘
           │
     evaluated_in
           │
    ┌──────▼──────────┐
    │ exp-060         │
    │ f1: 0.91        │
    │ precision: 0.88 │
    │ SUCCESS         │
    └─────────────────┘
```

Two datasets, three models, four experiments -- all connected, all traceable, all auditable. When your compliance officer asks "what data influenced model X?", you follow the arrows. When they ask "was model Y ever evaluated?", you check for outbound `evaluated_in` edges. No ambiguity.

This is not a new concept -- ML lineage tracking has been discussed for years. What's different here is that ModelLedger makes the graph explicit and inspectable. It is not buried inside a metadata database that only your platform team can query. It lives in your JSON files, renders in your report, and can be reviewed by anyone on the team, including non-technical stakeholders who need to sign off on compliance.

The edges are simple and declarative. You define them in your metadata:

```json
{
  "edges": [
    {"source": "fraud-detector-v2.1.0", "target": "transactions-v3", "relation": "trained_on"},
    {"source": "fraud-detector-v2.1.0", "target": "experiment-038", "relation": "evaluated_in"}
  ]
}
```

No DSL. No query language. No graph database. Just a list of edges that a human can read and a machine can validate.

## Why JSON Files Beat Databases for This Use Case

This is the section where experienced engineers will raise an eyebrow. No database? For compliance-critical metadata? Let me make the case.

**Version control.** JSON files live in your Git repo. Every change to your model metadata is a Git commit. You get a full audit trail of who changed what and when, for free. Try getting that from a Postgres table.

**Portability.** Your compliance metadata should outlive your infrastructure. Teams migrate cloud providers. They sunset internal tools. They reorganize and re-platform. A directory of JSON files survives all of that. A database does not.

**Reviewability.** A compliance report is only as trustworthy as the metadata that produced it. If that metadata lives in a database, reviewing it requires queries. If it lives in JSON files in a pull request, reviewing it requires reading.

**Zero ops.** No server to maintain. No connection strings to manage. No migrations to run. No backups to configure (Git is your backup). For a compliance tool, operational simplicity is a feature, not a limitation.

The tradeoff is obvious: this approach does not scale to thousands of models with millions of experiments. If you are at that scale, you need a metadata platform. ModelLedger is not trying to be that. It is designed for teams with tens to low hundreds of models who need compliance documentation without the overhead of a platform.

## How It Compares

**MLflow** is excellent for experiment tracking at scale, but it requires a tracking server, and it does not generate compliance reports. You can extract the data to build one, but you are writing that tooling yourself.

**Weights & Biases** has the best experiment visualization in the business, but it is a cloud service. Your metadata lives on someone else's infrastructure, which introduces its own compliance questions. It also does not produce audit-ready reports out of the box.

**DVC** handles data and model versioning beautifully but focuses on the version control problem, not the compliance reporting problem. It does not generate risk assessments or audit documents.

ModelLedger does not replace any of these tools. It occupies a different niche: taking your ML metadata (wherever it comes from) and producing auditable compliance documentation. You could even use it alongside MLflow or DVC, exporting metadata into ModelLedger's JSON format for report generation.

## What ModelLedger Won't Do (And What You Should Use Instead)

I want to be upfront about what ModelLedger is not:

- **It is not a model registry.** It does not store model artifacts. It tracks metadata about them. If you need artifact storage, look at MLflow Model Registry or DVC.
- **It is not an experiment tracker.** It does not hook into your training loop. You populate the metadata files yourself or write a script to export from your existing tracker.
- **It does not enforce anything.** It reports risks, it does not prevent deployments. Enforcement is a CI/CD concern -- wire ModelLedger's exit codes into your pipeline if you want to gate on compliance.
- **It is a young project.** The test suite is solid (48 tests passing, more than any other project in our toolkit), but the ecosystem around it is still early.

If you need a full MLOps platform, this is not it. If you need a compliance layer that sits on top of whatever you already use, keep reading.

## The Clock Is Ticking: Why This Matters Right Now

**You have 6 months. Your audit trail starts with one command.**

The EU AI Act is not theoretical. It is law. The timeline for high-risk AI system compliance is not "someday" -- it is August 2026. That is this summer. Organizations that deploy ML models in the EU (or serve EU users) need to demonstrate:

- **Data governance:** What data was used? How was it sourced? Is it documented?
- **Technical documentation:** How does the model work? What are its known limitations?
- **Record-keeping:** Can you trace decisions back to specific model versions and datasets?
- **Risk management:** Have you identified and mitigated risks?

ModelLedger directly addresses record-keeping and risk management. It does not solve the entire regulation, but it gives you a concrete, auditable artifact you can hand to a compliance officer and say: here is our model inventory, here is our lineage graph, here are the risks we've identified and their current status.

Most teams I talk to know they need this. They just have not started. The tooling felt too heavy, the requirements felt too vague, and the deadline felt too far away.

**The deadline is no longer far away. It is 6 months away. And "we're working on it" is not a compliance status.**

## Try It -- Before August, Not After

```bash
pip install modelledger

# See what a compliance report looks like
modelledger report --sample

# Point it at your own metadata
modelledger report --data ./your-metadata/ --format html

# Inspect your tracked artifacts
modelledger models list
modelledger datasets list
modelledger experiments list
```

The entire project is open source. The metadata format is documented. The report templates are Jinja2, so you can customize them for your organization's specific compliance requirements.

If your team ships ML models and cannot today produce a one-page summary of which models are in production, what data trained them, and whether they were properly evaluated -- you have a compliance gap. ModelLedger closes it in about ten minutes.

**The EU AI Act does not have a "we didn't know" clause. Start now.**

Run `modelledger report --sample`. Read the output. Send it to your compliance officer. Then decide if your team can afford to wait another month.

---

*ModelLedger is part of a broader MLOps toolkit. It is built with Click, Pydantic, Jinja2, structlog, and Rich. Contributions, feedback, and issues are welcome on GitHub.*
