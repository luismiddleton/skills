---
name: prompt-crafting
description: >-
  Use this skill whenever the user asks to write, improve, critique, debug, or
  structure a prompt, system prompt, task specification, or persistent agent
  instruction file (GEMINI.md, AGENTS.md, CLAUDE.md)—or when tailoring prompts
  for Antigravity, Codex, or Claude. Trigger even if they don't mention "prompt
  engineering" explicitly (e.g., "help me ask the AI to...", "make this prompt
  better", "why does the model keep ignoring my instructions?").
metadata:
  author: Luis Middleton
  version: "1.0"
---

# Prompt Crafting

Transform rough ideas or underperforming instructions into concrete, verifiable prompts tailored to the task type and target harness.

## 1. Ask vs. Draft Directly

Before drafting, check whether the request has enough signal:
- **Draft immediately** if the goal, target audience/model, and core constraints are clear or can be safely inferred. State any assumptions after the prompt.
- **Ask 2–3 targeted questions first** only if the goal is ambiguous or critical inputs are missing (e.g., unknown target harness, missing success criteria, or unclear output format). Never interrogate the user with a long questionnaire.

## 2. Select the Framework (Defaults, Not Menus)

Pick one primary framework based on the task:

| Task Type | Default Framework | Core Elements |
| :--- | :--- | :--- |
| **Coding, debugging, or agentic tasks** | **Antigravity 4-Part Spec** | Goal, Scope & Inputs, Constraints, Verification |
| **Copywriting, emails, stakeholder comms, persona tasks** | **CRAFT** | Context, Role, Action, Format, Target / Tone |
| **Multi-step workflows, analysis, strict schemas, or before/after examples** | Load [`references/frameworks.md`](./references/frameworks.md) | RISEN, CO-STAR, Few-Shot / CoT, and examples |

## 3. Check Target Harness & Instruction Layering

- **Target Harness:** Default to harness-agnostic structure unless the user specifies **Antigravity**, **Codex**, or **Claude / Claude Code**, or asks to author persistent repo instructions (`GEMINI.md`, `AGENTS.md`, `CLAUDE.md`).
- **Load [`references/harness-patterns.md`](./references/harness-patterns.md)** whenever:
  1. Tailoring a prompt for **Antigravity**, **Codex CLI**, or **Claude / Claude Code**.
  2. Deciding whether an instruction belongs in a **one-off turn prompt**, **persistent rules** (`GEMINI.md`, `AGENTS.md`, `CLAUDE.md`), or a **reusable skill** (`SKILL.md`).

## 4. Crafting Workflow

Follow this sequence for every prompt-crafting request:

1. **Diagnose gaps:** Identify what makes the current draft weak—vague verbs ("fix", "improve"), missing file/data scope, unstated constraints, or no verification check.
2. **Choose framework & harness:** Apply the default framework from Section 2 and any harness rules from [`references/harness-patterns.md`](./references/harness-patterns.md).
3. **Draft the prompt:** Write a self-contained, copyable prompt inside a fenced code block. Replace generic advice ("handle errors properly") with concrete specs ("return 400 JSON with `{ error }` on invalid input").
4. **Add verification (for task/agent prompts):** Include an explicit check the agent or user can run to prove success (test command, schema check, viewport check, or acceptance criteria).
5. **Present the result:** Format your response using the Output Template (Section 6).

## 5. Gotchas

- **Don't use CRAFT's Role/Tone for coding tasks:** Telling a coding agent *"You are a 10x senior engineer, be professional"* wastes tokens. Use **Scope & Inputs** (exact file paths, helpers to reuse) and **Verification** (exact test/lint commands) instead.
- **Don't ask Codex for upfront planning chatter:** In Codex CLI prompts, avoid *"First explain your plan step by step and give status updates"*; it burns tokens and can trigger premature halts.
- **Don't leave Claude constraints unexplained:** Modern Claude models interpret rules literally; state *why* a constraint exists (e.g., *"no markdown tables because output goes to a plain-text Slack webhook"*).
- **Don't mix data and instructions:** For long inputs, logs, or documents, wrap data in XML tags (`<inputs>`, `<logs>`) or fenced blocks and place instructions after the data.
- **Don't repeat repo-wide rules in turn prompts:** If a constraint applies to every task in a repo (package manager, test runner, style rule), recommend putting it in `GEMINI.md`, `AGENTS.md`, or `CLAUDE.md` rather than every prompt.

## 6. Output Template

Use this structure for single-prompt drafting; for critiques or persistent instruction files, replace `### Tailored Prompt` with `### Diagnosis` or `### Proposed Rules` as appropriate:

````markdown
### Tailored Prompt
> Framework: [e.g., Antigravity 4-Part / CRAFT] | Target: [e.g., Codex CLI / Claude / General]

```text
[Ready-to-paste prompt]
```

### Why This Works
- [1–3 concise bullets explaining key improvements or assumptions made]

### Optional Refinements
- [1–2 targeted ways to adapt it further if needed]
````
