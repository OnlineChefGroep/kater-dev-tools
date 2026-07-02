# Cloudflare Global MCP — Infrastructure

Server files for the `chef-cloudflare-global` MCP server deployed on bc-scan-2.

## Files

- `tools.mjs` — Shared tool definitions (50+ Cloudflare tools)
- `server-http.mjs` — HTTP/Streamable transport for remote access
- `package.json` — Node.js dependencies

## Deploy

```bash
# Copy files to host
scp *.mjs package.json bc-scan-2:/home/ubuntu/chef-cloudflare-global-mcp/

# Install
ssh bc-scan-2 "cd /home/ubuntu/chef-cloudflare-global-mcp && npm install"

# Deploy systemd units
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now chef-cloudflare-mcp cloudflared-mcp
```

## Tunnel

Managed via Cloudflare dashboard/API: tunnel `chef-cloudflare-mcp` routes `mcp-cf.chefgroep.online` → `localhost:3101`

## Reference

- Docs: `docs/cloudflare-mcp.md`
- Runbook: `CLOUDFLARE.md` (on server)
- Notion: Cloudflare Global MCP
