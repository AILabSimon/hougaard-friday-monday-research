"""Consolidate every material result into three CSVs + the decision-relevant charts."""
import sys, os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
from stats_util import wilson, newcombe_diff, two_prop_test

CH = OUT / "charts"; CH.mkdir(parents=True, exist_ok=True)
T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")
W = pd.read_parquet(DERIVED / "triples" / "triples_weekly.parquet")
S3 = pd.read_parquet(DERIVED / "triples" / "triples_session3.parquet")
P = pd.read_parquet(DERIVED / "monday_paths.parquet")
G = pd.read_parquet(DERIVED / "monday_grid.parquet")

GRP = lambda df: np.where(df.instrument.isin(["NAS100", "US500", "YF_ES", "YF_NQ"]), "US_INDEX",
                 np.where(df.asset_class == "FX", "FX",
                 np.where(df.instrument.isin(["BTCUSD"]), "CRYPTO", "COMMOD")))
T["grp"] = GRP(T); Y["grp"] = GRP(Y); P["grp"] = GRP(P); G["grp"] = GRP(G)


def logit_fit(X, y, ridge=1e-4, iters=200):
    X = np.asarray(X, float); y = np.asarray(y, float); b = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ b; p = 1 / (1 + np.exp(-np.clip(eta, -30, 30))); Wt = np.clip(p * (1 - p), 1e-8, None)
        H = X.T @ (X * Wt[:, None]) + ridge * np.eye(X.shape[1]); g = X.T @ (y - p) - ridge * b
        s = np.linalg.solve(H, g); b = b + s
        if np.max(np.abs(s)) < 1e-9: break
    eta = X @ b; p = 1 / (1 + np.exp(-np.clip(eta, -30, 30))); Wt = np.clip(p * (1 - p), 1e-8, None)
    return b, np.sqrt(np.diag(np.linalg.inv(X.T @ (X * Wt[:, None]) + ridge * np.eye(X.shape[1]))))


def ctrl_beta(d):
    d = d.dropna(subset=["atr_at_B"]).copy(); d = d[d.B_range > 0]
    if len(d) < 80 or d.trig_down.nunique() < 2: return np.nan, np.nan
    X = np.column_stack([np.ones(len(d)), d.trig_down.astype(float),
                         (d.B_close - d.B_low) / d.atr_at_B, d.B_range / d.atr_at_B])
    b, se = logit_fit(X, d.touch_low.values.astype(float))
    return b[1], b[1] / se[1]


def row(d, **meta):
    t, o = d[d.trig_down], d[~d.trig_down]
    if len(t) < 30 or len(o) < 30: return None
    k, n, ko, no = int(t.touch_low.sum()), len(t), int(o.touch_low.sum()), len(o)
    lo, hi = wilson(k, n); dlo, dhi = newcombe_diff(k, n, ko, no)
    p, h = two_prop_test(k, n, ko, no)
    b, z = ctrl_beta(d)
    med_t = np.nan
    return dict(**meta, n_eligible=len(d), n_trigger=n, touches=k, hit_rate=k / n,
                ci95_lo=lo, ci95_hi=hi, base_rate_all=d.touch_low.mean(),
                opposite_rate=ko / no, uplift_vs_opposite=k / n - ko / no,
                uplift_ci_lo=dlo, uplift_ci_hi=dhi, fisher_p=p, cohens_h=h,
                logit_beta_controlled=b, logit_z_controlled=z)


# ---------------------------------------------------------- core_results.csv
core = []
for sdef in ["RTH", "BROKER", "NYFX", "UTC", "LONDON"]:
    D = T[(T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0)]
    for inst, g in D.groupby("instrument"):
        r = row(g, dataset="Dukascopy_1m", instrument=inst, asset_group=g.grp.iloc[0],
                session_def=sdef, period="2016-2026", scope="Fri->Mon")
        if r: core.append(r)
    for grp, g in D.groupby("grp"):
        r = row(g, dataset="Dukascopy_1m", instrument=f"POOL_{grp}", asset_group=grp,
                session_def=sdef, period="2016-2026", scope="Fri->Mon")
        if r: core.append(r)
