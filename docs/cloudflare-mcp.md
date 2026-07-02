# Cloudflare Global MCP — Deployment Guide

Full Cloudflare management via MCP (50+ tools) running on bc-scan-2 behind Cloudflare Tunnel.

**Droid integration**: `chef-cloudflare-global` in `~/.factory/mcp.json`

## Architecture

```
Droid (Windows) ──→ https://mcp-cf.chefgroep.online/mcp (CF Tunnel)
                         │
                    bc-scan-2:3101 (Node MCP server)
                         │
                    Cloudflare v4 API (Global API Key)
```

## Quick Deploy (bc-scan-2)

```bash
# 1. Clone the MCP server
cd /home/ubuntu
git clone https://github.com/OnlineChefGroep/kater-dev-tools.git  # or copy files
mkdir -p chef-cloudflare-global-mcp

# 2. Copy server files
cp kater-dev-tools/infra/cloudflare-mcp/* chef-cloudflare-global-mcp/

# 3. Create .env (never commit!)
cat > chef-cloudflare-global-mcp/.env << 'EOF'
CLOUDFLARE_EMAIL=chefadmin@chefgroep.online
CLOUDFLARE_API_KEY=<your-global-api-key>
CLOUDFLARE_ACCOUNT_ID=3658edc5d94b8eb1fb06790e4b712877
PORT=3101
HOST=127.0.0.1
EOF

# 4. Install & start
cd chef-cloudflare-global-mcp
npm install
sudo cp ../kater-dev-tools/infra/cloudflare-mcp/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now chef-cloudflare-mcp cloudflared-mcp
```

## Tunnel Setup

The MCP server runs behind a dedicated Cloudflare Tunnel (`chef-cloudflare-mcp`):

1. Create tunnel via Cloudflare API or dashboard
2. DNS CNAME: `mcp-cf.chefgroep.online` → `<tunnel-id>.cfargotunnel.com`
3. Tunnel ingress: `mcp-cf.chefgroep.online` → `http://localhost:3101`
4. WAF skip rule on `chefgroep.online` zone for `mcp-cf.chefgroep.online`

## Service Management

```bash
# MCP server
sudo systemctl status chef-cloudflare-mcp
sudo systemctl restart chef-cloudflare-mcp
journalctl -u chef-cloudflare-mcp -f

# Tunnel
sudo systemctl status cloudflared-mcp
sudo systemctl restart cloudflared-mcp
```

## Droid Configuration

In `~/.factory/mcp.json`:

```json
{
  "chef-cloudflare-global": {
    "type": "streamableHttp",
    "url": "https://mcp-cf.chefgroep.online/mcp",
    "disabled": false
  },
  "chef-cloudflare-global-local": {
    "type": "stdio",
    "command": "node",
    "args": ["C:/Users/joep/chef-cloudflare-global-mcp/server.mjs"],
    "env": {
      "CLOUDFLARE_EMAIL": "chefadmin@chefgroep.online",
      "CLOUDFLARE_API_KEY": "<key>",
      "CLOUDFLARE_ACCOUNT_ID": "3658edc5d94b8eb1fb06790e4b712877"
    },
    "disabled": true
  }
}
```

## Tool Inventory (50+ tools)

See full runbook: `CLOUDFLARE.md`

| Category | Tools |
|----------|-------|
| Universal | `cf_request` (full API bypass) |
| Accounts/Zones | `cf_accounts_list/get`, `cf_zones_list/get/find/create/delete`, `cf_zone_settings/update`, `cf_zone_purge_cache` |
| DNS | `cf_dns_list/get/create/update/delete/export/import` |
| SSL/TLS | `cf_ssl_verify/universal/universal_update` |
| Workers | `cf_workers_list`, `cf_worker_get/get_code/put/delete`, `cf_worker_subdomains/routes/route_create/route_delete` |
| Pages | `cf_pages_projects/project_get/deployments/deployment_get/domains` |
| KV | `cf_kv_namespaces/list/read/write/delete`, `cf_kv_namespace_create/delete` |
| R2 | `cf_r2_buckets/objects`, `cf_r2_bucket_create/delete`, `cf_r2_object_get/delete` |
| D1 | `cf_d1_databases/get/create/delete/query` |
| Tunnels | `cf_tunnels_list/get/create/delete/config/config_update` |
| WAF/Firewall | `cf_waf_packages/rules/rule_update`, `cf_firewall_rules/rule_create/rule_delete`, `cf_rate_limits` |
| Analytics | `cf_analytics_dashboard/colos` |
| Logs/Audit | `cf_logpush_jobs`, `cf_logs_received`, `cf_audit_logs` |
| Admin | `cf_account_members/roles`, `cf_api_tokens/verify` |
| Fleet | `cf_fleet_summary` |

## Related

- Runbook: `CLOUDFLARE.md` (included with server)
- Skill: `~/.factory/skills/cloudflare-ops/SKILL.md`
- Droid: `~/.factory/droids/cloudflare-ops.md`
- Notion: [Cloudflare Global MCP](https://app.notion.com/p/391ecd7f1c1a81a3bf88eb066b19c3de)
