#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'policies/critical-2026-09-14.json'

def main() -> int:
    data=json.loads(P.read_text(encoding='utf-8'))
    errors=[]
    ids=set()
    for i,item in enumerate(data.get('items',[])):
        iid=item.get('id')
        if not iid:
            errors.append(f'item[{i}] missing id'); continue
        if iid in ids: errors.append(f'duplicate id: {iid}')
        ids.add(iid)
        for key in ('vendor','products','severity','hotfix_strategy','action','verify','sources'):
            if not item.get(key): errors.append(f'{iid}: missing {key}')
        if not isinstance(item.get('products'),list): errors.append(f'{iid}: products must be a list')
        for u in item.get('sources',[]):
            p=urlparse(u)
            if p.scheme != 'https' or not p.netloc: errors.append(f'{iid}: invalid source URL {u!r}')
        if item.get('actively_exploited') and not item.get('cves'):
            errors.append(f'{iid}: actively_exploited without CVE')
        pmap=item.get('fixed_versions_by_platform')
        if pmap is not None:
            if not isinstance(pmap,dict) or not pmap:
                errors.append(f'{iid}: fixed_versions_by_platform must be a non-empty object')
            else:
                for platform, version in pmap.items():
                    if not str(platform).strip() or not str(version).strip():
                        errors.append(f'{iid}: invalid platform fixed version {platform!r}={version!r}')
    coverage=data.get('cert_eu_2026_advisory_coverage',{})
    if coverage and not isinstance(coverage,dict):
        errors.append('cert_eu_2026_advisory_coverage must be an object')
    elif isinstance(coverage,dict):
        for adv,pids in coverage.items():
            if not isinstance(pids,list) or not pids:
                errors.append(f'{adv}: coverage mapping must be a non-empty list')
            elif any(pid not in ids for pid in pids):
                errors.append(f'{adv}: coverage references unknown policy id')
    out={'policy':str(P.name),'items':len(ids),'errors':errors,'status':'PASS' if not errors else 'FAIL'}
    print(json.dumps(out,indent=2))
    return 0 if not errors else 2
if __name__=='__main__': raise SystemExit(main())
