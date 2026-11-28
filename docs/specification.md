# Specification & Best Practices

Reference for the [Agent Skills specification](https://agentskills.io/home) and structural best practices.

## Directory Layout

```text
<skill-name>/
├── SKILL.md        # Required: YAML frontmatter + Markdown instructions
├── scripts/        # Optional: Executable helper CLIs
├── references/     # Optional: Deep docs, schemas, or examples (1 level deep)
├── assets/         # Optional: Templates, static files, or schemas used in output
└── evals/          # Optional: Trigger queries, test cases, and fixtures
```

## YAML Frontmatter (`SKILL.md`)

| Field | Required | Constraints |
| :--- | :--- | :--- |
| `name` | **Yes** | 1–64 chars; lowercase alphanumeric + hyphens (`a-z`, `0-9`, `-`); no leading, trailing, or consecutive hyphens; **must match parent directory name**. |
| `description` | **Yes** | 1–1024 chars, non-empty. States what the skill does and when to trigger it. |
| `license` | No | License identifier (e.g., `MIT`, `Apache-2.0`) or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (target agents, packages, network access). |
| `metadata` | No | String-to-string map (e.g., `author`, `version`). |
| `allowed-tools` | No *(Experimental)* | Space-separated list of pre-approved tools. |

## Progressive Disclosure

1. **Tier 1 — Discovery (Startup):** Only `name` and `description` load (~50–100 tokens/skill).
2. **Tier 2 — Activation (On Trigger):** Full `SKILL.md` body loads. Keep it **under 500 lines** and **under 5,000 tokens**.
3. **Tier 3 — Execution (On Demand):** `references/`, `scripts/`, and `assets/` load or execute only when explicitly needed.

## Best Practices

- **Concision is paramount:** The context window is a shared resource. Assume the model is capable; omit generic explanations and focus on domain-specific rules, workflows, and gotchas.
- **Ground in real workflows:** Capture concrete constraints, real edge cases, and observed failure modes rather than generic LLM-generated boilerplate.
- **Keep `references/` shallow and targeted:**
  - Store reference files one level deep (`references/<file>.md`) to avoid path/truncation issues.
  - Add a **Table of Contents** at the top of any reference file exceeding **100 lines**.
  - State explicit conditional triggers in `SKILL.md` for when to read each reference (e.g., *"Read `references/harness-patterns.md` when tailoring for Codex CLI"*), not vague hints.
- **Match degrees of freedom to fragility:** Use prose for judgment calls and `scripts/` for deterministic or error-prone steps.
