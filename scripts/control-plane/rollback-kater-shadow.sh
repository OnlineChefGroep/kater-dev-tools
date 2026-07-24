#!/usr/bin/env bash
set -euo pipefail

[[ $EUID -eq 0 ]] || {
  echo "chef-kater-shadow-rollback must run as root" >&2
  exit 1
}

backup_hint=/var/lib/chef/state/kater-shadow-last-backup
pre_backup=/var/lib/chef/backups/pre-kater-shadow-20260724T044939

systemctl stop chef-kater-shadow.service 2>/dev/null || true
systemctl disable chef-kater-shadow.service 2>/dev/null || true
rm -f /etc/systemd/system/chef-kater-shadow.service
systemctl daemon-reload
systemctl reset-failed chef-kater-shadow.service 2>/dev/null || true

if [[ -f "${backup_hint}" ]]; then
  echo "Last shadow backup recorded at: $(cat "${backup_hint}")"
fi
if [[ -d "${pre_backup}" ]]; then
  echo "Pre-shadow fleet backup available at: ${pre_backup}"
fi

echo "Shadow Kater stopped and unit removed. Laptop kater-local.service untouched."
echo "To restore shadow tree from last backup tarball, extract opt-chef-services-kater.tgz and etc-chef-kater.tgz from the backup directory above."
