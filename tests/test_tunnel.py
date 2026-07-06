from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

from kater.tunnel import (
    detect_cloudflared,
    detect_tailscale,
    generate_cloudflare_config,
    generate_tailscale_funnel_cmd,
    start_cloudflared,
    tunnel_overview,
)


def test_detect_cloudflared():
    result = detect_cloudflared()
    assert isinstance(result, bool)


def test_detect_tailscale():
    result = detect_tailscale()
    assert isinstance(result, bool)


def test_generate_cloudflare_config():
    config = generate_cloudflare_config(
        tunnel_name="my-tunnel",
        domain="kater.example.com",
    )
    assert "tunnel: my-tunnel" in config
    assert "kater.example.com" in config
    assert "localhost:9090" in config
    assert "ingress:" in config
    assert "api.kater" not in config


def test_generate_tailscale_funnel_cmd():
    cmd = generate_tailscale_funnel_cmd(port=9090)
    assert "tailscale" in cmd
    assert "funnel" in cmd
    assert "9090" in cmd


def test_tunnel_overview():
    overview = tunnel_overview(domain="test.example.com")
    assert "cloudflare" in overview
    assert "tailscale" in overview
    assert "available" in overview
    assert "client_configs" in overview
    assert overview["client_configs"]["cloudflare_url"] == "https://test.example.com/sse"


def test_tunnel_overview_defaults(monkeypatch):
    monkeypatch.delenv("KATER_DOMAIN", raising=False)
    overview = tunnel_overview()
    assert overview["suggested_domain"] == "kater.example.com"


def test_start_cloudflared_not_installed(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda cmd: None)
    info = start_cloudflared()
    assert info.running is False
    assert info.error is not None and "cloudflared not installed" in info.error
    assert info.provider == "cloudflare"


def test_start_cloudflared_managed_unit_success(monkeypatch):
    monkeypatch.setenv("KATER_TUNNEL_UNIT", "test-unit.service")

    def mock_which(cmd: str):
        if cmd in {"cloudflared", "systemctl"}:
            return f"/usr/bin/{cmd}"
        return None

    def mock_run(args, capture_output=True, text=True, timeout=8):
        # args: ["systemctl", "--user", <cmd>, <unit>]
        if args[:2] == ["systemctl", "--user"]:
            if args[2] == "cat" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="")
            if args[2] == "start" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="")
            if args[2] == "is-active" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="inactive")
        raise AssertionError(f"Unexpected subprocess.run call: {args}")

    monkeypatch.setattr("shutil.which", mock_which)
    monkeypatch.setattr("subprocess.run", mock_run)

    info = start_cloudflared(domain="test.local")
    assert info.running is True
    assert info.name == "test-unit.service"
    assert info.url == "https://test.local"
    assert info.error is None
    assert info.config["managed_unit"] == "test-unit.service"


def test_start_cloudflared_managed_unit_already_active(monkeypatch):
    monkeypatch.setenv("KATER_TUNNEL_UNIT", "test-unit.service")

    def mock_which(cmd: str):
        if cmd in {"cloudflared", "systemctl"}:
            return f"/usr/bin/{cmd}"
        return None

    def mock_run(args, capture_output=True, text=True, timeout=8):
        if args[:2] == ["systemctl", "--user"]:
            if args[2] == "cat" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="")
            if args[2] == "start" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="")
            if args[2] == "is-active" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="active")
        raise AssertionError(f"Unexpected subprocess.run call: {args}")

    monkeypatch.setattr("shutil.which", mock_which)
    monkeypatch.setattr("subprocess.run", mock_run)

    info = start_cloudflared(domain="test.local")
    assert info.running is True
    assert info.error == "Failed to start tunnel unit."


def test_start_cloudflared_managed_unit_fail(monkeypatch):
    monkeypatch.setenv("KATER_TUNNEL_UNIT", "test-unit.service")

    def mock_which(cmd: str):
        if cmd in {"cloudflared", "systemctl"}:
            return f"/usr/bin/{cmd}"
        return None

    def mock_run(args, capture_output=True, text=True, timeout=8):
        if args[:2] == ["systemctl", "--user"]:
            if args[2] == "cat" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="")
            if args[2] == "start" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="")
            if args[2] == "is-active" and args[3] == "test-unit.service":
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="inactive")
        raise AssertionError(f"Unexpected subprocess.run call: {args}")

    monkeypatch.setattr("shutil.which", mock_which)
    monkeypatch.setattr("subprocess.run", mock_run)

    info = start_cloudflared(domain="test.local")
    assert info.running is False
    assert info.error == "Failed to start tunnel unit."
    assert info.url is None


def test_start_cloudflared_popen_success(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda cmd: f"/usr/bin/{cmd}" if cmd == "cloudflared" else None)
    monkeypatch.delenv("KATER_TUNNEL_UNIT", raising=False)
    monkeypatch.setattr("time.sleep", lambda s: None)  # speed up test

    config_path = tmp_path / "my-tunnel.yml"

    m_proc = MagicMock()
    m_proc.poll.return_value = None  # Process is running
    m_proc.pid = 12345

    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: m_proc)

    info = start_cloudflared(
        tunnel_name="my-tunnel",
        config_path=str(config_path),
        domain="test.local",
    )

    assert info.running is True
    assert info.name == "my-tunnel"
    assert info.pid == 12345
    assert info.url == "https://test.local"
    assert info.error is None

    assert config_path.exists()
    assert "tunnel: my-tunnel" in config_path.read_text()


def test_start_cloudflared_popen_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "shutil.which",
        lambda cmd: f"/usr/bin/{cmd}" if cmd == "cloudflared" else None,
    )
    monkeypatch.delenv("KATER_TUNNEL_UNIT", raising=False)

    # Provide an existing config file so start_cloudflared doesn't need to write one.
    config_path = tmp_path / "my-tunnel.yml"
    config_path.write_text("tunnel: my-tunnel\n")

    def raise_exception(*args, **kwargs):
        raise Exception("spawn error")

    monkeypatch.setattr("subprocess.Popen", raise_exception)

    info = start_cloudflared(tunnel_name="my-tunnel", config_path=str(config_path))

    assert info.running is False
    assert info.error == "spawn error"
    assert info.provider == "cloudflare"
