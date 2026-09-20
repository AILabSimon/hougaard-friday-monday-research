"""Primary behavioural census: conditional vs unconditional, controls, robustness."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT
from stats_util import wilson, newcombe_diff, two_prop_test

OUT.mkdir(parents=True, exist_ok=True)
T = pd.read_parquet(DERIVED / "triples" / "triples_duka.parquet")
WD = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}


def cell(df, trig_col, event_col, **meta):
    n = len(df)
    sub = df[df[trig_col]] if trig_col else df
    nt, k = len(sub), int(sub[event_col].sum())
    lo, hi = wilson(k, nt)
    # base = complement of trigger (opposite condition)
    opp = df[~df[trig_col]] if trig_col else df.iloc[0:0]
    no, ko = len(opp), int(opp[event_col].sum())
    # unconditional over the whole eligible set
    ku = int(df[event_col].sum())
    dlo, dhi = newcombe_diff(k, nt, ku, n)
    pval, h = two_prop_test(k, nt, ko, no) if no else (np.nan, np.nan)
    return dict(**meta, trigger=trig_col or "ALL", event=event_col,
                n_eligible=n, n_trigger=nt, hits=k,
                rate=k / nt if nt else np.nan, ci_lo=lo, ci_hi=hi,
                base_rate_all=ku / n if n else np.nan,
                n_opp=no, opp_rate=ko / no if no else np.nan,
                uplift_vs_all=(k / nt - ku / n) if nt and n else np.nan,
                uplift_lo=dlo, uplift_hi=dhi,
                uplift_vs_opp=(k / nt - ko / no) if nt and no else np.nan,
                fisher_p=pval, cohens_h=h)


# ---------------------------------------------------------------- 1. CORE
rows = []
fri = T[(T.B_wd == 4)]
for strict in (True, False):
    f = fri[fri.C_wd == 0] if strict else fri
    tag = "MondayOnly" if strict else "NextSession"
    for (inst, sdef), g in f.groupby(["instrument", "sessdef"]):
        for ev in ("touch_low", "close_below", "gap_below"):
            rows.append(cell(g, "trig_down", ev, instrument=inst, sessdef=sdef,
                             scope=tag, period="full"))
core = pd.DataFrame(rows)
core.to_csv(OUT / "core_results.csv", index=False)

# ---------------------------------------------------------------- 2. CONTROLS
rows = []
for (inst, sdef), g in T.groupby(["instrument", "sessdef"]):
    for wd in range(5):
        gw = g[g.B_wd == wd]
        if len(gw) < 50:
            continue
        meta = dict(instrument=inst, sessdef=sdef, B_weekday=WD[wd],
                    C_weekday_mode=WD.get(int(gw.C_wd.mode().iloc[0]), "?"))
        # downside: failed high -> next session seeks B low
        rows.append(cell(gw, "trig_down", "touch_low", control="adjacent_down", **meta))
        # upside symmetry: failed low -> next session seeks B high
        rows.append(cell(gw, "trig_up", "touch_high", control="adjacent_up_symmetry", **meta))
        # placebo: does the failed-high condition predict the UPSIDE event?
        rows.append(cell(gw, "trig_down", "touch_high", control="placebo_wrongway", **meta))
controls = pd.DataFrame(rows)
controls.to_csv(OUT / "controls.csv", index=False)

# ---------------------------------------------------------------- 3. ROBUSTNESS (year)
rows = []
f = fri[fri.C_wd == 0]
for (inst, sdef, yr), g in f.groupby(["instrument", "sessdef", "year"]):
    if len(g) < 10:
        continue
    rows.append(cell(g, "trig_down", "touch_low", instrument=inst, sessdef=sdef,
                     scope="MondayOnly", period=str(yr)))
rob = pd.DataFrame(rows)
rob.to_csv(OUT / "robustness.csv", index=False)

# ---------------------------------------------------------------- summary print
print("=== LITERAL TEST: B=Friday, C=Monday, trig=Fri high < Thu high, event=Mon low <= Fri low ===")
for sdef in ["RTH", "BROKER", "NYFX", "UTC", "LONDON"]:
    s = core[(core.sessdef == sdef) & (core.scope == "MondayOnly") & (core.event == "touch_low")]
    tot_n, tot_k = s.n_trigger.sum(), s.hits.sum()
    tot_all, tot_ku = s.n_eligible.sum(), (s.base_rate_all * s.n_eligible).sum()
    print(f"{sdef:7s} pooled N={tot_n:5d} hit={tot_k/tot_n:.3f}  base(all Fri)={tot_ku/tot_all:.3f}  uplift={tot_k/tot_n-tot_ku/tot_all:+.3f}")
print()
print(core[(core.sessdef == 'RTH') & (core.scope == 'MondayOnly') & (core.event == 'touch_low')]
      [['instrument','n_trigger','rate','base_rate_all','opp_rate','uplift_vs_all','uplift_vs_opp','fisher_p']]
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
