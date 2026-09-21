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
RED, GREY, GREEN = "#c0392b", "#9aa5b1", "#27ae60"
G = pd.read_csv(OUT / "postcross_geometry.csv")
E = pd.read_csv(OUT / "postcross_economics.csv")

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4))
# (a) the reconciliation
ax = axes[0]
d = G[G.sessdef == "RTH"].set_index("group")
x = np.arange(2); w = .36
ax.bar(x - w/2, [d.loc["control", "MFE_atr_mean"], d.loc["control", "MAE_atr_mean"]], w,
       color=GREY, label="control")
ax.bar(x + w/2, [d.loc["triggered", "MFE_atr_mean"], d.loc["triggered", "MAE_atr_mean"]], w,
       color=RED, label="triggered")
ax.set_xticks(x); ax.set_xticklabels(["favourable\n(the 0.445 ATR figure)", "ADVERSE\nfrom the same entry"], fontsize=8)
ax.set_ylabel("mean excursion after the cross, ATR")
ax.legend(fontsize=8)
ax.set_title("The extra favourable move is matched\nby extra adverse move", fontsize=9.5)
for i, (c, t) in enumerate([(d.loc["control", "MFE_atr_mean"], d.loc["triggered", "MFE_atr_mean"]),
                            (d.loc["control", "MAE_atr_mean"], d.loc["triggered", "MAE_atr_mean"])]):
    ax.text(i + w/2, t + .012, f"+{t-c:.3f}", ha="center", fontsize=7.5)

# (b) the margin that is left
ax = axes[1]
xs = np.arange(2); lab = []
for i, sd in enumerate(["RTH", "BROKER"]):
    dd = G[G.sessdef == sd].set_index("group")
    ax.bar(i - .18, dd.loc["control", "MFE_minus_MAE"], .34, color=GREY)
    ax.bar(i + .18, dd.loc["triggered", "MFE_minus_MAE"], .34, color=RED)
    lab.append(sd)
ax.axhline(0, c="k", lw=1)
ax.axhline(0.023, c=GREEN, ls=":", lw=1.4)
ax.text(1.35, 0.026, "round-trip cost", fontsize=7, color=GREEN)
ax.set_xticks(xs); ax.set_xticklabels(lab)
ax.set_ylabel("mean (favourable − adverse), ATR")
ax.set_title("What is left over: +0.05 to +0.06 ATR\nof UNREALISABLE maxima", fontsize=9.5)

# (c) R attainment
ax = axes[2]
d = E[(E.sessdef == "RTH") & (E.construction.str.startswith("S2b"))].iloc[0]
d2 = E[(E.sessdef == "BROKER") & (E.construction.str.startswith("S2b"))].iloc[0]
ks = ["hit_1R", "hit_2R", "hit_3R"]
xs = np.arange(3)
ax.bar(xs - .18, [d[k] for k in ks], .34, color=RED, label="RTH")
ax.bar(xs + .18, [d2[k] for k in ks], .34, color="#2980b9", label="broker day")
ax.set_xticks(xs); ax.set_xticklabels(["reaches 1R", "reaches 2R", "reaches 3R"])
ax.set_ylabel("share of signals"); ax.legend(fontsize=8)
ax.set_title("2R+ is the programme objective.\nOnly 8–13% of signals ever see it.", fontsize=9.5)
fig.suptitle("Final futures/CFD test: statistically larger movement ≠ economically capturable", y=1.04)
fig.tight_layout(); fig.savefig(CH / "c4_01_postcross.png", bbox_inches="tight"); plt.close(fig)
print("ok")
