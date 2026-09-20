"""Monday intraday path anatomy from 1-minute bars.

For every (A,B,C) triple with B=Friday we walk C's 1m bars and record, relative to
C's open: first-touch minute of Friday's low, of Friday's high, of Thursday's high,
MFE/MAE, and the running excursion profile.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import (DERIVED, OUT, year_files, session_key, DUKA)

SESSDEFS = ["RTH", "BROKER"]


def monday_paths(inst, sdef, triples):
    """Return per-triple intraday path stats for the C session."""
    tr = triples[(triples.instrument == inst) & (triples.sessdef == sdef) &
                 (triples.B_wd == 4) & (triples.C_wd == 0)].copy()
    if tr.empty:
        return None
    want = dict(zip(pd.DatetimeIndex(tr.C_date).normalize(), tr.index))
    recs = {}
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low", "close"])
        ts = pd.DatetimeIndex(df["timestamp"])
        key, mask = session_key(ts, inst, sdef)
        df = df.loc[mask]
        kk = key[mask]
        df = df.assign(sdate=kk).sort_values("timestamp")
        for sdate, g in df.groupby("sdate", sort=False):
            idx = want.get(sdate)
            if idx is None:
                continue
            r = tr.loc[idx]
            o = g["open"].iloc[0]
            hi = g["high"].values; lo = g["low"].values
            t0 = g["timestamp"].iloc[0]
            mins = ((g["timestamp"] - t0).dt.total_seconds() / 60).values
            n = len(g)
            def first_le(arr, level):     # first minute low <= level
                w = np.flatnonzero(arr <= level)
                return mins[w[0]] if len(w) else np.nan
            def first_ge(arr, level):
                w = np.flatnonzero(arr >= level)
                return mins[w[0]] if len(w) else np.nan
            t_Blow = first_le(lo, r.B_low)
            t_Bhigh = first_ge(hi, r.B_high)
            t_Ahigh = first_ge(hi, r.A_high)
            runmin = np.minimum.accumulate(lo)
            runmax = np.maximum.accumulate(hi)
            # adverse excursion before Friday-low touch (short-from-open view)
            if not np.isnan(t_Blow):
                j = int(np.flatnonzero(lo <= r.B_low)[0])
                mae_before = runmax[j] - o
            else:
                mae_before = np.nan
            recs[idx] = dict(
                n_bars=n, session_minutes=mins[-1] + 1,
                C_open_px=o,
                t_Blow=t_Blow, t_Bhigh=t_Bhigh, t_Ahigh=t_Ahigh,
                frac_Blow=t_Blow / (mins[-1] + 1) if not np.isnan(t_Blow) else np.nan,
                mfe_down=o - lo.min(), mfe_up=hi.max() - o,
                mae_before_touch=mae_before,
            )
        del df
    if not recs:
        return None
    R = pd.DataFrame.from_dict(recs, orient="index")
    out = tr.join(R, how="inner")
    return out


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    insts = sys.argv[1:] or DUKA
    parts = []
    for inst in insts:
        for sdef in SESSDEFS:
            r = monday_paths(inst, sdef, T)
            if r is not None:
                parts.append(r)
                print(f"{inst} {sdef}: {len(r)} Mondays", flush=True)
    big = pd.concat(parts, ignore_index=True)
    big.to_parquet(DERIVED / "monday_paths.parquet", index=False)
    print("saved", len(big))
