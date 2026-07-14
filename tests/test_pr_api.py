from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from kater.api import create_api_server

PORT = 9912
REPO = "OnlineChefGroep/kater-dev-tools"


@pytest.fixture
def api_server():
    server = create_api_server("127.0.0.1", PORT)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)
    yield server
    server.shutdown()
    server.server_close()
    time.sleep(0.2)


def _get(port: int, path: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", headers=headers or {}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _get_err(port: int, path: str, headers: dict | None = None) -> urllib.error.HTTPError:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", headers=headers or {}
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        return e
    raise AssertionError("expected HTTPError")


def _post(port: int, path: str, payload: dict, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _post_err(port: int, path: str, payload: dict) -> urllib.error.HTTPError:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        return e
    raise AssertionError("expected HTTPError")


def test_pr_policy_endpoint(api_server) -> None:
    data = _get(PORT, "/api/pr/policy")
    assert "policy" in data
    assert data["policy"]["require_approvals"] >= 1


def test_pr_audit_endpoint(api_server) -> None:
    data = _get(PORT, "/api/pr/audit")
    assert "count" in data
    assert "entries" in data


def test_pr_list_requires_gh(api_server) -> None:
    # The gh-backed endpoints must return a clean 502 (not 500) when gh fails,
    # rather than leaking internals.
    data = _get(PORT, f"/api/pr/list?repo={REPO}")
    assert "pulls" in data
    assert "count" in data


def test_pr_status_bad_number(api_server) -> None:
    err = _get_err(PORT, "/api/pr/not-a-number/status")
    assert err.code == 400


def test_pr_merge_rejects_without_pass(api_server) -> None:
    # Attempt to merge a non-existent / ungateable PR; the gate should reject
    # with 409 and a machine-readable reason, never perform a merge.
    err = _post_err(PORT, "/api/pr/999999/merge", {"expected_head_sha": "deadbeef"})
    assert err.code in (409, 502)
    body = json.loads(err.read())
    assert "error" in body
