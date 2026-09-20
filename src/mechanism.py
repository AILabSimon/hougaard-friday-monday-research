"""Mechanism controls: does the Thu/Fri high condition add information beyond
the position of Friday's close within Friday's range?  Plus severity continuum
and the event-definition ladder."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
from stats_util import wilson, newcombe_diff, two_prop_test

T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
rows = []


def logit_fit(X, y, ridge=1e-4, iters=200):
    """Plain Newton-IRLS logistic regression (no statsmodels dependency)."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ b
        p = 1 / (1 + np.exp(-np.clip(eta, -30, 30)))
        W = np.clip(p * (1 - p), 1e-8, None)
        H = X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1])
        g = X.T @ (y - p) - ridge * b
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < 1e-9:
            break
    eta = X @ b
    p = 1 / (1 + np.exp(-np.clip(eta, -30, 30)))
    W = np.clip(p * (1 - p), 1e-8, None)
    cov = np.linalg.inv(X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1]))
    se = np.sqrt(np.diag(cov))
    return b, se


def run_logit(df, label, sdef, group):
    d = df.dropna(subset=["atr_at_B", "B_close_loc"]).copy()
    d["dist"] = (d.B_close - d.B_low) / d.atr_at_B
    d["Brange_atr"] = d.B_range / d.atr_at_B
    insts = sorted(d.instrument.unique())
    cols = {"const": np.ones(len(d)),
            "trig_down": d.trig_down.astype(float).values,
            "dist": d["dist"].values,
            "Brange_atr": d["Brange_atr"].values}
    for i in insts[1:]:
        cols[f"I_{i}"] = (d.instrument == i).astype(float).values
    names = list(cols)
    X = np.column_stack([cols[c] for c in names])
    y = d.touch_low.values.astype(float)
    b, se = logit_fit(X, y)
    # model without the distance control, for comparison
    names0 = ["const", "trig_down"] + [n for n in names if n.startswith("I_")]
    X0 = np.column_stack([cols[c] for c in names0])
    b0, se0 = logit_fit(X0, y)
    i_t = names.index("trig_down"); i_t0 = names0.index("trig_down")
    return dict(scope=label, sessdef=sdef, group=group, n=len(d),
                beta_trig_raw=b0[i_t0], se_raw=se0[i_t0], z_raw=b0[i_t0] / se0[i_t0],
                beta_trig_ctrl=b[i_t], se_ctrl=se[i_t], z_ctrl=b[i_t] / se[i_t],
                odds_raw=np.exp(b0[i_t0]), odds_ctrl=np.exp(b[i_t]),
                beta_dist=b[names.index("dist")], z_dist=b[names.index("dist")] / se[names.index("dist")])


GROUPS = {"US_INDEX": ["NAS100", "US500"],
          "FX": ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "USDJPY"],
          "COMMOD": ["XAUUSD", "XAGUSD", "WTIUSD"],
          "ALL": list(T.instrument.unique())}

out = []
for sdef in ["RTH", "BROKER", "NYFX", "UTC", "LONDON"]:
    S = T[T.sessdef == sdef]
    for gname, insts in GROUPS.items():
        fri = S[(S.B_wd == 4) & (S.C_wd == 0) & S.instrument.isin(insts)]
        if len(fri) > 200:
            out.append(run_logit(fri, "Fri->Mon", sdef, gname))
        oth = S[(S.B_wd < 4) & S.instrument.isin(insts)]
        if len(oth) > 200:
            out.append(run_logit(oth, "Mon-Thu->next", sdef, gname))
L = pd.DataFrame(out)
L.to_csv(OUT / "mechanism_logit.csv", index=False)
print("=== logistic: log-odds on trig_down, raw vs controlled for (Fri close - Fri low)/ATR and Fri range/ATR ===")
print(L[["scope", "sessdef", "group", "n", "beta_trig_raw", "z_raw", "beta_trig_ctrl", "z_ctrl", "odds_ctrl"]]
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# ------------------------------------------------- severity continuum
print("\n=== severity: Monday touch rate by shortfall (Thu high - Fri high)/ATR quintile ===")
srows = []
for sdef in ["RTH", "BROKER"]:
    for gname, insts in GROUPS.items():
        if gname == "ALL":
            continue
        d = T[(T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0) &
              T.instrument.isin(insts) & T.trig_down].dropna(subset=["shortfall_atr"]).copy()
        q = d.shortfall_atr.quantile([0, .2, .4, .6, .8, 1]).values
        d["b"] = pd.cut(d.shortfall_atr, np.unique(q), include_lowest=True)
        for bk, g in d.groupby("b", observed=True):
            srows.append(dict(sessdef=sdef, group=gname, bucket=str(bk), n=len(g),
                              rate=g.touch_low.mean(),
                              med_shortfall_atr=g.shortfall_atr.median()))
S = pd.DataFrame(srows)
S.to_csv(OUT / "severity.csv", index=False)
print(S.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# ------------------------------------------------- event-definition ladder
print("\n=== event definition ladder (Fri->Mon, triggered) ===")
lrows = []
for sdef in ["RTH", "BROKER"]:
    for gname, insts in GROUPS.items():
        d = T[(T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(insts)]
        t, o = d[d.trig_down], d[~d.trig_down]
        rec = dict(sessdef=sdef, group=gname, n_trig=len(t))
        for name, expr in [("touch", lambda x: x.touch_low),
                           ("pen>0.05R", lambda x: x.pen_frac_Brange > 0.05),
                           ("pen>0.25R", lambda x: x.pen_frac_Brange > 0.25),
                           ("pen>0.25ATR", lambda x: x.pen_frac_atr > 0.25),
                           ("close_below", lambda x: x.close_below),
                           ("gap_below", lambda x: x.gap_below),
                           ("dir_down", lambda x: x.C_dir_down)]:
            rec[name] = expr(t).mean()
            rec[name + "_opp"] = expr(o).mean()
        lrows.append(rec)
Ld = pd.DataFrame(lrows)
Ld.to_csv(OUT / "event_ladder.csv", index=False)
print(Ld.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
