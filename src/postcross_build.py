"""FINAL FUTURES/CFD TEST — the post-open-cross construction.

Signal (fully observable at the moment it fires, no hindsight):
  A. Monday first trades to +0.25 ATR or -0.25 ATR from its open   -> leg direction, t0
  B. Price subsequently trades back THROUGH the Monday open        -> cross, tc
  C. Enter at the open level in the direction of the cross:
       up leg   -> cross down through open -> SHORT
       down leg -> cross up   through open -> LONG

Entry is a stop order resting at the Monday open, so the fill is at that level (plus
slippage) by construction - it cannot be a phantom fill.  One trade per Monday: the FIRST
cross only.  Everything the strategy uses (leg direction, leg extreme, open level, time of
cross) is known at tc.

This pass records, from tc onward, the first-touch minute of a grid of levels measured in ATR
from the entry, separately on the favourable and adverse side, plus the leg extreme (for the
structural stop) and the session-close price.  Any stop/target pair can then be resolved
exactly by comparing first-touch minutes.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, year_files, session_key

LEG = 0.25
GRID = np.round(np.arange(0.25, 3.01, 0.25), 2)   # ATR distances from entry


def one(g, r):
    o = g.open.iloc[0]; a = r.atr_at_B
    hi = g.high.values; lo = g.low.values; n = len(g)
    rmax = np.maximum.accumulate(hi); rmin = np.minimum.accumulate(lo)
    wu = np.flatnonzero(rmax >= o + LEG * a)
    wd = np.flatnonzero(rmin <= o - LEG * a)
    tu = wu[0] if len(wu) else np.inf
    td = wd[0] if len(wd) else np.inf
    if not np.isfinite(min(tu, td)):
        return dict(signal=False, reason="no 0.25 ATR leg")
    up_leg = tu < td
    t0 = int(min(tu, td))
    # first cross back through the open AFTER the leg
    if up_leg:
        w = np.flatnonzero(np.minimum.accumulate(lo[t0:]) <= o)
    else:
        w = np.flatnonzero(np.maximum.accumulate(hi[t0:]) >= o)
    if not len(w):
        return dict(signal=False, reason="no open cross", leg_up=up_leg, t0=float(t0))
    tc = int(w[0] + t0)
    # leg extreme between t0 and the cross  (known at tc -> usable as a structural stop)
    leg_ext = float(hi[t0:tc + 1].max()) if up_leg else float(lo[t0:tc + 1].min())
    short = up_leg                      # cross down after an up leg -> short
    d = dict(signal=True, leg_up=up_leg, short=short, t0=float(t0), tc=float(tc),
             entry_px=float(o), atr=float(a), n_bars=n, bars_left=float(n - tc),
             leg_ext_px=leg_ext,
             leg_ext_atr=(leg_ext - o) / a if up_leg else (o - leg_ext) / a,
             close_px=float(g.close.iloc[-1]))
    if tc >= n - 1:
        d["degenerate"] = True
        for k in GRID:
            d[f"fav{k:.2f}"] = np.nan; d[f"adv{k:.2f}"] = np.nan
        d["t_legext"] = np.nan
        d["mfe_atr"] = 0.0; d["mae_atr"] = 0.0
        return d
    d["degenerate"] = False
    seg_hi = hi[tc:]; seg_lo = lo[tc:]
    fmax = np.maximum.accumulate(seg_hi); fmin = np.minimum.accumulate(seg_lo)
    mins = np.arange(len(seg_hi), dtype=float)
    for k in GRID:
        if short:
            wf = np.flatnonzero(fmin <= o - k * a)        # favourable = down
            wa = np.flatnonzero(fmax >= o + k * a)        # adverse    = up
        else:
            wf = np.flatnonzero(fmax >= o + k * a)
            wa = np.flatnonzero(fmin <= o - k * a)
        d[f"fav{k:.2f}"] = mins[wf[0]] + tc if len(wf) else np.nan
        d[f"adv{k:.2f}"] = mins[wa[0]] + tc if len(wa) else np.nan
    # structural stop: first touch of the leg extreme after the cross
    if short:
        w2 = np.flatnonzero(fmax >= leg_ext)
    else:
        w2 = np.flatnonzero(fmin <= leg_ext)
    d["t_legext"] = mins[w2[0]] + tc if len(w2) else np.nan
    d["mfe_atr"] = (o - seg_lo.min()) / a if short else (seg_hi.max() - o) / a
    d["mae_atr"] = (seg_hi.max() - o) / a if short else (o - seg_lo.min()) / a
    return d


def build(inst, sdef, T):
    tr = T[(T.instrument == inst) & (T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0) &
           (T.atr_at_B > 0) & (T.B_range > 0)].copy()
    want = {d_: i for d_, i in zip(pd.DatetimeIndex(tr.C_date).normalize(), tr.index)}
    recs = {}
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low", "close"])
        ts = pd.DatetimeIndex(df["timestamp"])
        key, mask = session_key(ts, inst, sdef)
        df = df.loc[mask].assign(sdate=key[mask]).sort_values("timestamp")
        for sdate, g in df.groupby("sdate", sort=False):
            i = want.get(sdate)
            if i is not None:
                recs[i] = one(g, tr.loc[i])
        del df
    return tr.join(pd.DataFrame.from_dict(recs, orient="index"), how="inner")


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    parts = []
    for inst in ["NAS100", "US500"]:
        for sdef in ["RTH", "BROKER"]:
            r = build(inst, sdef, T)
            print(f"{inst} {sdef}: {len(r)} Mondays, signal on {int(r.signal.sum())}", flush=True)
            parts.append(r)
    X = pd.concat(parts, ignore_index=True)
    X["week"] = pd.DatetimeIndex(X.C_date).to_period("W-SUN").astype(str)
    X["year"] = pd.DatetimeIndex(X.C_date).year
    X.to_parquet(DERIVED / "postcross.parquet", index=False)
    print("saved", len(X), "rows")
    s = X[X.signal == True]
    print("signal rate by trigger:", s.groupby(X.trig_down).size().to_dict())
