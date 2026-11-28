# Archify Routing & Execution Guide

Use this reference when Stage 1 selects **Archify** (standalone interactive HTML diagrams or one-page explainers).

## 1. Locating Archify

Check for an installed `archify` skill directory or CLI before invoking:
1. **Skill directory** (preferred—provides `SKILL.md`, `schemas/`, and `examples/`):
   - Project/local: `.agents/skills/archify/`
   - Global: `~/.agents/skills/archify/`, `~/.gemini/config/skills/archify/`
2. **Global CLI on `PATH`**: `which archify` (invoke as `archify <cmd>`, resolving package root via `dirname $(realpath $(which archify))/..` if schemas/examples are needed).

If `archify` is **not** installed, inform the user and fall back to **Mermaid** or **Obsidian `.canvas`** (except for `waterfall` or `explainer`, where Mermaid/Canvas cannot replicate proportional time axes or multi-panel HTML explainers—explain the limitation clearly).

---

## 2. Mermaid-to-Archify Upgrade Mapping

When upgrading existing Mermaid input into Archify JSON-IR, preserve topology and semantic meaning—do not copy Mermaid styling:

| Mermaid Block | Archify Type | Semantic Mapping |
| :--- | :--- | :--- |
| `flowchart` / `graph` | `workflow` or `architecture` | Use `architecture` for component/boundary maps; `workflow` for step-by-step processes and gates |
| `sequenceDiagram` | `sequence` | Participants -> semantic participants; arrows -> messages |
| `stateDiagram` / `stateDiagram-v2` | `lifecycle` | States and transitions retain meaning |
| `erDiagram` | `erd` | Entity/attribute names, PK/FK/unique keys, and cardinality retain meaning |
| `classDiagram` | `class` | Type kinds, selected members, and relationship kinds retain meaning |

---

## 3. Execution & Validation Workflow

When `archify` is available:

1. **Delegate to Archify's contract**: Read `<archify-dir>/SKILL.md` (if present) before authoring so you follow its current schema, quality profile, and evidence rules.
2. **Disambiguate type if unclear**:
   ```bash
   node <archify-dir>/bin/archify.mjs guide "<scenario>" --json
   ```
3. **Isolate artifacts**: Write `candidate.json` (or `candidate.archify.md` for `explainer`) and `<slug>.html` under `.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`.
4. **Read the matching Archify schema and example** from `<archify-dir>/schemas/` and `<archify-dir>/examples/` before authoring JSON-IR.
5. **Finalize & validate** (runs `validate`, `deliver`, strict `check`, and `browser-check`):
   ```bash
   node <archify-dir>/bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
   ```
   - For repository-backed diagrams, append `--repo-root <repo-root>`.
   - For dense ERDs (`>8` tables or `>50` fields), start with `--quality standard`.
   - Non-zero exit is a failure: inspect stdout/`evidence.summaryReceipt`, repair the candidate, and re-run `finalize`.
