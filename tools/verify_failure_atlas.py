#!/usr/bin/env python3
"""Read-only coherence checks for the bounded public failure-atlas tree."""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGES=ROOT/'packages'/'failure-atlas'
expected={f'{n:02d}' for n in range(1,12)}
found={p.name[:2] for p in PACKAGES.iterdir() if p.is_dir()}
errors=[]
if found != expected: errors.append('TOPIC_SET_MISMATCH')
for p in sorted(PACKAGES.iterdir()):
    if not p.is_dir():continue
    try:
        case=json.loads((p/'cases.json').read_text(encoding='utf-8'))
        if case['id'] != p.name[:2] or case['actual_vendor_client_fixed'] is not False:
            errors.append(p.name+':BAD_CASE_ID_OR_VENDOR_CLAIM')
        if case['production_actions_executed'] is not False:errors.append(p.name+':UNSAFE_PRODUCTION_CLAIM')
        if not (p/'README.md').is_file(): errors.append(p.name+':MISSING_README')
        if not (ROOT/'tests'/case['test_module']).is_file():errors.append(p.name+':MISSING_TEST')
        if len(case.get('links',[])) != len(set(case.get('links',[]))):errors.append(p.name+':DUPLICATE_LINK')
    except (OSError,KeyError,ValueError) as exc:errors.append(p.name+':INVALID_CASEPACK')
if errors:
    for e in errors:print(e)
    raise SystemExit(2)
print('FAILURE_ATLAS=PASS topic_packages=11 source_tests=11; no vendor host execution verified')
