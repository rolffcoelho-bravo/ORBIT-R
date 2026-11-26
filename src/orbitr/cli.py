"""Pinned original-source downloader, audit and time-ordered replay."""
import argparse, json, os, shutil, tempfile, urllib.request
from pathlib import Path
from .telemetry import URL,MD5,digest,load
from .baseline import Baseline

def download(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(path.parent),suffix=".csv");os.close(fd)
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"ORBIT-R/0.1 provenance"})
        with urllib.request.urlopen(req,timeout=120) as r,open(tmp,"wb") as out:shutil.copyfileobj(r,out)
        if digest(tmp,"md5")!=MD5:raise ValueError("Upstream MD5 mismatch; rejected")
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    path.with_suffix(".manifest.json").write_text(json.dumps({"source":URL,"doi":"10.5281/zenodo.12588359","md5":MD5,"sha256":digest(path),"kind":"real historical telemetry"},indent=2))
    return digest(path)

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=["fetch-data","audit-data","replay"])
    p.add_argument("--data",default="data/raw/segments.csv")
    p.add_argument("--db",default="data/state/orbitr.sqlite3")
    a=p.parse_args(argv)
    if a.command=="fetch-data":print(download(a.data));return
    samples=load(a.data,check=True)
    if a.command=="audit-data":
        print(json.dumps({"sha256":digest(a.data),"segments":len(samples),"channels":len({s.channel for s in samples}),"train":sum(s.train for s in samples),"test":sum(not s.train for s in samples)},indent=2));return
    from .app import State  # optional web dependency only needed by replay command
    state=State(a.db);model=Baseline().fit(samples);state.clear()
    for s in samples:state.write(s,model.assess(s))
    print(json.dumps({"mode":"historical real-data replay","processed":len(samples),"db":a.db,"sha256":digest(a.data)},indent=2))

if __name__=="__main__":main()
