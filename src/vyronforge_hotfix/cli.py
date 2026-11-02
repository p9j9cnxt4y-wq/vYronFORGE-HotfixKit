from __future__ import annotations
import argparse, json
from pathlib import Path
from importlib import resources
from .planner import plan
from .redact import redact, redact_data

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def main():
    p=argparse.ArgumentParser(prog='vyf-hotfix')
    sub=p.add_subparsers(dest='cmd', required=True)
    pp=sub.add_parser('plan', help='read-only remediation plan')
    pp.add_argument('--inventory', required=True)
    pp.add_argument('--policy', help='policy JSON; defaults to the version bundled with the installed package')
    pp.add_argument('--out')
    pp.add_argument('--redact-evidence', action='store_true', default=True)
    args=p.parse_args()
    if args.cmd=='plan':
        policy = load(args.policy) if args.policy else json.loads(resources.files('vyronforge_hotfix').joinpath('data/critical-2026-09-14.json').read_text(encoding='utf-8'))
        report=plan(load(args.inventory),policy)
        safe_report=redact_data(report) if args.redact_evidence else report
        raw=json.dumps(safe_report, indent=2)
        out=redact(raw) if args.redact_evidence else raw
        if args.out: Path(args.out).write_text(out+'\n',encoding='utf-8')
        print(out)

if __name__=='__main__': main()
