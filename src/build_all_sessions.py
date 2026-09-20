import sys, time, json
from pathlib import Path
import pandas as pd, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DUKA, SESSION_DEFS, build_sessions, DERIVED, ASSET_CLASS

DERIVED.mkdir(parents=True, exist_ok=True)
(DERIVED / "sessions").mkdir(exist_ok=True)

only = sys.argv[1:] or DUKA
log = {}
for inst in only:
    t0 = time.time()
    res = build_sessions(inst, "BID")
    for s, df in res.items():
        df = df.copy()
        df["weekday"] = pd.DatetimeIndex(df["sdate"]).dayofweek
        df["instrument"] = inst
        df["sessdef"] = s
        df.to_parquet(DERIVED / "sessions" / f"{inst}_{s}.parquet", index=False)
    log[inst] = {s: dict(n=len(d), first=str(d["sdate"].min()), last=str(d["sdate"].max()),
                         wd=dict(pd.DatetimeIndex(d["sdate"]).dayofweek.value_counts().sort_index()))
                 for s, d in res.items()}
    print(f"{inst} done in {time.time()-t0:.0f}s", flush=True)
    for s, d in res.items():
        wd = pd.DatetimeIndex(d["sdate"]).dayofweek.value_counts().sort_index().to_dict()
        print(f"   {s:7s} n={len(d):6d} {d['sdate'].min().date()}..{d['sdate'].max().date()} wd={wd} medbars={int(d['n_bars'].median())}", flush=True)
json.dump(log, open(DERIVED / "sessions_build_log.json", "w"), indent=1, default=str)
print("ALL DONE")
