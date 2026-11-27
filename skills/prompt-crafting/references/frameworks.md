# Prompt Engineering Frameworks

Load this reference when crafting prompts for multi-step workflows, analytical writing, structured extraction, or when you need concrete before/after examples of CRAFT and Antigravity 4-Part.

## 1. Antigravity 4-Part Spec (Coding & Agentic Tasks)

Best for: bug fixes, feature implementation, refactoring, and CLI/IDE agent tasks.

| Part | What to Specify | Example |
| :--- | :--- | :--- |
| **Goal** | Exact outcome to achieve | Add token-bucket rate limiting to `POST /api/export`. |
| **Scope & Inputs** | Files, modules, helpers, or logs to use/ignore | Edit `src/routes/export.ts`; reuse `createLimiter` in `src/lib/limiter.ts`. |
| **Constraints** | Boundaries, libraries to avoid, invariants | Do not add new npm dependencies. Keep 429 responses JSON-formatted. |
| **Verification** | Repeatable command or check proving success | Add unit tests for burst & window reset, then run `pnpm test export`. |

**Vague vs. Concrete:**
- *Vague:* "Fix the search page so it works better on mobile."
- *Concrete:* "Fix horizontal overflow on the search results table below 480px in `src/styles/search.scss` without changing desktop column widths. Verify at 390px viewport width."

---

## 2. CRAFT (Communication, Copy & Persona Tasks)

Best for: emails, marketing copy, stakeholder updates, documentation, and creative writing.

- **C — Context:** Background situation and why the task exists.
- **R — Role:** Expert persona or perspective to adopt.
- **A — Action:** Exact deliverable and verb (draft, rewrite, summarize).
- **F — Format:** Structural layout (word count, bullets, subject line, JSON).
- **T — Target / Tone:** Who will read it (audience) and how it should sound (voice).

**Example:**
- *Rough:* "Write an email about our new eco-shipping option."
- *CRAFT:*
  - **Context:** We are a 3PL logistics provider launching 100% carbon-neutral routing for Shopify brands next month.
  - **Role:** High-converting B2B SaaS/logistics email copywriter.
  - **Action:** Write an outreach email introducing the feature to prospective merchants.
  - **Format:** Subject line + 3 short paragraphs + 3-bullet cost-savings summary + CTA button text.
  - **Target / Tone:** E-commerce ops managers skeptical of greenwashing; direct, data-backed, zero fluff.

---

## 3. Specialized Frameworks (Tie-Breakers)

Choose one of these only when Antigravity 4-Part or CRAFT doesn't fit:

| Need | Use | Why / Key Pattern |
| :--- | :--- | :--- |
| **Repeatable multi-step agent workflow or system prompt** | **RISEN** | Role, Instructions, **Steps** (ordered gates), End Goal, **Narrowing** (hard exclusions). |
| **Analytical report, RFC, or editorial comparison** | **CO-STAR** | Context, Objective, **Style**, Tone, **Audience**, Response schema. |
| **Strict JSON/schema output, classification, or grading** | **Few-Shot + Scratchpad** | 3–5 diverse `<example>` pairs (including 1 edge case) + `<scratchpad>` reasoning before final answer. |

### RISEN Example (Triage Workflow)
- **Role:** Incident triage assistant.
- **Instructions:** Classify incoming bug reports by severity and route to the owning team.
- **Steps:** (1) Extract stack trace & affected endpoint; (2) Match endpoint to `CODEOWNERS`; (3) Assign P0–P3 using the rubric below.
- **End Goal:** Output a single JSON object `{ severity, owner, summary }`.
- **Narrowing:** Never invent stack frames or owners not present in the input; use `"unassigned"` if no match exists.
