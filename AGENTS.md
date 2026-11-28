# AGENTS.md

Guidance for authoring, evaluating, and maintaining [Agent Skills](https://agentskills.io/home.md) in this repository.

## Repository Layout

- Skills live under `skills/<skill-name>/` (see `skills/prompt-crafting/`).
- When adding a new skill, update the **Available Skills** table in `README.md`.

## Evaluation & Critique Rule (Mandatory)

> **Use a sub-agent critique only when creating a new skill or modifying an existing skill (`skills/<skill-name>/`).**
> Do not run a sub-agent critique for anything else (e.g., changes to `AGENTS.md`, `docs/`, or `README.md`). When creating or modifying a skill, spawn a dedicated sub-agent with fresh context to perform the critique rather than relying on self-review.

The critique sub-agent must load the relevant `docs/*.md` files before auditing and check: specification compliance, progressive disclosure & size budgets, description trigger precision/negative boundaries, script determinism/hygiene, and eval coverage.

## Core Rules

- **Keep `SKILL.md` lean:** Under 500 lines and 5,000 tokens. Keep `references/` one level deep with explicit conditional loading triggers.
- **Write `description` as a firing condition:** Third person, stating what the skill does, when to trigger it, and what it does *not* handle.
- **Use `scripts/` for deterministic steps:** Self-contained CLIs (PEP 723 for Python), non-interactive flags (no `stdin` prompts), and explicit exit codes.
- **Version every skill change:** Any modification under `skills/<skill-name>/` (including `evals/`) requires bumping `metadata.version` (`"X.Y.Z"`) and updating `README.md` and `CHANGELOG.md` via `uv run scripts/skill_version.py bump`.

## Reference Docs (Load on Demand)

| Read when... | File |
| :--- | :--- |
| Creating/restructuring a skill, checking frontmatter rules, or auditing progressive disclosure | [`docs/specification.md`](docs/specification.md) |
| Writing/optimizing a `description`, building `evals/trigger_queries.json`, or writing `evals/evals.json` | [`docs/descriptions-and-evals.md`](docs/descriptions-and-evals.md) |
| Adding or reviewing helper scripts in `scripts/` (PEP 723, CLI flags, exit codes) | [`docs/scripts.md`](docs/scripts.md) |
| Bumping skill versions, updating `CHANGELOG.md`, cutting tags, or reviewing PR bump rules | [`docs/versioning.md`](docs/versioning.md) |
