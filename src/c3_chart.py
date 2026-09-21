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
A = pd.read_csv(OUT / "c3_stageA_topology.csv")
X = pd.read_csv(OUT / "c3_joint_independence.csv")

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
# (a) the decisive test
ax = axes[0]
d = A[A.scope == "RTH all"].set_index("measure")
keys = ["larger_atr", "smaller_atr", "ratio_small_large"]
labs = ["larger side", "smaller side", "smaller / larger"]
xs = np.arange(3); w = .36
ax.bar(xs - w/2, [d.loc[k, "opp"] for k in keys], w, color=GREY, label="Fri high ≥ Thu high")
ax.bar(xs + w/2, [d.loc[k, "trig"] for k in keys], w, color=RED, label="Fri high < Thu high")
for i, k in enumerate(keys):
    p = d.loc[k, "p"]
    ax.text(i, max(d.loc[k, "opp"], d.loc[k, "trig"]) + .02,
            f"{d.loc[k,'diff']:+.3f}\n{'p<0.001' if p<0.001 else f'p={p:.2f}'}",
            ha="center", fontsize=7.5, color="black" if p < .05 else "#888")
ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=8)
ax.set_ylabel("ATR"); ax.legend(fontsize=7.5)
ax.set_title("Both sides expand, ratio unchanged\n→ proportional scaling, not one-sided", fontsize=9.5)

# (b) both-side threshold crossing
ax = axes[1]
ks = [0.25, 0.5, 0.75, 1.0]
for sc, c, m in [("RTH all", RED, "o"), ("BROKER all", BLUE, "s")]:
    dd = A[A.scope == sc].set_index("measure")
    ax.plot(ks, [dd.loc[f"both_{k}", "trig"] for k in ks], marker=m, color=c, label=f"{sc.split()[0]} triggered")
    ax.plot(ks, [dd.loc[f"both_{k}", "opp"] for k in ks], marker=m, color=c, ls="--", alpha=.55,
            label=f"{sc.split()[0]} opposite")
ax.set_xlabel("threshold, ATR"); ax.set_ylabel("P(BOTH sides reach it, same Monday)")
ax.legend(fontsize=7); ax.set_title("Same-session two-sided crossing", fontsize=9.5)

# (c) joint vs independence
ax = axes[2]
for sc, c in [("RTH all", RED), ("BROKER all", BLUE)]:
    for grp, ls in [("triggered", "-"), ("opposite", "--")]:
        s = X[(X.scope == sc) & (X.group == grp)]
        ax.plot(s.k, s.lift, ls, marker="o", color=c, alpha=1 if grp == "triggered" else .55,
                label=f"{sc.split()[0]} {grp}")
ax.axhline(1, c="k", lw=1)
ax.text(0.30, 1.03, "independence", fontsize=7)
ax.set_xlabel("threshold, ATR"); ax.set_ylabel("P(both) / [P(up)·P(down)]")
ax.legend(fontsize=7); ax.set_title("Still one-side-dominant days —\nbut less so when triggered", fontsize=9.5)
fig.suptitle("Cycle 3 closure: the joint topology of the Monday range expansion", y=1.04)
fig.tight_layout(); fig.savefig(CH / "c3_01_joint_topology.png", bbox_inches="tight"); plt.close(fig)

# --- sequence chart
B = pd.read_csv(OUT / "c3_stageB_sequences.csv")
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
ax = axes[0]
seq = ["leg0.25_retr100", "leg0.25_opp", "FULL SEQ leg0.25->open->opposite0.25",
       "leg0.5_retr100", "leg0.5_opp", "FULL SEQ leg0.5->open->opposite0.5"]
labs = ["0.25 leg →\ncross open", "0.25 leg →\nopposite 0.25", "full 0.25\nsequence",
        "0.5 leg →\ncross open", "0.5 leg →\nopposite 0.5", "full 0.5\nsequence"]
d = B[B.scope == "RTH all"].set_index("measure")
xs = np.arange(len(seq)); w = .36
ax.bar(xs - w/2, [d.loc[k, "opp"] for k in seq], w, color=GREY, label="opposite condition")
ax.bar(xs + w/2, [d.loc[k, "trig"] for k in seq], w, color=RED, label="triggered")
for i, k in enumerate(seq):
    p = d.loc[k, "p"]
    ax.text(i, max(d.loc[k, "opp"], d.loc[k, "trig"]) + .015, "n.s." if p >= .05 else f"p={p:.3f}",
            ha="center", fontsize=7, color="#888" if p >= .05 else "black")
ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=7); ax.set_ylabel("frequency")
ax.legend(fontsize=7.5); ax.set_title("RTH: the retracement itself is NOT elevated —\nonly the opposite extension after it", fontsize=9.5)

ax = axes[1]
pm = ["leg0.25_post_move_atr", "leg0.5_post_move_atr"]
for sc, c, off in [("RTH all", RED, -.18), ("BROKER all", BLUE, .18)]:
    dd = B[B.scope == sc].set_index("measure")
    xs2 = np.arange(2) + off
    ax.bar(xs2, [dd.loc[k, "trig"] for k in pm], .34, color=c, label=f"{sc.split()[0]} triggered",
           yerr=[[dd.loc[k, "trig"] - dd.loc[k, "opp"] for k in pm], [0, 0]], error_kw=dict(lw=0))
    ax.plot(xs2, [dd.loc[k, "opp"] for k in pm], "_", color="k", ms=22, mew=2)
ax.set_xticks([0, 1]); ax.set_xticklabels(["after 0.25 leg\n+ open cross", "after 0.5 leg\n+ open cross"], fontsize=8)
ax.set_ylabel("opposite-side movement available, ATR")
ax.legend(fontsize=7.5)
ax.set_title("Post-observation movement\n(black dash = opposite condition)", fontsize=9.5)
fig.suptitle("Cycle 3 closure: first-leg sequences", y=1.04)
fig.tight_layout(); fig.savefig(CH / "c3_02_sequences.png", bbox_inches="tight"); plt.close(fig)
print("ok", [p.name for p in sorted(CH.glob("c3_*.png"))])
