"""Adversarial checks: effective independence of the replication, and the strongest
reasonable ('double bottom') reading of the claim."""
import sys, os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
CH = OUT / "charts"
T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")

SETS = {
    "Duka NAS100+US500 RTH": T[(T.sessdef == "RTH") & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(["NAS100", "US500"])],
    "Duka NAS100+US500 BROKER": T[(T.sessdef == "BROKER") & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(["NAS100", "US500"])],
    "YF ES+NQ daily 2000-2026": Y[(Y.B_wd == 4) & (Y.C_wd == 0) & Y.instrument.isin(["YF_ES", "YF_NQ"])],
}
TOLS = [0, .05, .10, .25, .50, .75, 1.0]
rows = []
for lab, d in SETS.items():
    d = d.dropna(subset=["atr_at_B"])
    for tol in TOLS:
        ev = d.C_low <= d.B_low + tol * d.atr_at_B
        rows.append(dict(dataset=lab, tol_ATR=tol, n_trigger=int(d.trig_down.sum()),
                         rate=ev[d.trig_down].mean(), opposite=ev[~d.trig_down].mean(),
                         uplift=ev[d.trig_down].mean() - ev[~d.trig_down].mean()))
T2 = pd.DataFrame(rows); T2.to_csv(OUT / "tolerance_ladder.csv", index=False)

# independence
rows = []
def pair(d, i1, i2, lab):
    a = d[d.instrument == i1].set_index("C_date"); b = d[d.instrument == i2].set_index("C_date")
    j = a.join(b, rsuffix="_2", how="inner")
    return dict(pair=lab, n=len(j),
                corr_outcome=np.corrcoef(j.touch_low.astype(float), j.touch_low_2.astype(float))[0, 1],
                corr_trigger=np.corrcoef(j.trig_down.astype(float), j.trig_down_2.astype(float))[0, 1],
                agreement=(j.touch_low == j.touch_low_2).mean())
D = T[(T.sessdef == "RTH") & (T.B_wd == 4) & (T.C_wd == 0)]
rows += [pair(D, "NAS100", "US500", "NAS100 vs US500 (Dukascopy RTH)"),
         pair(D, "EURUSD", "GBPUSD", "EURUSD vs GBPUSD"),
         pair(D, "EURUSD", "USDJPY", "EURUSD vs USDJPY"),
         pair(Y[(Y.B_wd == 4) & (Y.C_wd == 0)], "YF_ES", "YF_NQ", "ES vs NQ (Yahoo daily)")]
a = D[D.instrument == "NAS100"].set_index("C_date")
b = Y[(Y.B_wd == 4) & (Y.C_wd == 0) & (Y.instrument == "YF_NQ")].set_index("C_date")
j = a.join(b, rsuffix="_y", how="inner")
rows.append(dict(pair="NAS100 CFD vs NQ futures (cross-vendor)", n=len(j),
                 corr_outcome=np.corrcoef(j.touch_low.astype(float), j.touch_low_y.astype(float))[0, 1],
                 corr_trigger=np.corrcoef(j.trig_down.astype(float), j.trig_down_y.astype(float))[0, 1],
                 agreement=(j.touch_low == j.touch_low_y).mean()))
pd.DataFrame(rows).to_csv(OUT / "independence.csv", index=False)

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True, "grid.alpha": .3,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(8.5, 4))
for lab, c in zip(SETS, ["#c0392b", "#e67e22", "#2c3e50"]):
    d = T2[T2.dataset == lab]
    ax.plot(d.tol_ATR, d.rate, marker="o", color=c, label=f"{lab} — triggered")
    ax.plot(d.tol_ATR, d.opposite, marker="o", ls="--", color=c, alpha=.55, label=f"{lab} — opposite")
ax.axhline(.9, ls=":", c="k", lw=.9); ax.text(.76, .905, "Hougaard's \">90%\"", fontsize=7.5)
ax.set_xlabel("tolerance on the retest, in ATR14  (0 = strict touch of Friday's low)")
ax.set_ylabel("P(event)")
ax.set_title("The high hit rates are reachable only with a tolerance so loose\nthat the opposite condition does almost as well")
ax.legend(fontsize=7, loc="lower right")
fig.tight_layout(); fig.savefig(CH / "09_tolerance_ladder.png", bbox_inches="tight"); plt.close(fig)

# redo placebo chart with better legend placement
pl = pd.read_csv(OUT / "placebo.csv")
fig, ax = plt.subplots(figsize=(8.5, 3.8))
y = np.arange(len(pl))
ax.barh(y, pl.shuffle_mean, xerr=1.96 * pl.shuffle_sd, height=.45, color="#9aa5b1",
        label="placebo: temporal pairing destroyed (95% band)")
ax.scatter(pl.observed_uplift, y, color="#c0392b", zorder=5, s=45, label="observed uplift")
ax.set_yticks(y); ax.set_yticklabels(pl.dataset, fontsize=7.5)
ax.set_xlim(0, max(pl.observed_uplift.max(), (pl.shuffle_mean + 2 * pl.shuffle_sd).max()) * 1.28)
ax.set_xlabel("uplift in P(touch Friday low) vs opposite condition")
ax.set_title("Placebo: does the effect survive destroying the temporal pairing?")
ax.legend(fontsize=7.5, loc="lower right", framealpha=.95)
fig.tight_layout(); fig.savefig(CH / "03_placebo.png", bbox_inches="tight"); plt.close(fig)
print(T2.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
