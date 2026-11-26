"""Only deterministic manufactured software fixtures; never empirical evidence."""
import csv
from datetime import datetime,timedelta,timezone
from orbitr.telemetry import load,is_train
from orbitr.baseline import Baseline

def test_original_schema_and_split(tmp_path):
    p=tmp_path/"segments.csv"
    t=datetime(2020,1,1,tzinfo=timezone.utc)
    with p.open("w",newline="") as stream:
        w=csv.writer(stream);w.writerow(["timestamp","channel","value","label","segment","sampling","train"])
        for i in range(16):
            for j in range(4):
                w.writerow([(t+timedelta(minutes=i,seconds=j)).isoformat(),"SENSOR",i*.001+j,"0",i,"1",str(i<13)])
    segments=load(p)
    assert len(segments)==16
    assert segments[0].values==(0.0,1.0,2.0,3.0)
    trained=Baseline().fit(segments)
    assert "SENSOR" in trained.profiles
    assert trained.assess(segments[-1]).status in ("NORMAL","INVESTIGATE")
    assert trained.profiles==Baseline().fit(segments[:13]).profiles

def test_bad_split_rejected():
    import pytest
    with pytest.raises(ValueError):is_train("unknown")
