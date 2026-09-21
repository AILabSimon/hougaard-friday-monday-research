"""CYCLE 2 — the gap-consumed vs travelled-to decomposition on ES and NQ, 2000-2026.

Issue #1 makes ES/NQ the primary Stage C instruments.  Their 1-minute history in this
library is ONE MONTH (Yahoo serves ~30 days of 1m), so minute-level path work is impossible
on them.  The decisive Cycle-2 decomposition, however, needs only daily bars:

    opened below Friday's low   ->  the level was consumed before Monday traded
    opened at/above and touched ->  Monday travelled to it

so it can be replicated on 26 years of ES/NQ and on the five opening-location buckets the
issue specifies.  Week-clustered bootstrap throughout.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260927)
NB = 2000

Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")
T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")


def prep(d, src):
    d = d[(d.B_wd == 4) & (d.C_wd == 0) & (d.atr_at_B > 0) & (d.B_range > 0)].copy()
    d["week"] = pd.DatetimeIndex(d.C_date).to_period("W-SUN").astype(str)
    d["year"] = pd.DatetimeIndex(d.C_date).year
    d["source"] = src
    d["open_below_Blow"] = d.C_open < d.B_low
    d["open_above_Bhigh"] = d.C_open > d.B_high
    d["touch_low"] = d.C_low <= d.B_low
    d["low_by_gap"] = d.open_below_Blow
    d["travelled_to_low"] = d.touch_low & ~d.open_below_Blow
    d["open_loc"] = (d.C_open - d.B_low) / d.B_range
    # the five opening-location buckets named in the mandate
    near = 0.15
    d["open_bucket"] = np.select(
        [d.open_below_Blow, d.open_above_Bhigh, d.open_loc <= near, d.open_loc >= 1 - near],
        ["1 gaps below Fri low", "5 opens above Fri range",
         "3 opens near Fri low", "4 opens near Fri high"],
        default="2 opens inside Fri range")
    d["gap_atr"] = (d.C_open - d.B_close) / d.atr_at_B
    d["gap_frac_Brange"] = (d.C_open - d.B_close) / d.B_range
    d["mfe_down_atr"] = (d.C_open - d.C_low) / d.atr_at_B
    d["mfe_up_atr"] = (d.C_high - d.C_open) / d.atr_at_B
    d["ret_close_atr"] = (d.C_close - d.C_open) / d.atr_at_B
    return d


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


ES = prep(Y[Y.instrument.isin(["YF_ES", "YF_NQ"])], "Yahoo ES+NQ daily")
CF = prep(T[(T.sessdef == "RTH") & T.instrument.isin(["NAS100", "US500"])], "Dukascopy RTH")
CB = prep(T[(T.sessdef == "BROKER") & T.instrument.isin(["NAS100", "US500"])], "Dukascopy BROKER")

MEAS = ["touch_low", "low_by_gap", "travelled_to_low", "gap_atr", "gap_frac_Brange",
        "open_loc", "open_below_Blow", "open_above_Bhigh",
        "mfe_down_atr", "mfe_up_atr", "ret_close_atr"]
rows = []
for name, d in [("Yahoo ES+NQ daily 2000-2026", ES),
                ("Yahoo ES+NQ daily 2000-2015 (DEV)", ES[ES.year <= 2015]),
                ("Yahoo ES+NQ daily 2016-2026 (VAL)", ES[ES.year >= 2016]),
                ("Yahoo ES alone", ES[ES.instrument == "YF_ES"]),
                ("Yahoo NQ alone", ES[ES.instrument == "YF_NQ"]),
                ("Dukascopy NAS100+US500 RTH", CF),
                ("Dukascopy NAS100+US500 BROKER", CB)]:
    for c in MEAS:
        r = boot(d, c)
        if r:
            rows.append(dict(sample=name, measure=c, **r))
R = pd.DataFrame(rows)
R.to_csv(OUT / "c2_decomposition.csv", index=False)

# --- conditional on the level still being reachable, on ES/NQ daily
rows2 = []
for name, d in [("Yahoo ES+NQ daily 2000-2026", ES),
                ("Yahoo ES+NQ 2000-2015 (DEV)", ES[ES.year <= 2015]),
                ("Yahoo ES+NQ 2016-2026 (VAL)", ES[ES.year >= 2016]),
                ("Dukascopy NAS100+US500 RTH", CF)]:
    t = d[~d.open_below_Blow]
    for c in ["touch_low", "mfe_down_atr", "mfe_up_atr", "ret_close_atr"]:
        r = boot(t, c)
        if r:
            rows2.append(dict(sample=name, scope="opens AT/ABOVE Fri low", measure=c, **r))
R2 = pd.DataFrame(rows2)
R2.to_csv(OUT / "c2_decomposition_tradeable.csv", index=False)

# --- the five opening buckets
rows3 = []
for name, d in [("Yahoo ES+NQ daily", ES), ("Dukascopy RTH", CF)]:
    for b, g in d.groupby("open_bucket"):
        for c in ["touch_low", "mfe_down_atr", "ret_close_atr"]:
            r = boot(g, c)
            if r:
                rows3.append(dict(sample=name, bucket=b, measure=c, **r))
        rows3.append(dict(sample=name, bucket=b, measure="__frequency__",
                          n_trig=int(g.trig_down.sum()), n_opp=int((~g.trig_down).sum()),
                          trig=g.trig_down.sum() / d.trig_down.sum(),
                          opp=(~g.trig_down).sum() / (~d.trig_down).sum(),
                          diff=g.trig_down.sum() / d.trig_down.sum() - (~g.trig_down).sum() / (~d.trig_down).sum(),
                          ci_lo=np.nan, ci_hi=np.nan, p=np.nan))
R3 = pd.DataFrame(rows3)
R3.to_csv(OUT / "c2_open_buckets.csv", index=False)

pd.set_option("display.width", 250)
print("=== DECOMPOSITION: is the effect the gap, or Monday's travel? ===")
key = ["touch_low", "low_by_gap", "travelled_to_low", "gap_atr"]
print(R[R.measure.isin(key)].pivot_table(index="sample", columns="measure",
      values=["trig", "opp", "diff", "p"]).round(4).to_string())
print("\n=== conditional on the level still reachable at the open ===")
print(R2.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print("\n=== five opening-location buckets: share of Mondays ===")
f = R3[R3.measure == "__frequency__"]
print(f[["sample", "bucket", "n_trig", "trig", "opp", "diff"]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
