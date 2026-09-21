"""STAGE D part 2 — the non-directional family, plus the full economics table Issue #1 asks for.

Stage C (corrected) shows the residual is a TWO-SIDED REACH effect: in the tradeable state on
the 24-hour session, max down-excursion +0.149 ATR (p=0.003) AND max up-excursion +0.096 ATR
(p=0.001), with no change in direction, return, or opening-range break direction.  The issue
explicitly warns not to assume the manifestation is bearish, so the natural construction is a
symmetric breakout.

D4  OCO straddle at Monday's open:
      buy-stop  at open + k*ATR,  sell-stop at open - k*ATR, one-cancels-other
      whichever fills first is the trade; stop = the opposite level (risk 2k*ATR)
      target = m*ATR beyond the entry;  expiry = session close, marked to close
      no entry if neither level trades
Reported for every family: N, trades/year, win rate, mean/median R, expectancy, MFE/MAE,
1R/2R/3R attainment, year and dev/validation robustness, triggered vs control, net of costs.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260928)
NB = 1200
SPREAD = {"NAS100": 3.42, "US500": 0.51}
SLIP = {"NAS100": 1.0, "US500": 0.25}

G = pd.read_parquet(DERIVED / "c2_grid.parquet")
M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
G = G.merge(M[["instrument", "sessdef", "C_date", "open_below_Brange", "open_above_Brange",
               "mfe_down_atr", "mfe_up_atr"]],
            on=["instrument", "sessdef", "C_date"], how="left")
G["week"] = pd.DatetimeIndex(G.C_date).to_period("W-SUN").astype(str)
G["year"] = pd.DatetimeIndex(G.C_date).year
G["cost_px"] = G.instrument.map(SPREAD) + 2 * G.instrument.map(SLIP)
o = lambda k: f"o{k:+.2f}"


def straddle(d, k, m):
    """Returns (R net, filled, win, loss, dirn, MFE in R, MAE in R)."""
    a = d.atr_at_B.values; op = d.C_open_px.values
    tu = d[o(k)].values.astype(float)      # buy-stop level touched
    td = d[o(-k)].values.astype(float)     # sell-stop level touched
    up_first = np.isfinite(tu) & (~np.isfinite(td) | (tu < td))
    dn_first = np.isfinite(td) & (~np.isfinite(tu) | (td < tu))
    filled = up_first | dn_first
    et = np.where(up_first, tu, np.where(dn_first, td, np.nan))
    risk = 2 * k * a
    # long branch: target o+(k+m), stop o-k ; short branch: target o-(k+m), stop o+k
    t_tgt = np.where(up_first, d[o(k + m)].values, np.where(dn_first, d[o(-(k + m))].values, np.nan)).astype(float)
    t_stp = np.where(up_first, d[o(-k)].values, np.where(dn_first, d[o(k)].values, np.nan)).astype(float)
    hit_t = filled & np.isfinite(t_tgt) & (t_tgt > et)
    hit_s = filled & np.isfinite(t_stp) & (t_stp > et)
    win = hit_t & (~hit_s | (t_tgt < t_stp))
    loss = hit_s & (~hit_t | (t_stp < t_tgt))
    entry_px = np.where(up_first, op + k * a, op - k * a)
    mtm = np.where(up_first, d.C_close.values - entry_px, entry_px - d.C_close.values) / risk
    Rg = np.where(win, m / (2 * k), np.where(loss, -1.0, np.where(filled, mtm, np.nan)))
    R = Rg - d.cost_px.values / risk
    R = np.where(filled, R, np.nan)
    # excursions in R, from the entry
    mfe = np.where(up_first, (op + a * d.mfe_up_atr.values) - entry_px,
                   entry_px - (op - a * d.mfe_down_atr.values)) / risk
    mae = np.where(up_first, entry_px - (op - a * d.mfe_down_atr.values),
                   (op + a * d.mfe_up_atr.values) - entry_px) / risk
    return R, filled, win, loss, up_first, mfe, mae


def cluster(d, R, trig, nb=NB):
    ok = np.isfinite(R)
    if ok.sum() < 60:
        return None
    d2 = d[ok]; R2 = R[ok]; t2 = trig[ok]
    if t2.sum() < 25 or (~t2).sum() < 25:
        return None
    wk = d2.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
    bt, bd = [], []
    for _ in range(nb):
        ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
        rr, tt = R2[ii], t2[ii]
        if tt.sum() < 5 or (~tt).sum() < 5:
            continue
        bt.append(rr[tt].mean()); bd.append(rr[tt].mean() - rr[~tt].mean())
    bt = np.array(bt); bd = np.array(bd)
    return dict(meanR_trig=R2[t2].mean(), medR_trig=np.median(R2[t2]),
                meanR_opp=R2[~t2].mean(),
                trig_ci_lo=np.quantile(bt, .025), trig_ci_hi=np.quantile(bt, .975),
                p_trig_vs_zero=2 * min((bt <= 0).mean(), (bt >= 0).mean()),
                diff=R2[t2].mean() - R2[~t2].mean(),
                diff_ci_lo=np.quantile(bd, .025), diff_ci_hi=np.quantile(bd, .975),
                p_diff=2 * min((bd <= 0).mean(), (bd >= 0).mean()))


rows = []
for sdef in ["RTH", "BROKER"]:
    d = G[(G.sessdef == sdef) & (~G.open_below_Brange)].copy()
    trig = d.trig_down.values
    nyears = d.year.nunique()
    for k in [0.25, 0.5]:
        for m in [0.5, 1.0, 1.5]:
            R, f, w, l, up, mfe, mae = straddle(d, k, m)
            r = cluster(d, R, trig)
            if not r:
                continue
            ft = f & trig
            Rt = R[ft]
            rec = dict(sessdef=sdef, family="D4 OCO straddle at Monday open",
                       rule=f"trigger ±{k} ATR, stop = opposite level (risk {2*k} ATR), target {m} ATR ({m/(2*k):.2f}R)",
                       n_trig_weeks=int(trig.sum()), n_trades=int(ft.sum()),
                       fill_rate=f[trig].mean(), trades_per_year=ft.sum() / nyears / 2,  # 2 instruments
                       long_share=up[ft].mean(),
                       win_rate=w[ft].mean(), loss_rate=l[ft].mean(),
                       expectancy_R=np.nanmean(Rt),
                       MFE_R_median=np.nanmedian(mfe[ft]), MAE_R_median=np.nanmedian(mae[ft]),
                       hit_1R=np.nanmean(mfe[ft] >= 1), hit_2R=np.nanmean(mfe[ft] >= 2),
                       hit_3R=np.nanmean(mfe[ft] >= 3), **r)
            # dev / validation and year consistency
            dev = ft & (d.year.values <= 2020); val = ft & (d.year.values >= 2021)
            rec["meanR_DEV_2016_2020"] = np.nanmean(R[dev]); rec["n_DEV"] = int(dev.sum())
            rec["meanR_VAL_2021_2026"] = np.nanmean(R[val]); rec["n_VAL"] = int(val.sum())
            yr = pd.Series(R[ft]).groupby(d.year.values[ft]).mean()
            rec["positive_years"] = int((yr > 0).sum()); rec["n_years"] = int(yr.notna().sum())
            rows.append(rec)

D4 = pd.DataFrame(rows)
D4.to_csv(OUT / "stageD4_nondirectional.csv", index=False)
pd.set_option("display.width", 280)
print("=== D4 OCO straddle, net of costs, triggered weeks ===")
print(D4[["sessdef", "rule", "n_trades", "trades_per_year", "fill_rate", "long_share", "win_rate",
          "expectancy_R", "trig_ci_lo", "trig_ci_hi", "p_trig_vs_zero", "meanR_opp", "diff", "p_diff",
          "hit_1R", "hit_2R", "hit_3R", "meanR_DEV_2016_2020", "meanR_VAL_2021_2026", "positive_years", "n_years"]]
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# --- diagnostic: does the trigger predict Monday's absolute range?
Md = M.copy()
Md["week"] = pd.DatetimeIndex(Md.C_date).to_period("W-SUN").astype(str)
Md["range_atr"] = Md.mfe_down_atr + Md.mfe_up_atr
rows = []
for sdef in ["RTH", "BROKER"]:
    for scope, dd in [("all", Md[Md.sessdef == sdef]),
                      ("tradeable", Md[(Md.sessdef == sdef) & ~Md.open_below_Brange])]:
        y = dd.range_atr.values; t = dd.trig_down.values
        wk = dd.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
        bs = []
        for _ in range(1500):
            ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
            yy, tt = y[ii], t[ii]
            if tt.sum() < 5 or (~tt).sum() < 5:
                continue
            bs.append(yy[tt].mean() - yy[~tt].mean())
        bs = np.array(bs)
        rows.append(dict(sessdef=sdef, scope=scope, n_trig=int(t.sum()),
                         trig=y[t].mean(), opp=y[~t].mean(), diff=y[t].mean() - y[~t].mean(),
                         ci_lo=np.quantile(bs, .025), ci_hi=np.quantile(bs, .975),
                         p=2 * min((bs <= 0).mean(), (bs >= 0).mean())))
Rg = pd.DataFrame(rows)
Rg.to_csv(OUT / "c2_range_expansion.csv", index=False)
print("\n=== diagnostic: Monday total excursion (down+up) in ATR ===")
print(Rg.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
