from __future__ import annotations

import json
import re
from typing import Any

from typer.testing import CliRunner, Result

from kater.cli import app

runner = CliRunner()


def run_cli(args: list[str], **kwargs: Any) -> Result:
    """Helper to run CLI commands with NO_COLOR and robustly stripped output."""
    env = kwargs.pop("env", {})
    env.setdefault("NO_COLOR", "1")
    result = runner.invoke(app, args, env=env, **kwargs)

    # Strip ANSI escape sequences from output for robust matching.
    # Since result.output is often a read-only property, we use monkey-patching
    # on the instance to allow overriding it.
    clean_output = re.sub(r"\x1b\[[0-9;]*[mGKF]", "", result.output)

    # Simple instance override if possible, otherwise we'd need a wrapper class.
    # tyepr.testing.Result (from click) might have a read-only property 'output'.
    try:
        # Try overriding the property at the instance level.
        result.__dict__["output"] = clean_output
    except Exception:
        # If that fails (e.g. __dict__ doesn't work for this object), we'll just
        # have to live with a slightly messy result object, but we've tried.
        pass

    # Re-verify clean_output is what we want.
    # We can also just attach it as a new attribute if the property is stubborn.
    setattr(result, "clean_output", clean_output)
    return result


def test_cli_help_starts() -> None:
    result = run_cli(["--help"])

    assert result.exit_code == 0
    assert "Kater" in result.clean_output or "Developer MCP gateway" in result.clean_output


def test_doctor_json() -> None:
    result = run_cli(["doctor", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["profiles"] == ["core"]


def test_doctor_json_with_apply(tmp_path) -> None:
    result = run_cli(
        ["doctor", "--profile", "research", "--fix-plan", "--apply", "--yes", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert "apply_result" in payload
    assert payload["profiles"] == ["research"]


def test_apply_requires_yes() -> None:
    result = run_cli(["doctor", "--apply"])

    assert result.exit_code == 2
    assert "--apply requires --yes" in result.clean_output


def test_profiles_json() -> None:
    result = run_cli(["profiles", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert "core" in payload["profiles"]


def test_tools_json() -> None:
    result = run_cli(["tools", "--profile", "core", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["profile"] == "core"
    names = {t["name"] for t in payload["tools"]}
    assert "kater_profiles" in names
    assert "kater_doctor" in names


def test_chains_json() -> None:
    result = run_cli(["chains", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert len(payload["chains"]) > 0
    names = {c["name"] for c in payload["chains"]}
    assert "research_brief" in names


def test_chains_filtered_by_profile() -> None:
    result = run_cli(["chains", "--profile", "utrecht"])

    assert result.exit_code == 0
    assert "utrecht_status" in result.clean_output
    assert "research_brief" not in result.clean_output


def test_chain_run_research_brief() -> None:
    result = run_cli(
        ["chain", "run", "research_brief", "--profile", "research", "--json"]
    )

    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["chain"] == "research_brief"
    assert len(payload["steps"]) > 0


def test_chain_run_unknown() -> None:
    result = run_cli(["chain", "run", "nonexistent"])

    assert result.exit_code == 1
    assert "not found" in result.clean_output


def test_mcp_serve_profile_flag() -> None:
    result = run_cli(["mcp", "serve", "--help"])

    assert result.exit_code == 0
    assert "--profile" in result.clean_output


def test_version() -> None:
    result = run_cli(["version"])
    assert result.exit_code == 0
    assert result.clean_output.strip()


def test_config_json() -> None:
    result = run_cli(["config", "--profile", "core", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["profile"] == "core"
    assert "kater" in payload["mcpServers"]


def test_adapters_json() -> None:
    result = run_cli(["adapters", "--profile", "ops", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["total"] > 0


def test_mcp_list_json() -> None:
    result = run_cli(["mcp", "list", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["total"] > 10
    names = {s["name"] for s in payload["servers"]}
    assert "github" in names
    assert "cloudflare" in names


def test_mcp_list_filtered_by_profile() -> None:
    result = run_cli(["mcp", "list", "--profile", "ops", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    names = {s["name"] for s in payload["servers"]}
    assert "github" in names
    assert "exa" not in names


def test_mcp_status_known() -> None:
    result = run_cli(["mcp", "status", "github", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["name"] == "github"
    assert payload["transport"] == "stdio"


def test_mcp_status_unknown() -> None:
    result = run_cli(["mcp", "status", "nonexistent"])
    assert result.exit_code == 1
    assert "unknown" in result.clean_output


def test_init_creates_kater_dir(tmp_path) -> None:
    result = run_cli(["init", "--profile", "ops", "--force", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert len(payload["created"]) > 0


def test_serve_help() -> None:
    result = run_cli(["serve", "--help"])
    assert result.exit_code == 0
    assert "--api-port" in result.clean_output
    assert "--mcp-port" in result.clean_output


def test_enable_server() -> None:
    result = run_cli(["enable", "github", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["enabled"] is True


def test_disable_server() -> None:
    result = run_cli(["disable", "sentry", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["enabled"] is False


def test_toggle_server() -> None:
    result = run_cli(["toggle", "exa", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert "enabled" in payload


def test_enable_unknown() -> None:
    result = run_cli(["enable", "nonexistent"])
    assert result.exit_code == 1


def test_deploy_list() -> None:
    result = run_cli(["deploy", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    names = {f["name"] for f in payload["formats"]}
    assert "docker" in names
    assert "cloudflare" in names


def test_deploy_render() -> None:
    result = run_cli(["deploy", "render", "docker", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["format"] == "docker-compose"


def test_deploy_render_cloudflare() -> None:
    result = run_cli(
        ["deploy", "render", "cloudflare", "--domain", "kater.test.com", "--json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["format"] == "cloudflare-tunnel"


def test_auth_status() -> None:
    result = run_cli(["auth", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert "mode" in payload


def test_auth_set_apikey() -> None:
    result = run_cli(["auth", "set", "apikey", "--key", "test-key", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["mode"] == "apikey"
    assert "test-key" in payload["api_keys"]


def test_auth_set_none() -> None:
    result = run_cli(["auth", "set", "none", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["mode"] == "none"


def test_settings_json() -> None:
    result = run_cli(["settings", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.clean_output)
    assert payload["version"] == 2
    assert "auth" in payload
