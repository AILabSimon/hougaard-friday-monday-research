"""STAGE D — entry families, restricted to what Stage C actually justifies.

Stage C found NO change in Monday's direction, timing, sequencing or opening-range behaviour.
What it did find, in the tradeable state (Monday opens at/above Friday's low):
   touch rate       +8.7pp  (p = 0.017)
   max down-reach   +0.12 ATR (p < 0.001)
and, in the full sample only, deeper penetration once Friday's low is breached.

So three families are tested and no others:
   D1  short at Monday's open                       (reach effect, no timing edge to exploit)
   D2  short on a limit above the open              (reach effect + unchanged up-excursion)
   D3  short on the break of Friday's low           (penetration effect)
Each is run triggered vs opposite, with week-clustered bootstrap intervals on the
DIFFERENCE, and after costs.

Costs: Dukascopy 2024 median spread 3.42 pts NAS100, 0.51 pts US500; plus 1 tick slippage
per side.  Charged as 2 x (half-spread + slip) on entry+exit, converted to R.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260925)
NB = 1200
SPREAD = {"NAS100": 3.42, "US500": 0.51}
SLIP = {"NAS100": 1.0, "US500": 0.25}

G = pd.read_parquet(DERIVED / "c2_grid.parquet")
M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
G = G.merge(M[["instrument", "sessdef", "C_date", "open_below_Brange", "open_above_Brange",
               "t_Blow", "mon_n"]], on=["instrument", "sessdef", "C_date"], how="left")
G["week"] = pd.DatetimeIndex(G.C_date).to_period("W-SUN").astype(str)
G["cost_px"] = G.instrument.map(SPREAD) + 2 * G.instrument.map(SLIP)
o = lambda k: f"o{k:+.2f}"
lw = lambda k: f"l{k:+.2f}"


def resolve(d, entry_px, entry_t, targ_px, stop_px, close_px):
    """R and outcome given entry/target/stop prices and first-touch minute arrays."""
    risk = stop_px - entry_px
    ok = (risk > 0) & np.isfinite(entry_t)
    R = np.full(len(d), np.nan)
    win = np.zeros(len(d), bool); loss = np.zeros(len(d), bool)
    return ok, risk, R, win, loss


def run(d, tag, entry_t, entry_px, tk, sk, anchor_col_t, anchor_col_s, cost_r_den):
    """Generic: entry at entry_px/entry_t; target/stop are grid levels with first-touch times."""
    tt = d[anchor_col_t].values.astype(float)     # target first-touch minute
    ts = d[anchor_col_s].values.astype(float)     # stop first-touch minute
    et = entry_t.astype(float)
    filled = np.isfinite(et)
    # target/stop only count if reached AFTER the fill
    hit_t = filled & np.isfinite(tt) & (tt > et)
    hit_s = filled & np.isfinite(ts) & (ts > et)
    win = hit_t & (~hit_s | (tt < ts))
    loss = hit_s & (~hit_t | (ts < tt))
    R_gross = np.where(win, tk / sk, np.where(loss, -1.0,
                       np.where(filled, (entry_px - d.C_close.values) / (sk * d.atr_at_B.values), np.nan)))
    cost_R = d.cost_px.values / cost_r_den
    R = R_gross - cost_R
    R[~filled] = np.nan
    return win, loss, filled, R_gross, R


def cluster_diff(d, R, trig, nb=NB):
    ok = np.isfinite(R)
    d2 = d[ok]; R2 = R[ok]; t2 = trig[ok]
    if t2.sum() < 25 or (~t2).sum() < 25:
        return None
    wk = d2.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
    bs_t, bs_d = [], []
    for _ in range(nb):
        ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
        rr, tt_ = R2[ii], t2[ii]
        if tt_.sum() < 5 or (~tt_).sum() < 5:
            continue
        bs_t.append(rr[tt_].mean()); bs_d.append(rr[tt_].mean() - rr[~tt_].mean())
    bs_t = np.array(bs_t); bs_d = np.array(bs_d)
    return dict(n_trig=int(t2.sum()), n_opp=int((~t2).sum()),
                meanR_trig=R2[t2].mean(), meanR_opp=R2[~t2].mean(),
                medR_trig=np.median(R2[t2]),
                trig_ci_lo=np.quantile(bs_t, .025), trig_ci_hi=np.quantile(bs_t, .975),
                p_trig_vs_zero=2 * min((bs_t <= 0).mean(), (bs_t >= 0).mean()),
                diff=R2[t2].mean() - R2[~t2].mean(),
                diff_ci_lo=np.quantile(bs_d, .025), diff_ci_hi=np.quantile(bs_d, .975),
                p_diff=2 * min((bs_d <= 0).mean(), (bs_d >= 0).mean()))


rows = []
for sdef in ["RTH", "BROKER"]:
    base = G[(G.sessdef == sdef)].copy()
    trade = base[~base.open_below_Brange].copy()        # tradeable state only
    a = trade.atr_at_B.values; op = trade.C_open_px.values
    trig = trade.trig_down.values

    # ---------- D1: short at the open
    for sk in [0.5, 0.75, 1.0]:
        for tk in [0.5, 1.0, 1.5, 2.0]:
            et = np.zeros(len(trade))
            w, l, f, Rg, R = run(trade, "D1", et, op, tk, sk, o(-tk), o(sk), sk * a)
            r = cluster_diff(trade, R, trig)
            if r:
                rows.append(dict(sessdef=sdef, family="D1 short at Monday open",
                                 rule=f"stop {sk} ATR / target {tk} ATR ({tk/sk:.1f}R)",
                                 fill_rate=f.mean(), win=w[trig].mean(), loss=l[trig].mean(),
                                 meanR_gross_trig=np.nanmean(Rg[trig]), **r))
    # ---------- D2: short on a limit above the open
    for ek in [0.25, 0.5]:
        for sk in [0.5, 0.75]:
            for tk in [1.0, 1.5, 2.0]:
                et = trade[o(ek)].values.astype(float)
                epx = op + ek * a
                w, l, f, Rg, R = run(trade, "D2", et, epx, tk, sk, o(ek - tk), o(ek + sk), sk * a)
                r = cluster_diff(trade, R, trig)
                if r:
                    rows.append(dict(sessdef=sdef, family="D2 short limit above open",
                                     rule=f"entry +{ek} ATR / stop {sk} / target {tk} ({tk/sk:.1f}R)",
                                     fill_rate=f.mean(), win=w[trig].mean(), loss=l[trig].mean(),
                                     meanR_gross_trig=np.nanmean(Rg[trig]), **r))
    # ---------- D3: short the break of Friday's low
    # DEFECT GUARD: on Mondays that open BELOW Friday's low the level is already gone, so an
    # "entry at Friday's low" is a phantom fill worth a median 1.23R of unattainable profit.
    # D3a keeps them (shown only to expose the defect); D3b is the honest version.
    for tag, b in [("D3a INVALID (incl. gap-through)", base.copy()),
                   ("D3b short break of Friday low", base[~base.open_below_Brange].copy())]:
        ab = b.atr_at_B.values; trig_b = b.trig_down.values
        for sk in [0.25, 0.5, 0.75]:
            for tk in [0.5, 1.0, 1.5]:
                et = b[lw(0.0)].values.astype(float)       # entry on the touch of Friday's low
                epx = b.B_low.values
                w, l, f, Rg, R = run(b, "D3", et, epx, tk, sk, lw(-tk), lw(sk), sk * ab)
                r = cluster_diff(b, R, trig_b)
                if r:
                    rows.append(dict(sessdef=sdef, family=tag,
                                     rule=f"stop {sk} ATR / target {tk} ATR ({tk/sk:.1f}R)",
                                     fill_rate=f.mean(), win=w[trig_b & f].mean() if (trig_b & f).any() else np.nan,
                                     loss=l[trig_b & f].mean() if (trig_b & f).any() else np.nan,
                                     meanR_gross_trig=np.nanmean(Rg[trig_b]), **r))

R = pd.DataFrame(rows)
R.to_csv(OUT / "stageD_entries.csv", index=False)
pd.set_option("display.width", 260)
for sdef in ["RTH", "BROKER"]:
    print(f"\n############ {sdef} — net of costs ############")
    s = R[R.sessdef == sdef]
    print(s[["family", "rule", "n_trig", "fill_rate", "win", "meanR_trig", "trig_ci_lo", "trig_ci_hi",
             "p_trig_vs_zero", "meanR_opp", "diff", "p_diff"]]
          .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\nAny construction with a triggered mean R significantly > 0 after costs?")
print(R[(R.trig_ci_lo > 0)][["sessdef", "family", "rule", "meanR_trig", "trig_ci_lo"]].to_string(index=False))
