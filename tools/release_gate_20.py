#!/usr/bin/env python3
"""Twenty-plus independent release-content checks. Local, read-only and offline.

These checks do NOT grant permission for a GitHub push or a production run.
FPP host attestations and native Windows CI remain separate external gates.
"""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlparse
R=Path(__file__).resolve().parents[1]

class ReadinessError(ValueError):pass

def need(ok:bool,reason:str='ASSERTION_FAIL')->None:
    if not ok: raise ReadinessError(reason)

def data(path:str):return json.loads((R/path).read_text('utf-8'))

def git_metadata_excluded(root: Path) -> bool:
    """Validate the release file list, not local checkout administrative state.

    A checkout may contain .git; release archives must use the verified source
    manifest and never include any .git path component.
    """
    manifest = root / 'evidence' / 'SHA256SUMS.txt'
    try:
        lines = manifest.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeError):
        return False
    if not lines:
        return False
    seen = set()
    for line in lines:
        if '  ' not in line:
            return False
        digest, name = line.split('  ', 1)
        parts = name.split('/')
        if (not re.fullmatch(r'[0-9a-f]{64}', digest)
                or not name or '\\' in name or ':' in name
                or any(part in ('', '.', '..') for part in parts)
                or any(part.casefold() == '.git' for part in parts)
                or name.casefold() in seen):
            return False
        seen.add(name.casefold())
    return True



idx=data('docs/failure-atlas/CASE_INDEX.json')
reg=data('docs/failure-atlas/FINDINGS_REGISTER_20261029.json')
up=data('docs/failure-atlas/UPSTREAM_STATUS_20261029.json')
policy=data('policies/critical-2026-09-14.json')
casefiles=sorted((R/'packages/failure-atlas').glob('*/cases.json'))
cases=[json.loads(p.read_text('utf-8')) for p in casefiles]
issues={x['number'] for x in up['issues']}
F=reg['findings']
checks=[]

def check(name, fn):
    try:fn();checks.append({'id':f'{len(checks)+1:02d}','name':name,'status':'PASS'})
    except Exception as exc:
        checks.append({'id':f'{len(checks)+1:02d}','name':name,'status':'FAIL','reason':type(exc).__name__})

check('01-version-metadata',lambda: need('version = "0.4.1rc1"' in (R/'pyproject.toml').read_text()))
check('02-python-module-version',lambda: need('0.4.1rc1' in (R/'src/vyronforge_hotfix/__init__.py').read_text()))
check('03-current-index-version',lambda: need(idx['repository_candidate']=='v0.4.1-rc1'))
check('04-historical-evidence-marked',lambda: need('historical' in (R/'README.md').read_text().lower()))
check('05-only-one-changelog-heading',lambda: need((R/'CHANGELOG.md').read_text().count('# Changelog')==1))
check('06-topics-count-eleven',lambda: need(len(idx['topics'])==11))
check('07-case-file-count-eleven',lambda: need(len(cases)==11))
check('08-topic-ids-unique',lambda: need(len({x['id'] for x in idx['topics']})==11))
check('09-topic-case-ids-match',lambda: need({c['id'] for c in cases}=={x['id'] for x in idx['topics']}))
check('10-case-tests-exist',lambda: need(all((R/'tests'/c['test_module']).is_file() for c in cases)))
check('11-no-prod-operations-claimed',lambda: need(all(c['production_actions_executed'] is False for c in cases)))
check('12-no-vendor-binary-fixed',lambda: need(all(c['actual_vendor_client_fixed'] is False for c in cases)))
check('13-case-publication-status',lambda: need(all(c['publication_status']=='NOT_PUBLISHED' for c in cases)))
check('14-findings-count',lambda: need(len(F)==reg['finding_count'] and len(F)>=50))
check('15-findings-unique',lambda: need(len({x['id'] for x in F})==len(F)))
check('16-findings-match-topic-scope',lambda: need({x['topic_id'] for x in F}=={c['id'] for c in cases}))
check('17-no-attributed-proprietary-fix',lambda: need(all(x['vendor_binary_fixed'] is False for x in F)))
check('18-no-unproven-internal-root-cause-claims',lambda: need(all(x['authoritative_root_cause_proven'] is False for x in F)))
check('19-upstream-issues-exact-retrieval-date',lambda: need(up['retrieval_date']=='2026-10-29'))
check('20-upstream-links-are-published-IDs',lambda: need(all(set(x['upstream_issues'])<=issues for x in F)))
check('21-upstream-URL-owner-correct',lambda: need(all(urlparse(x['url']).path==f'/openai/codex/issues/{x["number"]}' for x in up['issues'])))
check('22-source-dated-policy-snapshot',lambda: need(policy['snapshot']=='2026-09-14'))
check('23-dated-policy-count',lambda: need(len(policy['items'])==34))
check('24-eu-advisory-count',lambda: need(len(policy['cert_eu_2026_advisory_coverage'])==12))
check('25-license-present-MIT',lambda: need((R/'LICENSE').is_file() and 'MIT License' in (R/'LICENSE').read_text()))
check('26-no-proprietary-binary-files',lambda: need(not any(p.suffix.lower() in {'.exe','.dll','.dmp','.pfx','.pem','.key','.vhdx','.img'} for p in R.rglob('*') if p.is_file())))
check('27-no-Git-metadata-in-release-manifest',lambda: need(git_metadata_excluded(R)))
check('28-no-explicit-FPP-as-gate-substitute',lambda: need('PRECONDITION_ONLY_NOT_EXECUTION_AUTHORIZED' in (R/'src/vyronforge_failure_atlas/contracts.py').read_text()))
check('29-CI-plans-Windows-and-Linux',lambda: need(all(n in (R/'.github/workflows/ci.yml').read_text() for n in ('windows-latest','ubuntu-latest','python tools/verify_wheel.py','python tools/verify_release_manifest.py'))))
check('30-scripts-default-audit-only',lambda: need('Mode=\'Audit\'' in (R/'scripts/windows/patch-security-updates.ps1').read_text() and 'MODE="${1:---audit}"' in (R/'scripts/linux/patch-security-updates.sh').read_text() and "if a.apply:" in (R/'scripts/containment/nft_mgmt_lockdown.py').read_text()))
check('31-historical-evidence-still-present',lambda: need(all((R/x).exists() for x in ('evidence/FAILURE_ATLAS_VERIFY_20261024.json','evidence/RELEASE_CANDIDATE_VERIFY_2026-10-19.json'))))
check('32-no-publish-claim-in-metadata',lambda: need(reg['boundary']['github_publication']=='NOT_DONE'))
check('33-fpp-actual-host-not-claimed',lambda: need(reg['boundary']['fpp_actual_host']=='NOT_RUN'))
check('34-windows-native-CI-not-claimed',lambda: need(reg['boundary']['windows_remote_ci']=='NOT_RUN'))
check('35-review-artefacts-exist',lambda: need(all((R/x).is_file() for x in ('docs/failure-atlas/ALL_FINDINGS_20261029.md','docs/failure-atlas/UPSTREAM_STATUS_20261029.json','docs/failure-atlas/README.md'))))

ok=sum(x['status']=='PASS' for x in checks)
result={'schema':'vyronforge-local-release-checks/1','checked_as_of':'2026-10-29','checks':checks,'passed':ok,'total':len(checks),'status':'PASS_LOCAL_CONTENT' if ok==len(checks) else 'FAIL_LOCAL_CONTENT','windows_remote_ci':'NOT_RUN','fpp_host_attestation':'NOT_RUN','github_published':'NOT_DONE'}
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['status']=='PASS_LOCAL_CONTENT' else 2)
