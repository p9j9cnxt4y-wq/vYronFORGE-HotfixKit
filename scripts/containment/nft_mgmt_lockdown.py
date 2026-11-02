#!/usr/bin/env python3
import argparse, ipaddress, subprocess, sys

def render(cidr, ports):
    net=ipaddress.ip_network(cidr, strict=False)
    family='ip6' if net.version==6 else 'ip'
    plist=', '.join(str(p) for p in sorted(set(ports)))
    return f"""table inet vyronforge_hotfix {{
  chain input {{
    type filter hook input priority -5; policy accept;
    iifname "lo" tcp dport {{ {plist} }} accept
    {family} saddr {net.with_prefixlen} tcp dport {{ {plist} }} accept
    tcp dport {{ {plist} }} drop
  }}
}}\n"""

def main():
    ap=argparse.ArgumentParser(description='Generate/apply a fail-closed management-port lockdown at an upstream Linux nftables control point.')
    ap.add_argument('--management-cidr', required=True)
    ap.add_argument('--ports', required=True, help='comma-separated TCP ports')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ack-network-impact', action='store_true')
    a=ap.parse_args()
    ports=[int(x) for x in a.ports.split(',') if x.strip()]
    if not ports or any(p<1 or p>65535 for p in ports): raise SystemExit('VYF_DENY_BAD_PORT')
    rules=render(a.management_cidr,ports)
    print(rules,end='')
    if a.apply:
      if not a.ack_network_impact: raise SystemExit('VYF_DENY_ACK_NETWORK_IMPACT_REQUIRED')
      subprocess.run(['nft','-f','-'], input=rules, text=True, check=True)
      print('VYF_APPLY_OK', file=sys.stderr)
if __name__=='__main__': main()
