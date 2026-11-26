"""Read-only historical real-data spacecraft telemetry replay/API. NOT A LIVE DOWNLINK."""
import json,os,sqlite3,threading,time
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .telemetry import load,digest
from .baseline import Baseline

class State:
    def __init__(self,path):
        self.path=str(path);Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY, source_key TEXT UNIQUE, channel TEXT, ts TEXT,
            label TEXT, train INTEGER, status TEXT, score REAL, threshold REAL,
            explanation TEXT, samples INTEGER, trace TEXT)""")
    def db(self):
        db=sqlite3.connect(self.path,timeout=10);db.row_factory=sqlite3.Row;return db
    def clear(self):
        with self.db() as db:db.execute("DELETE FROM events")
    def write(self,s,result):
        step=max(1,len(s.values)//110)
        trace=[{"ts":t.isoformat(),"v":v} for t,v in zip(s.times[::step],s.values[::step])]
        with self.db() as db:
            db.execute("""INSERT OR IGNORE INTO events(source_key,channel,ts,label,train,status,score,threshold,explanation,samples,trace)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(s.channel+":"+s.segment,s.channel,s.start.isoformat(),
            s.label,int(s.train),result.status,result.score,result.threshold,result.explanation,len(s.values),json.dumps(trace)))
    def events(self,channel="",limit=100):
        with self.db() as db:
            if channel:r=db.execute("SELECT * FROM events WHERE channel=? ORDER BY id DESC LIMIT ?",(channel,min(500,max(1,limit)))).fetchall()
            else:r=db.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?",(min(500,max(1,limit)),)).fetchall()
        return [{**dict(x),"trace":json.loads(x["trace"])} for x in r]
    def stats(self):
        with self.db() as db:
            n=db.execute("SELECT count(*) FROM events").fetchone()[0]
            channels=db.execute("SELECT count(DISTINCT channel) FROM events").fetchone()[0]
            statuses={a:b for a,b in db.execute("SELECT status,count(*) FROM events GROUP BY status").fetchall()}
        return {"segments":n,"channels":channels,"assessments":statuses}

store=None;worker=None;error=None;sourcehash=None;segments_count=0;counter=0;finished=False

def run_replay(samples,pace):
    global counter,finished
    model=Baseline().fit(samples);store.clear()
    for s in samples:
        store.write(s,model.assess(s));counter+=1
        if pace>0:time.sleep(pace)
    finished=True

@asynccontextmanager
async def lifespan(app):
    global store,worker,error,sourcehash,segments_count,counter,finished
    store=State(os.getenv("ORBITR_DB","data/state/orbitr.sqlite3"))
    path=os.getenv("ORBITR_DATA","data/raw/segments.csv")
    if Path(path).is_file():
        try:
            samples=load(path);sourcehash=digest(path);segments_count=len(samples)
            counter=0;finished=False
            worker=threading.Thread(target=run_replay,args=(samples,float(os.getenv("ORBITR_PACE","0.5"))),daemon=True)
            worker.start()
        except Exception as exc:error=f"Raw data rejected: {type(exc).__name__}: {exc}"
    else:error="No original source data. Run: python -m orbitr.cli fetch-data"
    yield

app=FastAPI(title="ORBIT-R Research Monitor",version="0.1.0",lifespan=lifespan)

@app.get("/health")
def health():return {"service":"ok","source_loaded":sourcehash is not None,"mode":"historical replay" if sourcehash else "no data"}

@app.get("/api/status")
def status():return {"name":"ORBIT-R","mode":"HISTORICAL REAL-DATA REPLAY — NOT LIVE TELEMETRY","doi":"10.5281/zenodo.12588359","sha256":sourcehash,"processed":counter,"total":segments_count,"complete":finished,"error":error,"stats":store.stats() if store else {}}

@app.get("/api/events")
def events(channel:str="",limit:int=100):return {"items":store.events(channel,limit) if store else []}

@app.get("/api/channels")
def channels():return {"channels":sorted({e["channel"] for e in store.events("",500)}) if store else []}

@app.get("/",response_class=HTMLResponse)
def home():return (Path(__file__).parent/"web.html").read_text(encoding="utf-8")
