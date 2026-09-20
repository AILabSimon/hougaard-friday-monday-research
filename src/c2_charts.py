import sys, os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
CH = OUT / "charts"
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True, "grid.alpha": .3,
                     "axes.spines.top": False, "axes.spines.right": False})
RED, GREY, BLUE = "#c0392b", "#9aa5b1", "#2980b9"

# ---------------- C1: the decomposition
C = pd.read_csv(OUT / "stageC_path.csv")
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for ax, sdef in zip(axes, ["RTH", "BROKER"]):
    d = C[C.sessdef == sdef].set_index("measure")
    keys = ["touch_Blow", "low_by_gap", "travelled_to_low"]
    labs = ["Monday touches\nFriday's low", "…already gone at the open\n(gap through)",
            "…TRAVELLED to during Monday\n(the only tradeable part)"]
    x = np.arange(3); w = .36
    ax.bar(x - w/2, [d.loc[k, "opp_mean"] for k in keys], w, color=GREY, label="Fri high ≥ Thu high")
    ax.bar(x + w/2, [d.loc[k, "trig_mean"] for k in keys], w, color=RED, label="Fri high < Thu high")
    for i, k in enumerate(keys):
        p = d.loc[k, "p_cluster"]
        ax.text(i, max(d.loc[k, "opp_mean"], d.loc[k, "trig_mean"]) + .02,
                f"Δ{d.loc[k,'diff']:+.3f}\n{'p<0.001' if p<0.001 else f'p={p:.3f}'}",
                ha="center", fontsize=7.5,
                color="black" if p < .05 else "#777")
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=7.5)
    ax.set_title(f"{sdef} day"); ax.set_ylim(0, .62)
axes[0].set_ylabel("probability"); axes[0].legend(fontsize=8)
fig.suptitle("Where the Friday-low effect actually comes from\n"
             "Under Hougaard's own RTH definition it is the weekend gap, not Monday's path", y=1.06)
fig.tight_layout(); fig.savefig(CH / "c2_01_gap_vs_travelled.png", bbox_inches="tight"); plt.close(fig)

# ---------------- C2: what changes / what doesn't, in the tradeable state
K = pd.read_csv(OUT / "stageC_conditional.csv")
d = K[(K.sessdef == "RTH") & (K.scope == "opens AT/ABOVE Fri low (tradeable)")].copy()
order = ["touch_Blow", "mfe_down_atr", "seq_low_first", "Blow_by30", "Blow_by60",
         "first_move_dn", "or15_dn", "or30_dn", "dir60_up", "net30_atr", "net60_atr",
         "ret_close_atr", "mfe_up_atr", "pen_after_Blow_atr", "bounce_after_Blow_atr",
         "mae_before_Blow_atr"]
lab = {"touch_Blow": "touches Friday's low", "mfe_down_atr": "max down-excursion (ATR)",
       "seq_low_first": "low before high", "Blow_by30": "low touched by 30 min",
       "Blow_by60": "low touched by 60 min", "first_move_dn": "first 0.25-ATR move is down",
       "or15_dn": "15-min opening range breaks DOWN", "or30_dn": "30-min opening range breaks DOWN",
       "dir60_up": "up after 60 min", "net30_atr": "net (down−up) 30 min",
       "net60_atr": "net (down−up) 60 min", "ret_close_atr": "Monday close − open",
       "mfe_up_atr": "max up-excursion (ATR)", "pen_after_Blow_atr": "penetration past the low",
       "bounce_after_Blow_atr": "bounce off the low", "mae_before_Blow_atr": "adverse move before the low"}
d = d.set_index("measure").reindex(order).dropna(subset=["diff"])
y = np.arange(len(d))[::-1]
fig, ax = plt.subplots(figsize=(8.5, 5.2))
col = [RED if p < .05 else GREY for p in d.p]
for i, (xv, yv, c) in enumerate(zip(d["diff"], y, col)):
    ax.plot([d.ci_lo.iloc[i], d.ci_hi.iloc[i]], [yv, yv], color=c, lw=1.6)
    ax.plot(xv, yv, "o", color=c, ms=5)
ax.axvline(0, c="k", lw=1)
ax.set_yticks(y); ax.set_yticklabels([lab[i] for i in d.index], fontsize=8)
ax.set_xlabel("triggered − opposite   (week-clustered 95% CI)")
ax.set_title("Monday path when the level is still reachable at the open\n"
             "Only eventual reach changes. Timing, direction and sequencing do not.", fontsize=10)
fig.tight_layout(); fig.savefig(CH / "c2_02_tradeable_state.png", bbox_inches="tight"); plt.close(fig)

# ---------------- C3: dependence-aware forest
A = pd.read_csv(OUT / "stageA_dependence.csv")
A = A[~A["sample"].str.startswith("CONTROL")].reset_index(drop=True)
y = np.arange(len(A))[::-1]
fig, ax = plt.subplots(figsize=(9, 5))
for i, r in enumerate(A.itertuples()):
    yy = y[i]
    c = RED if r.p_cluster_2sided < .05 else GREY
    ax.plot([r.ci_lo_cluster, r.ci_hi_cluster], [yy, yy], color=c, lw=1.8)
    ax.plot(r.beta_ctrl, yy, "o", color=c, ms=5)
    ax.plot([r.beta_ctrl - 1.96 * r.se_naive, r.beta_ctrl + 1.96 * r.se_naive], [yy + .28, yy + .28],
            color=BLUE, lw=1.0, alpha=.7)
ax.axvline(0, c="k", lw=1)
ax.set_yticks(y); ax.set_yticklabels(A["sample"], fontsize=7.5)
ax.set_xlabel("controlled logistic coefficient on the trigger")
ax.set_title("Stage A — week-clustered intervals (thick) vs Cycle-1 naive intervals (thin blue)\n"
             "Red = 95% interval excludes zero", fontsize=10)
fig.tight_layout(); fig.savefig(CH / "c2_03_dependence.png", bbox_inches="tight"); plt.close(fig)

# ---------------- C4: Stage D, and the defect
D = pd.read_csv(OUT / "stageD_entries.csv")
d = D[D.sessdef == "RTH"].copy()
fam_order = ["D1 short at Monday open", "D2 short limit above open",
             "D3a INVALID (incl. gap-through)", "D3b short break of Friday low"]
fig, ax = plt.subplots(figsize=(9.5, 4.2))
pos = 0; ticks, labels = [], []
for f in fam_order:
    s = d[d.family == f]
    xs = np.arange(len(s)) + pos
    c = "#7f8c8d" if f.startswith("D3a") else RED
    ax.bar(xs, s.meanR_trig, .7, color=c,
           yerr=[s.meanR_trig - s.trig_ci_lo, s.trig_ci_hi - s.meanR_trig],
           ecolor="k", capsize=2, error_kw=dict(lw=.8))
    ticks.append(xs.mean()); labels.append(f.replace(" ", "\n", 1))
    pos += len(s) + 1.5
ax.axhline(0, c="k", lw=1)
ax.set_xticks(ticks); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("mean R per trade, net of costs\n(triggered weeks, week-clustered 95% CI)")
ax.set_title("Stage D — every construction tested.  D3a's apparent edge is a phantom fill:\n"
             "on gap-through Mondays you cannot sell at Friday's low, worth a median 1.23R of free profit.",
             fontsize=9.5)
fig.tight_layout(); fig.savefig(CH / "c2_04_stageD.png", bbox_inches="tight"); plt.close(fig)
print("charts:", [p.name for p in sorted(CH.glob("c2_*.png"))])
