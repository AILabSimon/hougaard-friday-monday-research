"""First-touch minute for a grid of ATR-spaced levels around Monday's open.
Lets any open-anchored stop/target combination be simulated exactly from 1m bars."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, year_files, session_key

KS = np.round(np.arange(-3.0, 3.01, 0.25), 2)     # level = C_open + k*ATR


def grid(inst, sdef, triples):
    tr = triples[(triples.instrument == inst) & (triples.sessdef == sdef) &
                 (triples.B_wd == 4) & (triples.C_wd == 0) & (triples.atr_at_B > 0)].copy()
    want = dict(zip(pd.DatetimeIndex(tr.C_date).normalize(), tr.index))
    recs = {}
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low"])
        ts = pd.DatetimeIndex(df["timestamp"])
        key, mask = session_key(ts, inst, sdef)
        df = df.loc[mask].assign(sdate=key[mask]).sort_values("timestamp")
        for sdate, g in df.groupby("sdate", sort=False):
            idx = want.get(sdate)
            if idx is None:
                continue
            r = tr.loc[idx]
            o = g["open"].iloc[0]; atr = r.atr_at_B
            hi = g["high"].values; lo = g["low"].values
            n = len(g)
            mins = np.arange(n, dtype=float)
            rec = {"C_open_px": o, "n": n}
            runmin = np.minimum.accumulate(lo); runmax = np.maximum.accumulate(hi)
            for k in KS:
                lvl = o + k * atr
                if k < 0:
                    w = np.flatnonzero(runmin <= lvl)
                else:
                    w = np.flatnonzero(runmax >= lvl)
                rec[f"t{k:+.2f}"] = mins[w[0]] if len(w) else np.nan
            recs[idx] = rec
        del df
    if not recs:
        return None
    R = pd.DataFrame.from_dict(recs, orient="index")
    return tr.join(R, how="inner")


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    parts = []
    for inst in sys.argv[1:]:
        for sdef in ["RTH", "BROKER"]:
            r = grid(inst, sdef, T)
            if r is not None:
                parts.append(r); print(inst, sdef, len(r), flush=True)
    pd.concat(parts, ignore_index=True).to_parquet(DERIVED / "monday_grid.parquet", index=False)
    print("saved")
