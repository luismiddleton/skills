#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
skill_version.py
Validate, bump, and tag Agent Skills in this repository using SemVer.

Commands:
  validate  Validate SKILL.md frontmatter, README.md, CHANGELOG.md, and PR bumps.
  bump      Increment a skill's metadata.version and sync README.md + CHANGELOG.md.
  tag       Create an annotated <skill>/vX.Y.Z git tag (and optional push/release).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
README_ROW_RE = re.compile(
    r"^\|\s*`(?P<name>[^`]+)`\s*\|\s*`(?P<version>[^`]+)`\s*\|(?P<rest>.*)$"
)
CHANGELOG_HEADING_RE = re.compile(r"^##\s+\[([^\]]+)\](?:\s*-\s*.*)?$")

BUMP_CHANGELOG_SECTION = {
    "major": "Changed",
    "minor": "Added",
    "patch": "Changed",
}


def parse_semver(version: str) -> tuple[int, int, int] | None:
    """Return a (major, minor, patch) tuple if valid strict SemVer, else None."""
    match = SEMVER_RE.fullmatch(version.strip())
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def split_frontmatter(content: str) -> tuple[str, str, str]:
    """Split a SKILL.md document into (line_ending, frontmatter_yaml, body)."""
    line_ending = "\r\n" if "\r\n" in content else "\n"
    normalized = content.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError("Missing opening YAML frontmatter delimiter '---'")
    end_idx = normalized.find("\n---\n", 4)
    if end_idx == -1:
        if normalized.endswith("\n---"):
            end_idx = len(normalized) - 4
            body = ""
        else:
            raise ValueError("Missing closing YAML frontmatter delimiter '---'")
    else:
        body = normalized[end_idx + 5 :]
    frontmatter = normalized[4:end_idx]
    return line_ending, frontmatter, body


