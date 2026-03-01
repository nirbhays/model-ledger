# ModelLedger Blog Post -- Gemini Image Generation Prompts

> **Style Guide (applies to ALL images below)**
> - Modern, clean, minimalist tech aesthetic -- flat design / light isometric
> - Dark theme: primary background dark slate `#1a2332`, card/panel backgrounds `#1e2d3d`
> - Accent colours: gold/amber `#ffc107` (warnings), red `#ff5252` (high risk), green `#4caf50` (compliance/pass), soft blue `#42a5f5` (info/nodes), white `#ffffff` (text/lines)
> - Professional enough for Medium, eye-catching enough to stop a scroll
> - No stock-photo realism -- use flat vector illustration, clean iconography, and subtle isometric depth
> - Compliance/audit/legal visual metaphors: shields, checkmarks, document icons, magnifying glasses, gavel silhouettes
> - Consistent rounded-rectangle card motif across all images
> - All text in the images should use a clean sans-serif typeface (Inter, Roboto, or similar)

---

### Image 1: Hero / Cover Image
**Filename:** `modelledger-blog-hero.png`
**Dimensions:** 1200x630
**Prompt:**
Create a wide hero banner illustration in a dark, modern tech aesthetic. The background is a deep dark slate (#1a2332) with a subtle radial gradient lightening slightly toward the center. On the left side, render a large, stylized shield icon in green (#4caf50) with a checkmark inside it, representing compliance. To the right of the shield, display the text "ModelLedger" in bold white sans-serif type and directly below it, in smaller gold/amber (#ffc107) text, "ML Compliance in One Command." In the upper-right area, render a flat-design countdown clock face showing the hands near midnight, with the text "August 2026" in amber below it and a small pulsing-style concentric circle animation effect (drawn as static concentric rings in amber with decreasing opacity) to convey urgency. Along the bottom, place a thin horizontal timeline bar running left to right, marked with tick marks and labels: "Today" on the left (white dot), "6 Months" in the middle (amber dot), and "EU AI Act Deadline" on the right (red dot, #ff5252). Scatter faint, low-opacity icons in the background: a document page, a database cylinder, a directed-graph snippet, and a gavel silhouette -- all in a slightly lighter shade of the slate (#253545) to create subtle texture. The overall feel should be urgent but controlled, professional but bold. Flat vector style, no photorealism, no gradients on the icons -- solid flat fills only.

**Alt Text:** ModelLedger hero banner showing a green compliance shield, a countdown clock pointing to the August 2026 EU AI Act deadline, and a timeline bar illustrating the six months remaining.
**Placement:** Top of the blog post, above the title or immediately below the title/subtitle.

---

### Image 2: The Compliance Gap
**Filename:** `modelledger-blog-compliance-gap.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design illustration on a dark slate (#1a2332) background showing three side-by-side vertical "buckets" or columns, each represented as a rounded-rectangle card with a slightly lighter panel background (#1e2d3d) and a thin 1px border.

**Bucket 1 (left):** Label at the top in white text: "No Tracking." Inside the card, draw chaotic icons -- a messy notebook icon, a Slack logo silhouette, a floppy disk with a question mark, files scattered at angles. At the bottom of the card, a red (#ff5252) "X" badge with the label "AUDIT FAIL" in small red text.

**Bucket 2 (center):** Label: "Partial Tracking." Inside, draw cleaner but disconnected icons -- an MLflow-style logo placeholder, a bar chart, a Git branch icon, and a spreadsheet icon -- but with visible dotted lines between them that are broken or disconnected, symbolizing fragmentation. At the bottom, the same red "X" badge and "AUDIT FAIL" label.

**Bucket 3 (right):** Label: "Over-Engineered." Inside, draw an overwhelming tangle of connected boxes, arrows going in every direction, tiny microservice icons stacked on top of each other, a database, a Kubernetes wheel icon, and a cloud icon -- all crammed together to look intimidatingly complex. At the bottom, the same red "X" badge and "AUDIT FAIL" label.

Below all three buckets, center a single line of amber (#ffc107) text: "None of these produce a compliance report." The visual message: it does not matter how much or how little you track -- without a compliance-first tool, you fail the audit. Flat vector style, clean lines, no photorealism.

**Alt Text:** Three illustrated buckets labeled No Tracking, Partial Tracking, and Over-Engineered Tracking, each marked with a red Audit Fail badge, with the caption: None of these produce a compliance report.
**Placement:** In or directly below the "The Compliance Gap Nobody Talks About" section.

---

### Image 3: One Command
**Filename:** `modelledger-blog-one-command.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design illustration of a stylized terminal window floating on a dark slate (#1a2332) background. The terminal window should have a dark (#0d1117) inner background, a thin rounded-rectangle border in soft blue (#42a5f5), and three small colored dots (red, yellow, green) in the top-left corner to mimic a macOS terminal title bar. Inside the terminal, render the following lines in a clean monospaced font:

Line 1 (dimmed gray #888): `$ pip install modelledger`
Line 2 (dimmed gray): `Successfully installed modelledger-0.1.0`
Line 3 (blank)
Line 4 (bright white): `$ modelledger report --sample`
Line 5 (green #4caf50): `--- Generating compliance report...`
Line 6 (green): `--- Risk assessment: 5 categories scanned`
Line 7 (green): `--- Lineage graph: 3 models, 2 datasets, 4 experiments`
Line 8 (bold green): `Report saved: compliance-report.md`
Line 9 (amber #ffc107): `Done in 0.8s`

To the right of the terminal window, at a slight angle, show a stylized document icon (white page with lines of text and a green checkmark badge in its corner) with the label "compliance-report.md" beneath it in small white text. Draw a curved arrow (dashed, in amber) from the terminal to the document, implying the command produced the report. Flat vector style, no drop shadows, clean geometry.

**Alt Text:** Illustrated terminal window showing the commands pip install modelledger and modelledger report sample, with output indicating a compliance report was generated in 0.8 seconds, and an arrow pointing to a document icon representing the output report.
**Placement:** In the "One Command to Compliance" section, after the first code block.

---

### Image 4: Report Output
**Filename:** `modelledger-blog-report-output.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design illustration showing a stylized compliance report document on a dark slate (#1a2332) background. The report is represented as a tall rounded-rectangle card (#1e2d3d background, thin white border) divided into three clearly labeled sections stacked vertically, each separated by a thin horizontal divider line:

**Section 1 -- "Model Inventory":** Show a miniature table with three rows. Column headers in bold white: Model, Version, Framework, Git Commit. The first row has all cells filled (use short placeholder text in soft blue). The second row has one cell highlighted in red (#ff5252) with the text "(missing)" to show a gap. The third row has another red "(missing)" cell. Use a small table-grid icon to the left of the section title.

**Section 2 -- "Risk Assessment":** Show three risk flag lines. The first two start with a red badge labeled "HIGH" followed by a short description line in white. The third starts with an amber badge labeled "WARN" followed by a description. Use a small warning-triangle icon to the left of the section title.

**Section 3 -- "Dataset Registry":** Show a miniature table with two rows, all cells filled in green (#4caf50) tinted text to imply completeness. Include a column for "Hash (SHA256)" with truncated hash values. Use a small database-cylinder icon to the left of the section title.

At the very top of the card, show a report header: "ML Compliance Report" in bold white, with a small timestamp "Generated: 2026-02-15" in gray beneath it. In the top-right corner of the card, place a small green shield-with-checkmark icon. The overall effect should feel like a clean, structured, auditor-ready document. Flat vector, no photorealism.

**Alt Text:** Stylized compliance report document showing three sections: a Model Inventory table with some missing fields highlighted in red, a Risk Assessment section with HIGH and WARN severity flags, and a Dataset Registry table with complete entries in green.
**Placement:** In the "What's Actually in a Report" section, before or after the Markdown code block.

---

### Image 5: Lineage Graph
**Filename:** `modelledger-blog-lineage-graph.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design directed graph diagram on a dark slate (#1a2332) background illustrating ML model lineage. Use rounded-rectangle nodes with distinct color coding by type:

**Dataset nodes** (top level): Two nodes with a soft teal/cyan (#26c6da) fill and a small database icon inside. Labels: "raw-clickstream-v2" and "customer-segments-v4".

**Model nodes** (middle level): Three nodes with a soft blue (#42a5f5) fill and a small brain/neural-network icon inside. Labels: "recommender v3.1.0 (pytorch)", "click-predictor v1.2.0 (sklearn)", "churn-model v2.0.0 (xgboost)".

**Experiment nodes** (bottom level): Four nodes with a soft purple (#ab47bc) fill and a small flask/beaker icon inside. Labels: "exp-051 ndcg:0.71 SUCCESS", "exp-054 ndcg:0.74 SUCCESS", "exp-055 auc:0.89 SUCCESS", "exp-060 f1:0.91 SUCCESS". Each experiment node should have a tiny green checkmark badge in its corner to indicate SUCCESS.

**Edges:** Draw clean directional arrows (white or light gray, with arrowheads) between nodes. From "raw-clickstream-v2" draw arrows down to "recommender" and "click-predictor", labeled "trained_on" in small amber (#ffc107) text along the edge. From each model draw arrows down to its experiment nodes, labeled "evaluated_in" in small amber text. From "customer-segments-v4" draw an arrow to "churn-model" labeled "trained_on", and from "churn-model" to "exp-060" labeled "evaluated_in."

Add a small legend in the bottom-right corner: a teal square labeled "Dataset", a blue square labeled "Model", a purple square labeled "Experiment". The layout should flow top-to-bottom like a DAG, clean and readable, with enough spacing between nodes. Flat vector style, clean edges, no 3D.

**Alt Text:** Directed acyclic graph showing ML model lineage: two dataset nodes at the top connect via trained_on edges to three model nodes in the middle, which connect via evaluated_in edges to four experiment nodes at the bottom, each showing metrics and a success status.
**Placement:** In the "The Lineage Graph, Explained" section, replacing or accompanying the ASCII graph.

---

### Image 6: Risk Assessment
**Filename:** `modelledger-blog-risk-assessment.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design illustration on a dark slate (#1a2332) background showing a vertical list of five risk assessment cards, each as a horizontal rounded-rectangle row. Each row has three elements: a severity badge on the left, an icon in the center-left, and a description on the right.

**Row 1:** A bold red (#ff5252) badge reading "HIGH". A broken-link chain icon. Text in white: "Missing dataset reference -- training data unknown." Model name "fallback-ranker v0.9.0" in small gray text below.

**Row 2:** A bold red badge reading "HIGH". A code-branch icon with a question mark. Text: "Missing git commit -- code provenance unverifiable." Model name "churn-predictor v1.4.0" in small gray below.

**Row 3:** An amber (#ffc107) badge reading "WARN". A flask icon with an X mark. Text: "No experiments found -- model never evaluated." Model name "fallback-ranker v0.9.0" in small gray below.

**Row 4:** An amber badge reading "WARN". A red X-circle icon. Text: "Experiment FAILED -- results should not be used." Experiment name "experiment-042" in small gray below.

**Row 5:** An amber badge reading "WARN". A bar-chart icon with a question mark. Text: "Experiment has no recorded metrics -- evaluation meaningless." Experiment name "experiment-047" in small gray below.

Separate each row with a thin horizontal line in a very dark gray (#2a3a4a). At the top of the image, display a header: "Automated Risk Assessment" in bold white with a small warning-triangle icon in amber beside it. At the bottom, display a small caption in green (#4caf50): "5 risk categories auto-detected per report." The overall feel should be like a structured dashboard panel showing clear, actionable risk flags. Flat vector, no photorealism.

**Alt Text:** Risk assessment panel showing five flagged issues: two HIGH-severity risks for missing dataset references and missing git commits, and three WARN-severity risks for unevaluated models, failed experiments, and missing metrics, each with an icon and description.
**Placement:** In the "What's Actually in a Report" section, near the risk categories bullet list.

---

### Image 7: Auditor Questions
**Filename:** `modelledger-blog-auditor-questions.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design illustration on a dark slate (#1a2332) background showing a two-column layout. The left column is labeled "Auditor Asks" in white with a small magnifying-glass icon, and the right column is labeled "ModelLedger Answers" in green (#4caf50) with a small shield-checkmark icon.

Show six rows, each as a horizontal card spanning both columns with a thin divider between rows:

**Row 1:** Left: "List every ML model in production?" (white text). Right: "Model Inventory table" (green text) with a green checkmark icon.

**Row 2:** Left: "What data trained this model?" Right: "Lineage Graph -- trained_on edges" with a green checkmark.

**Row 3:** Left: "How was this model evaluated?" Right: "Experiments + evaluated_in edges" with a green checkmark.

**Row 4:** Left: "Can you reproduce this model?" Right: "Git commit + dataset hash" with a green checkmark.

**Row 5:** Left: "Any known risks or gaps?" Right: "Risk Assessment -- auto-detected" with a green checkmark.

**Row 6:** Left: "When was this documentation generated?" Right: "Timestamped report header" with a green checkmark.

The left column questions should have a subtle question-mark icon beside each. The right column answers should feel confident and resolved -- use green text and prominent checkmark icons. At the bottom center, display in bold amber (#ffc107) text: "Every question answered. One command." The layout should feel like a clean Q&A checklist. Flat vector, sans-serif type, no photorealism.

**Alt Text:** Two-column checklist showing six common auditor questions on the left and the corresponding ModelLedger feature that answers each on the right, with green checkmarks confirming every question is addressed.
**Placement:** In the "What Auditors Actually Ask" section, replacing or accompanying the table.

---

### Image 8: Countdown Clock
**Filename:** `modelledger-blog-countdown.png`
**Dimensions:** 800x500
**Prompt:**
Create a flat-design illustration on a dark slate (#1a2332) background centered on urgency and a ticking deadline. In the center, render a large circular countdown timer or clock face with a thick amber (#ffc107) ring as the outer border. The ring should be partially filled (roughly 75% depleted, 25% remaining) to visually show time running out -- the depleted portion in dark gray (#2a3a4a) and the remaining arc in bright amber. Inside the circle, display "6" in very large bold white numerals, with "months remaining" in smaller white text directly below.

Above the clock, display "EU AI Act Deadline" in bold white text with a small EU flag icon (simplified: blue rectangle with a circle of gold/amber stars) to its left.

Below the clock, display "August 2026" in large bold red (#ff5252) text.

Beneath that, show a single-line call to action in a rounded-rectangle button shape with a green (#4caf50) fill: "modelledger report --sample" in white monospaced text, styled like a terminal command.

In the four corners of the image, place small faint icons representing what's at stake: top-left a document/report icon, top-right a warning triangle, bottom-left a shield, bottom-right a gavel -- all in low-opacity (#253545) to add texture without distraction. The overall mood should be professional urgency: the deadline is real, the clock is ticking, but there is a clear action to take. Flat vector, no photorealism, clean geometry.

**Alt Text:** Countdown clock illustration showing 6 months remaining until the August 2026 EU AI Act deadline, with a partially depleted amber timer ring and a green call-to-action button reading modelledger report sample.
**Placement:** In "The Clock Is Ticking" section or at the very end of the post as a closing visual.

---

## Usage Notes

- **Generation order:** Generate Image 1 (hero) first to establish the visual language, then use it as a style reference for the remaining images.
- **Gemini settings:** Use the highest available resolution. If Gemini offers style or mood parameters, select "digital illustration" or "flat vector" and avoid any photorealistic or painterly modes.
- **Post-processing:** After generation, verify that all text in the images is legible at the intended display size. Re-generate with larger font sizes if any text is too small to read at 800px width.
- **Accessibility:** Every image has alt text above. Use these as the `alt` attribute in the blog's `<img>` tags and also as `title` text for hover tooltips.
- **Consistency check:** Before publishing, view all eight images side by side and confirm they share the same dark-slate background tone, the same accent colour palette, and the same flat-vector aesthetic. Re-generate any outlier.
