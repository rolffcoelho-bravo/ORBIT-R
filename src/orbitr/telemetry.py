"""Version-pinned original OPS-SAT segment reader, preserving source timing."""
from __future__ import annotations
import csv, hashlib, math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

URL="https://zenodo.org/records/12588359/files/segments.csv?download=1"
MD5="1f4b6ffd0359efac96a6698ff557e0f9"
REQUIRED={"timestamp","channel","value","label","segment","sampling","train"}

def digest(path, algo="sha256"):
    h=hashlib.new(algo)
    with open(path,"rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):h.update(block)
    return h.hexdigest()

def is_train(x):
    x=str(x).strip().lower()
    if x in ("true","t","1","yes"):return True
    if x in ("false","f","0","no"):return False
    raise ValueError("ambiguous train flag: "+x)

def parse_time(x):
    t=datetime.fromisoformat(x.replace("Z","+00:00"))
    if t.tzinfo is None or t.utcoffset() is None:raise ValueError("Source timestamp lacks a timezone")
    return t.astimezone(timezone.utc)

@dataclass(frozen=True)
class Segment:
    channel:str
    segment:str
    times:tuple
    values:tuple
    label:str
    train:bool
    sampling:str
    @property
    def start(self):return self.times[0]
    @property
    def end(self):return self.times[-1]

def load(path,check=False):
    path=Path(path)
    if not path.is_file():raise FileNotFoundError("Original telemetry missing: "+str(path))
    if check and digest(path,"md5")!=MD5:raise ValueError("Pinned source checksum mismatch")
    g={}
    with path.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        if not REQUIRED.issubset(reader.fieldnames or []):raise ValueError("Invalid original OPS-SAT schema")
        for row in reader:
            key=(row["channel"],row["segment"])
            value=float(row["value"])
            if not math.isfinite(value):raise ValueError("Nonfinite source observation")
            train=is_train(row["train"])
            t=parse_time(row["timestamp"])
            if key not in g:g[key]=[[],[],str(row["label"]),train,str(row["sampling"])]
            item=g[key]
            if item[2]!=str(row["label"]) or item[3]!=train or item[4]!=str(row["sampling"]):
                raise ValueError("Inconsistent split/annotation/sampling")
            item[0].append(t);item[1].append(value)
    out=[]
    for (channel,sid),(times,values,label,train,sampling) in g.items():
        if len(values)<3:continue
        # Python's stable sort retains source order for simultaneous readings.
        pairs=sorted(zip(times,values),key=lambda pair:pair[0])
        out.append(Segment(channel,sid,tuple(t for t,v in pairs),tuple(v for t,v in pairs),label,train,sampling))
    if not out:raise ValueError("No valid source observations")
    return sorted(out,key=lambda s:(s.start,s.channel,s.segment))
