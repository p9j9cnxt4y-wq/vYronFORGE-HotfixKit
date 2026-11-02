#!/usr/bin/env python3
"""Fail closed on obvious public-release privacy hazards; not a DLP guarantee.

The scan does not contact a service and deliberately scans text files. Unknown
binary content is rejected. Use an additional independent review before push.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {'.git', '.venv', '__pycache__', '.pytest_cache', 'build', 'dist'}
SKIP_FILES = {Path('evidence/SHA256SUMS.txt'), Path('evidence/ci-report.json')}
PATTERNS = {
    'private_ipv4': re.compile(r'\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b'),
    'mac_address': re.compile(r'\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b'),
    'windows_user_path': re.compile(r'(?i)\b[A-Z]:\\Users\\[^\\\s]+'),
    'posix_user_path': re.compile(r'(?<![\w])/(?:home|Users)/[^/\s]+'),
    'private_dns_name': re.compile(r'(?i)\b(?:' + ('local'+'host') + r'|[A-Za-z0-9.-]+\.(?:' + ('loc'+'al|l'+'an|inter'+'nal') + r'))\b'),
    'private_key_marker': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token': re.compile(r'\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b'),
    'aws_access_key': re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
    'bearer_header': re.compile(r'(?i)\b(?:authorization|proxy-authorization)\s*[:=]\s*(?:bearer|basic)\s+[A-Za-z0-9+/_.=-]{10,}'),
    'jwt_like': re.compile(r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b'),
}
SECRET_ASSIGNMENT = re.compile(
    r'''(?ix)\b(?:token|access[_-]?token|refresh[_-]?token|auth[_-]?token|api[_-]?key|x[_-]?api[_-]?key|password|passwd|secret|client[_-]?secret|secret[_-]?key|authorization|proxy[_-]?authorization|session[_-]?id)\b\s*[:=]\s*["']?([^\s"',;}]+)'''
)
SAFE_SECRET_VALUES = {'[REDACTED_SECRET]', 'REDACTED', 'example', 'placeholder'}

def scan_tree(root: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    scanned = 0
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(part in SKIP_PARTS or part.endswith('.egg-info') for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root)
        if rel in SKIP_FILES:
            continue
        if path.is_symlink():
            errors.append(f'{rel}: SYMLINK_NOT_ALLOWED')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            errors.append(f'{rel}: NON_UTF8_BINARY')
            continue
        scanned += 1
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                errors.append(f'{rel}: {name}')
        for match in SECRET_ASSIGNMENT.finditer(text):
            val = match.group(1).strip('"\'')
            if val not in SAFE_SECRET_VALUES and not val.startswith('[REDACTED_'):
                errors.append(f'{rel}: assigned_secret_literal')
                break
    return scanned, sorted(set(errors))

if __name__=='__main__':
    n, errors = scan_tree(ROOT)
    if errors:
        print('PUBLICATION_SCAN=FAIL')
        for e in errors: print(e)
        raise SystemExit(2)
    print(f'PUBLICATION_SCAN=PASS files={n}')
