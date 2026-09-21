"""Two remaining Issue #1 requirements:
  (1) Fri->Mon versus every adjacent weekday pair under the SAME week-clustered treatment
  (2) the full economics table for D1/D2/D3b: trades/year, 1R/2R/3R attainment, MFE/MAE,
      year consistency and development vs validation
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260930)
NB = 1500


def logit(X, y, ridge=1e-3, iters=80):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); W = np.clip(p * (1 - p), 1e-8, None)
        try:
            s = np.linalg.solve(X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1]),
                                X.T @ (y - p) - ridge * b)
        except np.linalg.LinAlgError:
            return None
        b += s
        if np.max(np.abs(s)) < 1e-9:
            break
    return b


def design(d, ctrl=True):
    cols = [np.ones(len(d)), d.trig_down.astype(float).values]
    if ctrl:
        cols += [((d.B_close - d.B_low) / d.atr_at_B).values, (d.B_range / d.atr_at_B).values]
    for i in sorted(d.instrument.unique())[1:]:
        cols.append((d.instrument == i).astype(float).values)
    return np.column_stack(cols)


# ---------------------------------------------- (1) weekday pairs, clustered
T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
Y = pd.read_parquet(DERIVED / "triples" / "triples_yf.parquet")
WD = ["Mon", "Tue", "Wed", "Thu", "Fri"]
rows = []
for src, D, insts, sdefs in [("Dukascopy NAS100+US500", T, ["NAS100", "US500"], ["RTH", "BROKER"]),
                             ("Yahoo ES+NQ daily", Y, ["YF_ES", "YF_NQ"], ["YF_DAILY"])]:
    for sdef in sdefs:
        base = D[(D.instrument.isin(insts)) & (D.atr_at_B > 0) & (D.B_range > 0)]
        if sdef != "YF_DAILY":
            base = base[base.sessdef == sdef]
        for wd in range(5):
            d = base[base.B_wd == wd].copy()
            if len(d) < 200:
                continue
            d["week"] = pd.DatetimeIndex(d.C_date).to_period("W-SUN").astype(str)
            b = logit(design(d), d.touch_low.values.astype(float))
            b0 = logit(design(d, False), d.touch_low.values.astype(float))
            if b is None:
                continue
            wk = d.week.values; uw = np.unique(wk); ibw = {w: np.flatnonzero(wk == w) for w in uw}
            bs = []
            for _ in range(NB):
                ii = np.concatenate([ibw[w] for w in RNG.choice(uw, size=len(uw), replace=True)])
                s = d.iloc[ii]
                if s.trig_down.nunique() < 2:
                    continue
                bb = logit(design(s), s.touch_low.values.astype(float))
                if bb is not None:
                    bs.append(bb[1])
            bs = np.array(bs)
            t, o = d[d.trig_down], d[~d.trig_down]
            rows.append(dict(source=src, session_def=sdef, B_weekday=WD[wd],
                             next_session=WD[int(d.C_wd.mode().iloc[0])] if sdef != "YF_DAILY" else WD[int(d.C_wd.mode().iloc[0])],
                             n=len(d), n_weeks=d.week.nunique(),
                             raw_rate=t.touch_low.mean(), opp_rate=o.touch_low.mean(),
                             raw_uplift=t.touch_low.mean() - o.touch_low.mean(),
                             beta_raw=b0[1], beta_ctrl=b[1], OR_ctrl=np.exp(b[1]),
                             ci_lo=np.quantile(bs, .025), ci_hi=np.quantile(bs, .975),
                             p_cluster=2 * min((bs <= 0).mean(), (bs >= 0).mean())))
W = pd.DataFrame(rows)
W.to_csv(OUT / "c2_weekday_pairs.csv", index=False)
pd.set_option("display.width", 260)
print("=== Fri->Mon vs every adjacent weekday pair, same week-clustered treatment ===")
print(W[["source", "session_def", "B_weekday", "n", "raw_uplift", "beta_ctrl", "OR_ctrl",
         "ci_lo", "ci_hi", "p_cluster"]].to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# ---------------------------------------------- (2) full economics for D1/D2/D3b
SPREAD = {"NAS100": 3.42, "US500": 0.51}; SLIP = {"NAS100": 1.0, "US500": 0.25}
G = pd.read_parquet(DERIVED / "c2_grid.parquet")
M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
G = G.merge(M[["instrument", "sessdef", "C_date", "open_below_Brange", "mfe_down_atr", "mfe_up_atr"]],
            on=["instrument", "sessdef", "C_date"], how="left")
G["year"] = pd.DatetimeIndex(G.C_date).year
G["cost_px"] = G.instrument.map(SPREAD) + 2 * G.instrument.map(SLIP)
o = lambda k: f"o{k:+.2f}"; lw = lambda k: f"l{k:+.2f}"

def econ(d, name, rule, et, epx, t_tgt, t_stp, risk, mfe_px, mae_px):
    filled = np.isfinite(et)
    hit_t = filled & np.isfinite(t_tgt) & (t_tgt > et)
    hit_s = filled & np.isfinite(t_stp) & (t_stp > et)
    win = hit_t & (~hit_s | (t_tgt < t_stp)); loss = hit_s & (~hit_t | (t_stp < t_tgt))
    tgt_R = np.abs(epx - np.where(np.isfinite(t_tgt), epx, epx)) # placeholder
    mtm = (epx - d.C_close.values) / risk
    Rg = np.where(win, np.nan, np.where(loss, -1.0, np.where(filled, mtm, np.nan)))
    return filled, win, loss, Rg

rows = []
for sdef in ["RTH", "BROKER"]:
    d = G[(G.sessdef == sdef) & ~G.open_below_Brange].copy()
    a = d.atr_at_B.values; op = d.C_open_px.values; trig = d.trig_down.values
    nyr = d.year.nunique()
    for sk, tk in [(0.5, 1.0), (0.75, 1.5), (1.0, 2.0)]:
        et = np.zeros(len(d)); risk = sk * a
        t_tgt = d[o(-tk)].values.astype(float); t_stp = d[o(sk)].values.astype(float)
        win = np.isfinite(t_tgt) & (~np.isfinite(t_stp) | (t_tgt < t_stp))
        loss = np.isfinite(t_stp) & (~np.isfinite(t_tgt) | (t_stp < t_tgt))
        R = np.where(win, tk / sk, np.where(loss, -1.0, (op - d.C_close.values) / risk)) - d.cost_px.values / risk
        mfe = (op - (op - a * d.mfe_down_atr.values)) / risk   # favourable = down for a short
        mae = ((op + a * d.mfe_up_atr.values) - op) / risk
        sel = trig
        yr = pd.Series(R[sel]).groupby(d.year.values[sel]).mean()
        rows.append(dict(sessdef=sdef, family="D1 short at Monday open",
                         rule=f"stop {sk} ATR / target {tk} ATR ({tk/sk:.0f}R)",
                         n_trades=int(sel.sum()), trades_per_year=sel.sum() / nyr / 2,
                         win_rate=win[sel].mean(), loss_rate=loss[sel].mean(),
                         mean_R=np.nanmean(R[sel]), median_R=np.nanmedian(R[sel]),
                         expectancy_R=np.nanmean(R[sel]),
                         MFE_R_median=np.nanmedian(mfe[sel]), MAE_R_median=np.nanmedian(mae[sel]),
                         hit_1R=np.nanmean(mfe[sel] >= 1), hit_2R=np.nanmean(mfe[sel] >= 2),
                         hit_3R=np.nanmean(mfe[sel] >= 3),
                         meanR_DEV_2016_2020=np.nanmean(R[sel & (d.year.values <= 2020)]),
                         meanR_VAL_2021_2026=np.nanmean(R[sel & (d.year.values >= 2021)]),
                         positive_years=int((yr > 0).sum()), n_years=int(yr.notna().sum()),
                         meanR_control=np.nanmean(R[~trig])))
    # D3b: break of Friday's low, genuine crosses only
    et = d[lw(0.0)].values.astype(float); epx = d.B_low.values
    for sk, tk in [(0.5, 1.0), (0.75, 1.5)]:
        risk = sk * a
        t_tgt = d[lw(-tk)].values.astype(float); t_stp = d[lw(sk)].values.astype(float)
        filled = np.isfinite(et)
        win = filled & np.isfinite(t_tgt) & (t_tgt > et) & (~(np.isfinite(t_stp) & (t_stp > et)) | (t_tgt < t_stp))
        loss = filled & np.isfinite(t_stp) & (t_stp > et) & (~(np.isfinite(t_tgt) & (t_tgt > et)) | (t_stp < t_tgt))
        R = np.where(win, tk / sk, np.where(loss, -1.0, np.where(filled, (epx - d.C_close.values) / risk, np.nan))) - d.cost_px.values / risk
        R = np.where(filled, R, np.nan)
        sel = trig & filled
        mfe = (epx - (op - a * d.mfe_down_atr.values)) / risk
        mae = ((op + a * d.mfe_up_atr.values) - epx) / risk
        yr = pd.Series(R[sel]).groupby(d.year.values[sel]).mean()
        rows.append(dict(sessdef=sdef, family="D3b short break of Friday low",
                         rule=f"stop {sk} ATR / target {tk} ATR ({tk/sk:.0f}R)",
                         n_trades=int(sel.sum()), trades_per_year=sel.sum() / nyr / 2,
                         win_rate=win[sel].mean(), loss_rate=loss[sel].mean(),
                         mean_R=np.nanmean(R[sel]), median_R=np.nanmedian(R[sel]),
                         expectancy_R=np.nanmean(R[sel]),
                         MFE_R_median=np.nanmedian(mfe[sel]), MAE_R_median=np.nanmedian(mae[sel]),
                         hit_1R=np.nanmean(mfe[sel] >= 1), hit_2R=np.nanmean(mfe[sel] >= 2),
                         hit_3R=np.nanmean(mfe[sel] >= 3),
                         meanR_DEV_2016_2020=np.nanmean(R[sel & (d.year.values <= 2020)]),
                         meanR_VAL_2021_2026=np.nanmean(R[sel & (d.year.values >= 2021)]),
                         positive_years=int((yr > 0).sum()), n_years=int(yr.notna().sum()),
                         meanR_control=np.nanmean(R[~trig & filled])))
E = pd.DataFrame(rows)
E.to_csv(OUT / "c2_economics_full.csv", index=False)
print("\n=== full economics (Issue #1 reporting set), triggered weeks, net of costs ===")
print(E.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
