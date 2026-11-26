"""Manufactured fixture verifies that evaluation labels stay off the dashboard API."""
from datetime import datetime, timezone
from types import SimpleNamespace
import asyncio
import importlib
import os
import sqlite3
from unittest.mock import patch
import pytest

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
    with state.db() as db:
        stored=db.execute("SELECT label,train FROM events").fetchone()
    assert tuple(stored)==(None,None)


def test_channel_inventory_includes_older_events(tmp_path):
    state=State(tmp_path / "monitor.sqlite3")
    with state.db() as db:
        db.executemany("INSERT INTO events(source_key,channel) VALUES(?,?)",
                       [(str(i),"OLDER" if i==0 else "RECENT") for i in range(501)])
    assert state.channels()==["OLDER","RECENT"]


def test_database_context_closes_connection(tmp_path):
    state=State(tmp_path/"monitor.sqlite3")
    with state.db() as connection:
        assert connection.execute("SELECT 1").fetchone()[0]==1
    with pytest.raises(sqlite3.ProgrammingError,match="closed"):
        connection.execute("SELECT 1")


def test_startup_rejects_unpinned_source_and_clears_stale_events(tmp_path):
    database=tmp_path/"monitor.sqlite3"
    state=State(database)
    with state.db() as db:
        db.execute("INSERT INTO events(source_key,channel) VALUES('old','OLD')")
    source=tmp_path/"manufactured.csv"
    source.write_text("timestamp,channel,value,label,segment,sampling,train\n",encoding="utf-8")
    monitor=importlib.import_module("orbitr.app")

    async def check():
        with patch.dict(os.environ,{"ORBITR_DB":str(database),"ORBITR_DATA":str(source)}):
            async with monitor.lifespan(monitor.app):
                assert monitor.sourcehash is None
                assert "checksum" in monitor.error
                assert monitor.store.events()==[]
    asyncio.run(check())
