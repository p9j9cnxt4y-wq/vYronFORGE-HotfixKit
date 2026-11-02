"""Local-only, byte-exact execution-boundary primitives.

Does not intercept or patch Codex/ChatGPT, contact servers, or perform SSH.
The caller explicitly chooses a *local* Python fixture/script to execute.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class BoundaryIntegrityError(ValueError):
    """A declared byte-preserving boundary changed its payload."""


class LocalExecutionError(RuntimeError):
    """The local child did not execute successfully or on time."""


def digest(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise TypeError("EXPECTED_EXACT_BYTES")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class BoundaryReceipt:
    status: str
    expected_sha256: str
    actual_sha256: str
    expected_length: int
    actual_length: int


def verify_exact_bytes(expected: bytes, actual: bytes) -> BoundaryReceipt:
    """Fail-closed; no raw payload bytes appear in exceptions or receipts."""
    expected_hash = digest(expected)
    actual_hash = digest(actual)
    result = BoundaryReceipt(
        status="PASS" if expected == actual else "FAIL_BYTE_MUTATION",
        expected_sha256=expected_hash,
        actual_sha256=actual_hash,
        expected_length=len(expected),
        actual_length=len(actual),
    )
    if result.status != "PASS":
        raise BoundaryIntegrityError("BOUNDARY_BYTE_MUTATION")
    return result


def utf8_payload(text: str) -> bytes:
    if not isinstance(text, str):
        raise TypeError("EXPECTED_TEXT")
    return text.encode("utf-8", errors="strict")


@dataclass(frozen=True)
class LocalProcessResult:
    exit_code: int
    stdin_sha256: str
    stdout_sha256: str
    stdout: bytes
    stderr: bytes


def run_local_python_file(
    script: Path,
    *,
    stdin: bytes = b"",
    args: Sequence[str] = (),
    timeout_seconds: float = 10.0,
    interpreter: str | None = None,
) -> LocalProcessResult:
    """Execute a local .py file without a shell, stdin encoding, or PTY.

    No subprocess command line, stderr, or source text is ever printed here.
    Not a sandbox: only call on trusted local scripts or synthetic fixtures.
    """
    script = Path(script)
    if script.suffix.casefold() != ".py" or not script.is_file():
        raise LocalExecutionError("LOCAL_PYTHON_FILE_REQUIRED")
    if not isinstance(stdin, bytes):
        raise TypeError("STDIN_MUST_BE_BYTES")
    if not 0 < timeout_seconds <= 60:
        raise ValueError("BOUNDED_TIMEOUT_REQUIRED")
    if any(not isinstance(value, str) for value in args):
        raise TypeError("ARGV_MUST_BE_STRINGS")
    argv = [interpreter or sys.executable, "-I", str(script), *args]
    try:
        result = subprocess.run(
            argv,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=False,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise LocalExecutionError("LOCAL_CHILD_TIMEOUT") from None
    except OSError as error:
        raise LocalExecutionError("LOCAL_CHILD_START_FAILED") from None
    if result.returncode != 0:
        raise LocalExecutionError("LOCAL_CHILD_NONZERO_EXIT")
    return LocalProcessResult(
        exit_code=result.returncode,
        stdin_sha256=digest(stdin),
        stdout_sha256=digest(result.stdout),
        stdout=result.stdout,
        stderr=result.stderr,
    )
