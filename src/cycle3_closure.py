"""CYCLE 3 CLOSURE — the decisive test and the sequence measures, week-clustered."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20261001)
NB = 2000
X = pd.read_parquet(DERIVED / "c3_topology.parquet")


def boot(d, col, nb=NB):
    d = d.dropna(subset=[col])
    if len(d) < 60 or d.trig_down.nunique() < 2:
        return None
    y = d[col].astype(float).values; t = d.trig_down.values
    if t.sum() < 20 or (~t).sum() < 20:
        return None
    wk = d.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
    bs = []
    for _ in range(nb):
        ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
        yy, tt = y[ii], t[ii]
        if tt.sum() < 5 or (~tt).sum() < 5:
            continue
        bs.append(yy[tt].mean() - yy[~tt].mean())
    bs = np.array(bs)
    return dict(n_trig=int(t.sum()), n_opp=int((~t).sum()),
                trig=y[t].mean(), opp=y[~t].mean(), diff=y[t].mean() - y[~t].mean(),
                ci_lo=np.quantile(bs, .025), ci_hi=np.quantile(bs, .975),
                p=2 * min((bs <= 0).mean(), (bs >= 0).mean()))


SCOPES = []
for sdef in ["RTH", "BROKER"]:
    SCOPES.append((f"{sdef} all", X[X.sessdef == sdef]))

# ---------------------------------------------------------------- Stage A
MEAS = (["up_atr", "dn_atr", "total_range_atr", "larger_atr", "smaller_atr",
         "ratio_small_large", "larger_side_up", "high_before_low", "t_high", "t_low"]
        + [f"{s}_{k}" for k in [0.25, 0.5, 0.75, 1.0] for s in ["up", "dn", "both", "one_only", "neither"]]
        + [f"t_first_{k}" for k in [0.25, 0.5]]
        + [f"first_side_up_{k}" for k in [0.25, 0.5]])
rows = []
for name, d in SCOPES:
    for c in MEAS:
        r = boot(d, c)
        if r:
            rows.append(dict(scope=name, measure=c, **r))
A = pd.DataFrame(rows)
A.to_csv(OUT / "c3_stageA_topology.csv", index=False)

# ---------------------------------------------------------------- independence check
ind = []
for name, d in SCOPES:
    for k in [0.25, 0.5, 0.75, 1.0]:
        for lab, sub in [("triggered", d[d.trig_down]), ("opposite", d[~d.trig_down])]:
            pu = sub[f"up_{k}"].mean(); pd_ = sub[f"dn_{k}"].mean(); pb = sub[f"both_{k}"].mean()
            ind.append(dict(scope=name, k=k, group=lab, n=len(sub),
                            P_up=pu, P_dn=pd_, P_both_observed=pb,
                            P_both_if_independent=pu * pd_,
                            excess=pb - pu * pd_,
                            lift=pb / (pu * pd_) if pu * pd_ > 0 else np.nan))
I = pd.DataFrame(ind)
I.to_csv(OUT / "c3_joint_independence.csv", index=False)

# ---------------------------------------------------------------- Stage B sequences
SEQ = []
for k in [0.25, 0.5]:
    SEQ += [f"leg{k}_retr50", f"leg{k}_retr100", f"leg{k}_opp",
            f"leg{k}_t", f"leg{k}_t_retr100", f"leg{k}_t_opp", f"leg{k}_leg_ext_atr",
            f"leg{k}_post_move_atr"]
rows = []
for name, d in SCOPES:
    for c in SEQ:
        r = boot(d, c)
        if r:
            rows.append(dict(scope=name, measure=c, **r))
    # complementary full-sequence frequency: first leg -> back through open -> opposite k
    for k in [0.25, 0.5]:
        d2 = d.copy()
        d2[f"full_seq_{k}"] = d2[f"leg{k}_retr100"].fillna(False).astype(bool) & d2[f"leg{k}_opp"].fillna(False).astype(bool)
        r = boot(d2, f"full_seq_{k}")
        if r:
            rows.append(dict(scope=name, measure=f"FULL SEQ leg{k}->open->opposite{k}", **r))
B = pd.DataFrame(rows)
B.to_csv(OUT / "c3_stageB_sequences.csv", index=False)

pd.set_option("display.width", 250)
print("######## THE DECISIVE TEST: does the SMALLER side expand too? ########")
key = ["up_atr", "dn_atr", "larger_atr", "smaller_atr", "ratio_small_large", "total_range_atr"]
print(A[A.measure.isin(key)][["scope", "measure", "trig", "opp", "diff", "ci_lo", "ci_hi", "p"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\n######## both-side threshold crossing ########")
k2 = [f"{s}_{k}" for k in [0.25, 0.5, 0.75, 1.0] for s in ["both", "one_only"]]
print(A[A.measure.isin(k2)][["scope", "measure", "trig", "opp", "diff", "ci_lo", "ci_hi", "p"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\n######## same-day joint vs independence ########")
print(I.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\n######## first-leg ordering / retracement / complementary sequence ########")
print(B[["scope", "measure", "n_trig", "trig", "opp", "diff", "ci_lo", "ci_hi", "p"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\n######## first-side direction and timing ########")
k3 = ["larger_side_up", "high_before_low", "first_side_up_0.25", "first_side_up_0.5",
      "t_first_0.25", "t_first_0.5", "t_high", "t_low"]
print(A[A.measure.isin(k3)][["scope", "measure", "trig", "opp", "diff", "ci_lo", "ci_hi", "p"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
