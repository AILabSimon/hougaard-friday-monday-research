"""STAGE C — Monday opening path: does the Thu/Fri trigger change HOW Monday develops?

Every measure is compared triggered vs opposite condition, with week-clustered bootstrap
intervals on the difference.  Nothing is assumed to be bearish.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

RNG = np.random.default_rng(20260923)
NB = 1500
M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
M["week"] = pd.DatetimeIndex(M.C_date).to_period("W-SUN").astype(str)
M["seq_low_first"] = M.seq.isin(["low_only", "low_then_high"])
M["net60_atr"] = M.dn60_atr - M.up60_atr
M["net30_atr"] = M.dn30_atr - M.up30_atr
M["net15_atr"] = M.dn15_atr - M.up15_atr
M["net5_atr"] = M.dn5_atr - M.up5_atr
# opening location classes
M["open_class"] = np.select(
    [M.open_below_Brange, M.open_above_Brange,
     M.open_loc_in_Brange <= 0.25, M.open_loc_in_Brange >= 0.75],
    ["below Fri range", "above Fri range", "lower quarter", "upper quarter"],
    default="middle")
# was Friday's low already consumed by the gap?
M["low_by_gap"] = M.open_below_Brange
M["travelled_to_low"] = M.touch_Blow & ~M.open_below_Brange


def diff_boot(d, col, nb=NB):
    """triggered mean - opposite mean, week-cluster bootstrap."""
    d = d.dropna(subset=[col])
    if d.trig_down.nunique() < 2 or len(d) < 60:
        return None
    y = d[col].astype(float).values; t = d.trig_down.values
    wk = d.week.values; uw = np.unique(wk)
    ibw = {w: np.flatnonzero(wk == w) for w in uw}
    obs = y[t].mean() - y[~t].mean()
    bs = []
    for _ in range(nb):
        pick = RNG.choice(uw, size=len(uw), replace=True)
        ii = np.concatenate([ibw[w] for w in pick])
        yy, tt = y[ii], t[ii]
        if tt.sum() < 5 or (~tt).sum() < 5:
            continue
        bs.append(yy[tt].mean() - yy[~tt].mean())
    bs = np.array(bs)
    return dict(n_trig=int(t.sum()), n_opp=int((~t).sum()),
                trig_mean=y[t].mean(), opp_mean=y[~t].mean(), diff=obs,
                ci_lo=np.quantile(bs, .025), ci_hi=np.quantile(bs, .975),
                p_cluster=2 * min((bs <= 0).mean(), (bs >= 0).mean()))


MEASURES = [
    # opening location
    ("gap_atr", "weekend gap / ATR"),
    ("open_to_Blow_atr", "Mon open above Fri low / ATR"),
    ("open_loc_in_Brange", "Mon open location inside Fri range"),
    ("open_below_Brange", "Mon opens BELOW Fri range"),
    ("open_above_Brange", "Mon opens ABOVE Fri range"),
    # opening path
    ("up5_atr", "up-excursion first 5m"), ("dn5_atr", "down-excursion first 5m"),
    ("up15_atr", "up 15m"), ("dn15_atr", "down 15m"),
    ("up30_atr", "up 30m"), ("dn30_atr", "down 30m"),
    ("up60_atr", "up 60m"), ("dn60_atr", "down 60m"),
    ("net5_atr", "net (dn-up) 5m"), ("net15_atr", "net 15m"),
    ("net30_atr", "net 30m"), ("net60_atr", "net 60m"),
    ("ret5_atr", "return first 5m"), ("ret15_atr", "return 15m"),
    ("ret30_atr", "return 30m"), ("ret60_atr", "return 60m"),
    ("dir15_up", "Mon up after 15m"), ("dir30_up", "Mon up after 30m"),
    ("dir60_up", "Mon up after 60m"),
    ("first_move_dn", "first 0.25-ATR move is DOWN"),
    # whole session
    ("mfe_down_atr", "session max down-excursion"),
    ("mfe_up_atr", "session max up-excursion"),
    ("ret_close_atr", "Monday close - open"),
    ("mon_high_before_low", "Monday high before Monday low"),
    # level interaction
    ("touch_Blow", "touches Fri low"), ("touch_Bhigh", "touches Fri high"),
    ("seq_low_first", "reaches Fri low BEFORE Fri high"),
    ("low_by_gap", "Fri low consumed by the gap"),
    ("travelled_to_low", "TRAVELLED to Fri low during Monday"),
    ("Blow_by15", "Fri low touched within 15m"),
    ("Blow_by30", "Fri low touched within 30m"),
    ("Blow_by60", "Fri low touched within 60m"),
    ("Bhigh_by60", "Fri high touched within 60m"),
    ("pen_after_Blow_atr", "penetration beyond Fri low after touch"),
    ("bounce_after_Blow_atr", "bounce from Fri low after touch"),
    ("mae_before_Blow_atr", "adverse excursion before Fri-low touch"),
]
M["first_move_dn"] = M.first_move_dir == "dn"

rows = []
for sdef in ["RTH", "BROKER"]:
    d = M[M.sessdef == sdef]
    for c, lab in MEASURES:
        r = diff_boot(d, c)
        if r:
            rows.append(dict(sessdef=sdef, measure=c, label=lab, **r))
R = pd.DataFrame(rows)
R["bh_rank"] = R.groupby("sessdef").p_cluster.rank(method="first")
R["bh_crit"] = 0.05 * R.bh_rank / R.groupby("sessdef").p_cluster.transform("size")
R["survives_BH05"] = R.p_cluster <= R.bh_crit
R.to_csv(OUT / "stageC_path.csv", index=False)
pd.set_option("display.width", 260)
print("=== Monday path measures that differ, triggered vs opposite (BH 5%, week-clustered) ===")
s = R[R.survives_BH05].sort_values(["sessdef", "p_cluster"])
print(s[["sessdef", "measure", "label", "n_trig", "trig_mean", "opp_mean", "diff", "ci_lo", "ci_hi", "p_cluster"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\n{len(s)} of {len(R)} measures differ.")

print("\n=== opening-range break direction, triggered vs opposite ===")
for sdef in ["RTH", "BROKER"]:
    d = M[M.sessdef == sdef]
    for k in [15, 30]:
        ct = pd.crosstab(d.trig_down, d[f"or{k}_break"], normalize="index")
        print(f"-- {sdef} OR{k} --"); print(ct.to_string(float_format=lambda x: f"{x:.3f}"))

print("\n=== path sequence distribution ===")
for sdef in ["RTH", "BROKER"]:
    d = M[M.sessdef == sdef]
    ct = pd.crosstab(d.trig_down, d.seq, normalize="index")
    print(f"-- {sdef} --"); print(ct.to_string(float_format=lambda x: f"{x:.3f}"))

print("\n=== opening location class distribution ===")
for sdef in ["RTH"]:
    d = M[M.sessdef == sdef]
    print(pd.crosstab(d.trig_down, d.open_class, normalize="index").to_string(float_format=lambda x: f"{x:.3f}"))
