from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from .versioning import at_least, is_supported_version

SEV = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "OPERATIONAL": 1}

@dataclass
class Finding:
    asset_id: str
    policy_id: str
    vendor: str
    severity: str
    state: str
    score: int
    reason: str
    action: str
    verify: str
    sources: list[str]

    def to_dict(self): return asdict(self)

def _norm_vendor(value: str) -> str:
    return ''.join(ch for ch in str(value).lower() if ch.isalnum())

def _vendor_matches(asset_vendor: str, policy_vendor: str) -> bool:
    # Vendor identity is part of the trust boundary: a product-name substring alone
    # must not map an unrelated vendor into a remediation policy. Slash-separated
    # policy names declare explicit aliases (for example Broadcom/VMware).
    av=_norm_vendor(asset_vendor)
    if not av:
        return False
    aliases=[_norm_vendor(v) for v in str(policy_vendor).split('/') if _norm_vendor(v)]
    return av in aliases  # Identity must match a declared vendor or exact alias

def _matches(asset: dict[str, Any], item: dict[str, Any]) -> bool:
    if not _vendor_matches(str(asset.get('vendor','')), str(item.get('vendor',''))):
        return False
    product=str(asset.get('product','')).lower()
    return any(p.lower() in product for p in item.get('products', []))

def _branch_gate(current: str, fixed_versions: dict[str, str]) -> tuple[str, str] | None:
    matches=[(prefix, minimum) for prefix, minimum in fixed_versions.items()
             if current.lower()==prefix.lower() or
             any(current.lower().startswith(prefix.lower()+separator) for separator in ('.','-'))]
    if not matches:
        return None
    prefix, minimum=max(matches, key=lambda x: len(x[0]))
    if at_least(current, minimum):
        return 'PASS_FIXED', f'{current} >= {minimum} ({prefix} branch)'
    return 'DENY_VULNERABLE', f'{current} < {minimum} ({prefix} branch)'

def _state(asset: dict[str, Any], item: dict[str, Any]) -> tuple[str,str]:
    if item.get('verification_status','VERIFIED') != 'VERIFIED':
        return 'REQUIRES_VENDOR_VERIFY','current vendor evidence for this policy is not verified'
    current=str(asset.get('version','')).strip()
    required_component=item.get('required_component')
    if required_component and str(asset.get('component','')).strip().lower()!=required_component:
        return 'REQUIRES_VENDOR_VERIFY','the affected component must be inventoried explicitly'
    comparable=any(item.get(k) for k in ('fixed_versions_by_edition','fixed_versions_by_platform','minimum_operational_baseline','minimum_fixed_version','auto_compare_fixed_versions')) or item.get('id')=='VMWARE-VMSA-2026-0007'
    if comparable and not is_supported_version(current):
        return 'DENY_UNKNOWN','missing, unsupported or prerelease version cannot establish a fixed state'
    if item.get('fixed_versions_by_edition'):
        edition=str(asset.get('edition','')).strip().lower()
        minimum=item['fixed_versions_by_edition'].get(edition)
        if not minimum:
            return 'REQUIRES_VENDOR_VERIFY','an explicitly supported product edition is required'
        return ('PASS_FIXED',f'{current} >= {minimum} ({edition})') if at_least(current,minimum) else ('DENY_VULNERABLE',f'{current} < {minimum} ({edition})')
    if item.get('fixed_versions_by_platform'):
        if not current: return 'DENY_UNKNOWN','product version missing'
        platform=str(asset.get('platform','')).strip().lower()
        if not platform: return 'REQUIRES_VENDOR_VERIFY','platform is required for a platform-specific fixed build'
        aliases={'win32':'windows','win64':'windows','windows 11':'windows','windows 10':'windows','darwin':'macos','osx':'macos','mac os':'macos'}
        platform=aliases.get(platform,platform)
        minimum=item['fixed_versions_by_platform'].get(platform)
        if not minimum: return 'REQUIRES_VENDOR_VERIFY',f'no fixed build declared for platform {platform}'
        return ('PASS_FIXED', f'{current} >= {minimum} ({platform})') if at_least(current, minimum) else ('DENY_VULNERABLE', f'{current} < {minimum} ({platform})')
    if item.get('minimum_operational_baseline'):
        if not current: return 'DENY_UNKNOWN','product version missing'
        minimum=item['minimum_operational_baseline']
        return ('PASS_FIXED', f'{current} >= {minimum}') if at_least(current, minimum) else ('DENY_VULNERABLE', f'{current} < {minimum}')
    if item.get('minimum_fixed_version'):
        if not current: return 'DENY_UNKNOWN','product version missing'
        minimum=item['minimum_fixed_version']
        return ('PASS_FIXED', f'{current} >= {minimum}') if at_least(current, minimum) else ('DENY_VULNERABLE', f'{current} < {minimum}')
    if item.get('id') == 'VMWARE-VMSA-2026-0007':
        if not current: return 'DENY_UNKNOWN','product version missing'
        return ('PASS_FIXED','26H1u1 or later') if at_least(current,'26H1u1') else ('DENY_VULNERABLE','below 26H1u1')
    if item.get('auto_compare_fixed_versions') and item.get('fixed_versions'):
        if not current: return 'DENY_UNKNOWN','product version missing'
        result=_branch_gate(current,item['fixed_versions'])
        if result is not None: return result
        return 'REQUIRES_VENDOR_VERIFY','version branch is not safely comparable by this policy'
    # Proprietary appliances often need vendor build/branch logic, configuration preconditions or authenticated portal data.
    # Unknown is intentionally fail-closed rather than pretending a generic comparator is authoritative.
    return 'REQUIRES_VENDOR_VERIFY','vendor-specific patch state must be verified'

def _terminal_status(findings: list[dict[str, Any]], unassessed: list[str], asset_count: int) -> str:
    if asset_count == 0:
        return 'WARN_EMPTY_INVENTORY'
    if any(f['state'].startswith('DENY') for f in findings):
        return 'WARN_REMEDIATION_REQUIRED'
    if unassessed:
        return 'WARN_UNASSESSED_ASSETS'
    if any(f['state'] == 'REQUIRES_VENDOR_VERIFY' for f in findings):
        return 'WARN_VENDOR_VERIFICATION_REQUIRED'
    return 'PASS_FIXED'

def plan(inventory: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    findings=[]
    matched_assets=set()
    assets=inventory.get('assets', [])
    for asset_index,asset in enumerate(assets):
        for item in policy.get('items', []):
            if not _matches(asset,item): continue
            matched_assets.add(asset_index)
            state, reason = _state(asset,item)
            score = SEV.get(item.get('severity','LOW'),1)*20
            if item.get('actively_exploited'): score += 15
            if asset.get('internet_exposed'): score += 10
            if asset.get('criticality') == 'critical': score += 5
            findings.append(Finding(
                asset_id=str(asset.get('id','unknown')),
                policy_id=item['id'], vendor=item['vendor'], severity=item['severity'],
                state=state, score=min(score,100), reason=reason,
                action=item['action'], verify=item['verify'], sources=item.get('sources',[])
            ).to_dict())
    findings.sort(key=lambda f:(-f['score'],f['asset_id'],f['policy_id']))
    unassessed=[str(a.get('id','unknown')) for index,a in enumerate(assets) if index not in matched_assets]
    return {
        'schema':2, 'snapshot':policy.get('snapshot'),
        'assets':len(assets), 'findings':findings,
        'unassessed_assets':unassessed,
        'terminal_status':_terminal_status(findings,unassessed,len(assets))
    }
