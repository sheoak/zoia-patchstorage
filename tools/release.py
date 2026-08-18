#!/usr/bin/env python3
"""Per-patch versions, derived from the commits that touched each patch.

A tag points at a commit, which in a monorepo means the whole tree — so the
version lives in the patch's own directory instead. `VERSION` is the number on
its own, for anything that wants to read it cheaply; `CHANGELOG.md` is the same
number with what changed under it.

Which patches move is decided by the files a commit touched, not by its scope:
a commit can say `fix(hierophant)` and edit the wrong directory, and the files
are the thing that is true. How far they move is decided by the type.

    ./tools/release.py            write VERSION and CHANGELOG where they are due
    ./tools/release.py --check    say what is due, write nothing
    ./tools/release.py --lint     check the commit messages of a range
    ./tools/release.py --lint-msg FILE   check one message, for a commit hook

Note this reads commit messages, not the pedal. A `fix:` you have not played is
still a bump, so the number says "this changed", never "this is good".
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCHES = ROOT / "patches"

FIRST_VERSION = "0.1.0"

# Conventional commits, with the `!` that marks a break.
SUBJECT = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<break>!)?: (?P<summary>.+)$")

# Only these move the number. The rest are housekeeping and say so.
BUMPS = {"feat": "minor", "fix": "patch", "perf": "patch"}
TYPES = set(BUMPS) | {"docs", "style", "refactor", "test", "build", "ci", "chore", "revert"}

HEADINGS = {"feat": "Added", "fix": "Fixed", "perf": "Changed"}

# Written by this tool; a commit that only touches them is not a change to the
# patch, or every release would earn another one.
GENERATED = {"VERSION", "CHANGELOG.md"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def commits_since_release(name: str) -> list[tuple[str, str]]:
    """Commits touching this patch since its VERSION was last written."""
    version_file = f"patches/{name}/VERSION"
    boundary = git("log", "-1", "--format=%H", "--", version_file)

    span = [f"{boundary}..HEAD"] if boundary else []
    log = git("log", *span, "--format=%H%x00%s", "--", f"patches/{name}")
    if not log:
        return []

    out = []
    for line in log.split("\n"):
        sha, _, subject = line.partition("\x00")
        touched = git("show", "--name-only", "--format=", sha).split("\n")
        # A commit that only rewrote the changelog is not a change to the patch.
        real = [
            path for path in touched
            if path.startswith(f"patches/{name}/") and Path(path).name not in GENERATED
        ]
        if real:
            out.append((sha, subject))
    return out


def bump(current: str, level: str) -> str:
    major, minor, patch = (int(part) for part in current.split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def level_for(subjects: list[str]) -> str | None:
    level = None
    for subject in subjects:
        match = SUBJECT.match(subject)
        if not match:
            continue
        if match["break"] or "BREAKING CHANGE" in subject:
            return "major"
        candidate = BUMPS.get(match["type"])
        if candidate == "minor":
            level = "minor"
        elif candidate == "patch" and level is None:
            level = "patch"
    return level


def entry(version: str, subjects: list[str]) -> str:
    sections: dict[str, list[str]] = {}
    for subject in subjects:
        match = SUBJECT.match(subject)
        if not match or match["type"] not in HEADINGS:
            continue
        heading = "Changed" if match["break"] else HEADINGS[match["type"]]
        summary = match["summary"]
        sections.setdefault(heading, []).append(summary[0].upper() + summary[1:])

    lines = [f"## [{version}] — {date.today().isoformat()}", ""]
    for heading in ("Added", "Changed", "Fixed"):
        if heading not in sections:
            continue
        lines.append(f"### {heading}")
        lines += [f"- {line}" for line in sections[heading]]
        lines.append("")
    return "\n".join(lines)


def exempt(subject: str) -> bool:
    """A merge or a revert is written by git, not by a person, so it is let by.

    On a pull request GitHub checks out the merge commit rather than the branch
    tip, so without this every PR fails on a subject nobody typed.
    """
    return subject.startswith("Merge ") or subject.startswith("Revert ")


def lint(revision_range: str) -> int:
    log = git("log", revision_range, "--format=%H%x00%s")
    problems = []
    for line in filter(None, log.split("\n")):
        sha, _, subject = line.partition("\x00")
        if exempt(subject):
            continue
        match = SUBJECT.match(subject)
        if not match:
            problems.append(f"{sha[:8]} not a conventional commit: {subject}")
        elif match["type"] not in TYPES:
            problems.append(f"{sha[:8]} unknown type {match['type']!r}: {subject}")

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(f"\nExpected `type(scope): summary`, type one of {', '.join(sorted(TYPES))}.",
              file=sys.stderr)
    return 1 if problems else 0


def lint_message(text: str) -> int:
    subject = text.strip().split("\n")[0]
    if exempt(subject):
        return 0

    match = SUBJECT.match(subject)
    if match and match["type"] in TYPES:
        return 0

    print(f"not a conventional commit: {subject}", file=sys.stderr)
    print(f"Expected `type(scope): summary`, type one of {', '.join(sorted(TYPES))}.",
          file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    if "--lint-msg" in argv:
        return lint_message(Path(argv[argv.index("--lint-msg") + 1]).read_text())

    if "--lint" in argv:
        index = argv.index("--lint")
        return lint(argv[index + 1] if len(argv) > index + 1 else "origin/main..HEAD")

    dry = "--check" in argv
    moved = False

    for directory in sorted(p for p in PATCHES.iterdir() if p.is_dir()):
        name = directory.name
        history = commits_since_release(name)
        if not history:
            continue

        subjects = [subject for _, subject in history]
        level = level_for(subjects)
        version_file = directory / "VERSION"
        current = version_file.read_text().strip() if version_file.exists() else None

        if level is None and current:
            print(f"{name}: {len(history)} commit(s), nothing that moves the number")
            continue

        version = bump(current, level) if current else FIRST_VERSION
        moved = True
        print(f"{name}: {current or '—'} -> {version}  ({len(history)} commit(s))")
        if dry:
            continue

        version_file.write_text(f"{version}\n")
        changelog = directory / "CHANGELOG.md"
        previous = changelog.read_text() if changelog.exists() else f"# {name}\n"
        header, _, rest = previous.partition("\n\n")
        changelog.write_text(
            f"{header.rstrip()}\n\n{entry(version, subjects)}\n{rest}".rstrip() + "\n"
        )

    if not moved:
        print("nothing to release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
