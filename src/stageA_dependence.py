"""STAGE A — dependence-aware confirmation of the US-equity Friday->Monday residual.

NAS100/US500/ES/NQ observations that share a Monday are not independent (Cycle 1: outcome
correlation 0.75-0.79).  Ordinary regression SEs therefore understate uncertainty.  Here the
unit of resampling is the CALENDAR WEEK, so every instrument-observation belonging to the same
week moves together.  Two estimators are reported:

  1. cluster bootstrap on the controlled logistic coefficient (weeks resampled with replacement)
  2. cluster bootstrap on the raw uplift (trigger rate - opposite rate)

The question is only whether the research decision changes.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260921)
NB = 2000


def logit_fit(X, y, ridge=1e-4, iters=100):
    X = np.asarray(X, float); y = np.asarray(y, float); b = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ b; p = 1 / (1 + np.exp(-np.clip(eta, -30, 30))); W = np.clip(p * (1 - p), 1e-8, None)
        H = X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1])
        g = X.T @ (y - p) - ridge * b
        try:
            s = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            return None
        b = b + s
        if np.max(np.abs(s)) < 1e-9:
            break
    return b


def design(d, with_ctrl=True):
    cols = [np.ones(len(d)), d.trig_down.astype(float).values]
    if with_ctrl:
        cols += [((d.B_close - d.B_low) / d.atr_at_B).values,
                 (d.B_range / d.atr_at_B).values]
    insts = sorted(d.instrument.unique())
    for i in insts[1:]:
        cols.append((d.instrument == i).astype(float).values)
    return np.column_stack(cols)


def prep(d):
    d = d.dropna(subset=["atr_at_B"]).copy()
    d = d[(d.atr_at_B > 0) & (d.B_range > 0)]
    d["week"] = pd.DatetimeIndex(d.C_date).to_period("W-SUN").astype(str)
    return d.reset_index(drop=True)


def cluster_boot(d, nb=NB):
    """Resample WEEKS with replacement; recompute controlled beta and raw uplift."""
    weeks = d.week.values
    uw = np.unique(weeks)
    idx_by_week = {w: np.flatnonzero(weeks == w) for w in uw}
    betas, uplifts, raws = [], [], []
    for _ in range(nb):
        pick = RNG.choice(uw, size=len(uw), replace=True)
        idx = np.concatenate([idx_by_week[w] for w in pick])
        s = d.iloc[idx]
        if s.trig_down.nunique() < 2:
            continue
        b = logit_fit(design(s), s.touch_low.values.astype(float))
        b0 = logit_fit(design(s, with_ctrl=False), s.touch_low.values.astype(float))
        if b is None or b0 is None:
            continue
        betas.append(b[1]); raws.append(b0[1])
        t = s.touch_low[s.trig_down].mean(); o = s.touch_low[~s.trig_down].mean()
        uplifts.append(t - o)
    return np.array(betas), np.array(raws), np.array(uplifts)


def naive_se(d):
    X = design(d); y = d.touch_low.values.astype(float)
    b = logit_fit(X, y)
    eta = X @ b; p = 1 / (1 + np.exp(-np.clip(eta, -30, 30))); W = np.clip(p * (1 - p), 1e-8, None)
    cov = np.linalg.inv(X.T @ (X * W[:, None]) + 1e-4 * np.eye(X.shape[1]))
    return b[1], np.sqrt(np.diag(cov))[1]


def report(d, label, nb=NB):
    if len(d) < 80 or d.trig_down.nunique() < 2:
        return None
    b_ctrl, se_naive = naive_se(d)
    b_raw = logit_fit(design(d, with_ctrl=False), d.touch_low.values.astype(float))[1]
    t = d.touch_low[d.trig_down]; o = d.touch_low[~d.trig_down]
    bb, br, bu = cluster_boot(d, nb)
    n_weeks = d.week.nunique()
    return dict(
        sample=label, n_obs=len(d), n_weeks=n_weeks, n_trig=len(t),
        instruments=d.instrument.nunique(),
        raw_rate=t.mean(), opposite_rate=o.mean(), raw_uplift=t.mean() - o.mean(),
        beta_raw=b_raw,
        beta_ctrl=b_ctrl, OR_ctrl=np.exp(b_ctrl),
        se_naive=se_naive, z_naive=b_ctrl / se_naive,
        se_cluster=bb.std(),
        infl=bb.std() / se_naive,
        ci_lo_cluster=np.quantile(bb, .025), ci_hi_cluster=np.quantile(bb, .975),
        p_cluster_2sided=2 * min((bb <= 0).mean(), (bb >= 0).mean()),
        uplift_ci_lo=np.quantile(bu, .025), uplift_ci_hi=np.quantile(bu, .975),
        beta_raw_ci_lo=np.quantile(br, .025), beta_raw_ci_hi=np.quantile(br, .975),
        n_boot=len(bb))


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")
    IDX_D = ["NAS100", "US500"]; IDX_Y = ["YF_ES", "YF_NQ"]
    rows = []

    # ---- pooled US equity complex, per source and per session definition
    for sdef in ["RTH", "BROKER", "UTC"]:
        d = prep(T[(T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(IDX_D)])
        rows.append(report(d, f"Dukascopy NAS100+US500 {sdef} 2016-2026"))
    dy = prep(Y[(Y.B_wd == 4) & (Y.C_wd == 0) & Y.instrument.isin(IDX_Y)])
    rows.append(report(dy, "Yahoo ES+NQ daily 2000-2026"))

    # ---- individual instruments (no cross-instrument dependence at all)
    for inst in IDX_D:
        d = prep(T[(T.sessdef == "RTH") & (T.B_wd == 4) & (T.C_wd == 0) & (T.instrument == inst)])
        rows.append(report(d, f"{inst} RTH alone 2016-2026"))
    for inst in IDX_Y:
        d = prep(Y[(Y.B_wd == 4) & (Y.C_wd == 0) & (Y.instrument == inst)])
        rows.append(report(d, f"{inst} daily alone 2000-2026"))

    # ---- development / validation, as frozen in Cycle 1
    rows.append(report(prep(Y[(Y.B_wd == 4) & (Y.C_wd == 0) & Y.instrument.isin(IDX_Y) & (Y.year <= 2015)]),
                       "DEV  Yahoo ES+NQ 2000-2015"))
    rows.append(report(prep(Y[(Y.B_wd == 4) & (Y.C_wd == 0) & Y.instrument.isin(IDX_Y) & (Y.year >= 2016)]),
                       "VAL  Yahoo ES+NQ 2016-2026"))
    rows.append(report(prep(T[(T.sessdef == "RTH") & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(IDX_D)]),
                       "VAL  Dukascopy RTH 2016-2026 (2nd vendor)"))

    # ---- regime split on the long series
    for lab, a, b in [("2000-2007", 2000, 2007), ("2008-2012", 2008, 2012),
                      ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2026)]:
        rows.append(report(prep(Y[(Y.B_wd == 4) & (Y.C_wd == 0) & Y.instrument.isin(IDX_Y) &
                                  Y.year.between(a, b)]), f"Yahoo ES+NQ {lab}", nb=800))

    # ---- control: the same machinery on Mon-Thu (should be much weaker)
    rows.append(report(prep(Y[(Y.B_wd < 4) & Y.instrument.isin(IDX_Y)]),
                       "CONTROL Yahoo ES+NQ Mon-Thu->next", nb=800))
    rows.append(report(prep(T[(T.sessdef == "RTH") & (T.B_wd < 4) & T.instrument.isin(IDX_D)]),
                       "CONTROL Dukascopy RTH Mon-Thu->next", nb=800))

    R = pd.DataFrame([r for r in rows if r])
    R.to_csv(OUT / "stageA_dependence.csv", index=False)
    pd.set_option("display.width", 260)
    print(R[["sample", "n_obs", "n_weeks", "raw_uplift", "beta_raw", "beta_ctrl", "OR_ctrl",
             "se_naive", "se_cluster", "infl", "ci_lo_cluster", "ci_hi_cluster",
             "p_cluster_2sided"]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
