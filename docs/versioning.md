# Skill Versioning & Releases

Reference for Semantic Versioning (SemVer), changelog entries, git tagging, and consumer version pinning across skills in this repository.

## Version Storage (`SKILL.md`)

Per the [Agent Skills specification](https://agentskills.io/specification.md), `SKILL.md` has no top-level `version` field; `metadata` is an arbitrary **string-to-string** map. Every skill in this repository must declare a quoted 3-part SemVer string under `metadata.version`:

```yaml
metadata:
  author: Luis Middleton
  version: "1.0.0"
```

Always quote the version string so YAML does not parse values like `1.0` as floats.

## SemVer Contract

- **`MAJOR` (`X.0.0`):** Breaking changes to a skill's contract or interface—renaming the skill, changing `scripts/` CLI flags or output schemas, removing workflows/capabilities, or shifting trigger boundaries in a breaking way.
- **`MINOR` (`0.Y.0`):** Backward-compatible additions—new workflows, frameworks, `references/`, `assets/`, or expanded trigger coverage.
- **`PATCH` (`0.0.Z`):** Fixes and non-breaking improvements—wording clarity, typo fixes, script bug fixes, `description` tuning, and **`evals/` additions or updates**.

> **Strict Bump Policy:** Every pull request modifying any file under `skills/<skill-name>/` (including `evals/`-only changes) must increment `metadata.version` and add a matching entry in the root [`CHANGELOG.md`](../CHANGELOG.md).

## Tags & Root Changelog

- **Git tags:** Slash-namespaced per skill: `<skill-name>/vX.Y.Z` (e.g., `prompt-crafting/v1.0.0`).
- **Changelog:** All release notes live in the root [`CHANGELOG.md`](../CHANGELOG.md) rather than inside `skills/<skill-name>/`, keeping installed skill directories lean for consumers. Each entry uses the heading `## [<skill-name>/vX.Y.Z] - YYYY-MM-DD`.

## Release Workflow (`scripts/skill_version.py`)

Use the PEP 723 CLI at [`scripts/skill_version.py`](../scripts/skill_version.py):

```bash
# 1. Bump a skill's metadata.version, README.md table, and CHANGELOG.md
uv run scripts/skill_version.py bump prompt-crafting patch --summary "Expand trigger eval coverage"

# 2. Validate all skills (pass --base-ref origin/main to check PR bump requirements)
uv run scripts/skill_version.py validate --base-ref origin/main

# 3. After merging to main, create (and optionally push/release) the git tag
uv run scripts/skill_version.py tag prompt-crafting --push --release
```

## Pinning Versions (`npx skills`)

Because slash-namespaced tags contain `/`, quote the full GitHub tree URL when pinning a release with `npx skills`:

```bash
npx skills add "https://github.com/luismiddleton/skills/tree/prompt-crafting/v1.0.0/skills/prompt-crafting"
```

Projects can lock and restore exact skill states reproducibly via `skills-lock.json` (`npx skills experimental_install --frozen-lockfile`).
