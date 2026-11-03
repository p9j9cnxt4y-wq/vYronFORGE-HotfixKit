#!/usr/bin/env bash
set -euo pipefail
MODE="${1:---audit}"
case "$MODE" in --audit|--apply) ;; *) echo "usage: $0 [--audit|--apply]" >&2; exit 64;; esac
if [[ "$MODE" == "--apply" && "${EUID:-$(id -u)}" -ne 0 ]]; then echo VYF_DENY_ROOT_REQUIRED >&2; exit 77; fi

if command -v dnf >/dev/null 2>&1; then
  dnf -q updateinfo list security
  if [[ "$MODE" == "--apply" ]]; then dnf -y upgrade --security; fi
elif command -v yum >/dev/null 2>&1; then
  yum -q updateinfo list security
  if [[ "$MODE" == "--apply" ]]; then yum -y update --security; fi
elif command -v zypper >/dev/null 2>&1; then
  zypper --non-interactive list-patches --category security
  if [[ "$MODE" == "--apply" ]]; then zypper --non-interactive patch --category security; fi
elif command -v unattended-upgrade >/dev/null 2>&1; then
  if [[ "$MODE" == "--audit" ]]; then unattended-upgrade --dry-run --debug; else unattended-upgrade -d; fi
elif command -v apt-get >/dev/null 2>&1; then
  echo 'VYF_WARN_APT_SECURITY_ONLY_HELPER_MISSING: install/use unattended-upgrades; refusing broad automatic upgrade.' >&2
  apt-get -s upgrade
  if [[ "$MODE" == "--apply" ]]; then echo 'VYF_DENY_APT_BROAD_UPGRADE_NOT_AUTOMATED' >&2; exit 78; fi
else
  echo VYF_DENY_UNSUPPORTED_PACKAGE_MANAGER >&2; exit 69
fi
