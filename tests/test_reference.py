"""Only deterministic manufactured software fixtures; never empirical evidence."""
import csv
from datetime import datetime,timedelta,timezone
from orbitr.telemetry import load,is_train
from orbitr.baseline import Baseline
import pytest

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
    with pytest.raises(ValueError):is_train("unknown")


def test_simultaneous_readings_keep_source_order_and_checksum_gate(tmp_path):
    path=tmp_path/"segments.csv"
    with path.open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["timestamp","channel","value","label","segment","sampling","train"])
        for time,value in [("2020-01-01T00:00:00Z",2),("2020-01-01T00:00:00Z",1),
                           ("2020-01-01T00:00:01Z",3)]:
            writer.writerow([time,"TEST",value,"a2","one","1s","true"])
    assert load(path)[0].values==(2.0,1.0,3.0)
    with pytest.raises(ValueError,match="checksum"):
        load(path,check=True)


def test_refit_discards_old_baseline_profiles(tmp_path):
    path=tmp_path/"segments.csv"
    with path.open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["timestamp","channel","value","label","segment","sampling","train"])
        for i in range(12):
            for j in range(3):
                writer.writerow([f"2020-01-01T00:{i:02d}:{j:02d}Z","A",j,"a2",i,"1s","true"])
    model=Baseline().fit(load(path))
    assert "A" in model.profiles
    model.fit([])
    assert model.profiles=={}


@pytest.mark.parametrize("timestamp,value,sampling,expected",[
    ("2020-01-01T00:00:00",1,"1s","timezone"),
    ("2020-01-01T00:00:00Z","nan","1s","Nonfinite"),
    ("2020-01-01T00:00:00Z",1,"different","sampling"),
])
def test_source_anomalies_fail_closed(tmp_path,timestamp,value,sampling,expected):
    path=tmp_path/"segments.csv"
    with path.open("w",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["timestamp","channel","value","label","segment","sampling","train"])
        writer.writerow(["2020-01-01T00:00:00Z","A",1,"a2","one","1s","true"])
        writer.writerow([timestamp,"A",value,"a2","one",sampling,"true"])
        writer.writerow(["2020-01-01T00:00:02Z","A",2,"a2","one","1s","true"])
    with pytest.raises(ValueError,match=expected):
        load(path)
