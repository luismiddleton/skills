---
name: diagram-crafting
description: >-
  Create, convert, validate, and fix diagrams across Mermaid (inline Markdown),
  Obsidian .canvas, and standalone interactive HTML (routed via Archify). Use
  when drawing flowcharts, mapping out codebases, or visualizing how systems
  or workflows work—including API sequences, data flows, state lifecycles,
  database schemas (ERDs), class models, module trees, timelines, and request
  waterfalls; converting/upgrading Mermaid to .canvas (collapsible backups) or
  HTML; fixing broken .canvas layouts; or turning docs into flows or one-page
  HTML explainers. Not for live monitoring dashboards, numeric data
  charts/plots, UI mockups/wireframes, icons/raster images, or knowledge-graph
  audits/vault organization.
metadata:
  author: Luis Middleton
  version: "1.0.0"
---

# Diagram Crafting (`diagram-crafting`)

Standardize visual architecture and technical diagrams across **Mermaid** (inline Markdown), **Obsidian `.canvas`** (spatial 2D maps), and **Archify** (validated standalone interactive HTML).

---

## 1. Workflow: Format & Type Selection

Select the output format first (**Stage 1**), then select the diagram type (**Stage 2**).

### Stage 1: Format Selection Triggers

**Default tie-breaker** (when no format is specified): use **Mermaid** for inline repo/Markdown docs, **Obsidian `.canvas`** when targeting an Obsidian vault, and **Archify** when standalone interactive HTML, repo-evidence grounding (`--repo-root`), dense ERDs (`>8` tables), `waterfall`, or `explainer` is requested.

| Option | Select When (Trigger Points) | Do NOT Select When |
| :--- | :--- | :--- |
| **Mermaid** | Inline Markdown docs, READMEs, PRs, or OKF notes; text-diffable diagrams; dual-view backup inside `> [!NOTE]-`. | Interactive HTML, dark/light theme toggle, motion, or SVG/WebM export is requested. |
| **Obsidian `.canvas`** | Target is an Obsidian vault or `.canvas` file; spatial 2D layout with Markdown/code cards, color semantics (`1`–`6`), and `group` containers; converting Mermaid to Canvas. | Target is a non-Obsidian README, standalone shareable HTML page, or proportional clock/duration chart. |
| **Archify** *(HTML)* | User asks for standalone/explorable HTML, dark/light theme, live motion, SVG/PNG/WebM export, upgrading Mermaid to interactive HTML, repo-evidence diagrams (`--repo-root`), dense multi-domain ERDs (`>8` tables or `>50` fields), proportional `timeline`/`waterfall` spans, or a one-page `explainer`. | Target is inline Markdown-only Mermaid, an Obsidian `.canvas` file, numeric data plots, or a live telemetry dashboard. |

### Stage 2: Diagram Type Selection Triggers

| Diagram / Mode | Mermaid | Archify Type | Workflow Trigger Points |
| :--- | :--- | :--- | :--- |
| **Architecture** | `flowchart TD` + `subgraph` | `architecture` | Services, cloud/security boundaries, VPCs, infrastructure, component maps |
| **Workflow** | `flowchart TD` / `LR` | `workflow` | Approval gates, CI/CD pipelines, runbooks, tool calls, step-by-step flows |
| **Sequence** | `sequenceDiagram` | `sequence` | API call chains, request lifecycles, async traces, actor back-and-forth |
| **Data Flow** | `flowchart LR` | `dataflow` | ETL/ELT pipelines, data lineage, governance, consumers, event routing |
| **Lifecycle / State** | `stateDiagram-v2` | `lifecycle` | Status transitions, retries, waiting and terminal states |
| **ERD** | `erDiagram` | `erd` | Tables/entities, attributes, PK/FK/unique keys, cardinality, domain groups |
| **Class / Type** | `classDiagram` | `class` | Classes, interfaces, members, inheritance/composition/realization |
| **Tree** | `flowchart TD` | `tree` | Single-parent containment: repo/module trees, capability decompositions |
| **Timeline** | `timeline` / `flowchart LR` | `timeline` | Incident reviews, release histories, events on a proportional clock *(Archify preferred for proportional spacing)* |
| **Waterfall** | *(use Archify)* | `waterfall` | Span durations, overlap, and nesting of a request or agent run on a time axis |
| **Explainer** | *(use Archify)* | `explainer` | User asks for a shareable one-page summary with conclusion first and structured panels |

