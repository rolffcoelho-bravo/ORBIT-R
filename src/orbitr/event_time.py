"""Source-bound event-time contracts for future native multichannel adapters."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from urllib.parse import urlparse


def utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must carry a timezone")
    return value.astimezone(timezone.utc)


def source_ok(uri: str, sha256: str) -> None:
    if urlparse(uri).scheme not in {"https", "file"}:
        raise ValueError("source URI must be an HTTPS or file URI")
    if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256.lower()):
        raise ValueError("source SHA-256 must be a 64-digit hexadecimal digest")


@dataclass(frozen=True)
class Reading:
    mission_id: str
    channel_id: str
    event_time_utc: datetime
    ingest_time_utc: datetime
    value: float
    quality: str
    source_uri: str
    source_sha256: str

    def __post_init__(self) -> None:
        if not self.mission_id or not self.channel_id or not self.quality:
            raise ValueError("mission, channel and quality are required")
        if not isfinite(self.value):
            raise ValueError("nonfinite telemetry value")
        object.__setattr__(self, "event_time_utc", utc(self.event_time_utc))
        object.__setattr__(self, "ingest_time_utc", utc(self.ingest_time_utc))
        source_ok(self.source_uri, self.source_sha256)


@dataclass(frozen=True)
class Command:
    mission_id: str
    command_id: str
    event_time_utc: datetime
    available_time_utc: datetime
    source_uri: str
    source_sha256: str

    def __post_init__(self) -> None:
        if not self.mission_id or not self.command_id:
            raise ValueError("mission and command ID are required")
        object.__setattr__(self, "event_time_utc", utc(self.event_time_utc))
        object.__setattr__(self, "available_time_utc", utc(self.available_time_utc))
        source_ok(self.source_uri, self.source_sha256)


def validate_readings(rows: list[Reading]) -> list[Reading]:
    """Preserve source order; reject duplicates and per-channel time reversal."""
    last: dict[tuple[str, str], datetime] = {}
    for row in rows:
        key = row.mission_id, row.channel_id
        previous = last.get(key)
        if previous is not None and row.event_time_utc <= previous:
            raise ValueError(f"duplicate or nonmonotonic source time for {key}")
        last[key] = row.event_time_utc
    return rows


def commands_as_of(commands: list[Command], mission_id: str, decision_time: datetime) -> list[Command]:
    """Only commands both executed and available by the decision time qualify."""
    instant = utc(decision_time)
    return [command for command in commands if command.mission_id == mission_id
            and command.event_time_utc <= instant and command.available_time_utc <= instant]
