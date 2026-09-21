"""Is the Monday range-expansion effect real, or just Friday's own range predicting Monday's?

OLS of Monday total excursion (down+up, ATR units) on the trigger, controlling for Friday's
range/ATR, Friday's close-in-range and instrument.  Week-clustered bootstrap.  Also ES/NQ
daily 2000-2026 using (high-low)/ATR, and dev/validation splits.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260929)
NB = 1500


def ols(X, y):
    return np.linalg.solve(X.T @ X + 1e-8 * np.eye(X.shape[1]), X.T @ y)


def fit(d, ycol, ctrl=True):
    z = lambda s: (s - s.mean()) / (s.std() if s.std() else 1)
    cols = [np.ones(len(d)), d.trig_down.astype(float).values]
    if ctrl:
        cols += [z(d.B_range_atr).values, z(d.B_close_loc).values]
    for i in sorted(d.instrument.unique())[1:]:
        cols.append((d.instrument == i).astype(float).values)
    X = np.column_stack(cols)
    return ols(X, d[ycol].values.astype(float))[1], X


def boot_beta(d, ycol, ctrl=True, nb=NB):
    b, _ = fit(d, ycol, ctrl)
    wk = d.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
    bs = []
    for _ in range(nb):
        ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
        s = d.iloc[ii]
        if s.trig_down.nunique() < 2:
            continue
        try:
            bb, _ = fit(s, ycol, ctrl)
            bs.append(bb)
        except np.linalg.LinAlgError:
            continue
    bs = np.array(bs)
    return dict(beta=b, ci_lo=np.quantile(bs, .025), ci_hi=np.quantile(bs, .975),
                p=2 * min((bs <= 0).mean(), (bs >= 0).mean()))


M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
M["week"] = pd.DatetimeIndex(M.C_date).to_period("W-SUN").astype(str)
M["year"] = pd.DatetimeIndex(M.C_date).year
M["range_atr"] = M.mfe_down_atr + M.mfe_up_atr

Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")
Y = Y[(Y.B_wd == 4) & (Y.C_wd == 0) & (Y.atr_at_B > 0) & (Y.B_range > 0) &
      Y.instrument.isin(["YF_ES", "YF_NQ"])].copy()
Y["week"] = pd.DatetimeIndex(Y.C_date).to_period("W-SUN").astype(str)
Y["year"] = pd.DatetimeIndex(Y.C_date).year
Y["range_atr"] = (Y.C_high - Y.C_low) / Y.atr_at_B
Y["B_range_atr"] = Y.B_range / Y.atr_at_B
Y["B_close_loc"] = (Y.B_close - Y.B_low) / Y.B_range
Y["open_below_Blow"] = Y.C_open < Y.B_low

rows = []
SETS = [("Dukascopy NAS100+US500 RTH", M[M.sessdef == "RTH"], "range_atr"),
        ("Dukascopy NAS100+US500 RTH, tradeable", M[(M.sessdef == "RTH") & ~M.open_below_Brange], "range_atr"),
        ("Dukascopy NAS100+US500 BROKER", M[M.sessdef == "BROKER"], "range_atr"),
        ("Dukascopy NAS100+US500 BROKER, tradeable", M[(M.sessdef == "BROKER") & ~M.open_below_Brange], "range_atr"),
        ("Yahoo ES+NQ daily 2000-2026", Y, "range_atr"),
        ("Yahoo ES+NQ daily DEV 2000-2015", Y[Y.year <= 2015], "range_atr"),
        ("Yahoo ES+NQ daily VAL 2016-2026", Y[Y.year >= 2016], "range_atr"),
        ("Yahoo ES alone", Y[Y.instrument == "YF_ES"], "range_atr"),
        ("Yahoo NQ alone", Y[Y.instrument == "YF_NQ"], "range_atr"),
        ("Yahoo ES+NQ, tradeable", Y[~Y.open_below_Blow], "range_atr")]
for name, d, yc in SETS:
    d = d.dropna(subset=[yc, "B_range_atr", "B_close_loc"])
    if len(d) < 120:
        continue
    raw = boot_beta(d, yc, ctrl=False)
    ctl = boot_beta(d, yc, ctrl=True)
    rows.append(dict(sample=name, n=len(d), n_trig=int(d.trig_down.sum()),
                     trig_mean=d[yc][d.trig_down].mean(), opp_mean=d[yc][~d.trig_down].mean(),
                     beta_raw=raw["beta"], raw_lo=raw["ci_lo"], raw_hi=raw["ci_hi"], p_raw=raw["p"],
                     beta_ctrl=ctl["beta"], ctrl_lo=ctl["ci_lo"], ctrl_hi=ctl["ci_hi"], p_ctrl=ctl["p"],
                     pct_uplift=ctl["beta"] / d[yc][~d.trig_down].mean() * 100))
R = pd.DataFrame(rows)
R.to_csv(OUT / "c2_range_effect.csv", index=False)
pd.set_option("display.width", 260)
print("=== Monday RANGE EXPANSION: trigger coefficient in ATR units ===")
print("    (controlled = + Friday range/ATR, Friday close-in-range, instrument FE)")
print(R[["sample", "n", "trig_mean", "opp_mean", "beta_raw", "p_raw", "beta_ctrl",
         "ctrl_lo", "ctrl_hi", "p_ctrl", "pct_uplift"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