*Obsidian `.canvas` mapping:* Any structural, workflow, data-flow, or lifecycle diagram in Stage 2 maps to 2D `text` cards (`color` `1`–`6`) enclosed in `group` containers with labeled directional edges.

---

## 2. Reference Loading Triggers

Load `references/` files **only** when their trigger applies:
- **Obsidian `.canvas` authoring or conversion**: Read [references/canvas-schema.md](./references/canvas-schema.md) for node types, color codes (`1`–`6`), and group enclosure rules. Use [assets/templates/canvas-template.json](./assets/templates/canvas-template.json) as a starter skeleton.
- **Mermaid authoring or Dual-View embedding**: Read [references/mermaid-patterns.md](./references/mermaid-patterns.md) for arrow semantics, quoting rules, subgraphs, and `> [!NOTE]-` callout syntax.
- **Archify HTML diagrams or explainers**: Read [references/archify-routing.md](./references/archify-routing.md) for Archify CLI discovery, Mermaid-to-Archify mapping, `finalize` gates, and fallback behavior.

---

## 3. Core Standards & Procedures

### Obsidian `.canvas` Geometry Standards

| Parameter | Standard Value | Rationale |
| :--- | :--- | :--- |
| **Horizontal Labeled Edge Gap** | $\ge 180\text{px}$ (Default: $200\text{px}$) | Prevents edge label boxes from overlapping node cards. |
| **Vertical Labeled Edge Gap** | $\ge 70\text{px}$ (Default: $80\text{px}$) | Gives vertical decision branches adequate clearance. |
| **Base Node Padding** | $50\text{px}$ safety margin | Absorbs Obsidian's internal card padding and header margins. |
| **Text / Code Line Allowance** | $30\text{px}$ text, $32\text{px}$ code | Prevents text clipping and card scrollbars. |

Never hardcode arbitrary node heights; compute height as:

$$\text{Height} = 50 + (\text{Headings} \times 18) + (\text{Text Lines} \times 30) + (\text{Code Lines} \times 32)$$

Minimum card sizes: **1-line title** (`100px` H × `300–340px` W), **3–4 line card** (`180px` H × `340–400px` W), **policy/code card** (`380–480px` H × `560–680px` W).

### Dual-View Markdown Embed (Canvas + Mermaid Backup)

When embedding a `.canvas` alongside a Mermaid backup, use native Obsidian collapsible callouts—**never** use HTML `<details>` or `<summary>` tags inside blockquotes (they break Obsidian's parser):

````markdown
> [!CANVAS] **Interactive Canvas View**
> **[Open Interactive Architecture Canvas](path/to/diagram.canvas)** `[[path/to/diagram.canvas|Open in Canvas Tab]]`

> [!NOTE]- Mermaid Diagram Backup (Click to expand)
> ```mermaid
> flowchart TD
>     A --> B
> ```
````

---

## 4. Validation Loop

### For Obsidian `.canvas`
Run the bundled validator from this skill's directory (or pass its path) until every file reports `[PASS]`:

```bash
python3 scripts/validate_canvas.py path/to/*.canvas
```

- `Risk of text clipping`: Increase node `height` using the formula above (always round up).
- `Label will collide with nodes`: Increase horizontal gap to $\ge 180\text{px}$ or vertical gap to $\ge 70\text{px}$.
- `Group enclosure padding`: Expand `group` bounds so all enclosed nodes have $\ge 40\text{px}$ margin on every side.

### For Archify HTML
Run `finalize` with `--quality showcase --json` (or `--quality standard` for dense first-pass ERDs) as detailed in [references/archify-routing.md](./references/archify-routing.md), and fix any failing gate before delivering the HTML link.
