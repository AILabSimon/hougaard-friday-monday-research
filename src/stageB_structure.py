"""STAGE B — does the TYPE of Thursday/Friday structure change Monday's behaviour?

Only triggered weeks (H_FRI < H_THU) are used: the question is heterogeneity WITHIN the
trigger, not whether the trigger works.  Every variable is measurable at Friday's close.
Continuous association first (rank correlation + tercile table); no variable is turned into a
filter here.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats as sps
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT

M = pd.read_parquet(DERIVED / "c2_monday_path.parquet")
F = pd.read_parquet(DERIVED / "c2_friday_path.parquet")
key = ["instrument", "sessdef", "B_date"]
D = M.merge(F[key + [c for c in F.columns if c.startswith("fri_")]], on=key, how="left")
D["week"] = pd.DatetimeIndex(D.C_date).to_period("W-SUN").astype(str)

VARS = {
    # --- Thursday
    "A_range_atr": "Thu range / ATR",
    "A_close_loc": "Thu close location in Thu range",
    "A_bear": "Thu was a down day",
    # --- Friday interaction with Thursday
    "shortfall_atr": "(Thu high - Fri high) / ATR",
    "fri_min_gap_to_Ahigh_atr": "closest Fri approach to Thu high / ATR",
    "fri_frac_closest": "when Fri came closest to Thu high (frac of session)",
    "fri_frac_high": "when Fri made its high (frac of session)",
    "B_inside": "Friday was an inside day",
    "B_took_Alow": "Friday took Thursday's low",
    # --- Friday structure
    "B_range_atr": "Fri range / ATR",
    "B_close_loc": "Fri close location in Fri range",
    "B_bear": "Friday was a down day",
    "B_below_Aclose": "Fri closed below Thu close",
    "fri_last_hour_ret_atr": "Fri last-hour return / ATR",
    "fri_high_before_low": "Fri high came before Fri low",
    "B_body_ratio": "Fri body / range",
}
OUTCOMES = {
    "touch_Blow": "Mon touches Fri low",
    "seq_low_first": "Mon reaches Fri low BEFORE Fri high",
    "dn60_atr": "Mon down-excursion in first 60m / ATR",
    "net60_atr": "Mon (down - up) excursion first 60m / ATR",
    "ret_close_atr": "Mon close - open / ATR",
    "mfe_down_atr": "Mon max down-excursion / ATR",
}
D["seq_low_first"] = D.seq.isin(["low_only", "low_then_high"])
D["net60_atr"] = D.dn60_atr - D.up60_atr

rows = []
for sdef in ["RTH", "BROKER"]:
    d = D[(D.sessdef == sdef) & D.trig_down].copy()
    for v, vlab in VARS.items():
        x = d[v]
        if x.dtype == bool:
            x = x.astype(float)
        for o, olab in OUTCOMES.items():
            y = d[o].astype(float)
            m = x.notna() & y.notna()
            if m.sum() < 80:
                continue
            rho, p = sps.spearmanr(x[m], y[m])
            # tercile contrast (low vs high tercile of the variable)
            try:
                q = pd.qcut(x[m], 3, labels=["lo", "mid", "hi"], duplicates="drop")
            except Exception:
                continue
            g = y[m].groupby(q, observed=True)
            if len(g) < 2 or "lo" not in g.groups or "hi" not in g.groups:
                continue
            lo_, hi_ = g.get_group("lo"), g.get_group("hi")
            tt = sps.ttest_ind(hi_, lo_, equal_var=False)
            rows.append(dict(sessdef=sdef, variable=v, variable_label=vlab,
                             outcome=o, outcome_label=olab, n=int(m.sum()),
                             spearman_rho=rho, spearman_p=p,
                             lo_tercile=lo_.mean(), mid_tercile=g.get_group("mid").mean() if "mid" in g.groups else np.nan,
                             hi_tercile=hi_.mean(), hi_minus_lo=hi_.mean() - lo_.mean(),
                             welch_p=tt.pvalue))
R = pd.DataFrame(rows)
R["bh_rank"] = R.groupby("sessdef").spearman_p.rank()
R["bh_crit"] = 0.05 * R.bh_rank / R.groupby("sessdef").spearman_p.transform("size")
R["survives_BH05"] = R.spearman_p <= R.bh_crit
R.to_csv(OUT / "stageB_structure.csv", index=False)

pd.set_option("display.width", 260)
print("=== associations surviving Benjamini-Hochberg 5% within each session definition ===")
s = R[R.survives_BH05].sort_values(["sessdef", "spearman_p"])
print(s[["sessdef", "variable", "outcome", "n", "spearman_rho", "spearman_p",
         "lo_tercile", "hi_tercile", "hi_minus_lo"]].to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\n{len(s)} of {len(R)} tested associations survive BH.")
print("\n=== strongest 12 by |rho| regardless of BH (RTH) ===")
r = R[R.sessdef == "RTH"].reindex(R[R.sessdef == "RTH"].spearman_rho.abs().sort_values(ascending=False).index)
print(r.head(12)[["variable", "outcome", "n", "spearman_rho", "spearman_p", "lo_tercile", "hi_tercile"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
