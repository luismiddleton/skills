"""Unit tests for scripts/skill_version.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import skill_version  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _init_sample_repo(root: Path, version_line: str = '  version: "1.0.0"') -> None:
    skill_dir = root / "skills" / "alpha-skill"
    (skill_dir / "evals").mkdir(parents=True, exist_ok=True)
    (skill_dir / "evals" / "evals.json").write_text('{"evals": []}\n', encoding="utf-8")

    meta_block = f"metadata:\n  author: Test\n{version_line}\n" if version_line else ""
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: alpha-skill\n"
        "description: >-\n"
        "  Handle alpha workflows.\n"
        f"{meta_block}"
        "---\n\n"
        "# Alpha Skill\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Skills\n\n"
        "| Skill | Version | Description | Location |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| `alpha-skill` | `1.0.0` | Alpha | [`skills/alpha-skill/`](./skills/alpha-skill/SKILL.md) |\n",
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n"
        "## [alpha-skill/v1.0.0] - 2026-11-28\n\n"
        "### Added\n"
        "- Initial baseline.\n",
        encoding="utf-8",
    )


class SkillVersionTests(unittest.TestCase):
    def test_validate_passes_on_valid_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_sample_repo(root)
            versions, issues = skill_version.validate_repo(root)
            self.assertEqual(issues, [])
            self.assertEqual(versions, {"alpha-skill": "1.0.0"})

    def test_validate_rejects_unquoted_float_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_sample_repo(root, version_line="  version: 1.0")
            _, issues = skill_version.validate_repo(root)
            self.assertTrue(any("must be a string" in msg for msg in issues))
            self.assertTrue(any("must be a quoted SemVer string" in msg for msg in issues))

    def test_bump_preserves_folded_description_and_syncs_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_sample_repo(root)
            rc = skill_version.main(
                [
                    "--repo-root",
                    str(root),
                    "bump",
                    "alpha-skill",
                    "patch",
                    "--summary",
                    "Add eval case.",
                ]
            )
            self.assertEqual(rc, 0)
            skill_text = (root / "skills" / "alpha-skill" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("description: >-\n  Handle alpha workflows.", skill_text)
            self.assertIn('  version: "1.0.1"', skill_text)
            self.assertIn("## [alpha-skill/v1.0.1]", (root / "CHANGELOG.md").read_text(encoding="utf-8"))
            versions, issues = skill_version.validate_repo(root)
            self.assertEqual(issues, [])
            self.assertEqual(versions, {"alpha-skill": "1.0.1"})

    def test_base_ref_requires_bump_even_for_evals_only_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_sample_repo(root)
            _git(root, "init", "-b", "main")
            _git(root, "config", "user.name", "Test")
            _git(root, "config", "user.email", "test@example.com")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "chore: initial")
            _git(root, "checkout", "-b", "feat/eval-update")

            (root / "skills" / "alpha-skill" / "evals" / "evals.json").write_text(
                '{"evals": [{"id": 1}]}\n', encoding="utf-8"
            )
            _git(root, "add", ".")
            _git(root, "commit", "-m", "test: add eval case")

            _, issues_unbumped = skill_version.validate_repo(root, base_ref="main")
            self.assertTrue(
                any("without bumping metadata.version" in msg for msg in issues_unbumped)
            )

            rc = skill_version.main(
                [
                    "--repo-root",
                    str(root),
                    "bump",
                    "alpha-skill",
                    "patch",
                    "--summary",
                    "Add eval case.",
                ]
            )
            self.assertEqual(rc, 0)
            _, issues_bumped = skill_version.validate_repo(root, base_ref="main")
            self.assertEqual(issues_bumped, [])

    def test_base_ref_allows_legacy_normalization_to_1_0_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_sample_repo(root, version_line='  version: "1.0"')
            _git(root, "init", "-b", "main")
            _git(root, "config", "user.name", "Test")
            _git(root, "config", "user.email", "test@example.com")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "chore: legacy 1.0")
            _git(root, "checkout", "-b", "feat/normalize")

            _init_sample_repo(root, version_line='  version: "1.0.0"')
            _git(root, "add", ".")
            _git(root, "commit", "-m", "chore: normalize to 1.0.0")

            _, issues = skill_version.validate_repo(root, base_ref="main")
            self.assertEqual(issues, [])

    def test_tag_creates_slash_namespaced_annotated_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_sample_repo(root)
            _git(root, "init", "-b", "main")
            _git(root, "config", "user.name", "Test")
            _git(root, "config", "user.email", "test@example.com")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "chore: initial")

            rc = skill_version.main(["--repo-root", str(root), "tag", "alpha-skill"])
            self.assertEqual(rc, 0)
            tags = subprocess.run(
                ["git", "-C", str(root), "tag", "-l"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
            self.assertEqual(tags, ["alpha-skill/v1.0.0"])


if __name__ == "__main__":
    unittest.main()
