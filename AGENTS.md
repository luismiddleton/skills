# AGENTS.md

Guidance for authoring, evaluating, and maintaining [Agent Skills](https://agentskills.io/home) in this repository.

## Repository Layout

- Skills live under `skills/<skill-name>/` (see `skills/prompt-crafting/` for an example).
- When adding a new skill, also update the **Available Skills** table in `README.md`.

## Evaluation & Critique Rule (Mandatory)

> **Always use a sub-agent when evaluating against best practices.**
> Whenever you evaluate a skill (or changes to a skill or `AGENTS.md`) against the standards below, spawn a dedicated sub-agent with a fresh context to perform the critique. Do not rely solely on self-review in the authoring context.

The critique sub-agent must inspect and report findings against:
1. **Specification compliance** (frontmatter fields, naming rules, directory layout).
2. **Progressive disclosure & size** (`SKILL.md` `<500` lines / `<5,000` tokens, shallow references, conditional loading).
3. **Description quality** (third-person firing conditions, explicit triggers, negative boundaries).
4. **Script hygiene** (determinism vs. judgment, PEP 723 inline metadata, meaningful exit codes).
5. **Eval coverage** (`trigger_queries.json` positive/near-miss balance, `evals.json` observable assertions).

---

## 1. Specification (`SKILL.md` & Directory Structure)

A skill is a self-contained directory:

```text
<skill-name>/
├── SKILL.md        # Required: YAML frontmatter + Markdown instructions
├── scripts/        # Optional: Executable helper CLIs
├── references/     # Optional: Deep docs, schemas, or examples (1 level deep)
├── assets/         # Optional: Templates, static files, or schemas used in output
└── evals/          # Optional: Trigger queries, test cases, and fixtures
```

### YAML Frontmatter

| Field | Required | Constraints |
| :--- | :--- | :--- |
| `name` | **Yes** | 1–64 chars; lowercase alphanumeric + hyphens (`a-z`, `0-9`, `-`); no leading, trailing, or consecutive hyphens; **must match parent directory name**. |
| `description` | **Yes** | 1–1024 chars, non-empty. States what the skill does and when to trigger it. |
| `license` | No | License identifier (e.g., `MIT`, `Apache-2.0`) or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (target agents, packages, network access). |
| `metadata` | No | String-to-string map (e.g., `author`, `version`). |
| `allowed-tools` | No *(Experimental)* | Space-separated list of pre-approved tools. |

### Progressive Disclosure

1. **Tier 1 — Discovery (Startup):** Only `name` and `description` load (~50–100 tokens/skill).
2. **Tier 2 — Activation (On Trigger):** Full `SKILL.md` body loads. Keep it **under 500 lines** and **under 5,000 tokens**.
3. **Tier 3 — Execution (On Demand):** `references/`, `scripts/`, and `assets/` load or execute only when explicitly needed.

---

## 2. Best Practices

- **Concision is paramount:** The context window is a shared resource. Assume the model is capable; omit generic explanations and focus on domain-specific rules, workflows, and gotchas.
- **Ground in real workflows:** Capture concrete constraints, real edge cases, and observed failure modes rather than generic LLM-generated boilerplate.
- **Keep `references/` shallow and targeted:**
  - Store reference files one level deep (`references/<file>.md`) to avoid path/truncation issues.
  - Add a **Table of Contents** at the top of any reference file exceeding **100 lines**.
  - State explicit conditional triggers in `SKILL.md` for when to read each reference (e.g., *"Read `references/harness-patterns.md` when tailoring for Codex CLI"*), not vague hints.
- **Match degrees of freedom to fragility:** Use prose for judgment calls and `scripts/` for deterministic or error-prone steps.

---

## 3. Optimizing Descriptions

The `description` field is the router during Discovery. Write it as a **firing condition**, not a passive summary:

- **Use third person** and state both capability and trigger conditions clearly.
- **Include explicit "Use when" triggers:** Cover natural user phrasings, file types, and intents—even when the user omits technical jargon.
- **Include negative triggers / boundaries:** State what the skill does *not* handle to prevent false positives and cross-triggering with adjacent skills.
- **Test and iterate with `evals/trigger_queries.json`:**
  - Include `should_trigger: true` cases (diverse phrasings, implicit intent) and `should_trigger: false` cases (**near-misses** that share vocabulary but belong to another workflow).
  - Use a **~60/40 train/validation split** to avoid overfitting to test phrasings.
  - Broaden triggers for undertriggering (`should_trigger: true` misses); tighten boundaries for false positives (`should_trigger: false` hits).

---

## 4. Evals

Use dataset-driven evaluation instead of ad-hoc "vibe-testing":

- **Store test cases in `evals/evals.json`** (and input fixtures in `evals/files/`):
  ```json
  {
    "skill_name": "my-skill",
    "evals": [
      {
        "id": 1,
        "prompt": "Realistic user prompt with concrete paths/inputs",
        "expected_output": "Observable description of a passing result",
        "files": ["evals/files/sample.csv"]
      }
    ]
  }
  ```
- **Write verifiable assertions:** Target concrete, observable criteria (e.g., valid JSON, required sections, exact command usage) rather than vague judgments ("output is good").
- **Grade and benchmark:**
  - Combine deterministic checks (scripts/regex/schema validation) with rubric-based LLM-as-judge grading (`grading.json`, `timing.json`).
  - Aggregate pass rates, token usage, and latency into `benchmark.json`, comparing **with-skill** vs. **without-skill** (or prior versions) to catch regressions.

---

## 5. Using Scripts

Move repetitive, fragile, or deterministic operations into `scripts/` as small, self-contained CLIs:

- **Self-contained via PEP 723:** Declare Python dependencies inline so scripts run with `uv run` or `pipx run` without polluting the repo with `requirements.txt` or `pyproject.toml`:
  ```python
  #!/usr/bin/env python3
  # /// script
  # requires-python = ">=3.11"
  # dependencies = ["requests<3"]
  # ///
  ```
- **Non-interactive CLI design:** Accept CLI flags/arguments with clear `--help` output; never prompt for interactive `stdin` input (which hangs agent runs).
- **Explicit exit codes and diagnostics:** Return `0` on success and non-zero (`1`, `2`, etc.) on failure, printing actionable errors to `stderr`/`stdout` so the agent can diagnose and recover.
- **Avoid library bloat:** Keep each script focused on a single operational bottleneck.