Dy = Y[(Y.B_wd == 4) & (Y.C_wd == 0)]
for inst, g in Dy.groupby("instrument"):
    r = row(g, dataset="Yahoo_daily_futures", instrument=inst, asset_group=g.grp.iloc[0],
            session_def="YF_DAILY", period="2000-2026", scope="Fri->Mon")
    if r: core.append(r)
for grp, g in Dy.groupby("grp"):
    r = row(g, dataset="Yahoo_daily_futures", instrument=f"POOL_{grp}", asset_group=grp,
            session_def="YF_DAILY", period="2000-2026", scope="Fri->Mon")
    if r: core.append(r)
# time-to-touch on the pooled sets
tt = P[P.trig_down & P.t_Blow.notna()].groupby(["sessdef", "grp"]).frac_Blow.median().to_dict()
CORE = pd.DataFrame(core)
CORE["median_frac_session_to_touch"] = [tt.get((r.session_def, r.asset_group), np.nan) for r in CORE.itertuples()]
CORE.to_csv(OUT / "core_results.csv", index=False)

# ---------------------------------------------------------- controls.csv
ctl = []
for sdef in ["RTH", "BROKER"]:
    D = T[T.sessdef == sdef]
    for wd in range(5):
        for grp, g in D[D.B_wd == wd].groupby("grp"):
            r = row(g, control="adjacent_weekday_down", dataset="Dukascopy_1m",
                    asset_group=grp, session_def=sdef, B_weekday=["Mon","Tue","Wed","Thu","Fri"][wd])
            if r: ctl.append(r)
        # upside symmetry
        for grp, g in D[D.B_wd == wd].groupby("grp"):
            gg = g.rename(columns={"trig_down": "_td", "touch_low": "_tl",
                                   "trig_up": "trig_down", "touch_high": "touch_low"})
            r = row(gg, control="upside_symmetry", dataset="Dukascopy_1m",
                    asset_group=grp, session_def=sdef, B_weekday=["Mon","Tue","Wed","Thu","Fri"][wd])
            if r: ctl.append(r)
        # placebo wrong-way
        for grp, g in D[D.B_wd == wd].groupby("grp"):
            gg = g.rename(columns={"touch_low": "_tl", "touch_high": "touch_low"})
            r = row(gg, control="placebo_wrong_direction", dataset="Dukascopy_1m",
                    asset_group=grp, session_def=sdef, B_weekday=["Mon","Tue","Wed","Thu","Fri"][wd])
            if r: ctl.append(r)
for grp, g in W.groupby("asset_class"):
    r = row(g, control="weekly_analogue", dataset="Dukascopy_1m", asset_group=grp,
            session_def="WEEKLY(broker days)", B_weekday="week")
    if r: ctl.append(r)
S3["pair"] = S3.B_slot.astype(str) + "->" + S3.C_slot.astype(str)
for (ac, pr), g in S3.groupby(["asset_class", "pair"]):
    r = row(g, control="intraday_session_analogue", dataset="Dukascopy_1m",
            asset_group=ac, session_def="SESSION3(UTC blocks)", B_weekday=pr)
    if r: ctl.append(r)
CTL = pd.DataFrame(ctl)
pl = pd.read_csv(OUT / "placebo.csv")
pl["control"] = "placebo_path_shuffle"
CTL = pd.concat([CTL, pl], ignore_index=True)
CTL.to_csv(OUT / "controls.csv", index=False)

