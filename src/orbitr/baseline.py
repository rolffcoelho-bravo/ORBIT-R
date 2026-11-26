"""Transparent public baseline; its statistical novelty is NOT claimed."""
from __future__ import annotations
import math, statistics
from dataclasses import dataclass

def features(s):
    x=s.values
    d=[b-a for a,b in zip(x,x[1:])]
    return (statistics.median(x),math.log1p(statistics.pstdev(x)),math.log1p(statistics.median(abs(a) for a in d)),math.log1p(max(abs(a) for a in d)),math.log1p((s.end-s.start).total_seconds()))

def profile(rows):
    med=tuple(statistics.median(r[i] for r in rows) for i in range(len(rows[0])))
    mad=tuple(max(1e-6,statistics.median(abs(r[i]-med[i]) for r in rows)*1.4826) for i in range(len(med)))
    return med,mad

def score(v,center,mad):
    return max(min(1e6,abs(x-a)/b) for x,a,b in zip(v,center,mad))

@dataclass
class Finding:
    status:str
    score:float|None
    threshold:float|None
    explanation:str

class Baseline:
    def __init__(self):self.profiles={}
    def fit(self,segments):
        groups={}
        for s in segments:
            if s.train:groups.setdefault(s.channel,[]).append(s)
        for channel,group in groups.items():
            group.sort(key=lambda s:(s.end,s.segment))
            if len(group)<10:continue
            k=max(6,min(len(group)-3,int(len(group)*.65)))
            med,mad=profile([features(s) for s in group[:k]])
            calibration=sorted(score(features(s),med,mad) for s in group[k:])
            threshold=max(3.0,calibration[min(len(calibration)-1,math.ceil(.95*len(calibration))-1)])
            self.profiles[channel]=(med,mad,threshold)
        return self
    def assess(self,s):
        if s.channel not in self.profiles:return Finding("ABSTAIN",None,None,"Insufficient training evidence")
        med,mad,limit=self.profiles[s.channel]
        value=score(features(s),med,mad)
        return Finding("INVESTIGATE" if value>limit else "NORMAL",round(value,4),round(limit,4),"Reference robust feature score; not a failure probability")
