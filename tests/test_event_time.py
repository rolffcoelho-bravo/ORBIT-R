"""Manufactured event fixtures; not empirical telemetry evidence."""
from datetime import datetime, timedelta, timezone

import pytest

from orbitr.event_time import Command, Reading, commands_as_of, validate_readings


T = datetime(2020, 1, 1, tzinfo=timezone.utc)
HASH = "a" * 64
URI = "https://example.org/TEST_FIXTURE.csv"


def reading(at: datetime, channel: str = "A") -> Reading:
    return Reading("TEST_MISSION", channel, at, at + timedelta(seconds=2),
                   1.0, "TEST_FIXTURE", URI, HASH)


def test_monotonicity_is_per_channel_and_source_order_is_preserved():
    rows = [reading(T, "A"), reading(T, "B"), reading(T + timedelta(seconds=1), "A")]
    assert validate_readings(rows) is rows
    with pytest.raises(ValueError, match="nonmonotonic"):
        validate_readings([reading(T), reading(T)])


def test_future_or_late_command_is_not_visible():
    commands = [
        Command("TEST_MISSION", "past", T, T, URI, HASH),
        Command("TEST_MISSION", "late", T, T + timedelta(minutes=2), URI, HASH),
        Command("TEST_MISSION", "future", T + timedelta(minutes=2), T, URI, HASH),
    ]
    assert [c.command_id for c in commands_as_of(commands, "TEST_MISSION", T)] == ["past"]


def test_naive_time_and_invalid_source_are_rejected():
    with pytest.raises(ValueError, match="timezone"):
        reading(datetime(2020, 1, 1))
    with pytest.raises(ValueError, match="SHA-256"):
        Reading("M", "C", T, T, 1.0, "ok", URI, "bad")
    with pytest.raises(ValueError, match="host"):
        Reading("M", "C", T, T, 1.0, "ok", "https:missing-host", HASH)
