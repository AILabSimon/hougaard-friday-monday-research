import sys, os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import OUT
CH = OUT / "charts"
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True, "grid.alpha": .3,
                     "axes.spines.top": False, "axes.spines.right": False})
RED, GREY = "#c0392b", "#9aa5b1"

# --- 05: corrected decomposition, RTH vs ES/NQ
D = pd.read_csv(OUT / "c2_decomposition.csv")
sets = ["Dukascopy NAS100+US500 RTH", "Dukascopy NAS100+US500 BROKER", "Yahoo ES+NQ daily 2000-2026"]
labs = ["NAS100/US500\nRTH day (6.5h)", "NAS100/US500\nbroker day (23h)", "ES + NQ\nfutures day, 2000-2026"]
keys = ["low_by_gap", "travelled_to_low"]
fig, ax = plt.subplots(figsize=(9, 4.2))
x = np.arange(len(sets)); w = .38
gap = [D[(D["sample"] == s) & (D.measure == "low_by_gap")]["diff"].iloc[0] for s in sets]
trv = [D[(D["sample"] == s) & (D.measure == "travelled_to_low")]["diff"].iloc[0] for s in sets]
pg = [D[(D["sample"] == s) & (D.measure == "low_by_gap")].p.iloc[0] for s in sets]
pt = [D[(D["sample"] == s) & (D.measure == "travelled_to_low")].p.iloc[0] for s in sets]
b1 = ax.bar(x - w/2, gap, w, color=GREY, label="already gone at the open (gap through)")
b2 = ax.bar(x + w/2, trv, w, color=RED, label="TRAVELLED to during the session")
for i in range(len(sets)):
    ax.text(x[i] - w/2, gap[i] + .004, f"+{gap[i]:.3f}\n{'p<0.001' if pg[i]<0.001 else f'p={pg[i]:.3f}'}",
            ha="center", fontsize=7.5)
    ax.text(x[i] + w/2, trv[i] + .004, f"+{trv[i]:.3f}\n{'p<0.001' if pt[i]<0.001 else f'p={pt[i]:.3f}'}",
            ha="center", fontsize=7.5, color="black" if pt[i] < .05 else "#888")
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=8.5)
ax.set_ylabel("contribution to the uplift in P(Monday reaches Friday's low)")
ax.set_ylim(0, max(max(gap), max(trv)) * 1.35)
ax.legend(fontsize=8)
ax.set_title("Gap or travel?  It depends entirely on the session window you trade.\n"
             "In a cash-hours window the level is mostly gone at the bell; in a futures session it is travelled to.",
             fontsize=9.5)
fig.tight_layout(); fig.savefig(CH / "c2_05_decomposition_by_session.png", bbox_inches="tight"); plt.close(fig)

# --- 06: weekday pairs, clustered
W = pd.read_csv(OUT / "c2_weekday_pairs.csv")
fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
for ax, (src, sdef, t) in zip(axes, [("Dukascopy NAS100+US500", "RTH", "NAS100/US500 — RTH"),
                                     ("Dukascopy NAS100+US500", "BROKER", "NAS100/US500 — broker day"),
                                     ("Yahoo ES+NQ daily", "YF_DAILY", "ES+NQ — 2000-2026")]):
    d = W[(W.source == src) & (W.session_def == sdef)].set_index("B_weekday").reindex(["Mon", "Tue", "Wed", "Thu", "Fri"])
    xs = np.arange(5)
    for i, r in enumerate(d.itertuples()):
        c = RED if r.p_cluster < .05 else GREY
        ax.plot([xs[i], xs[i]], [r.ci_lo, r.ci_hi], color=c, lw=2)
        ax.plot(xs[i], r.beta_ctrl, "o", color=c, ms=6)
    ax.axhline(0, c="k", lw=1); ax.set_xticks(xs); ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri"])
    ax.set_title(t, fontsize=9.5); ax.set_xlabel("day whose high failed")
axes[0].set_ylabel("controlled logit β on the trigger\n(week-clustered 95% CI)")
fig.suptitle("Friday→Monday is the strongest weekday pair under identical uncertainty treatment", y=1.04)
fig.tight_layout(); fig.savefig(CH / "c2_06_weekday_pairs.png", bbox_inches="tight"); plt.close(fig)

# --- 07: range expansion, the surviving effect
Rg = pd.read_csv(OUT / "c2_range_effect.csv")
Rg = Rg.iloc[::-1].reset_index(drop=True)
y = np.arange(len(Rg))
fig, ax = plt.subplots(figsize=(9, 4.6))
for i, r in enumerate(Rg.itertuples()):
    c = RED if r.p_ctrl < .05 else GREY
    ax.plot([r.ctrl_lo, r.ctrl_hi], [y[i], y[i]], color=c, lw=2.2)
    ax.plot(r.beta_ctrl, y[i], "o", color=c, ms=6)
    ax.text(r.ctrl_hi + .006, y[i], f"+{r.pct_uplift:.0f}%", va="center", fontsize=7.5, color=c)
ax.axvline(0, c="k", lw=1)
ax.set_yticks(y); ax.set_yticklabels(Rg["sample"], fontsize=7.5)
ax.set_xlabel("extra Monday range when Friday failed Thursday's high, in ATR14\n"
              "(controlled for Friday range/ATR, Friday close-in-range, instrument)")
ax.set_title("The effect that does survive everything: Monday's range expands\n"
             "Two-sided, so no directional construction captures it", fontsize=10)
fig.tight_layout(); fig.savefig(CH / "c2_07_range_expansion.png", bbox_inches="tight"); plt.close(fig)
print("charts:", [p.name for p in sorted(CH.glob("c2_0[567]*.png"))])
