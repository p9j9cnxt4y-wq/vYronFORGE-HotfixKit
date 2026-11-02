"""Synthetic QGA-like response validation; no real guest or network access.

The v1 protocol is deliberately structured JSON, not nested tab-delimited shell
strings. It denies empty stdout, absent entrypoint, malformed base64, unbounded
records, unknown keys, and undeclared output fields.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
from typing import Any

MAGIC = "VYF_GUEST_RECORDS_V1"
TARGET = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")
CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
RECORD_KEYS = {"target", "state", "detail_code"}
ALLOWED_STATES = {"OK", "WARN", "UNKNOWN"}


class GuestProtocolError(ValueError):
    """A guest result is not complete and valid under the declared contract."""


def encode_guest_records(records: list[dict[str, str]]) -> bytes:
    validate_records(records)
    envelope = {"protocol": MAGIC, "completed": True, "record_count": len(records), "records": records}
    return (json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def validate_records(records: Any) -> list[dict[str, str]]:
    if not isinstance(records, list) or not (1 <= len(records) <= 32):
        raise GuestProtocolError("INVALID_RECORD_COUNT")
    for record in records:
        if not isinstance(record, dict) or set(record) != RECORD_KEYS:
            raise GuestProtocolError("RECORD_SCHEMA_MISMATCH")
        target, state, code = record["target"], record["state"], record["detail_code"]
        if not isinstance(target, str) or not TARGET.fullmatch(target):
            raise GuestProtocolError("INVALID_TARGET_ID")
        if not isinstance(state, str) or state not in ALLOWED_STATES:
            raise GuestProtocolError("INVALID_STATE")
        if not isinstance(code, str) or not CODE.fullmatch(code):
            raise GuestProtocolError("INVALID_DETAIL_CODE")
    return records


def decode_guest_records(stdout: bytes) -> list[dict[str, str]]:
    if not isinstance(stdout, bytes):
        raise TypeError("STDOUT_MUST_BE_BYTES")
    if not stdout or len(stdout) > 65536:
        raise GuestProtocolError("EMPTY_OR_OVERSIZED_STDOUT")
    try:
        text = stdout.decode("utf-8", errors="strict")
        object_value = json.loads(text)
    except (UnicodeError, json.JSONDecodeError):
        raise GuestProtocolError("NON_JSON_GUEST_OUTPUT") from None
    if not isinstance(object_value, dict) or set(object_value) != {
        "protocol", "completed", "record_count", "records"
    }:
        raise GuestProtocolError("ENVELOPE_SCHEMA_MISMATCH")
    if object_value["protocol"] != MAGIC or object_value["completed"] is not True:
        raise GuestProtocolError("GUEST_COMPLETION_NOT_PROVEN")
    records = validate_records(object_value["records"])
    count = object_value["record_count"]
    if type(count) is not int or count != len(records):
        raise GuestProtocolError("RECORD_COUNT_MISMATCH")
    return records


def make_synthetic_qga_reply(stdout: bytes, *, exit_code: int = 0, stderr: bytes = b"") -> dict[str, Any]:
    """Build only a local QGA-shaped fixture; this function does not contact QGA."""
    if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
        raise TypeError("STREAM_MUST_BE_BYTES")
    return {"return": {"exited": True, "exitcode": exit_code,
                       "out-data": base64.b64encode(stdout).decode("ascii"),
                       "err-data": base64.b64encode(stderr).decode("ascii")}}


def parse_synthetic_qga_reply(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, dict) or set(value) != {"return"}:
        raise GuestProtocolError("QGA_REPLY_SCHEMA_MISMATCH")
    reply = value["return"]
    if not isinstance(reply, dict) or set(reply) != {"exited", "exitcode", "out-data", "err-data"}:
        raise GuestProtocolError("QGA_RESULT_SCHEMA_MISMATCH")
    if reply["exited"] is not True or type(reply["exitcode"]) is not int or reply["exitcode"] != 0:
        raise GuestProtocolError("GUEST_PROCESS_NOT_SUCCESSFUL")
    try:
        if not isinstance(reply["out-data"], str) or not isinstance(reply["err-data"], str):
            raise ValueError
        stdout = base64.b64decode(reply["out-data"], validate=True)
        stderr = base64.b64decode(reply["err-data"], validate=True)
    except (binascii.Error, ValueError):
        raise GuestProtocolError("INVALID_QGA_BASE64") from None
    # stderr is not returned or logged: it might carry sensitive diagnostics.
    if len(stderr) > 65536:
        raise GuestProtocolError("OVERSIZED_STDERR")
    return decode_guest_records(stdout)


def decode_legacy_tab_record(stdout: bytes) -> tuple[str, str, str]:
    """Compatibility validator: reject literal backslash-t and CRLF framing."""
    if not isinstance(stdout, bytes) or b"\r" in stdout or not stdout.endswith(b"\n"):
        raise GuestProtocolError("BAD_LEGACY_LINE_ENDING")
    if stdout.count(b"\n") != 1:
        raise GuestProtocolError("BAD_LEGACY_LINE_COUNT")
    fields = stdout[:-1].split(b"\t")
    if len(fields) != 4 or fields[0] != b"VSAFE":
        raise GuestProtocolError("BAD_LEGACY_FIELD_DELIMITER")
    try:
        values = tuple(x.decode("ascii", "strict") for x in fields[1:])
    except UnicodeDecodeError:
        raise GuestProtocolError("INVALID_LEGACY_ENCODING") from None
    target, state, code = values
    validate_records([{"target": target, "state": state, "detail_code": code}])
    return values
