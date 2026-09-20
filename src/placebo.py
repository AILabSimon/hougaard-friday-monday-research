"""Placebo controls.

P1  Random trigger with the same marginal frequency -> must give zero uplift (sanity).
P2  Path shuffle: keep Friday's geometry, but give Monday a randomly drawn *other*
    Monday's normalised behaviour (gap, up-excursion, down-excursion in ATR units),
    drawn within the same instrument and year.  This preserves every marginal
    distribution and destroys only the actual temporal pairing.  If the measured
    uplift survives the shuffle it is pure level geometry, not a conditional effect.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260920)
NSIM = 1000


def prep(d):
    d = d.dropna(subset=["atr_at_B"]).copy()
    d = d[(d.atr_at_B > 0) & (d.B_range > 0)]
    d["gap_n"] = (d.C_open - d.B_close) / d.atr_at_B
    d["dn_n"] = (d.C_open - d.C_low) / d.atr_at_B
    d["up_n"] = (d.C_high - d.C_open) / d.atr_at_B
    d["need"] = (d.B_close - d.B_low) / d.atr_at_B      # how far below Friday's close the target is
    return d


def shuffled_uplift(d, nsim=NSIM):
    out = np.empty(nsim)
    keys = (d.instrument.astype(str) + "_" + d.year.astype(str)).values
    gap, dn = d.gap_n.values, d.dn_n.values
    need, trig = d.need.values, d.trig_down.values
    idx_by_key = {k: np.flatnonzero(keys == k) for k in np.unique(keys)}
    for s in range(nsim):
        perm = np.arange(len(d))
        for k, ii in idx_by_key.items():
            perm[ii] = RNG.permutation(ii)
        touch = (gap[perm] - dn[perm]) <= -need
        out[s] = touch[trig].mean() - touch[~trig].mean()
    return out


if __name__ == "__main__":
    T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
    Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")
    rows = []
    sets = {
        "Duka US_INDEX RTH Fri->Mon": prep(T[(T.sessdef == "RTH") & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(["NAS100", "US500"])]),
        "Duka US_INDEX BROKER Fri->Mon": prep(T[(T.sessdef == "BROKER") & (T.B_wd == 4) & (T.C_wd == 0) & T.instrument.isin(["NAS100", "US500"])]),
        "Duka FX BROKER Fri->Mon": prep(T[(T.sessdef == "BROKER") & (T.B_wd == 4) & (T.C_wd == 0) & (T.asset_class == "FX")]),
        "Duka US_INDEX BROKER Mon-Thu": prep(T[(T.sessdef == "BROKER") & (T.B_wd < 4) & T.instrument.isin(["NAS100", "US500"])]),
        "YF ES+NQ Fri->Mon": prep(Y[(Y.B_wd == 4) & (Y.C_wd == 0) & Y.instrument.isin(["YF_ES", "YF_NQ"])]),
    }
    for name, d in sets.items():
        obs = d.touch_low[d.trig_down].mean() - d.touch_low[~d.trig_down].mean()
        # sanity: reconstruct touch from normalised quantities
        recon = ((d.gap_n - d.dn_n) <= -d.need)
        recon_ok = (recon == d.touch_low).mean()
        sim = shuffled_uplift(d)
        # P1 random trigger
        p1 = []
        tr = d.trig_down.values; tl = d.touch_low.values
        for _ in range(200):
            rt = RNG.permutation(tr)
            p1.append(tl[rt].mean() - tl[~rt].mean())
        rows.append(dict(dataset=name, n=len(d), recon_accuracy=recon_ok,
                         observed_uplift=obs,
                         shuffle_mean=sim.mean(), shuffle_sd=sim.std(),
                         shuffle_p=(np.abs(sim) >= abs(obs)).mean(),
                         shuffle_q95=np.quantile(sim, .95),
                         randtrig_mean=np.mean(p1), randtrig_sd=np.std(p1)))
    R = pd.DataFrame(rows)
    R.to_csv(OUT / "placebo.csv", index=False)
    print(R.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
