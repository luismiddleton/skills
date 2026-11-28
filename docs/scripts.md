# Using Scripts

Reference for bundling executable helpers under `scripts/`.

## Guidelines

- **Use scripts for deterministic or fragile steps:** Move repetitive parsing, formatting, validation, or API calls out of prose and into small, self-contained CLIs.
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
