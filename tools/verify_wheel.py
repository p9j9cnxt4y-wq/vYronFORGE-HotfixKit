#!/usr/bin/env python3
"""Fail-closed wheel verification against RECORD and the exact local source tree.

Does not import, install, or execute code from the wheel. Designed to catch
synthetic duplicate-member, missing/incorrect RECORD and source-mismatch cases.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import io
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

REQUIRED = {
    'vyronforge_hotfix/__init__.py',
    'vyronforge_hotfix/cli.py',
    'vyronforge_hotfix/planner.py',
    'vyronforge_hotfix/redact.py',
    'vyronforge_hotfix/versioning.py',
    'vyronforge_hotfix/execution_integrity.py',
    'vyronforge_hotfix/guest_protocol.py',
    'vyronforge_hotfix/data/critical-2026-09-14.json',
    'vyronforge_hotfix/data/critical-2026-11-02.json',
    'vyronforge_failure_atlas/__init__.py',
    'vyronforge_failure_atlas/contracts.py',
}


class WheelRefusal(ValueError):
    """Safe failure code; no wheel content is disclosed in error messages."""


def _safe_name(name: str) -> bool:
    if not isinstance(name, str) or not name or '\\' in name or '\x00' in name:
        return False
    p = PurePosixPath(name)
    return not (p.is_absolute() or '..' in p.parts or '.' in p.parts or ':' in name
                or name.startswith('/') or '//' in name or name.endswith('/'))


def verify_wheel(wheel_path: Path, root: Path, required: set[str] | None = None) -> int:
    """Verify one wheel. No filesystem writes, imports or interpreter execution."""
    required = REQUIRED if required is None else required
    with zipfile.ZipFile(wheel_path) as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        names = [i.filename for i in infos]
        if not infos or len(infos) > 2000 or sum(i.file_size for i in infos) > 32 * 1024 * 1024:
            raise WheelRefusal('WHEEL_SIZE_OR_COUNT_BOUNDARY')
        if len(names) != len(set(names)) or len(names) != len(set(n.casefold() for n in names)):
            raise WheelRefusal('WHEEL_DUPLICATE_MEMBER')
        if any(not _safe_name(i.filename) for i in infos):
            raise WheelRefusal('WHEEL_UNSAFE_MEMBER_PATH')
        if any(stat.S_ISLNK(i.external_attr >> 16) for i in infos):
            raise WheelRefusal('WHEEL_SYMLINK_MEMBER')
        if not required <= set(names):
            raise WheelRefusal('WHEEL_REQUIRED_PAYLOAD_MISSING')
        records = [x for x in names if re.fullmatch(r'[^/]+\.dist-info/RECORD', x)]
        if len(records) != 1:
            raise WheelRefusal('WHEEL_RECORD_MISSING_OR_AMBIGUOUS')
        record = records[0]
        try:
            rows = list(csv.reader(io.StringIO(z.read(record).decode('utf-8', 'strict'))))
        except (UnicodeError, csv.Error):
            raise WheelRefusal('WHEEL_RECORD_MALFORMED') from None
        if any(len(row) != 3 or not row[0] for row in rows):
            raise WheelRefusal('WHEEL_RECORD_MALFORMED')
        paths = [row[0] for row in rows]
        if len(paths) != len(set(paths)) or set(paths) != set(names):
            raise WheelRefusal('WHEEL_RECORD_COVERAGE_MISMATCH')
        for name, encoded, size in rows:
            if name == record:
                if encoded or size:
                    raise WheelRefusal('WHEEL_RECORD_SELF_HASH_NOT_EMPTY')
                continue
            if not encoded.startswith('sha256=') or not size.isdecimal():
                raise WheelRefusal('WHEEL_RECORD_MISSING_DIGEST_OR_SIZE')
            payload = z.read(name)
            expected = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode('ascii').rstrip('=')
            if encoded != 'sha256=' + expected or int(size) != len(payload):
                raise WheelRefusal('WHEEL_RECORD_CONTENT_MISMATCH')
        src = root / 'src'
        source_files = {
            p.relative_to(src).as_posix(): p.read_bytes()
            for pkg in ('vyronforge_hotfix', 'vyronforge_failure_atlas')
            for p in (src / pkg).rglob('*')
            if p.is_file() and p.suffix in ('.py', '.json')
            and '__pycache__' not in p.parts
        }
        if not source_files or not set(source_files) <= set(names):
            raise WheelRefusal('WHEEL_SOURCE_COVERAGE_MISMATCH')
        for name, data in source_files.items():
            if z.read(name) != data:
                raise WheelRefusal('WHEEL_SOURCE_CONTENT_MISMATCH')
        metadata = [x for x in names if re.fullmatch(r'[^/]+\.dist-info/METADATA',x)]
        if len(metadata)!=1:
            raise WheelRefusal('WHEEL_METADATA_MISSING_OR_AMBIGUOUS')
        v = re.search(r'(?m)^Version:\s*(\S+)', z.read(metadata[0]).decode('utf-8','strict'))
        declared = re.search(r'(?m)^__version__\s*=\s*["\']([^"\']+)',
                             (src/'vyronforge_hotfix/__init__.py').read_text('utf-8'))
        if not v or not declared or v.group(1) != declared.group(1):
            raise WheelRefusal('WHEEL_VERSION_MISMATCH')
        return len(infos)


def main() -> int:
    wheel_dir=Path(sys.argv[1] if len(sys.argv)>1 else 'dist')
    root=Path(__file__).resolve().parents[1]
    wheels=sorted(wheel_dir.glob('vyronforge_hotfixkit-*.whl'))
    if len(wheels)!=1:
        print('WHEEL_CONTENT=FAIL:EXPECTED_ONE_WHEEL')
        return 2
    try:
        n=verify_wheel(wheels[0],root)
    except (WheelRefusal,OSError,zipfile.BadZipFile,UnicodeError) as exc:
        print(f'WHEEL_CONTENT=FAIL:{type(exc).__name__ if not isinstance(exc,WheelRefusal) else str(exc)}')
        return 2
    print(f'WHEEL_CONTENT=PASS:records={n}; source_bytes_match=true; digest=sha256')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
