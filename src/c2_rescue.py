"""STAGE E — adversarial check, run in RESCUE direction because Cycle 2's conclusion is
negative.  Question: is the tradeable component ('Monday travelled to Friday's low') or the
tradeable-state touch uplift significant in ANY defensible subset?  Subsets are chosen before
looking at results and are reported in full, so the multiplicity is visible.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260926)
M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
M["week"] = pd.DatetimeIndex(M.C_date).to_period("W-SUN").astype(str)
M["year"] = pd.DatetimeIndex(M.C_date).year
M["travelled_to_low"] = M.touch_Blow & ~M.open_below_Brange


def boot(d, col, nb=1500):
    d = d.dropna(subset=[col])
    y = d[col].astype(float).values; t = d.trig_down.values
    if t.sum() < 15 or (~t).sum() < 15:
        return None
    wk = d.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
    bs = []
    for _ in range(nb):
        ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
        yy, tt = y[ii], t[ii]
        if tt.sum() < 3 or (~tt).sum() < 3:
            continue
        bs.append(yy[tt].mean() - yy[~tt].mean())
    bs = np.array(bs)
    return dict(n_trig=int(t.sum()), trig=y[t].mean(), opp=y[~t].mean(),
                diff=y[t].mean() - y[~t].mean(),
                ci_lo=np.quantile(bs, .025), ci_hi=np.quantile(bs, .975),
                p=2 * min((bs <= 0).mean(), (bs >= 0).mean()))


B = M[M.sessdef == "RTH"]
T = B[~B.open_below_Brange]
rows = []
SUBSETS = [("all", B), ("NAS100", B[B.instrument == "NAS100"]), ("US500", B[B.instrument == "US500"]),
           ("2016-2020", B[B.year <= 2020]), ("2021-2026", B[B.year >= 2021]),
           ("opens INSIDE Fri range", B[(~B.open_below_Brange) & (~B.open_above_Brange)]),
           ("opens in lower half of Fri range", B[(~B.open_below_Brange) & (B.open_loc_in_Brange <= .5)]),
           ("high-range Fridays (top half B_range/ATR)", B[B.B_range_atr >= B.B_range_atr.median()])]
for lab, d in SUBSETS:
    r = boot(d, "travelled_to_low")
    if r:
        rows.append(dict(test="travelled_to_low", subset=lab, **r))
for lab, d in [("all tradeable", T), ("NAS100", T[T.instrument == "NAS100"]),
               ("US500", T[T.instrument == "US500"]),
               ("2016-2020", T[T.year <= 2020]), ("2021-2026", T[T.year >= 2021])]:
    for c in ["touch_Blow", "mfe_down_atr"]:
        r = boot(d, c)
        if r:
            rows.append(dict(test=f"tradeable-state {c}", subset=lab, **r))
# leave-one-year-out on the headline effect
yr = []
for y_, g in B.groupby("year"):
    t, o = g[g.trig_down], g[~g.trig_down]
    if len(t) < 8 or len(o) < 8:
        continue
    yr.append(dict(year=y_, n_trig=len(t), trig=t.touch_Blow.mean(), opp=o.touch_Blow.mean(),
                   diff=t.touch_Blow.mean() - o.touch_Blow.mean()))
Y = pd.DataFrame(yr)
loo = [(Y.drop(i)["diff"] * Y.drop(i).n_trig).sum() / Y.drop(i).n_trig.sum() for i in Y.index]
rows.append(dict(test="headline touch effect", subset="leave-one-year-out (worst)",
                 n_trig=int(Y.n_trig.sum()), trig=np.nan, opp=np.nan, diff=min(loo),
                 ci_lo=np.nan, ci_hi=np.nan, p=np.nan))
R = pd.DataFrame(rows)
R.to_csv(OUT / "stageE_rescue.csv", index=False)
Y.to_csv(OUT / "stageE_year_by_year.csv", index=False)
pd.set_option("display.width", 250)
print(R.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\nheadline effect positive in {(Y['diff'] > 0).sum()}/{len(Y)} years; "
      f"worst leave-one-year-out pooled uplift {min(loo):.4f}")
