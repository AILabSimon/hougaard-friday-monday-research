"""CYCLE 3 CLOSURE — same-Monday joint excursion topology.

The CI runner that executed Issue #2 had no access to the per-Monday derived parquet or the
1-minute store, so it could not settle Stage A's central question:

    is the validated Monday range expansion genuinely TWO-SIDED WITHIN THE SAME SESSION,
    or is it cross-day averaging of random ONE-SIDED expansion?

That question has a decisive local test.  If expansion were one-sided in a random direction,
the LARGER side would expand and the SMALLER side would not; the smaller/larger ratio would be
flat or fall.  If it is genuinely two-sided, the SMALLER side expands too and the ratio holds.

One 1-minute pass adds the sequence measures the review also asked for: first-leg ordering,
retracement of the first leg, open-cross, and the complementary opposite-side extension.
NAS100/US500, RTH and broker day, 2016-2026.  No new market data is loaded beyond the same
1-minute bars Cycle 2 already used.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT, year_files, session_key

KS = [0.25, 0.5, 0.75, 1.0]
LEGS = [0.25, 0.5]


def seq_feats(g, r):
    """One Monday session -> joint topology and sequence measures."""
    o = g.open.iloc[0]; a = r.atr_at_B
    hi = g.high.values; lo = g.low.values; n = len(g)
    rmax = np.maximum.accumulate(hi); rmin = np.minimum.accumulate(lo)
    mins = np.arange(n, dtype=float)
    up = (hi.max() - o) / a; dn = (o - lo.min()) / a
    d = dict(up_atr=up, dn_atr=dn, total_range_atr=up + dn,
             larger_atr=max(up, dn), smaller_atr=min(up, dn),
             ratio_small_large=min(up, dn) / max(up, dn) if max(up, dn) > 0 else np.nan,
             larger_side_up=up >= dn)
    def t_up(k):
        w = np.flatnonzero(rmax >= o + k * a); return float(w[0]) if len(w) else np.nan
    def t_dn(k):
        w = np.flatnonzero(rmin <= o - k * a); return float(w[0]) if len(w) else np.nan
    for k in KS:
        tu, td = t_up(k), t_dn(k)
        d[f"up_{k}"] = up >= k; d[f"dn_{k}"] = dn >= k
        d[f"both_{k}"] = (up >= k) and (dn >= k)
        d[f"one_only_{k}"] = ((up >= k) != (dn >= k))
        d[f"neither_{k}"] = (up < k) and (dn < k)
        d[f"t_up_{k}"] = tu; d[f"t_dn_{k}"] = td
        d[f"first_side_up_{k}"] = (not np.isnan(tu)) and (np.isnan(td) or tu < td)
        d[f"t_first_{k}"] = np.nanmin([tu, td]) if not (np.isnan(tu) and np.isnan(td)) else np.nan
    # ---- first-leg sequences
    # DEFECT FIX (Cycle 3): extremes after the first leg must be accumulated FROM t0, not read
    # off the session-wide running accumulators, which already contain the open and make every
    # retracement trivially true.  Retracement levels are measured against the LEG THRESHOLD
    # (o +/- k*ATR), not against the eventual extreme, so there is no look-ahead.
    for k in LEGS:
        tu, td = t_up(k), t_dn(k)
        blank = ["t", "retr50", "retr100", "t_retr100", "opp", "t_opp",
                 "leg_ext_atr", "post_move_atr", "t_leg_ext"]
        if np.isnan(tu) and np.isnan(td):
            d[f"leg{k}_dir"] = "none"
            for s_ in blank:
                d[f"leg{k}_{s_}"] = np.nan
            d[f"leg{k}_retr50"] = np.nan; d[f"leg{k}_retr100"] = np.nan; d[f"leg{k}_opp"] = np.nan
            continue
        up_first = (not np.isnan(tu)) and (np.isnan(td) or tu < td)
        t0 = int(tu if up_first else td)
        d[f"leg{k}_dir"] = "up" if up_first else "dn"
        d[f"leg{k}_t"] = float(t0)
        if up_first:
            fwd_min = np.minimum.accumulate(lo[t0:])          # from the leg touch onward
            fwd_max = np.maximum.accumulate(hi[t0:])
            lvl50, lvl100 = o + 0.5 * k * a, o
            w50 = np.flatnonzero(fwd_min <= lvl50)
            w100 = np.flatnonzero(fwd_min <= lvl100)
            d[f"leg{k}_retr50"] = len(w50) > 0
            d[f"leg{k}_retr100"] = len(w100) > 0
            d[f"leg{k}_t_retr100"] = float(w100[0] + t0) if len(w100) else np.nan
            j_ext = int(np.argmax(fwd_max[:w100[0] + 1])) if len(w100) else int(np.argmax(fwd_max))
            d[f"leg{k}_leg_ext_atr"] = (fwd_max[j_ext] - o) / a
            d[f"leg{k}_t_leg_ext"] = float(j_ext + t0)
            if len(w100):
                j = int(w100[0] + t0)
                after = np.minimum.accumulate(lo[j:])
                wo = np.flatnonzero(after <= o - k * a)
                d[f"leg{k}_opp"] = len(wo) > 0
                d[f"leg{k}_t_opp"] = float(wo[0] + j) if len(wo) else np.nan
                d[f"leg{k}_post_move_atr"] = (o - lo[j:].min()) / a
            else:
                d[f"leg{k}_opp"] = False
                d[f"leg{k}_t_opp"] = np.nan; d[f"leg{k}_post_move_atr"] = np.nan
        else:
            fwd_min = np.minimum.accumulate(lo[t0:])
            fwd_max = np.maximum.accumulate(hi[t0:])
            lvl50, lvl100 = o - 0.5 * k * a, o
            w50 = np.flatnonzero(fwd_max >= lvl50)
            w100 = np.flatnonzero(fwd_max >= lvl100)
            d[f"leg{k}_retr50"] = len(w50) > 0
            d[f"leg{k}_retr100"] = len(w100) > 0
            d[f"leg{k}_t_retr100"] = float(w100[0] + t0) if len(w100) else np.nan
            j_ext = int(np.argmin(fwd_min[:w100[0] + 1])) if len(w100) else int(np.argmin(fwd_min))
            d[f"leg{k}_leg_ext_atr"] = (o - fwd_min[j_ext]) / a
            d[f"leg{k}_t_leg_ext"] = float(j_ext + t0)
            if len(w100):
                j = int(w100[0] + t0)
                after = np.maximum.accumulate(hi[j:])
                wo = np.flatnonzero(after >= o + k * a)
                d[f"leg{k}_opp"] = len(wo) > 0
                d[f"leg{k}_t_opp"] = float(wo[0] + j) if len(wo) else np.nan
                d[f"leg{k}_post_move_atr"] = (hi[j:].max() - o) / a
            else:
                d[f"leg{k}_opp"] = False
                d[f"leg{k}_t_opp"] = np.nan; d[f"leg{k}_post_move_atr"] = np.nan
    ih, il = int(np.argmax(hi)), int(np.argmin(lo))
    d.update(t_high=ih, t_low=il, high_before_low=ih < il, n_bars=n)
    return d


def build(inst, sdef, T):
    tr = T[(T.instrument == inst) & (T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0) &
           (T.atr_at_B > 0) & (T.B_range > 0)].copy()
    want = {d_: i for d_, i in zip(pd.DatetimeIndex(tr.C_date).normalize(), tr.index)}
    recs = {}
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low"])
        ts = pd.DatetimeIndex(df["timestamp"])
        key, mask = session_key(ts, inst, sdef)
        df = df.loc[mask].assign(sdate=key[mask]).sort_values("timestamp")
        for sdate, g in df.groupby("sdate", sort=False):
            i = want.get(sdate)
            if i is not None:
                recs[i] = seq_feats(g, tr.loc[i])
        del df
    return tr.join(pd.DataFrame.from_dict(recs, orient="index"), how="inner")


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    parts = []
    for inst in ["NAS100", "US500"]:
        for sdef in ["RTH", "BROKER"]:
            r = build(inst, sdef, T)
            print(f"{inst} {sdef}: {len(r)}", flush=True)
            parts.append(r)
    X = pd.concat(parts, ignore_index=True)
    X["week"] = pd.DatetimeIndex(X.C_date).to_period("W-SUN").astype(str)
    X.to_parquet(DERIVED / "c3_topology.parquet", index=False)
    print("saved", len(X), "rows,", X.shape[1], "cols")
