#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'policies'/'critical-2026-09-14.json'
data=json.loads(P.read_text(encoding='utf-8'))
ids={x['id'] for x in data.get('items',[])}
coverage=data.get('cert_eu_2026_advisory_coverage',{})
expected={f'2026-{i:03d}' for i in range(1,13)}
errors=[]
missing=sorted(expected-set(coverage))
if missing: errors.append('missing advisory mappings: '+','.join(missing))
for adv, policy_ids in sorted(coverage.items()):
    if not policy_ids: errors.append(f'{adv}: empty policy mapping')
    for pid in policy_ids:
        if pid not in ids: errors.append(f'{adv}: unknown policy id {pid}')
    # Require at least one mapped policy to cite this CERT-EU advisory directly,
    # except later superseding policy groups that deliberately share a product family.
    url=f'https://www.cert.europa.eu/publications/security-advisories/{adv}/'
    if not any(url in next(x for x in data['items'] if x['id']==pid).get('sources',[]) for pid in policy_ids):
        errors.append(f'{adv}: no mapped policy cites {url}')
out={'expected':len(expected),'mapped':len(coverage),'errors':errors,'status':'PASS' if not errors else 'FAIL'}
print(json.dumps(out,indent=2))
raise SystemExit(0 if not errors else 2)
