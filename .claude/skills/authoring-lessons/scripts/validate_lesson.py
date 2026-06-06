#!/usr/bin/env python3
"""Validate a lesson against the handbook's Definition of Done (structural part).

Checks that a lesson README:
  1. declares a valid **Type**;
  2. has a `## Prerequisites` section, and every LOCAL link in it points to an
     existing file (the dependency-graph edges must resolve);
  3. has a non-empty `## Sources` section;
  4. (practice / theory+practice) references runnable code — reported as a warning.

This is the mechanical half of the DoD. Semantic checks (claims actually backed,
uncertainty flagged, real output shown) stay with the author and the reviewer.

Usage:
    python validate_lesson.py <lesson-dir-or-README.md>

Exit code 0 if no errors (warnings allowed), 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_TYPES = {"theory", "theory+practice", "practice"}
_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _section(body: str, heading: str) -> str | None:
    """Return the text of a `## heading` section, or None if absent."""
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
    m = pat.search(body)
    return m.group(1) if m else None


def validate(target: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    readme = target / "README.md" if target.is_dir() else target
    if not readme.is_file():
        return [f"no README.md found at {readme}"], []

    body = readme.read_text(encoding="utf-8")
    lesson_dir = readme.parent

    # 1. Type
    m = re.search(r"\*\*Type:\*\*\s*([A-Za-z+]+)", body)
    if not m:
        errors.append("missing `**Type:**` declaration in the header")
        lesson_type = None
    elif m.group(1) not in VALID_TYPES:
        errors.append(f"invalid Type {m.group(1)!r}; expected one of {sorted(VALID_TYPES)}")
        lesson_type = None
    else:
        lesson_type = m.group(1)

    # 2. Prerequisites: section present, local links resolve
    prereqs = _section(body, "Prerequisites")
    if prereqs is None:
        errors.append("missing `## Prerequisites` section")
    else:
        for link in _LINK.findall(prereqs):
            if link.startswith(("http://", "https://", "#")):
                continue  # only local edges are part of the graph
            resolved = (lesson_dir / link).resolve()
            if not resolved.exists():
                errors.append(f"prerequisite link does not resolve: {link}")

    # 3. Sources: present and non-empty
    sources = _section(body, "Sources")
    if sources is None:
        errors.append("missing `## Sources` section")
    elif not _LINK.search(sources):
        errors.append("`## Sources` has no source links")

    # 4. Practice lessons should reference runnable code (warning)
    if lesson_type in {"practice", "theory+practice"}:
        code = list(lesson_dir.glob("*.py"))
        if not code:
            warnings.append(
                f"Type is {lesson_type!r} but no .py file found in {lesson_dir}/"
            )

    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    target = Path(sys.argv[1])
    errors, warnings = validate(target)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK: passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
