"""Higher-timeframe generalisation (weekly, intraday session) + placebo controls."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DERIVED, OUT, DUKA, year_files, ASSET_CLASS
from stats_util import newcombe_diff, two_prop_test
from build_triples import true_range

def logit_fit(X, y, ridge=1e-4, iters=200):
    X=np.asarray(X,float); y=np.asarray(y,float); b=np.zeros(X.shape[1])
    for _ in range(iters):
        eta=X@b; p=1/(1+np.exp(-np.clip(eta,-30,30))); W=np.clip(p*(1-p),1e-8,None)
        H=X.T@(X*W[:,None])+ridge*np.eye(X.shape[1]); g=X.T@(y-p)-ridge*b
        s=np.linalg.solve(H,g); b=b+s
        if np.max(np.abs(s))<1e-9: break
    eta=X@b; p=1/(1+np.exp(-np.clip(eta,-30,30))); W=np.clip(p*(1-p),1e-8,None)
    cov=np.linalg.inv(X.T@(X*W[:,None])+ridge*np.eye(X.shape[1]))
    return b, np.sqrt(np.diag(cov))


def triples_from(d, inst, label):
    d = d.sort_values("sdate").reset_index(drop=True)
    d["range"] = d.high - d.low
    d["tr"] = true_range(d.high.values, d.low.values, np.r_[d.close.values[0], d.close.values[:-1]])
    d["atr14"] = d.tr.rolling(14, min_periods=5).mean()
    A, B, C = d.iloc[:-2].reset_index(drop=True), d.iloc[1:-1].reset_index(drop=True), d.iloc[2:].reset_index(drop=True)
    t = pd.DataFrame(dict(instrument=inst, scale=label, asset_class=ASSET_CLASS[inst],
        A_high=A.high, A_low=A.low, B_high=B.high, B_low=B.low, B_close=B.close,
        B_open=B.open, B_range=B.range, C_high=C.high, C_low=C.low, C_close=C.close,
        atr_at_B=B.atr14, B_date=B.sdate))
    if "slot" in d.columns:
        t["B_slot"] = B["slot"].values; t["C_slot"] = C["slot"].values
    t["trig_down"] = t.B_high < t.A_high
    t["touch_low"] = t.C_low <= t.B_low
    t["trig_up"] = t.B_low > t.A_low
    t["touch_high"] = t.C_high >= t.B_high
    return t


# ---------------- weekly bars from BROKER daily sessions ----------------
def weekly(inst):
    d = pd.read_parquet(DERIVED / "sessions" / f"{inst}_BROKER.parquet")
    d = d[d.weekday <= 4]
    d = d[d.n_bars >= 300].copy()
    d["wk"] = pd.DatetimeIndex(d.sdate).to_period("W-FRI").start_time
    g = d.groupby("wk")
    w = pd.DataFrame(dict(open=g.open.first(), high=g.high.max(), low=g.low.min(),
                          close=g.close.last(), nd=g.size())).reset_index()
    w = w[w.nd >= 4].rename(columns={"wk": "sdate"})
    return triples_from(w, inst, "WEEKLY")


# ---------------- intraday sessions (Asia / London / NY) ----------------
SLOTS = [("ASIA", 0, 7), ("LONDON", 7, 13), ("NY", 13, 21)]   # UTC hours, [start,end)

def sessions3(inst):
    parts = []
    for y, p in year_files("1m", inst, "BID"):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low", "close"])
        ts = pd.DatetimeIndex(df.timestamp)
        h = ts.hour
        lab = np.full(len(df), "", dtype=object)
        for name, a, b in SLOTS:
            lab[(h >= a) & (h < b)] = name
        keep = lab != ""
        df = df.loc[keep].assign(slot=lab[keep], day=ts[keep].normalize().tz_localize(None))
        g = df.groupby(["day", "slot"], sort=False)
        parts.append(pd.DataFrame(dict(open=g.open.first(), high=g.high.max(), low=g.low.min(),
                                       close=g.close.last(), n=g.size())).reset_index())
        del df
    s = pd.concat(parts, ignore_index=True)
    s = s[s.n >= 60].copy()
    order = {"ASIA": 0, "LONDON": 1, "NY": 2}
    s["ord"] = s.slot.map(order)
    s = s.sort_values(["day", "ord"]).reset_index(drop=True)
    s["sdate"] = s.day + pd.to_timedelta(s["ord"] * 8, unit="h")
    return triples_from(s, inst, "SESSION3")


def summarise(t, key):
    rows = []
    for k, g in t.groupby(key):
        tt, oo = g[g.trig_down], g[~g.trig_down]
        if len(tt) < 40 or len(oo) < 40:
            continue
        lo, hi = newcombe_diff(int(tt.touch_low.sum()), len(tt), int(oo.touch_low.sum()), len(oo))
        p, _ = two_prop_test(int(tt.touch_low.sum()), len(tt), int(oo.touch_low.sum()), len(oo))
        # controlled logit
        d = g.dropna(subset=["atr_at_B"]).copy(); d = d[d.B_range > 0]
        d["dist"] = (d.B_close - d.B_low) / d.atr_at_B; d["br"] = d.B_range / d.atr_at_B
        X = np.column_stack([np.ones(len(d)), d.trig_down.astype(float), d.dist, d.br])
        b, se = logit_fit(X, d.touch_low.values.astype(float))
        rows.append(dict(key=str(k), n_trig=len(tt), rate=tt.touch_low.mean(),
                         n_opp=len(oo), opp=oo.touch_low.mean(),
                         upl=tt.touch_low.mean() - oo.touch_low.mean(), lo=lo, hi=hi, p=p,
                         beta_ctrl=b[1], z_ctrl=b[1] / se[1],
                         up_rate=g[g.trig_up].touch_high.mean(),
                         up_opp=g[~g.trig_up].touch_high.mean()))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    W = pd.concat([weekly(i) for i in DUKA], ignore_index=True)
    W.to_parquet(DERIVED / "triples" / "triples_weekly.parquet", index=False)
    print("=== WEEKLY analogue: week high < prior week high -> next week takes this week's low ===")
    print(summarise(W, "instrument").to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    W["g"] = W.asset_class
    print(summarise(W, "g").to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    S = pd.concat([sessions3(i) for i in DUKA], ignore_index=True)
    S.to_parquet(DERIVED / "triples" / "triples_session3.parquet", index=False)
    S["g"] = S.asset_class + "|" + S.B_slot.astype(str) + "->" + S.C_slot.astype(str)
    print("\n=== INTRADAY SESSION analogue (Asia/London/NY, UTC blocks) ===")
    print(summarise(S, "g").to_string(index=False, float_format=lambda x: f"{x:.3f}"))
