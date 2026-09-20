"""Independent replication set: Yahoo daily futures bars (ES/NQ/CL/GC/SI + micros),
long history back to 2000 for ES/NQ.  Session = Yahoo's daily bar (exchange day)."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import CANON, DERIVED
from build_triples import true_range

YF = ["YF_ES", "YF_NQ", "YF_CL", "YF_GC", "YF_SI"]   # skip micros (duplicate the big contracts)
CLS = {"YF_ES": "US_INDEX", "YF_NQ": "US_INDEX", "YF_CL": "ENERGY",
       "YF_GC": "METAL", "YF_SI": "METAL"}


def load(inst):
    base = CANON / "1d" / inst / "TRADE"
    v = (base / "CURRENT").read_text().strip()
    man = json.loads((base / v / "MANIFEST.json").read_text())
    d = pd.concat([pd.read_parquet(base / f["path"])
                   for f in sorted(man["files"], key=lambda x: x["year"])], ignore_index=True)
    d["sdate"] = pd.DatetimeIndex(d["timestamp"]).tz_convert("UTC").tz_localize(None).normalize()
    d = d.drop_duplicates("sdate").sort_values("sdate").reset_index(drop=True)
    d["weekday"] = d["sdate"].dt.dayofweek
    return d[d.weekday <= 4].reset_index(drop=True)


def triples(inst):
    d = load(inst)
    d["range"] = d.high - d.low
    d["tr"] = true_range(d.high.values, d.low.values, np.r_[d.close.values[0], d.close.values[:-1]])
    d["atr14"] = d.tr.rolling(14, min_periods=5).mean()
    A, B, C = d.iloc[:-2].reset_index(drop=True), d.iloc[1:-1].reset_index(drop=True), d.iloc[2:].reset_index(drop=True)
    t = pd.DataFrame({
        "instrument": inst, "sessdef": "YF_DAILY", "asset_class": CLS[inst],
        "A_date": A.sdate, "B_date": B.sdate, "C_date": C.sdate,
        "B_wd": B.weekday, "C_wd": C.weekday, "year": B.sdate.dt.year,
        "A_high": A.high, "A_low": A.low, "A_open": A.open, "A_close": A.close,
        "B_high": B.high, "B_low": B.low, "B_open": B.open, "B_close": B.close,
        "C_high": C.high, "C_low": C.low, "C_open": C.open, "C_close": C.close,
        "A_range": A.range, "B_range": B.range, "C_range": C.range,
        "atr_at_B": B.atr14, "gapB": (C.sdate - B.sdate).dt.days,
    })
    t["trig_down"] = t.B_high < t.A_high
    t["trig_up"] = t.B_low > t.A_low
    t["touch_low"] = t.C_low <= t.B_low
    t["touch_high"] = t.C_high >= t.B_high
    t["close_below"] = t.C_close < t.B_low
    t["gap_below"] = t.C_open < t.B_low
    t["pen_frac_Brange"] = (t.B_low - t.C_low) / t.B_range.replace(0, np.nan)
    t["shortfall_atr"] = (t.A_high - t.B_high) / t.atr_at_B.replace(0, np.nan)
    t["B_close_loc"] = (t.B_close - t.B_low) / t.B_range.replace(0, np.nan)
    t["C_dir_down"] = (t.C_open - t.C_low) > (t.C_high - t.C_open)
    t["C_gap_atr"] = (t.C_open - t.B_close) / t.atr_at_B.replace(0, np.nan)
    return t


if __name__ == "__main__":
    all_ = []
    for i in YF:
        t = triples(i)
        print(i, len(t), t.B_date.min().date(), t.B_date.max().date())
        all_.append(t)
    big = pd.concat(all_, ignore_index=True)
    big.to_parquet(DERIVED / "triples" / "triples_yf.parquet", index=False)
    print("total", len(big))
