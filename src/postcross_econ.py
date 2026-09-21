"""FINAL FUTURES/CFD TEST — economics of the post-open-cross construction.

Three coarse risk constructions only, chosen from the observed geometry, no grid:
  S1  structural stop beyond the initial-leg extreme (risk = leg extreme - open), target 2R
  S2  coarse 0.5 ATR stop, targets 1R / 2R / 3R
  S3  S2 at 2R plus one management variant: move to break-even once +1R is reached

Costs: Dukascopy 2024 median spread (NAS100 3.42, US500 0.51) + 1 tick slippage per side,
charged on entry and exit and converted to R by the construction's own risk.
One trade per Monday.  No overlapping positions (a single Monday session per instrument).
Unresolved trades are marked to the session close.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20261010)
NB = 1500
SPREAD = {"NAS100": 3.42, "US500": 0.51}
SLIP = {"NAS100": 1.0, "US500": 0.25}
GRID = np.round(np.arange(0.25, 3.01, 0.25), 2)

X = pd.read_parquet(DERIVED / "postcross.parquet")
X = X[(X.signal == True) & (X.degenerate == False)].copy()
X["cost_px"] = X.instrument.map(SPREAD) + 2 * X.instrument.map(SLIP)


def nearest(k):
    return GRID[np.argmin(np.abs(GRID - k))]


def resolve(d, risk_atr, targ_R, be_at_R=None, struct=False):
    """Return R (net), win, loss, mfe_R, mae_R.  risk_atr in ATR; struct -> use leg extreme."""
    a = d.atr.values
    risk_px = (d.leg_ext_atr.values * a) if struct else (risk_atr * a)
    t_stop = d.t_legext.values.astype(float) if struct else d[f"adv{nearest(risk_atr):.2f}"].values.astype(float)
    tgt_atr = targ_R * (d.leg_ext_atr.values if struct else np.full(len(d), risk_atr))
    # favourable-side first touch at the target distance (grid, per-row)
    t_tgt = np.full(len(d), np.nan)
    for i, ta in enumerate(tgt_atr):
        t_tgt[i] = d[f"fav{nearest(ta):.2f}"].values[i]
    hit_t = np.isfinite(t_tgt); hit_s = np.isfinite(t_stop)
    win = hit_t & (~hit_s | (t_tgt < t_stop))
    loss = hit_s & (~hit_t | (t_stop < t_tgt))
    # mark-to-close for unresolved
    sgn = np.where(d.short.values, 1.0, -1.0)
    mtm_px = sgn * (d.entry_px.values - d.close_px.values)
    R = np.where(win, targ_R, np.where(loss, -1.0, mtm_px / risk_px))
    if be_at_R is not None:
        t_be = np.full(len(d), np.nan)
        be_atr = be_at_R * (d.leg_ext_atr.values if struct else np.full(len(d), risk_atr))
        for i, ba in enumerate(be_atr):
            t_be[i] = d[f"fav{nearest(ba):.2f}"].values[i]
        reached_be = np.isfinite(t_be) & (~hit_s | (t_be < t_stop))
        # after BE: a later adverse return to entry closes at 0 (minus costs)
        t_back = np.full(len(d), np.nan)
        back = d[f"adv{GRID[0]:.2f}"].values.astype(float)   # proxy: first adverse 0.25 ATR
        _ = back
        # exact: entry level itself is crossed again -> approximate with the 0.25 adverse grid
        stopped_be = reached_be & ~win & np.isfinite(back) & (back > t_be)
        R = np.where(win, targ_R, np.where(stopped_be, 0.0, R))
        loss = loss & ~stopped_be
    cost_R = d.cost_px.values / risk_px
    R = R - cost_R
    mfe_R = d.mfe_atr.values * a / risk_px
    mae_R = d.mae_atr.values * a / risk_px
    return R, win, loss, mfe_R, mae_R


def cluster(d, R, trig, nb=NB):
    ok = np.isfinite(R)
    d2, R2, t2 = d[ok], R[ok], trig[ok]
    if t2.sum() < 20 or (~t2).sum() < 20:
        return {}
    wk = d2.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
    bt, bd = [], []
    for _ in range(nb):
        ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
        rr, tt = R2[ii], t2[ii]
        if tt.sum() < 5 or (~tt).sum() < 5:
            continue
        bt.append(rr[tt].mean()); bd.append(rr[tt].mean() - rr[~tt].mean())
    bt, bd = np.array(bt), np.array(bd)
    return dict(trig_ci_lo=np.quantile(bt, .025), trig_ci_hi=np.quantile(bt, .975),
                p_trig_vs_zero=2 * min((bt <= 0).mean(), (bt >= 0).mean()),
                diff=R2[t2].mean() - R2[~t2].mean(),
                diff_ci_lo=np.quantile(bd, .025), diff_ci_hi=np.quantile(bd, .975),
                p_diff=2 * min((bd <= 0).mean(), (bd >= 0).mean()))


def max_dd(r):
    e = np.cumsum(r); return float((np.maximum.accumulate(e) - e).max()) if len(e) else np.nan


CONS = [("S1 structural stop (leg extreme), target 2R", None, 2.0, None, True),
        ("S2a 0.5 ATR stop, target 1R", 0.5, 1.0, None, False),
        ("S2b 0.5 ATR stop, target 2R", 0.5, 2.0, None, False),
        ("S2c 0.5 ATR stop, target 3R", 0.5, 3.0, None, False),
        ("S3  0.5 ATR stop, target 2R, BE at +1R", 0.5, 2.0, 1.0, False)]

rows = []
for sdef in ["RTH", "BROKER"]:
    d = X[X.sessdef == sdef].reset_index(drop=True)
    trig = d.trig_down.values
    nyears = d.year.nunique()
    for name, ratr, tR, be, struct in CONS:
        R, win, loss, mfe, mae = resolve(d, ratr, tR, be, struct)
        sel = trig & np.isfinite(R)
        ctl = (~trig) & np.isfinite(R)
        yr = pd.Series(R[sel]).groupby(d.year.values[sel]).mean()
        rec = dict(sessdef=sdef, construction=name,
                   n_trades=int(sel.sum()), trades_per_year=sel.sum() / nyears / 2,
                   win_rate=win[sel].mean(), loss_rate=loss[sel].mean(),
                   mean_R=np.nanmean(R[sel]), median_R=np.nanmedian(R[sel]),
                   expectancy_R=np.nanmean(R[sel]),
                   MFE_R_median=np.nanmedian(mfe[sel]), MFE_R_mean=np.nanmean(mfe[sel]),
                   MAE_R_median=np.nanmedian(mae[sel]), MAE_R_mean=np.nanmean(mae[sel]),
                   hit_1R=np.nanmean(mfe[sel] >= 1), hit_2R=np.nanmean(mfe[sel] >= 2),
                   hit_3R=np.nanmean(mfe[sel] >= 3),
                   cost_R_median=np.nanmedian(d.cost_px.values[sel] /
                                              ((d.leg_ext_atr.values[sel] if struct else ratr) * d.atr.values[sel])),
                   max_drawdown_R=max_dd(R[sel]),
                   meanR_control=np.nanmean(R[ctl]), n_control=int(ctl.sum()),
                   meanR_DEV_2016_2020=np.nanmean(R[sel & (d.year.values <= 2020)]),
                   n_DEV=int((sel & (d.year.values <= 2020)).sum()),
                   meanR_VAL_2021_2026=np.nanmean(R[sel & (d.year.values >= 2021)]),
                   n_VAL=int((sel & (d.year.values >= 2021)).sum()),
                   positive_years=int((yr > 0).sum()), n_years=int(yr.notna().sum()))
        rec.update(cluster(d, R, trig))
        rows.append(rec)

E = pd.DataFrame(rows)
E.to_csv(OUT / "postcross_economics.csv", index=False)
pd.set_option("display.width", 300)
cols = ["sessdef", "construction", "n_trades", "trades_per_year", "win_rate", "mean_R", "median_R",
        "trig_ci_lo", "trig_ci_hi", "p_trig_vs_zero", "meanR_control", "diff", "p_diff"]
print("=== NET OF COSTS, triggered weeks ===")
print(E[cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\n=== geometry: is there enough movement after the cross to pay 2R? ===")
g = ["sessdef", "construction", "MFE_R_median", "MFE_R_mean", "MAE_R_median", "hit_1R", "hit_2R",
     "hit_3R", "cost_R_median", "max_drawdown_R", "positive_years", "n_years",
     "meanR_DEV_2016_2020", "meanR_VAL_2021_2026"]
print(E[g].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\nAny construction with triggered mean R significantly > 0 after costs?")
v = E[E.trig_ci_lo > 0]
print(v[["sessdef", "construction", "mean_R", "trig_ci_lo"]].to_string(index=False) if len(v) else "  NONE")
