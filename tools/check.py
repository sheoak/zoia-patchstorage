#!/usr/bin/env python3
"""Structural checks over the patch tree.

Deliberately shallow: a ZOIA patch is a fixed-size binary, so most of what can
go wrong is a file that never made it off the SD card whole, or a directory
somebody added without saying what is in it. Decoding the format needs the
editing skill, which is private, so CI does not attempt it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCHES = ROOT / "patches"

# A ZOIA patch is exactly 32 KiB, always.
PATCH_BYTES = 32768

# A tag would cover the whole tree, so each patch carries its own number.
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def main() -> int:
    problems: list[str] = []

    if not PATCHES.is_dir():
        print("no patches/ directory", file=sys.stderr)
        return 1

    directories = sorted(p for p in PATCHES.iterdir() if p.is_dir())

    if not directories:
        problems.append("patches/ is empty")

    for directory in directories:
        name = directory.name
        bins = sorted(directory.glob("*.bin"))

        if not bins:
            problems.append(f"{name}: no .bin")

        for binary in bins:
            size = binary.stat().st_size
            if size != PATCH_BYTES:
                problems.append(
                    f"{name}/{binary.name}: {size} bytes, expected {PATCH_BYTES}"
                )

        version = directory / "VERSION"
        if not version.is_file():
            problems.append(f"{name}: no VERSION")
        elif not VERSION.match(version.read_text().strip()):
            problems.append(
                f"{name}/VERSION: {version.read_text().strip()!r}, expected major.minor.patch"
            )

        if name != name.lower() or " " in name:
            problems.append(f"{name}: directory names are lower case, no spaces")

    for stray in sorted(PATCHES.glob("*.bin")):
        problems.append(f"{stray.name}: loose in patches/, give it a directory")

    for problem in problems:
        print(problem, file=sys.stderr)

    print(f"{len(directories)} patches checked")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
