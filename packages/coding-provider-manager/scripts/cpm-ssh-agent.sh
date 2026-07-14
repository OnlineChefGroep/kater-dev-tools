#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 <ssh-host> <agent-method> [json-params]" >&2
  exit 2
fi

host="$1"
method="$2"
params="${3:-{}}"
remote_bin="${CPM_REMOTE_BIN:-~/.local/bin/cpm}"

request="$(node -e '
const [method, raw] = process.argv.slice(1);
let params;
try { params = JSON.parse(raw); }
catch (error) { console.error(`Invalid JSON params: ${error.message}`); process.exit(2); }
process.stdout.write(JSON.stringify({ id: 1, method, params }) + "\n");
' "$method" "$params")"

printf '%s' "$request" | ssh -T "$host" "$remote_bin agent serve"
