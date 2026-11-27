# Harness-Specific Prompting Patterns

Load this reference when tailoring a prompt for **Antigravity**, **OpenAI Codex CLI**, or **Anthropic Claude / Claude Code**, or when authoring persistent repository instruction files.

## Cross-Harness Persistent Files

| Harness | Primary Persistent File(s) | Scope / Discovery | Key Rule |
| :--- | :--- | :--- | :--- |
| **Antigravity** | `GEMINI.md`, `.agents/rules/*.md`, `SKILL.md` | Hierarchical CWD → repo root; skills load on demand | Layer recurring rules out of turn prompts |
| **Codex CLI** | `AGENTS.md` (root + nested) | Root → target directory (closest wins) | Omit facts discoverable from `package.json` / config |
| **Claude Code** | `CLAUDE.md` | Project root / subdirectories | Keep under ~200 lines; document non-obvious decisions |

---

## 1. Google Antigravity

Grounded in `antigravity.google/docs/learn/prompting/`:

- **Treat prompts as technical specs:** Include Goal, Scope & Inputs, Constraints, and Verification so the agent never guesses architecture or paths.
- **Layer instructions deliberately:**
  - **Turn prompt:** Task-specific goal, target files, and verification command for *this* change.
  - **Rules (`GEMINI.md` / `.agents/rules/`):** Always-on repo invariants (package manager, test commands, forbidden patterns).
  - **Skills (`SKILL.md`):** Multi-step procedures and domain workflows loaded only when relevant.

---

## 2. OpenAI Codex CLI

Codex operates as an autonomous coding teammate across long tool-use stretches:

- **No upfront planning chatter:** Do **not** instruct Codex to *"output a detailed step-by-step plan first"* or *"give frequent status updates"*. Unnecessary narration wastes tokens and can trigger premature halts before work finishes.
- **Specify 4 things concisely:** Goal, Context/entry points, Boundaries (what *not* to touch), and Verification command (e.g., `pnpm test --watch=false`).
- **`AGENTS.md` hygiene (Less is More):**
  - Do not duplicate stack/folder info Codex can read from `package.json`, `pyproject.toml`, or `Cargo.toml`.
  - Include only non-obvious setup commands, architectural invariants, generated-file warnings, and verification protocols.
  - In monorepos, use nested `AGENTS.md` files per package so the closest file overrides parent rules.

---

## 3. Anthropic Claude & Claude Code

Modern Claude models follow instructions literally and parse XML tags semantically:

- **Use semantic XML tags to separate data from directives:** Wrap code, logs, or reference docs in descriptive tags (`<context>`, `<logs>`, `<code_snippet>`, `<instructions>`).
- **Data first, instructions last:** For long-context prompts, place documents and data blocks at the top and put the explicit task/query at the bottom.
- **Explain the *why* behind constraints:** Replace bare prohibitions (*"NEVER use ellipses"*) with rationale (*"Never use ellipses because output is read aloud by a TTS engine"*).
- **Be explicit with action verbs and verbosity:** Say *"Refactor `parseConfig` to throw on missing keys"* rather than *"Suggest improvements to `parseConfig`"*. State output format constraints directly (e.g., *"Use prose paragraphs; reserve markdown for inline code"*).
- **Few-shot with `<example>` tags:** Provide 3–5 diverse examples inside `<example>` tags when exact format consistency is required.
- **`CLAUDE.md` hygiene:** Keep under ~200 lines; focus on invisible architectural "why" decisions, legacy anti-patterns *not* to copy, rules you repeatedly correct, and exact build/test/lint commands.
