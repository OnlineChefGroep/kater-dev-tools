"""Robustness guards for the telemetry storage layer."""

from __future__ import annotations

from kater.storage import _jsonl_query, _row_to_dict, clear_all_events, insert_event

from kater.settings import KaterSettings, invalidate_settings_cache, save_settings


def test_jsonl_query_skips_corrupt_lines(tmp_path, monkeypatch) -> None:
    path = tmp_path / "telemetry.jsonl"
    path.write_text(
        '{"type":"tool_call","name":"a","timestamp":1}\n'
        "this is not json\n"
        "\n"
        '{"type":"tool_call","name":"b","timestamp":2}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("kater.storage._jsonl_path", lambda: path)

    events = _jsonl_query()
    assert [e["name"] for e in events] == ["a", "b"]


def test_jsonl_query_respects_limit(tmp_path, monkeypatch) -> None:
    lines = "".join(
        f'{{"type":"tool_call","name":"n{i}","timestamp":{i}}}\n' for i in range(10)
    )
    path = tmp_path / "telemetry.jsonl"
    path.write_text(lines, encoding="utf-8")
    monkeypatch.setattr("kater.storage._jsonl_path", lambda: path)

    recent = _jsonl_query(limit=3)
    assert [e["name"] for e in recent] == ["n7", "n8", "n9"]


def test_row_to_dict_tolerates_corrupt_metadata() -> None:
    row = {
        "type": "error",
        "name": "x",
        "timestamp": 1.0,
        "duration_ms": 0,
        "success": 0,
        "profile": None,
        "metadata": "{not valid json",
    }
    result = _row_to_dict(row)
    assert result["metadata"] == {"_parse_error": True}
    assert result["success"] is False


def test_clear_all_events_jsonl_empty(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    save_settings(KaterSettings(storage_backend="jsonl"))
    invalidate_settings_cache()

    path = tmp_path / ".kater" / "telemetry.jsonl"

    # File does not exist yet
    assert not path.exists()
    assert clear_all_events() == 0


def test_clear_all_events_jsonl_with_events(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    save_settings(KaterSettings(storage_backend="jsonl"))
    invalidate_settings_cache()

    for i in range(5):
        insert_event({"type": "tool_call", "name": f"n{i}", "timestamp": i})

    path = tmp_path / ".kater" / "telemetry.jsonl"
    assert path.exists()

    assert clear_all_events() == 5
    assert not path.exists()