# ---------------------------------------------------------- robustness.csv
rob = []
for sdef in ["RTH", "BROKER", "UTC"]:
    D = T[(T.sessdef == sdef) & (T.B_wd == 4) & (T.C_wd == 0)]
    for (grp, yr), g in D.groupby(["grp", "year"]):
        r = row(g, dataset="Dukascopy_1m", asset_group=grp, session_def=sdef,
                period=str(yr), scope="Fri->Mon")
        if r: rob.append(r)
for (grp, yr), g in Dy.groupby(["grp", "year"]):
    r = row(g, dataset="Yahoo_daily_futures", asset_group=grp, session_def="YF_DAILY",
            period=str(yr), scope="Fri->Mon")
    if r: rob.append(r)
for grp, insts in [("US_INDEX", ["YF_ES", "YF_NQ"]), ("COMMOD", ["YF_CL", "YF_GC", "YF_SI"])]:
    for lab, a, b in [("DEV 2000-2015", 2000, 2015), ("VAL 2016-2026", 2016, 2026)]:
        g = Dy[Dy.instrument.isin(insts) & Dy.year.between(a, b)]
        r = row(g, dataset="Yahoo_daily_futures", asset_group=grp, session_def="YF_DAILY",
                period=lab, scope="Fri->Mon FROZEN")
        if r: rob.append(r)
pd.DataFrame(rob).to_csv(OUT / "robustness.csv", index=False)

# ---------------------------------------------------------- CHARTS
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True,
                     "grid.alpha": .3, "axes.spines.top": False, "axes.spines.right": False})

# 1 conditional vs opposite vs unconditional
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for ax, sdef in zip(axes, ["RTH", "BROKER"]):
    d = CORE[(CORE.session_def == sdef) & CORE.instrument.str.startswith("POOL_")]
    x = np.arange(len(d)); w = .27
    ax.bar(x - w, d.opposite_rate, w, label="Fri high ≥ Thu high (opposite)", color="#9aa5b1")
    ax.bar(x, d.base_rate_all, w, label="all Fridays (unconditional)", color="#5b6b7c")
    ax.bar(x + w, d.hit_rate, w, label="Fri high < Thu high (trigger)", color="#c0392b")
    ax.set_xticks(x); ax.set_xticklabels([s.replace("POOL_", "") for s in d.instrument], rotation=20)
    ax.set_title(f"P(Monday low ≤ Friday low) — {sdef} day"); ax.axhline(.5, ls=":", c="k", lw=.8)
axes[0].set_ylabel("probability"); axes[0].legend(fontsize=7.5)
fig.suptitle("Literal hypothesis: conditional vs base rate (Dukascopy 1m, 2016-2026)", y=1.02)
fig.tight_layout(); fig.savefig(CH / "01_conditional_vs_base.png", bbox_inches="tight"); plt.close(fig)

# 2 adjacent weekday: Friday is not special (raw vs controlled)
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
c = CTL[(CTL.control == "adjacent_weekday_down") & (CTL.session_def == "BROKER")]
order = ["Mon", "Tue", "Wed", "Thu", "Fri"]
for ax, col, ttl in zip(axes, ["uplift_vs_opposite", "logit_beta_controlled"],
                        ["RAW uplift vs opposite condition", "AFTER controlling for close-in-range"]):
    for grp, g in c.groupby("asset_group"):
        g = g.set_index("B_weekday").reindex(order)
        ax.plot(order, g[col], marker="o", label=grp)
    ax.axhline(0, c="k", lw=.8); ax.set_title(ttl)
axes[0].set_ylabel("Δ probability"); axes[1].set_ylabel("logit β on trigger")
axes[1].legend(fontsize=8)
fig.suptitle("Is Friday→Monday special?  (BROKER day, all adjacent weekday pairs)", y=1.02)
fig.tight_layout(); fig.savefig(CH / "02_adjacent_weekday.png", bbox_inches="tight"); plt.close(fig)

