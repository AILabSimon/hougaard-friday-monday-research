"""STAGE B part 2 — which Thursday/Friday variables add information BEYOND the
close-in-range geometry that Cycle 1 already identified?

For each candidate variable v and outcome y, compare
    y ~ B_close_loc + B_range_atr + instrument          (base)
    y ~ B_close_loc + B_range_atr + instrument + v      (base + v)
Standardised coefficient on v, with a WEEK-CLUSTER bootstrap interval.
Only triggered weeks.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260922)
NB = 600

M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
F = pd.read_parquet(DERIVED / "c2_friday_path.parquet")
key = ["instrument", "sessdef", "B_date"]
D = M.merge(F[key + [c for c in F.columns if c.startswith("fri_")]], on=key, how="left")
D["week"] = pd.DatetimeIndex(D.C_date).to_period("W-SUN").astype(str)
D["seq_low_first"] = D.seq.isin(["low_only", "low_then_high"])
D["net60_atr"] = D.dn60_atr - D.up60_atr

VARS = ["shortfall_atr", "fri_frac_high", "fri_last_hour_ret_atr", "B_body_ratio",
        "B_bear", "B_inside", "B_took_Alow", "B_below_Aclose",
        "A_range_atr", "A_close_loc", "A_bear", "fri_high_before_low",
        "fri_first_hour_range_atr", "open_to_Blow_atr"]
OUT_BIN = ["touch_Blow", "seq_low_first"]
OUT_CON = ["dn60_atr", "net60_atr", "ret_close_atr", "mfe_down_atr"]


def logit(X, y, ridge=1e-3, iters=80):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); W = np.clip(p * (1 - p), 1e-8, None)
        H = X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1])
        try:
            s = np.linalg.solve(H, X.T @ (y - p) - ridge * b)
        except np.linalg.LinAlgError:
            return None
        b += s
        if np.max(np.abs(s)) < 1e-9:
            break
    return b


def ols(X, y, ridge=1e-6):
    return np.linalg.solve(X.T @ X + ridge * np.eye(X.shape[1]), X.T @ y)


def build_X(d, v=None):
    z = lambda s: (s - s.mean()) / (s.std() if s.std() else 1)
    cols = [np.ones(len(d)), z(d.B_close_loc).values, z(d.B_range_atr).values,
            (d.instrument == "US500").astype(float).values]
    if v is not None:
        x = d[v].astype(float)
        cols.append(z(x).values)
    return np.column_stack(cols)


rows = []
for sdef in ["RTH", "BROKER"]:
    d0 = D[(D.sessdef == sdef) & D.trig_down].copy()
    weeks = d0.week.values; uw = np.unique(weeks)
    idx_by_week = {w: np.flatnonzero(weeks == w) for w in uw}
    for v in VARS:
        d = d0.dropna(subset=[v, "B_close_loc", "B_range_atr"]).copy()
        if len(d) < 150 or d[v].astype(float).std() == 0:
            continue
        wk = d.week.values; uw2 = np.unique(wk)
        ibw = {w: np.flatnonzero(wk == w) for w in uw2}
        for y_ in OUT_BIN + OUT_CON:
            yy = d[y_].astype(float).values
            binary = y_ in OUT_BIN
            fit = logit if binary else ols
            b = fit(build_X(d, v), yy)
            if b is None:
                continue
            coef = b[-1]
            bs = []
            for _ in range(NB):
                pick = RNG.choice(uw2, size=len(uw2), replace=True)
                ii = np.concatenate([ibw[w] for w in pick])
                s = d.iloc[ii]
                if binary and s[y_].nunique() < 2:
                    continue
                bb = fit(build_X(s, v), s[y_].astype(float).values)
                if bb is not None:
                    bs.append(bb[-1])
            bs = np.array(bs)
            rows.append(dict(sessdef=sdef, variable=v, outcome=y_, n=len(d),
                             model="logit" if binary else "ols",
                             coef_std=coef, ci_lo=np.quantile(bs, .025),
                             ci_hi=np.quantile(bs, .975),
                             p_cluster=2 * min((bs <= 0).mean(), (bs >= 0).mean())))
R = pd.DataFrame(rows)
R["bh_rank"] = R.groupby("sessdef").p_cluster.rank(method="first")
R["bh_crit"] = 0.05 * R.bh_rank / R.groupby("sessdef").p_cluster.transform("size")
R["survives_BH05"] = R.p_cluster <= R.bh_crit
R.to_csv(OUT / "stageB_partial.csv", index=False)
pd.set_option("display.width", 250)
print("=== adds information BEYOND Friday close-in-range + range/ATR (BH 5%, week-clustered) ===")
s = R[R.survives_BH05].sort_values(["sessdef", "p_cluster"])
print(s[["sessdef", "variable", "outcome", "n", "coef_std", "ci_lo", "ci_hi", "p_cluster"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\n{len(s)} of {len(R)} survive.  Variables appearing: {sorted(s.variable.unique())}")
