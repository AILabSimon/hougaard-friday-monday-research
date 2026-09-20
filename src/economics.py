"""Economic tests of the hypothesis, and the Monday path evidence behind them.

Produces:
  results/monday_path.csv          first arrival, time-to-touch, MFE/MAE (ATR-normalised)
  results/strategy_expectancy.csv  every trade construction tested, triggered and not

Every construction is a SHORT, because that is what the hypothesis implies
(Monday seeks Friday's low).  Exits are resolved from 1-minute bars: for the
structural constructions by comparing the first-touch minute of Friday's low
(target) with that of Friday's high (invalidation); for the ATR constructions by
comparing first-touch minutes on a grid of levels anchored to Monday's open.
Unresolved trades are marked to Monday's close.  All figures are gross of costs;
Dukascopy 2024 median spread is ~2-3% of a 0.5-ATR stop (see METHODS.md).
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

P = pd.read_parquet(DERIVED / "monday_paths.parquet")
G = pd.read_parquet(DERIVED / "monday_grid.parquet")
for d in (P, G):
    d["grp"] = np.where(d.instrument.isin(["NAS100", "US500"]), "US_INDEX",
               np.where(d.asset_class == "FX", "FX",
               np.where(d.instrument == "BTCUSD", "CRYPTO", "COMMOD")))
P = P[P.atr_at_B > 0].copy()
G = G[G.atr_at_B > 0].copy()
col = lambda k: f"t{k:+.2f}"

# ------------------------------------------------------------------ Monday path
rows = []
for (sdef, grp), g in P.groupby(["sessdef", "grp"]):
    for trig in (True, False):
        t = g[g.trig_down == trig]
        if len(t) < 30:
            continue
        both = t.t_Blow.notna() & t.t_Bhigh.notna()
        lowfirst = t.t_Blow < t.t_Bhigh
        touched = t[t.t_Blow.notna()]
        rows.append(dict(
            sessdef=sdef, asset_group=grp, triggered=trig, n=len(t),
            reach_Fri_low=t.t_Blow.notna().mean(),
            reach_Fri_high=t.t_Bhigh.notna().mean(),
            reach_Thu_high=t.t_Ahigh.notna().mean(),
            reach_both=both.mean(),
            Fri_low_first=(t.t_Blow.notna() & (t.t_Bhigh.isna() | lowfirst)).mean(),
            Fri_high_first=(t.t_Bhigh.notna() & (t.t_Blow.isna() | ~lowfirst)).mean(),
            reach_neither=(t.t_Blow.isna() & t.t_Bhigh.isna()).mean(),
            Fri_low_first_given_both=lowfirst[both].mean(),
            touch_minute_p25=touched.t_Blow.quantile(.25),
            touch_minute_median=touched.t_Blow.median(),
            touch_minute_p75=touched.t_Blow.quantile(.75),
            touch_frac_session_median=touched.frac_Blow.median(),
            share_touched_in_first_30min=(touched.t_Blow <= 30).mean(),
            share_touched_in_first_60min=(touched.t_Blow <= 60).mean(),
            # excursions from Monday's open, ATR-normalised
            MFE_down_atr_median=(t.mfe_down / t.atr_at_B).median(),
            MFE_down_atr_mean=(t.mfe_down / t.atr_at_B).mean(),
            MAE_up_atr_median=(t.mfe_up / t.atr_at_B).median(),
            MAE_up_atr_mean=(t.mfe_up / t.atr_at_B).mean(),
            net_excursion_atr_mean=((t.mfe_down - t.mfe_up) / t.atr_at_B).mean(),
            MAE_before_touch_atr_median=(t.mae_before_touch / t.atr_at_B).median(),
            MAE_before_touch_atr_p90=(t.mae_before_touch / t.atr_at_B).quantile(.9),
        ))
PATH = pd.DataFrame(rows)
PATH.to_csv(OUT / "monday_path.csv", index=False)

# ------------------------------------------------------------------ strategies
rows = []


def add(sdef, grp, trig, name, entry, target, stop, n, win, loss, R, extra=""):
    R = np.asarray(R, float)
    rows.append(dict(sessdef=sdef, asset_group=grp, triggered=trig, construction=name,
                     entry=entry, target=target, stop=stop, notes=extra,
                     n=n, win_rate=win, loss_rate=loss,
                     unresolved_rate=1 - win - loss,
                     mean_R=np.nanmean(R), median_R=np.nanmedian(R),
                     sum_R=np.nansum(R), sd_R=np.nanstd(R),
                     R_per_trade_lo95=np.nanmean(R) - 1.96 * np.nanstd(R) / np.sqrt(max(np.isfinite(R).sum(), 1)),
                     R_per_trade_hi95=np.nanmean(R) + 1.96 * np.nanstd(R) / np.sqrt(max(np.isfinite(R).sum(), 1))))


# E1 — short at Friday's close, target Friday's low, invalidation Friday's high
for (sdef, grp), g in P.groupby(["sessdef", "grp"]):
    for trig in (True, False):
        d = g[(g.trig_down == trig) & (g.B_high > g.B_close)]
        if len(d) < 30:
            continue
        risk = d.B_high - d.B_close
        rr = (d.B_close - d.B_low) / risk
        tp = d.t_Blow.notna() & (d.t_Bhigh.isna() | (d.t_Blow < d.t_Bhigh))
        sl = d.t_Bhigh.notna() & (d.t_Blow.isna() | (d.t_Bhigh < d.t_Blow))
        R = np.where(tp, rr, np.where(sl, -1.0, (d.B_close - d.C_close) / risk))
        add(sdef, grp, trig, "E1 short Friday close", "Friday close", "Friday low",
            "Friday high", len(d), tp.mean(), sl.mean(), R,
            f"median R available = {rr.median():.2f}")

# E2 — short at Monday's open, target Friday's low, invalidation Friday's high
for (sdef, grp), g in P.groupby(["sessdef", "grp"]):
    for trig in (True, False):
        d = g[(g.trig_down == trig) & (g.C_open_px > g.B_low) & (g.B_high > g.C_open_px)]
        if len(d) < 30:
            continue
        risk = d.B_high - d.C_open_px
        rr = (d.C_open_px - d.B_low) / risk
        tp = d.t_Blow.notna() & (d.t_Bhigh.isna() | (d.t_Blow < d.t_Bhigh))
        sl = d.t_Bhigh.notna() & (d.t_Blow.isna() | (d.t_Bhigh < d.t_Blow))
        R = np.where(tp, rr, np.where(sl, -1.0, (d.C_open_px - d.C_close) / risk))
        add(sdef, grp, trig, "E2 short Monday open", "Monday open", "Friday low",
            "Friday high", len(d), tp.mean(), sl.mean(), R,
            f"median R available = {rr.median():.2f}; "
            f"{1 - len(d)/max(len(g[g.trig_down==trig]),1):.0%} of Mondays skipped (opened below Friday low)")

# E3 — short at Monday's open, fixed ATR stop and target
for (sdef, grp), g in G.groupby(["sessdef", "grp"]):
    for trig in (True, False):
        d = g[g.trig_down == trig]
        if len(d) < 30:
            continue
        for sk, tk in [(0.5, 0.5), (0.5, 1.0), (0.5, 1.5), (0.75, 1.5), (1.0, 1.0), (1.0, 2.0)]:
            ts = d[col(-tk)].values; tl = d[col(sk)].values
            win = ~np.isnan(ts) & (np.isnan(tl) | (ts < tl))
            loss = ~np.isnan(tl) & (np.isnan(ts) | (tl < ts))
            mtm = (d.C_open_px.values - d.C_close.values) / (sk * d.atr_at_B.values)
            R = np.where(win, tk / sk, np.where(loss, -1.0, mtm))
            add(sdef, grp, trig, f"E3 short Monday open {sk}/{tk} ATR", "Monday open",
                f"{tk} ATR below open ({tk/sk:.0f}R)", f"{sk} ATR above open",
                len(d), win.mean(), loss.mean(), R)

S = pd.DataFrame(rows)
S.to_csv(OUT / "strategy_expectancy.csv", index=False)

pd.set_option("display.width", 250)
print("--- Monday path, triggered, US indices ---")
print(PATH[(PATH.asset_group == "US_INDEX") & PATH.triggered][
    ["sessdef", "n", "reach_Fri_low", "reach_Fri_high", "Fri_low_first", "Fri_high_first",
     "share_touched_in_first_60min", "MFE_down_atr_median", "MAE_up_atr_median",
     "MAE_before_touch_atr_median"]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\n--- E1/E2, US indices ---")
print(S[(S.asset_group == "US_INDEX") & S.construction.str.startswith(("E1", "E2"))][
    ["sessdef", "construction", "triggered", "n", "win_rate", "loss_rate", "mean_R",
     "median_R", "R_per_trade_lo95", "R_per_trade_hi95", "notes"]]
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print(f"\n{len(S)} strategy rows, {len(PATH)} path rows")
