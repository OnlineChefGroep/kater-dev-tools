#!/usr/bin/env bash
set -euo pipefail

REF="${CPM_REF:-main}"
NPM_PREFIX="${CPM_NPM_PREFIX:-$HOME/.local}"
VERSION="0.4.0"
BASE="https://raw.githubusercontent.com/OnlineChefGroep/kater-dev-tools/${REF}/packages/coding-provider-manager"
ARTIFACT="onlinechefgroep-coding-provider-manager-${VERSION}.tgz"
EXPECTED="ac19a812464c0f75782b5812b3fb98604be0b428006a8a0174f706290346973c"

for command in node npm curl sha256sum; do
  command -v "$command" >/dev/null 2>&1 || { echo "Missing required command: $command" >&2; exit 127; }
done

node_major="$(node -p 'Number(process.versions.node.split(".")[0])')"
[ "$node_major" -ge 20 ] || { echo "Node.js 20 or newer is required" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl -fsSL "$BASE/artifacts/$ARTIFACT" -o "$tmp/$ARTIFACT"
echo "$EXPECTED  $tmp/$ARTIFACT" | sha256sum -c -
mkdir -p "$NPM_PREFIX"
npm install --global --prefix "$NPM_PREFIX" "$tmp/$ARTIFACT"

CPM="$NPM_PREFIX/bin/cpm"
"$CPM" --version
"$CPM" agent manifest

echo "Installed: $CPM"
case ":$PATH:" in
  *":$NPM_PREFIX/bin:"*) ;;
  *) echo "Add to PATH: export PATH=\"$NPM_PREFIX/bin:\$PATH\"" ;;
esac