# 3 placebo
fig, ax = plt.subplots(figsize=(8, 3.6))
pl2 = pd.read_csv(OUT / "placebo.csv")
y = np.arange(len(pl2))
ax.barh(y, pl2.shuffle_mean, xerr=1.96 * pl2.shuffle_sd, height=.45,
        color="#9aa5b1", label="placebo: path-shuffled (95% band)")
ax.scatter(pl2.observed_uplift, y, color="#c0392b", zorder=5, label="observed uplift")
ax.set_yticks(y); ax.set_yticklabels(pl2.dataset, fontsize=7.5)
ax.set_xlabel("uplift in P(touch Friday low) vs opposite condition")
ax.set_title("Placebo: does the effect survive destroying the temporal pairing?")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(CH / "03_placebo.png", bbox_inches="tight"); plt.close(fig)

# 4 year by year
fig, ax = plt.subplots(figsize=(9, 3.8))
for lab, ds, sdf, c_ in [("Yahoo ES+NQ daily 2000-2026", "Yahoo_daily_futures", "YF_DAILY", "#2c3e50"),
                         ("Dukascopy NAS100+US500 RTH 2016-2026", "Dukascopy_1m", "RTH", "#c0392b")]:
    d = pd.DataFrame(rob)
    d = d[(d.dataset == ds) & (d.session_def == sdf) & (d.asset_group == "US_INDEX") & d.period.str.isdigit()]
    ax.plot(d.period.astype(int), d.uplift_vs_opposite, marker="o", label=lab, color=c_)
ax.axhline(0, c="k", lw=.8); ax.set_ylabel("uplift vs opposite condition")
ax.set_title("US equity indices: year-by-year uplift, Friday→Monday"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(CH / "04_year_by_year.png", bbox_inches="tight"); plt.close(fig)

# 5 time-to-touch
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
for ax, sdef in zip(axes, ["RTH", "BROKER"]):
    for grp, g in P[(P.trig_down) & (P.sessdef == sdef) & P.t_Blow.notna()].groupby("grp"):
        ax.hist(g.frac_Blow, bins=25, histtype="step", density=True, label=grp, lw=1.4)
    ax.set_title(f"{sdef}: when in Monday is Friday's low first touched?")
    ax.set_xlabel("fraction of Monday session elapsed")
axes[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(CH / "05_time_to_touch.png", bbox_inches="tight"); plt.close(fig)

# 6 first arrival
fig, ax = plt.subplots(figsize=(8, 3.6))
rows = []
for (sdef, grp), g in P.groupby(["sessdef", "grp"]):
    t = g[g.trig_down]
    both = t.t_Blow.notna() & t.t_Bhigh.notna()
    rows.append(dict(k=f"{grp}\n{sdef}",
                     low_first=(t.t_Blow.notna() & (t.t_Bhigh.isna() | (t.t_Blow < t.t_Bhigh))).mean(),
                     high_first=(t.t_Bhigh.notna() & (t.t_Blow.isna() | (t.t_Bhigh < t.t_Blow))).mean(),
                     neither=(t.t_Blow.isna() & t.t_Bhigh.isna()).mean()))
d = pd.DataFrame(rows)
x = np.arange(len(d))
ax.bar(x, d.low_first, .6, label="Friday LOW reached first", color="#c0392b")
ax.bar(x, d.high_first, .6, bottom=d.low_first, label="Friday HIGH reached first", color="#2980b9")
ax.bar(x, d.neither, .6, bottom=d.low_first + d.high_first, label="neither", color="#bdc3c7")
ax.set_xticks(x); ax.set_xticklabels(d.k, fontsize=7); ax.set_ylabel("share of triggered Mondays")
ax.set_title("First arrival on triggered Mondays — the hypothesis says LOW, the data says it is a coin flip at best")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(CH / "06_first_arrival.png", bbox_inches="tight"); plt.close(fig)

print("core", len(CORE), "controls", len(CTL), "robustness", len(rob))
print("charts:", [p.name for p in sorted(CH.glob('*.png'))])
