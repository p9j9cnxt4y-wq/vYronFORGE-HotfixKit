#!/usr/bin/env bash
set -euo pipefail
MODE="dry-run"
case "${1:-}" in
  --apply) MODE="apply" ;;
  --rollback) MODE="rollback" ;;
  "") ;;
  *) echo "usage: $0 [--apply|--rollback]" >&2; exit 64 ;;
esac
CONF=/etc/modprobe.d/vyronforge-disable-algif_aead.conf
if [[ "$MODE" == "dry-run" ]]; then
  echo "MODE=DRY_RUN"
  echo "WOULD_WRITE=$CONF"
  echo "CONTENT=install algif_aead /bin/false"
  echo "WOULD_UNLOAD=algif_aead"
  exit 0
fi
if [[ $EUID -ne 0 ]]; then echo "ERROR=root_required" >&2; exit 77; fi
if [[ "$MODE" == "rollback" ]]; then
  rm -f "$CONF"
  echo "ROLLBACK=REMOVED_PERSISTENT_BLOCK"
  echo "NOTE=reboot_or_explicit_modprobe_required_to_restore_module_if_needed"
  exit 0
fi
printf '%s\n' 'install algif_aead /bin/false' > "$CONF"
if lsmod | awk '{print $1}' | grep -qx algif_aead; then
  rmmod algif_aead
fi
grep -Fxq 'install algif_aead /bin/false' "$CONF"
if lsmod | awk '{print $1}' | grep -qx algif_aead; then
  echo "VERIFY=FAIL_module_still_loaded" >&2; exit 2
fi
echo "VERIFY=PASS_algif_aead_blocked_and_unloaded"
