#!/usr/bin/env python3
"""One-command local synthetic contract verification; emits no child stdout."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vyronforge_hotfix.execution_integrity import (  # noqa: E402
    BoundaryIntegrityError, run_local_python_file, verify_exact_bytes,
)
from vyronforge_hotfix.guest_protocol import (  # noqa: E402
    GuestProtocolError, make_synthetic_qga_reply, parse_synthetic_qga_reply,
)


def verify():
    base = ROOT / "tests" / "fixtures"
    passed = []
    good = run_local_python_file(base / "guest_valid.py")
    records = parse_synthetic_qga_reply(make_synthetic_qga_reply(good.stdout))
    if len(records) != 3:
        raise RuntimeError("E2E_EXPECTED_THREE_SYNTHETIC_RECORDS")
    passed.append("LOCAL_FILE_TO_STDOUT_TO_QGA_TO_PARSER")
    for name in ("guest_missing_main.py", "guest_literal_tab.py"):
        bad = run_local_python_file(base / name)
        try:
            parse_synthetic_qga_reply(make_synthetic_qga_reply(bad.stdout))
        except GuestProtocolError:
            passed.append("NEGATIVE_" + name.replace(".py", "").upper())
        else:
            raise RuntimeError("MALFORMED_GUEST_OUTPUT_ACCEPTED")
    payload = b"x\ny\n"
    r = run_local_python_file(base / "echo_bytes.py", stdin=payload)
    verify_exact_bytes(payload, r.stdout)
    passed.append("BINARY_STDIN_STDOUT_EXACT")
    try:
        verify_exact_bytes(payload, payload.replace(b"\n", b"\r\n"))
    except BoundaryIntegrityError:
        passed.append("NEGATIVE_CRLF_MUTATION")
    else:
        raise RuntimeError("CRLF_MUTATION_NOT_REJECTED")
    return {"status": "PASS", "scope": "LOCAL_SYNTHETIC_ONLY", "checks": passed,
            "ssh_attempts": 0, "qga_remote_attempts": 0, "production_fix_claim": False}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), sort_keys=True))
    except Exception as exc:
        # Status intentionally excludes raw child output and secrets.
        print(json.dumps({"status": "FAIL", "scope": "LOCAL_SYNTHETIC_ONLY", "class": type(exc).__name__}))
        raise SystemExit(2)
