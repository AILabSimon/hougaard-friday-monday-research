"""Cycle 2 path datasets for the US equity index CFDs (1-minute resolution).

Two outputs, both keyed to the Cycle-1 triple table:
  derived/c2_friday_path.parquet  - how Friday's session developed (Stage B)
  derived/c2_monday_path.parquet  - how Monday's session opened and developed (Stage C)

ES/NQ have daily bars only in this library, so all intraday work is NAS100/US500,
2016-2026.  That is a real limitation of the evidence, not a choice.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, year_files, session_key

INSTS = ["NAS100", "US500"]
SDEFS = ["RTH", "BROKER"]
KS = [5, 15, 30, 60]


def sessions_1m(inst, sdef):
    """Yield (session_date, DataFrame of that session's 1m bars) in order."""
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low", "close"])
        ts = pd.DatetimeIndex(df["timestamp"])
        key, mask = session_key(ts, inst, sdef)
        df = df.loc[mask].assign(sdate=key[mask]).sort_values("timestamp")
        for sdate, g in df.groupby("sdate", sort=False):
            yield sdate, g
        del df


def friday_feats(g, r):
    """r = the triple row whose B (Friday) is this session."""
    o = g.open.iloc[0]; hi = g.high.values; lo = g.low.values; cl = g.close.values
    n = len(g); a = r.atr_at_B
    ih, il = int(np.argmax(hi)), int(np.argmin(lo))
    # closest approach to Thursday's high, and when
    gap_to_A = (r.A_high - hi) / a               # >0 = still below Thursday's high
    j = int(np.argmin(gap_to_A))
    last60 = cl[-1] - (cl[-61] if n > 61 else cl[0])
    return dict(
        fri_n=n,
        fri_t_high=ih, fri_t_low=il, fri_frac_high=ih / n, fri_frac_low=il / n,
        fri_high_before_low=ih < il,
        fri_t_closest_to_Ahigh=j, fri_frac_closest=j / n,
        fri_min_gap_to_Ahigh_atr=gap_to_A[j],
        fri_first_hour_range_atr=(hi[:60].max() - lo[:60].min()) / a if n > 60 else np.nan,
        fri_last_hour_ret_atr=last60 / a,
        fri_open_to_high_atr=(hi.max() - o) / a,
        fri_open_to_low_atr=(o - lo.min()) / a,
        # did Friday trade above Thursday's high intrabar at any point? (should be False)
        fri_breached_Ahigh=bool((hi >= r.A_high).any()),
    )


def monday_feats(g, r):
    o = g.open.iloc[0]; hi = g.high.values; lo = g.low.values; cl = g.close.values
    n = len(g); a = r.atr_at_B
    rmax = np.maximum.accumulate(hi); rmin = np.minimum.accumulate(lo)
    mins = np.arange(n, dtype=float)

    def first_ge(level):
        w = np.flatnonzero(rmax >= level); return float(w[0]) if len(w) else np.nan

    def first_le(level):
        w = np.flatnonzero(rmin <= level); return float(w[0]) if len(w) else np.nan

    d = dict(mon_n=n, mon_open=o,
             # ---- opening location
             gap_atr=(o - r.B_close) / a,
             gap_frac_Brange=(o - r.B_close) / r.B_range if r.B_range else np.nan,
             open_to_Blow_atr=(o - r.B_low) / a,
             open_to_Bhigh_atr=(r.B_high - o) / a,
             open_to_Ahigh_atr=(r.A_high - o) / a,
             open_loc_in_Brange=(o - r.B_low) / r.B_range if r.B_range else np.nan,
             open_above_Brange=o > r.B_high, open_below_Brange=o < r.B_low,
             )
    # ---- opening windows
    for k in KS:
        m = min(k, n)
        d[f"up{k}_atr"] = (hi[:m].max() - o) / a
        d[f"dn{k}_atr"] = (o - lo[:m].min()) / a
        d[f"ret{k}_atr"] = (cl[m - 1] - o) / a
        d[f"dir{k}_up"] = cl[m - 1] > o
        d[f"orh{k}"] = hi[:m].max(); d[f"orl{k}"] = lo[:m].min()
        # opening-range break after the window
        if n > m:
            wu = np.flatnonzero(hi[m:] > hi[:m].max())
            wd = np.flatnonzero(lo[m:] < lo[:m].min())
            tu = float(wu[0] + m) if len(wu) else np.nan
            td = float(wd[0] + m) if len(wd) else np.nan
            d[f"or{k}_t_up"] = tu; d[f"or{k}_t_dn"] = td
            if np.isnan(tu) and np.isnan(td):
                d[f"or{k}_break"] = "none"; d[f"or{k}_t"] = np.nan
            elif np.isnan(td) or (not np.isnan(tu) and tu < td):
                d[f"or{k}_break"] = "up"; d[f"or{k}_t"] = tu
            else:
                d[f"or{k}_break"] = "dn"; d[f"or{k}_t"] = td
            # continuation / failure after the break
            t = d[f"or{k}_t"]
            if not np.isnan(t):
                t = int(t)
                if d[f"or{k}_break"] == "dn":
                    lvl = lo[:m].min()
                    d[f"or{k}_cont_atr"] = (lvl - lo[t:].min()) / a
                    d[f"or{k}_fail_atr"] = (hi[t:].max() - lvl) / a
                else:
                    lvl = hi[:m].max()
                    d[f"or{k}_cont_atr"] = (hi[t:].max() - lvl) / a
                    d[f"or{k}_fail_atr"] = (lvl - lo[t:].min()) / a
            else:
                d[f"or{k}_cont_atr"] = np.nan; d[f"or{k}_fail_atr"] = np.nan
        else:
            for s in ("t_up", "t_dn", "break", "t", "cont_atr", "fail_atr"):
                d[f"or{k}_{s}"] = np.nan if s != "break" else "none"

    # ---- level interaction
    tB_lo = first_le(r.B_low); tB_hi = first_ge(r.B_high); tA_hi = first_ge(r.A_high)
    d.update(t_Blow=tB_lo, t_Bhigh=tB_hi, t_Ahigh=tA_hi,
             touch_Blow=not np.isnan(tB_lo), touch_Bhigh=not np.isnan(tB_hi))
    for k in KS:
        d[f"Blow_by{k}"] = (not np.isnan(tB_lo)) and tB_lo < k
        d[f"Bhigh_by{k}"] = (not np.isnan(tB_hi)) and tB_hi < k
    # excursions before the Friday-low touch (short-from-open view)
    if not np.isnan(tB_lo):
        j = int(tB_lo)
        d["mae_before_Blow_atr"] = (rmax[j] - o) / a
        d["pen_after_Blow_atr"] = (r.B_low - lo[j:].min()) / a
        d["bounce_after_Blow_atr"] = (hi[j:].max() - r.B_low) / a
        d["pen_after_Blow_30m_atr"] = (r.B_low - lo[j:j + 30].min()) / a
        d["bounce_after_Blow_30m_atr"] = (hi[j:j + 30].max() - r.B_low) / a
        d["close_vs_Blow_atr"] = (cl[-1] - r.B_low) / a
    else:
        for c in ["mae_before_Blow_atr", "pen_after_Blow_atr", "bounce_after_Blow_atr",
                  "pen_after_Blow_30m_atr", "bounce_after_Blow_30m_atr", "close_vs_Blow_atr"]:
            d[c] = np.nan
    # ---- whole-session shape
    ih, il = int(np.argmax(hi)), int(np.argmin(lo))
    d.update(mon_t_high=ih, mon_t_low=il, mon_high_before_low=ih < il,
             mfe_down_atr=(o - lo.min()) / a, mfe_up_atr=(hi.max() - o) / a,
             ret_close_atr=(cl[-1] - o) / a)
    # ---- first meaningful excursion (first move of 0.25 ATR from the open)
    thr = 0.25 * a
    wu = np.flatnonzero(rmax >= o + thr); wd = np.flatnonzero(rmin <= o - thr)
    tu = wu[0] if len(wu) else np.inf; td = wd[0] if len(wd) else np.inf
    d["first_move_dir"] = "up" if tu < td else ("dn" if td < tu else "none")
    d["first_move_t"] = float(min(tu, td)) if np.isfinite(min(tu, td)) else np.nan
    # ---- path sequence label
    if np.isnan(tB_lo) and np.isnan(tB_hi):
        seq = "neither"
    elif np.isnan(tB_hi):
        seq = "low_only"
    elif np.isnan(tB_lo):
        seq = "high_only"
    elif tB_lo < tB_hi:
        seq = "low_then_high"
    else:
        seq = "high_then_low"
    d["seq"] = seq
    return d


def build(inst, sdef, T):
    tr = T[(T.instrument == inst) & (T.sessdef == sdef) & (T.B_wd == 4) &
           (T.C_wd == 0) & (T.atr_at_B > 0) & (T.B_range > 0)].copy()
    bwant = {d: i for d, i in zip(pd.DatetimeIndex(tr.B_date).normalize(), tr.index)}
    cwant = {d: i for d, i in zip(pd.DatetimeIndex(tr.C_date).normalize(), tr.index)}
    frec, mrec = {}, {}
    for sdate, g in sessions_1m(inst, sdef):
        i = bwant.get(sdate)
        if i is not None:
            frec[i] = friday_feats(g, tr.loc[i])
        i = cwant.get(sdate)
        if i is not None:
            mrec[i] = monday_feats(g, tr.loc[i])
    F = tr.join(pd.DataFrame.from_dict(frec, orient="index"), how="inner")
    M = tr.join(pd.DataFrame.from_dict(mrec, orient="index"), how="inner")
    return F, M


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    FS, MS = [], []
    for inst in INSTS:
        for sdef in SDEFS:
            F, M = build(inst, sdef, T)
            print(f"{inst} {sdef}: friday {len(F)}  monday {len(M)}", flush=True)
            FS.append(F); MS.append(M)
    pd.concat(FS, ignore_index=True).to_parquet(DERIVED / "c2_friday_path.parquet", index=False)
    MM = pd.concat(MS, ignore_index=True)
    MM.to_parquet(DERIVED / "c2_monday_path.parquet", index=False)
    print("saved", len(MM), "Monday rows,", MM.shape[1], "columns")
