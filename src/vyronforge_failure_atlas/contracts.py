"""Non-executing integrity and state oracles for synthetic regression tests.

None of these functions grants execution authority, runs shell commands, reads
remote systems, deletes user files or patches proprietary software.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from datetime import datetime, timezone
from pathlib import Path


class AtlasRefusal(ValueError):
    """Raised on a fail-closed contract failure; ``code`` is safe for logs."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compare_exact_bytes(expected: bytes, received: bytes) -> dict:
    if not isinstance(expected, bytes) or not isinstance(received, bytes):
        raise AtlasRefusal('NON_BINARY_PAYLOAD')
    if expected != received:
        raise AtlasRefusal('BOUNDARY_BYTE_MUTATION')
    return {'status': 'PASS', 'length': len(expected), 'sha256': sha256(expected)}


def verify_guest_completion(stdout: bytes, *, exit_code: int, expected_count: int) -> dict:
    if exit_code != 0:
        raise AtlasRefusal('GUEST_NONZERO_EXIT')
    if not stdout or len(stdout) > 65536:
        raise AtlasRefusal('GUEST_OUTPUT_EMPTY_OR_OVERSIZED')
    try:
        obj = json.loads(stdout.decode('utf-8', errors='strict'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise AtlasRefusal('GUEST_MALFORMED_JSON') from None
    if not isinstance(obj, dict) or set(obj) != {'records', 'completed'} or obj.get('completed') is not True:
        raise AtlasRefusal('GUEST_COMPLETION_MISSING')
    records = obj.get('records')
    if not isinstance(records, list) or len(records) != expected_count or expected_count < 1:
        raise AtlasRefusal('GUEST_RECORD_COUNT_MISMATCH')
    if any(not isinstance(r, dict) or set(r) != {'label','state'} or not isinstance(r['label'], str)
           or not r['label'] or r['state'] not in ('SAFE','BLOCKED','UNKNOWN') for r in records):
        raise AtlasRefusal('GUEST_RECORD_SCHEMA_INVALID')
    return {'status':'PASS', 'record_count':len(records)}


def validate_relative_path(root: Path, raw: str) -> dict:
    if not isinstance(raw, str) or not raw or len(raw)>4096 or any(c in raw for c in ('\x00','\n','\r')):
        raise AtlasRefusal('PATH_MALFORMED')
    if raw.startswith(('~','/','\\')) or ':' in raw:
        raise AtlasRefusal('PATH_ABSOLUTE_OR_DEVICE')
    chunks = raw.replace('\\','/').split('/')
    if any(c in ('','.','..') or len(c)>255 or c.endswith(('.', ' ')) for c in chunks):
        raise AtlasRefusal('PATH_TRAVERSAL_OR_AMBIGUITY')
    reserved = {'CON','PRN','AUX','NUL'} | {f'{c}{i}' for c in ('COM','LPT') for i in range(1,10)}
    if any(c.split('.')[0].upper() in reserved for c in chunks):
        raise AtlasRefusal('WINDOWS_RESERVED_NAME')
    anchor = Path(root)
    if not anchor.exists() or anchor.is_symlink():
        raise AtlasRefusal('ROOT_NOT_TRUSTED')
    original = anchor.resolve(strict=True)
    cur = anchor
    for part in chunks:
        cur = cur / part
        if cur.is_symlink():
            raise AtlasRefusal('REPARSE_OR_SYMLINK_BOUNDARY')
    try:
        candidate = cur.resolve(strict=False)
        candidate.relative_to(original)
    except (ValueError, OSError, RuntimeError):
        raise AtlasRefusal('PATH_OUTSIDE_BOUND_ROOT') from None
    return {'status':'VALIDATED_REFERENCE_ONLY', 'relative': '/'.join(chunks)}


def gate_file_operation(*, action: str, path_safe: bool, readiness: bool, owner_grant: bool) -> str:
    # This reference *never* permits mutation; a productive isolated executor
    # must implement and verify separate authorization and OS enforcement.
    if action in ('DELETE','FORMAT','UNMOUNT','DEPLOY','WRITE','RESTART'):
        return 'DENY_MUTATION_NOT_SUPPORTED'
    if action != 'READ' or not path_safe or not readiness:
        return 'DENY_NOT_READY'
    return 'READ_REFERENCE_ONLY_NO_EXECUTION_AUTHORITY'


def check_budget(*, children: int, max_children: int, ram_mib: int,
                 max_ram_mib: int, elapsed_s: int, timeout_s: int) -> str:
    v=(children, max_children, ram_mib, max_ram_mib, elapsed_s, timeout_s)
    if any(type(x) is not int or x < 0 for x in v) or min(max_children,max_ram_mib,timeout_s) == 0:
        raise AtlasRefusal('INVALID_RESOURCE_BUDGET')
    if children > max_children or ram_mib > max_ram_mib or elapsed_s > timeout_s:
        raise AtlasRefusal('RESOURCE_ENVELOPE_BREACH')
    return 'WITHIN_RECORDED_LIMITS_NOT_OS_ENFORCED'


def readiness_precondition(receipt: dict, *, scope: str, digest: str,
                           now: datetime | None = None) -> str:
    # Compatibility precondition *not* the normative FPP 0.1.0 validator.
    if not isinstance(receipt, dict) or set(receipt) != {'status','scope','sha256','expires_at'}:
        raise AtlasRefusal('READINESS_SCHEMA_UNKNOWN')
    if (not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest)
        or receipt['status'] != 'FORGE_READY' or receipt['scope'] != scope
        or receipt['sha256'] != digest):
        raise AtlasRefusal('READINESS_BINDING_MISMATCH')
    now = now or datetime.now(timezone.utc)
    try:
        exp = datetime.fromisoformat(receipt['expires_at'].replace('Z','+00:00'))
        if exp.tzinfo is None or exp <= now:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise AtlasRefusal('READINESS_EXPIRED_OR_INVALID') from None
    return 'PRECONDITION_ONLY_NOT_EXECUTION_AUTHORIZED'


def skill_oracle(prompt: str) -> str:
    # Only a logical oracle for the synthetic fixture, not Codex host telemetry.
    if (re.search(r'(?<![A-Z0-9_])ROUTE_ALPHA_POSITIVE(?![A-Z0-9_])',prompt)
        and not re.search(r'(?<![A-Z0-9_])ROUTE_ALPHA_EXCLUDE(?![A-Z0-9_])',prompt)):
        return 'ALPHA_EXPECTED'
    return 'ALPHA_FORBIDDEN'


def classify_skill_trace(*, attempted_read: bool, body_loaded: bool,
                         internal_selection_event: bool) -> str:
    if internal_selection_event:
        return 'HOST_SELECTION_OBSERVED'
    if body_loaded:
        return 'BODY_LOADED_NO_INTERNAL_SELECTION_PROOF'
    if attempted_read:
        return 'TOOL_ATTEMPT_OBSERVED_NO_BODY_LOAD'
    return 'NO_SKILL_ACCESS_OBSERVED'


def classify_computer_use(*, discovered: bool, approved: bool, captured: bool,
                          input_confirmed: bool, closed: bool) -> str:
    if all((discovered, approved, captured, input_confirmed, closed)):
        return 'PASS_SYNTHETIC_STATE_CONTRACT'
    if discovered and not approved:
        return 'BLOCKED_APPROVAL'
    if approved and not captured:
        return 'BLOCKED_CAPTURE'
    if approved and captured and not input_confirmed:
        return 'BLOCKED_INPUT'
    return 'INCOMPLETE_NOT_PASS'


def classify_build(*, exit_code: int, observed_errors: list[str]) -> str:
    if exit_code == 0 and not observed_errors:
        return 'BUILD_PROCESS_EXIT_ZERO_ONLY'
    if 'MSB5021' in observed_errors and set(observed_errors) == {'MSB5021'}:
        return 'BLOCKED_CANCELLATION_CAUSE_UNKNOWN'
    if not observed_errors:
        return 'FAILED_NO_ROOT_CAUSE_TELEMETRY'
    return 'FAIL_FIRST_ERROR_REQUIRES_LOG_CORRELATION'


def classify_evidence(*, errors: int, unknown: int, mandatory_skipped: int, claimed_pass: bool) -> str:
    if any(type(x) is not int or x < 0 for x in (errors, unknown, mandatory_skipped)):
        raise AtlasRefusal('INVALID_EVIDENCE_COUNTS')
    if errors or unknown or mandatory_skipped:
        return 'FAIL_FALSE_PASS_CLAIM' if claimed_pass else 'WARN_INCOMPLETE'
    return 'PASS_BOUNDED_EVIDENCE_ONLY'


def validate_systemd_metadata(record: dict) -> str:
    allowed = {'opaque_ref','unit_type','active','pid','runtime_class'}
    if not isinstance(record, dict) or set(record) != allowed:
        raise AtlasRefusal('SYSTEMD_UNSAFE_OR_INCOMPLETE_FIELDS')
    if not isinstance(record['opaque_ref'],str) or not re.fullmatch('[0-9a-f]{16,64}', record['opaque_ref']):
        raise AtlasRefusal('SYSTEMD_BAD_OPAQUE_REF')
    if (record['unit_type'] not in ('service','socket','target') or type(record['active']) is not bool
        or type(record['pid']) is not int or not 0 <= record['pid'] <= 2147483647
        or record['runtime_class'] not in ('dotnet','python','native','unknown')):
        raise AtlasRefusal('SYSTEMD_UNSAFE_FIELD_VALUE')
    return 'PASS_MINIMAL_METADATA_SCHEMA_ONLY'


def correlate_label(label: str, *, run_key: bytes) -> str:
    if len(run_key) < 16 or not label:
        raise AtlasRefusal('CORRELATION_KEY_OR_LABEL_INVALID')
    return hmac.new(run_key,label.encode('utf-8'),hashlib.sha256).hexdigest()[:32]


def check_candidate_coverage(*, covered: int, relevant: int, cap: int = 8) -> str:
    if any(type(x) is not int for x in (covered,relevant,cap)) or cap <= 0 or min(covered,relevant) < 0:
        raise AtlasRefusal('COVERAGE_INVALID')
    if covered > cap or covered != relevant:
        return 'WARN_PARTIAL_DISCOVERY'
    return 'PASS_BOUNDED_COMPLETE_FOR_DECLARED_RELEVANT_SET'


def ack_chain(*, thread: bool, turn: bool, first_exec: bool, result: bool) -> str:
    if (turn and not thread) or (first_exec and not turn) or (result and not first_exec):
        return 'INVALID_EVENT_ORDER'
    if all((thread,turn,first_exec,result)):
        return 'RESULT_COMMITTED_SYNTHETIC_CONTRACT'
    if thread and not turn:
        return 'BLOCKED_TURN_NOT_STARTED'
    if turn and not first_exec:
        return 'BLOCKED_NO_EXECUTION_ACK'
    if first_exec and not result:
        return 'BLOCKED_RESULT_NOT_COMMITTED'
    return 'INCOMPLETE_NOT_PASS'


def label_source(*, path_hits: int, manifest_bindings: int, source_bytes_read: bool) -> str:
    if any(type(x) is not int or x < 0 for x in (path_hits,manifest_bindings)):
        raise AtlasRefusal('INVENTORY_INVALID')
    if path_hits and not manifest_bindings and not source_bytes_read:
        return 'PATH_HINTS_ONLY_SOURCE_AUTHORITY_UNKNOWN'
    if not source_bytes_read:
        return 'SOURCE_NOT_CONTENT_VERIFIED'
    return 'CONTENT_READ_NOT_CURRENT_AUTHORITY'


def publication_gate(*, unit_tests: bool, native_windows_ci: bool,
                     redacted: bool, license_reviewed: bool, owner_approved: bool) -> str:
    if not all((unit_tests,native_windows_ci,redacted,license_reviewed,owner_approved)):
        return 'NO_PUBLICATION_AUTHORITY'
    # Still no API credentials and no network operations in this package.
    return 'PUBLISH_PREREQUISITES_REPORTED_REQUIRES_AUTHORIZED_PUBLISHER'
