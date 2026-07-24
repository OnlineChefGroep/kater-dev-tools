#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 [--apply] [--ref SHA]" >&2
  exit 2
}

[[ $EUID -eq 0 ]] || {
  echo "install-kater-shadow must run as root" >&2
  exit 1
}

apply=0
ref=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) apply=1; shift ;;
    --ref) ref=${2:-}; shift 2 ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done

asset_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
install_root=/opt/chef/services/kater
config_root=/etc/chef/kater
state_root=/var/lib/chef/kater
backup_stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup_dir=/var/lib/chef/backups/kater-shadow-${backup_stamp}

preflight() {
  for command in python3 curl systemctl tailscale; do
    command -v "$command" >/dev/null
  done
  local avail_kb
  avail_kb=$(df -Pk / | awk 'NR==2 {print $4}')
  if [[ "$avail_kb" -lt 1048576 ]]; then
    echo "preflight: insufficient disk on / (need >=1GiB free)" >&2
    exit 1
  fi
  if ss -tlnH | grep -qE ':(9090|9091|9092)\b'; then
    echo "preflight: one of ports 9090/9091/9092 already in use" >&2
    ss -tlnH | grep -E ':(9090|9091|9092)\b' || true
    exit 1
  fi
}

ensure_identity() {
  if ! getent group kater-svc >/dev/null; then
    groupadd --system kater-svc
  fi
  if ! id kater-svc >/dev/null 2>&1; then
    useradd --system --home /var/lib/chef/kater --shell /usr/sbin/nologin \
      --gid kater-svc --create-home kater-svc
  fi
}

ensure_layout() {
  install -d -m 0750 -o root -g kater-svc "$config_root"
  install -d -m 0750 -o kater-svc -g kater-svc "$state_root"
  install -d -m 0755 -o root -g root "$install_root"
  install -d -m 0755 -o root -g root /var/log/chef/kater
}

write_config() {
  install -m 0640 -o root -g kater-svc "$asset_root/scripts/control-plane/kater.env.example" \
    "$config_root/kater.env"
  if [[ ! -f "$config_root/secrets.env" ]]; then
    install -m 0600 -o root -g root "$asset_root/scripts/control-plane/secrets.env.example" \
      "$config_root/secrets.env"
  fi
  if [[ ! -L "$install_root/.kater" ]]; then
    ln -sfn "$state_root" "$install_root/.kater"
  fi
}

sync_code() {
  rsync -a --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '.pytest_cache' \
    --exclude '.mypy_cache' \
    --exclude '.ruff_cache' \
    --exclude 'coverage.xml' \
    --exclude '.kater' \
    "$asset_root/" "$install_root/"
  if [[ -n "$ref" && -f "$install_root/.deploy-ref" ]]; then
    echo "$ref" >"$install_root/.deploy-ref"
  elif [[ -f "$asset_root/.git/HEAD" ]]; then
    git -C "$asset_root" rev-parse HEAD >"$install_root/.deploy-ref" 2>/dev/null || true
  fi
  chown -R root:root "$install_root"
  chmod -R a+rX "$install_root"
  chown -h kater-svc:kater-svc "$install_root/.kater" 2>/dev/null || true
}

install_uv() {
  if [[ ! -x /usr/local/bin/uv ]]; then
    curl -fsSL https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
  fi
}

build_venv() {
  cd "$install_root"
  /usr/local/bin/uv sync --no-dev --production
  chown -R kater-svc:kater-svc "$install_root/.venv"
}

install_unit() {
  install -m 0644 -o root -g root \
    "$asset_root/scripts/control-plane/chef-kater-shadow.service" \
    /etc/systemd/system/chef-kater-shadow.service
  install -m 0755 -o root -g root \
    "$asset_root/scripts/control-plane/rollback-kater-shadow.sh" \
    /usr/local/sbin/chef-kater-shadow-rollback
  systemctl daemon-reload
}

backup_existing() {
  install -d -m 0700 -o root -g root "$backup_dir"
  if [[ -d "$install_root" ]]; then
    tar -czf "$backup_dir/opt-chef-services-kater.tgz" -C /opt/chef/services kater 2>/dev/null || true
  fi
  if [[ -d "$config_root" ]]; then
    tar -czf "$backup_dir/etc-chef-kater.tgz" -C /etc/chef kater 2>/dev/null || true
  fi
  if systemctl list-unit-files chef-kater-shadow.service >/dev/null 2>&1; then
    systemctl show chef-kater-shadow.service -p FragmentPath,ActiveState,SubState \
      >"$backup_dir/unit-state.txt" 2>/dev/null || true
  fi
  echo "$backup_dir" > /var/lib/chef/state/kater-shadow-last-backup
}

preflight
ensure_identity
ensure_layout
write_config
backup_existing
sync_code
install_uv
build_venv
install_unit

if [[ "$apply" -eq 1 ]]; then
  systemctl enable chef-kater-shadow.service
  systemctl restart chef-kater-shadow.service
  systemctl is-active chef-kater-shadow.service
else
  echo "Dry run complete. Re-run with --apply to enable/start chef-kater-shadow.service"
fi
