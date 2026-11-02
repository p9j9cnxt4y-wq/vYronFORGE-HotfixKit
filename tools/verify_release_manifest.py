#!/usr/bin/env python3
"""Check immutable tracked source manifest; fail on missing/changed/unlisted tracked files."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "SHA256SUMS.txt"
SKIP = {".git", ".venv", ".pytest_cache", "__pycache__", "build", "dist"}
GENERATED = {Path("evidence/ci-report.json")}


def inventory():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in ROOT.rglob("*") if p.is_file() and not p.is_symlink()
            and not set(p.relative_to(ROOT).parts).intersection(SKIP)
            and not any(x.endswith(".egg-info") for x in p.relative_to(ROOT).parts)
            and p.relative_to(ROOT) not in GENERATED
            and p != MANIFEST}


def verify():
    expected = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        if "  " not in line:
            raise ValueError("INVALID_HASH_MANIFEST_FORMAT")
        digest, rel = line.split("  ", 1)
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("INVALID_HASH_DIGEST")
        if rel in expected:
            raise ValueError("DUPLICATE_MANIFEST_ENTRY")
        expected[rel] = digest
    current = inventory()
    if current != expected:
        raise ValueError("RELEASE_SOURCE_MANIFEST_MISMATCH")
    return len(expected)


if __name__ == "__main__":
    try:
        print(f"RELEASE_MANIFEST=PASS files={verify()}")
    except (OSError, ValueError) as exc:
        print(f"RELEASE_MANIFEST=FAIL class={type(exc).__name__}")
        raise SystemExit(2)
