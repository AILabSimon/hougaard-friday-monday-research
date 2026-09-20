"""STAGE C part 2 — condition on Monday's OPENING STATE.

A Friday low already consumed by the weekend gap is not tradeable on Monday.  The only
tradeable states are those where Monday opens at or above Friday's low.  Within those states,
does the Thu/Fri trigger still change anything?
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260924)
NB = 1500
M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
M["week"] = pd.DatetimeIndex(M.C_date).to_period("W-SUN").astype(str)
M["seq_low_first"] = M.seq.isin(["low_only", "low_then_high"])
M["net30_atr"] = M.dn30_atr - M.up30_atr
M["net60_atr"] = M.dn60_atr - M.up60_atr
M["first_move_dn"] = M.first_move_dir == "dn"
M["or15_dn"] = M.or15_break == "dn"
M["or30_dn"] = M.or30_break == "dn"
M["open_class"] = np.select(
    [M.open_below_Brange, M.open_above_Brange,
     M.open_loc_in_Brange <= 0.34, M.open_loc_in_Brange >= 0.67],
    ["below Fri range", "above Fri range", "lower third", "upper third"], default="middle")


def diff_boot(d, col, nb=NB):
    d = d.dropna(subset=[col])
    if d.trig_down.nunique() < 2 or len(d) < 50:
        return None
    y = d[col].astype(float).values; t = d.trig_down.values
    if t.sum() < 25 or (~t).sum() < 25:
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


MEAS = ["touch_Blow", "seq_low_first", "Blow_by30", "Blow_by60", "net30_atr", "net60_atr",
        "ret_close_atr", "mfe_down_atr", "mfe_up_atr", "first_move_dn", "or15_dn", "or30_dn",
        "dir60_up", "pen_after_Blow_atr", "bounce_after_Blow_atr", "mae_before_Blow_atr"]

rows = []
for sdef in ["RTH", "BROKER"]:
    base = M[M.sessdef == sdef]
    for scope, d in [("ALL Mondays", base),
                     ("opens AT/ABOVE Fri low (tradeable)", base[~base.open_below_Brange]),
                     ("opens INSIDE Fri range", base[(~base.open_below_Brange) & (~base.open_above_Brange)]),
                     ("opens ABOVE Fri range", base[base.open_above_Brange]),
                     ("opens BELOW Fri range (gap already through)", base[base.open_below_Brange])]:
        for c in MEAS:
            r = diff_boot(d, c)
            if r:
                rows.append(dict(sessdef=sdef, scope=scope, measure=c, **r))
R = pd.DataFrame(rows)
R.to_csv(OUT / "stageC_conditional.csv", index=False)
pd.set_option("display.width", 250)
for sdef in ["RTH", "BROKER"]:
    print(f"\n################ {sdef} ################")
    for scope in R[R.sessdef == sdef].scope.unique():
        s = R[(R.sessdef == sdef) & (R.scope == scope)]
        sig = s[s.p < 0.05]
        print(f"\n--- {scope}  (n_trig={s.n_trig.iloc[0]}, n_opp={s.n_opp.iloc[0]}) : "
              f"{len(sig)}/{len(s)} measures differ at p<0.05 ---")
        print(s[["measure", "trig", "opp", "diff", "ci_lo", "ci_hi", "p"]]
              .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
