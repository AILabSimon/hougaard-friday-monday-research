"""Level grids needed for Cycle-2 entry testing, NAS100/US500, RTH + BROKER.

  open grid : first-touch minute of  Monday_open + k*ATR,  k in [-3, +3] step 0.25
  low grid  : first-touch minute of  Friday_low  + k*ATR,  k in [-2, +2] step 0.25
Both are first-touch from session start, so ordering between any two levels is exact.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, year_files, session_key

KO = np.round(np.arange(-3.0, 3.01, 0.25), 2)
KL = np.round(np.arange(-2.0, 2.01, 0.25), 2)


def build(inst, sdef, T):
    tr = T[(T.instrument == inst) & (T.sessdef == sdef) & (T.B_wd == 4) &
           (T.C_wd == 0) & (T.atr_at_B > 0) & (T.B_range > 0)].copy()
    want = {d: i for d, i in zip(pd.DatetimeIndex(tr.C_date).normalize(), tr.index)}
    recs = {}
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low"])
        ts = pd.DatetimeIndex(df["timestamp"])
        key, mask = session_key(ts, inst, sdef)
        df = df.loc[mask].assign(sdate=key[mask]).sort_values("timestamp")
        for sdate, g in df.groupby("sdate", sort=False):
            i = want.get(sdate)
            if i is None:
                continue
            r = tr.loc[i]
            o = g.open.iloc[0]; a = r.atr_at_B
            rmax = np.maximum.accumulate(g.high.values)
            rmin = np.minimum.accumulate(g.low.values)
            n = len(g); mins = np.arange(n, dtype=float)
            rec = {"C_open_px": o, "n": n}
            for tag, base, ks in (("o", o, KO), ("l", r.B_low, KL)):
                for k in ks:
                    lvl = base + k * a
                    w = np.flatnonzero(rmin <= lvl) if k < 0 or tag == "l" and k <= 0 else np.flatnonzero(rmax >= lvl)
                    # for the low grid, negative k is below Friday's low (a down move),
                    # positive k is above it (an up move) -> direction by sign
                    if tag == "l":
                        w = np.flatnonzero(rmin <= lvl) if k <= 0 else np.flatnonzero(rmax >= lvl)
                    else:
                        w = np.flatnonzero(rmin <= lvl) if k < 0 else np.flatnonzero(rmax >= lvl)
                    rec[f"{tag}{k:+.2f}"] = mins[w[0]] if len(w) else np.nan
            recs[i] = rec
        del df
    return tr.join(pd.DataFrame.from_dict(recs, orient="index"), how="inner")


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    parts = []
    for inst in ["NAS100", "US500"]:
        for sdef in ["RTH", "BROKER"]:
            g = build(inst, sdef, T)
            print(inst, sdef, len(g), flush=True)
            parts.append(g)
    pd.concat(parts, ignore_index=True).to_parquet(DERIVED / "c2_grid.parquet", index=False)
    print("saved")
