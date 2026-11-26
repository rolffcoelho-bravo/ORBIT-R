"""Manufactured fixture verifies that evaluation labels stay off the dashboard API."""
from datetime import datetime, timezone
from types import SimpleNamespace

from orbitr.app import State


def test_dashboard_event_excludes_expert_labels_and_split(tmp_path):
    state = State(tmp_path / "monitor.sqlite3")
    sample = SimpleNamespace(
        channel="TEST_CHANNEL", segment="TEST_FIXTURE_1",
        start=datetime(2020, 1, 1, tzinfo=timezone.utc),
        times=[datetime(2020, 1, 1, tzinfo=timezone.utc)] * 3,
        values=[1.0, 2.0, 3.0], label="anomaly", train=False,
    )
    finding = SimpleNamespace(status="INVESTIGATE", score=4.0,
                              threshold=3.0, explanation="TEST_FIXTURE")
    state.write(sample, finding)
    row = state.events()[0]
    assert "label" not in row
    assert "train" not in row
    assert row["channel"] == "TEST_CHANNEL"
    assert row["trace"][0]["v"] == 1.0
