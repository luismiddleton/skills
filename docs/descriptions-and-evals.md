# Optimizing Descriptions & Evals

Reference for tuning skill discovery (`description`) and running dataset-driven evaluations (`evals/`).

## Optimizing Descriptions

The `description` field is the router during Discovery. Write it as a **firing condition**, not a passive summary:

- **Use third person** and state both capability and trigger conditions clearly.
- **Include explicit "Use when" triggers:** Cover natural user phrasings, file types, and intents—even when the user omits technical jargon.
- **Include negative triggers / boundaries:** State what the skill does *not* handle to prevent false positives and cross-triggering with adjacent skills.
- **Test and iterate with `evals/trigger_queries.json`:**
  - Include `should_trigger: true` cases (diverse phrasings, implicit intent) and `should_trigger: false` cases (**near-misses** that share vocabulary but belong to another workflow).
  - Use a **~60/40 train/validation split** to avoid overfitting to test phrasings.
  - Broaden triggers for undertriggering (`should_trigger: true` misses); tighten boundaries for false positives (`should_trigger: false` hits).

## Evals

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

## References

- [Optimizing Descriptions](https://agentskills.io/skill-creation/optimizing-descriptions.md)
- [Evaluating Skills](https://agentskills.io/skill-creation/evaluating-skills.md)