def parse_skill_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content into a dictionary."""
    _, fm_text, _ = split_frontmatter(content)
    data = yaml.safe_load(fm_text)
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must deserialize to a YAML mapping")
    return data


def _parse_readme_versions(readme_path: Path) -> dict[str, str]:
    if not readme_path.is_file():
        return {}
    versions: dict[str, str] = {}
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        match = README_ROW_RE.match(line.strip())
        if match:
            versions[match.group("name")] = match.group("version")
    return versions


def _parse_changelog_sections(changelog_path: Path) -> dict[str, str]:
    if not changelog_path.is_file():
        return {}
    sections: dict[str, list[str]] = {}
    current_key: str | None = None
    for line in changelog_path.read_text(encoding="utf-8").splitlines():
        match = CHANGELOG_HEADING_RE.match(line.strip())
        if match:
            current_key = match.group(1)
            sections.setdefault(current_key, [])
        elif current_key is not None:
            sections[current_key].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def _validate_single_skill(skill_dir: Path) -> tuple[str | None, list[str]]:
    issues: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None, [f"{skill_dir.name}: missing SKILL.md"]

    try:
        data = parse_skill_frontmatter(skill_md.read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError) as exc:
        return None, [f"{skill_dir.name}: invalid SKILL.md frontmatter ({exc})"]

    name = data.get("name")
    if not isinstance(name, str) or not name:
        issues.append(f"{skill_dir.name}: frontmatter 'name' must be a non-empty string")
    else:
        if len(name) > 64 or not NAME_RE.fullmatch(name):
            issues.append(
                f"{skill_dir.name}: 'name' ({name!r}) must be 1-64 lowercase alphanumeric/hyphen chars"
            )
        if name != skill_dir.name:
            issues.append(
                f"{skill_dir.name}: 'name' ({name!r}) does not match directory name"
            )

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        issues.append(f"{skill_dir.name}: frontmatter 'description' must be a non-empty string")
    elif len(description) > 1024:
        issues.append(
            f"{skill_dir.name}: 'description' exceeds 1024 chars ({len(description)})"
        )

    compatibility = data.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or len(compatibility) > 500
    ):
        issues.append(f"{skill_dir.name}: 'compatibility' must be a string <= 500 chars")

    metadata = data.get("metadata")
    version: str | None = None
    if not isinstance(metadata, dict):
        issues.append(f"{skill_dir.name}: frontmatter 'metadata' mapping is required")
    else:
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                issues.append(
                    f"{skill_dir.name}: metadata.{key} must be a string (quote values like \"1.0.0\")"
                )
        raw_version = metadata.get("version")
        if not isinstance(raw_version, str):
            issues.append(
                f"{skill_dir.name}: metadata.version must be a quoted SemVer string (e.g. \"1.0.0\")"
            )
        elif parse_semver(raw_version) is None:
            issues.append(
                f"{skill_dir.name}: metadata.version ({raw_version!r}) is not valid SemVer X.Y.Z"
            )
        else:
            version = raw_version

    return version, issues


def _validate_base_ref_bumps(
    repo_root: Path, base_ref: str, current_versions: dict[str, str]
) -> list[str]:
    issues: list[str] = []
    diff_proc = _run_git(repo_root, "diff", "--name-only", f"{base_ref}...HEAD", "--", "skills/")
    if diff_proc.returncode != 0:
        diff_proc = _run_git(repo_root, "diff", "--name-only", base_ref, "HEAD", "--", "skills/")
    if diff_proc.returncode != 0:
        return [f"Failed to diff against base ref {base_ref!r}: {diff_proc.stderr.strip()}"]

    changed_skills: set[str] = set()
    for rel_path in diff_proc.stdout.splitlines():
        parts = Path(rel_path).parts
        if len(parts) >= 2 and parts[0] == "skills":
            changed_skills.add(parts[1])

    for skill_name in sorted(changed_skills):
        if skill_name not in current_versions:
            # Skill directory was removed in this branch.
            continue
        show_proc = _run_git(repo_root, "show", f"{base_ref}:skills/{skill_name}/SKILL.md")
        if show_proc.returncode != 0:
            # Newly added skill; valid SemVer in HEAD is sufficient.
            continue
        try:
            base_data = parse_skill_frontmatter(show_proc.stdout)
        except (ValueError, yaml.YAMLError):
            continue
        base_metadata = base_data.get("metadata")
        base_ver_raw = base_metadata.get("version") if isinstance(base_metadata, dict) else None
        if not isinstance(base_ver_raw, str):
            # Allow bootstrapping unversioned skills to initial SemVer.
            continue
        base_tuple = parse_semver(base_ver_raw)
        if base_tuple is None:
            # Allow normalizing legacy non-3-part strings (e.g. "1.0" -> "1.0.0").
            continue
        head_ver = current_versions[skill_name]
        head_tuple = parse_semver(head_ver)
        if head_tuple is not None and head_tuple <= base_tuple:
            issues.append(
                f"{skill_name}: files under skills/{skill_name}/ changed without bumping "
                f"metadata.version (base={base_ver_raw}, head={head_ver})"
            )
    return issues


def validate_repo(repo_root: Path, base_ref: str | None = None) -> tuple[dict[str, str], list[str]]:
    """Validate all skills, README.md, CHANGELOG.md, and optional base-ref bumps."""
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        return {}, [f"Missing skills directory at {skills_dir}"]

    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        return {}, ["No skill directories found under skills/"]

    issues: list[str] = []
    versions: dict[str, str] = {}
    readme_versions = _parse_readme_versions(repo_root / "README.md")
    changelog_sections = _parse_changelog_sections(repo_root / "CHANGELOG.md")

    for skill_dir in skill_dirs:
        version, skill_issues = _validate_single_skill(skill_dir)
        issues.extend(skill_issues)
        if version is None:
            continue
        name = skill_dir.name
        versions[name] = version

        readme_ver = readme_versions.get(name)
        if readme_ver is None:
            issues.append(f"{name}: missing from README.md Available Skills table")
        elif readme_ver != version:
            issues.append(
                f"{name}: README.md version ({readme_ver}) does not match SKILL.md ({version})"
            )

        tag_key = f"{name}/v{version}"
        if tag_key not in changelog_sections:
            issues.append(f"{name}: CHANGELOG.md missing heading '## [{tag_key}]'")

    if base_ref:
        issues.extend(_validate_base_ref_bumps(repo_root, base_ref, versions))

    return versions, issues


def _replace_frontmatter_version(skill_md_path: Path, new_version: str) -> None:
    content = skill_md_path.read_text(encoding="utf-8")
    line_ending, fm_text, body = split_frontmatter(content)

    lines = fm_text.split("\n")
    in_metadata = False
    metadata_indent = 0
    replaced = False

    for idx, line in enumerate(lines):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if not stripped or stripped.startswith("#"):
            continue
        if indent == 0 and stripped.startswith("metadata:"):
            in_metadata = True
            metadata_indent = indent
            continue
        if in_metadata:
            if indent <= metadata_indent:
                in_metadata = False
            elif re.match(r"^version:\s*", stripped):
                lines[idx] = f'{" " * indent}version: "{new_version}"'
                replaced = True
                break

    if not replaced:
        raise ValueError(f"Could not locate metadata.version line in {skill_md_path}")

    updated = f"---\n{chr(10).join(lines)}\n---\n{body}"
    if line_ending != "\n":
        updated = updated.replace("\n", line_ending)
    skill_md_path.write_text(updated, encoding="utf-8")


def _update_readme_version(readme_path: Path, skill_name: str, new_version: str) -> None:
    lines = readme_path.read_text(encoding="utf-8").splitlines(keepends=True)
    updated = False
    for idx, line in enumerate(lines):
        match = README_ROW_RE.match(line.strip())
        if match and match.group("name") == skill_name:
            ending = "\r\n" if line.endswith("\r\n") else ("\n" if line.endswith("\n") else "")
            lines[idx] = f"| `{skill_name}` | `{new_version}` |{match.group('rest')}{ending}"
            updated = True
            break
    if not updated:
        raise ValueError(f"Could not locate '{skill_name}' row in {readme_path}")
    readme_path.write_text("".join(lines), encoding="utf-8")


def _prepend_changelog_entry(
    changelog_path: Path, skill_name: str, new_version: str, bump_part: str, summary: str
) -> None:
    today = dt.date.today().isoformat()
    section_title = BUMP_CHANGELOG_SECTION[bump_part]
    entry = f"## [{skill_name}/v{new_version}] - {today}\n\n### {section_title}\n- {summary}\n"

    if not changelog_path.is_file():
        changelog_path.write_text(f"# Changelog\n\n{entry}", encoding="utf-8")
        return

    content = changelog_path.read_text(encoding="utf-8")
    match = re.search(r"^##\s+\[", content, flags=re.MULTILINE)
    if match:
        idx = match.start()
        updated = f"{content[:idx]}{entry}\n{content[idx:]}"
    else:
        sep = "" if content.endswith("\n\n") else ("\n" if content.endswith("\n") else "\n\n")
        updated = f"{content}{sep}{entry}"
    changelog_path.write_text(updated, encoding="utf-8")


def cmd_validate(args: argparse.Namespace) -> int:
    versions, issues = validate_repo(args.repo_root, base_ref=args.base_ref)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1
    summary = ", ".join(f"{name}={ver}" for name, ver in sorted(versions.items()))
    print(f"OK: validated {len(versions)} skill(s) ({summary})")
    return 0


def cmd_bump(args: argparse.Namespace) -> int:
    repo_root: Path = args.repo_root
    skill_name: str = args.skill
    skill_md = repo_root / "skills" / skill_name / "SKILL.md"
    if not skill_md.is_file():
        print(f"ERROR: Skill '{skill_name}' not found at {skill_md}", file=sys.stderr)
        return 1

    _, issues = _validate_single_skill(skill_md.parent)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    data = parse_skill_frontmatter(skill_md.read_text(encoding="utf-8"))
    current_ver = data["metadata"]["version"]
    parsed = parse_semver(current_ver)
    assert parsed is not None
    major, minor, patch = parsed

    if args.part == "major":
        next_ver = f"{major + 1}.0.0"
    elif args.part == "minor":
        next_ver = f"{major}.{minor + 1}.0"
    else:
        next_ver = f"{major}.{minor}.{patch + 1}"

    summary = args.summary or f"Bump {skill_name} to {next_ver}."
    _replace_frontmatter_version(skill_md, next_ver)
    _update_readme_version(repo_root / "README.md", skill_name, next_ver)
    _prepend_changelog_entry(repo_root / "CHANGELOG.md", skill_name, next_ver, args.part, summary)

    print(f"Bumped {skill_name}: {current_ver} -> {next_ver}")
    return 0


def _tag_exists(repo_root: Path, tag_name: str, check_remote: bool) -> bool:
    """Return True if tag exists locally or (when check_remote=True) on origin."""
    local_proc = _run_git(repo_root, "rev-parse", "-q", "--verify", f"refs/tags/{tag_name}")
    if local_proc.returncode == 0:
        return True
    if not check_remote:
        return False

    remote_proc = _run_git(
        repo_root, "ls-remote", "--exit-code", "--tags", "origin", f"refs/tags/{tag_name}"
    )
    if remote_proc.returncode == 0:
        return True
    if remote_proc.returncode == 2:
        return False
    raise RuntimeError(
        f"Failed to query origin tags for '{tag_name}': {remote_proc.stderr.strip()}"
    )


def _tag_and_release_skill(
    repo_root: Path,
    skill_name: str,
    version: str,
    changelog_sections: dict[str, str],
    *,
    push: bool,
    release: bool,
    dry_run: bool,
    skip_existing: bool,
) -> str | None:
    """Create (and optionally push/release) a <skill>/vX.Y.Z tag. Returns error message or None."""
    tag_name = f"{skill_name}/v{version}"
    check_remote = push or release or skip_existing
    try:
        exists = _tag_exists(repo_root, tag_name, check_remote=check_remote)
    except RuntimeError as exc:
        if not (push or release):
            # Local-only dry-run/tag without an origin remote: fall back to local check.
            exists = _tag_exists(repo_root, tag_name, check_remote=False)
        else:
            return str(exc)

    if exists:
        if skip_existing:
            print(f"SKIP: {tag_name} already exists")
            return None
        return f"Tag '{tag_name}' already exists"

    if dry_run:
        actions = [f"create tag {tag_name}"]
        if push or release:
            actions.append("push to origin")
        if release:
            actions.append("create GitHub Release")
        print(f"DRY-RUN: would {', '.join(actions)}")
        return None

    tag_proc = _run_git(repo_root, "tag", "-a", tag_name, "-m", f"Release {tag_name}")
    if tag_proc.returncode != 0:
        return f"git tag failed for {tag_name}: {tag_proc.stderr.strip()}"
    print(f"Created tag {tag_name}")

    if push or release:
        push_proc = _run_git(repo_root, "push", "origin", tag_name)
        if push_proc.returncode != 0:
            return f"git push failed for {tag_name}: {push_proc.stderr.strip()}"
        print(f"Pushed tag {tag_name} to origin")

    if release:
        notes = changelog_sections.get(tag_name, "")
        gh_cmd = ["gh", "release", "create", tag_name, "--title", tag_name]
        if notes:
            gh_cmd.extend(["--notes", notes])
        else:
            gh_cmd.append("--generate-notes")
        gh_proc = subprocess.run(
            gh_cmd, cwd=str(repo_root), text=True, capture_output=True, check=False
        )
        if gh_proc.returncode != 0:
            return f"gh release create failed for {tag_name}: {gh_proc.stderr.strip()}"
        print(f"Created GitHub Release for {tag_name}")

    return None


def cmd_tag(args: argparse.Namespace) -> int:
    repo_root: Path = args.repo_root
    if not args.dry_run:
        status_proc = _run_git(repo_root, "status", "--porcelain")
        if status_proc.returncode != 0:
            print(f"ERROR: git status failed: {status_proc.stderr.strip()}", file=sys.stderr)
            return 1
        if status_proc.stdout.strip():
            print("ERROR: Working tree is dirty; commit changes before tagging.", file=sys.stderr)
            return 1

    versions, issues = validate_repo(repo_root)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    if args.all:
        targets = sorted(versions.keys())
    else:
        if args.skill not in versions:
            print(f"ERROR: Unknown skill '{args.skill}'", file=sys.stderr)
            return 1
        targets = [args.skill]

    changelog_sections = _parse_changelog_sections(repo_root / "CHANGELOG.md")
    for skill_name in targets:
        err = _tag_and_release_skill(
            repo_root,
            skill_name,
            versions[skill_name],
            changelog_sections,
            push=args.push,
            release=args.release,
            dry_run=args.dry_run,
            skip_existing=args.all,
        )
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Validate, bump, and tag Agent Skills in this repository."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_root,
        help="Repository root directory (defaults to parent of scripts/).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_val = subparsers.add_parser("validate", help="Validate skills, README.md, and CHANGELOG.md.")
    p_val.add_argument(
        "--base-ref",
        default=None,
        help="Git base ref to enforce SemVer bumps for any modified skill directories.",
    )
    p_val.set_defaults(func=cmd_validate)

    p_bump = subparsers.add_parser(
        "bump", help="Bump a skill's metadata.version and sync README.md and CHANGELOG.md."
    )
    p_bump.add_argument("skill", help="Skill directory name under skills/.")
    p_bump.add_argument("part", choices=("major", "minor", "patch"), help="SemVer part to bump.")
    p_bump.add_argument("--summary", default="", help="Changelog bullet summary for this release.")
    p_bump.set_defaults(func=cmd_bump)

    p_tag = subparsers.add_parser("tag", help="Create annotated <skill>/vX.Y.Z git tags.")
    tag_target = p_tag.add_mutually_exclusive_group(required=True)
    tag_target.add_argument("skill", nargs="?", help="Skill directory name under skills/.")
    tag_target.add_argument(
        "--all",
        action="store_true",
        help="Tag all skills whose current version is not yet tagged.",
    )
    p_tag.add_argument("--push", action="store_true", help="Push created tags to origin.")
    p_tag.add_argument(
        "--release",
        action="store_true",
        help="Push tags and create GitHub Releases via gh CLI.",
    )
    p_tag.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned tag/release actions without mutating git or GitHub.",
    )
    p_tag.set_defaults(func=cmd_tag)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
