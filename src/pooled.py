import pandas as pd, numpy as np
from stats_util import wilson, newcombe_diff

def pool(s: pd.DataFrame, by="B_weekday") -> pd.DataFrame:
    s = s.copy()
    s["ku"] = s.base_rate_all * s.n_eligible
    s["ko"] = s.opp_rate * s.n_opp
    g = s.groupby(by).agg(N=("n_trigger", "sum"), H=("hits", "sum"),
                          NE=("n_eligible", "sum"), KU=("ku", "sum"),
                          NO=("n_opp", "sum"), KO=("ko", "sum"))
    g["rate"] = g.H / g.N
    g["base"] = g.KU / g.NE
    g["opp"] = g.KO / g.NO
    g["upl_base"] = g.rate - g.base
    g["upl_opp"] = g.rate - g.opp
    ci = [newcombe_diff(int(r.H), int(r.N), int(round(r.KO)), int(r.NO)) for r in g.itertuples()]
    g["upl_opp_lo"] = [c[0] for c in ci]
    g["upl_opp_hi"] = [c[1] for c in ci]
    return g
