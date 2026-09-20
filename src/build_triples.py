"""Build the (A,B,C) consecutive-session triple table used by every test.

A = session t-1, B = session t (the 'Friday' slot), C = session t+1 (the 'Monday' slot).
Sessions are restricted to weekday Mon-Fri so that B=Friday -> C=Monday (or the next
trading session if Monday is a holiday, which is exactly Hougaard's own 'asterisk').
Everything downstream is a filter on this table.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sessionlib import DUKA, SESSION_DEFS, DERIVED, ASSET_CLASS

MIN_BARS = {"RTH": 200}     # require a reasonably complete session
DEFAULT_MIN_BARS = 300      # for 24h defs; stub Sunday/holiday sessions excluded


def true_range(h, l, c_prev):
    return np.maximum(h - l, np.maximum(np.abs(h - c_prev), np.abs(l - c_prev)))


def build(inst, sdef):
    f = DERIVED / "sessions" / f"{inst}_{sdef}.parquet"
    d = pd.read_parquet(f)
    d = d[d["weekday"] <= 4].copy()                      # Mon-Fri sessions only
    thr = MIN_BARS.get(sdef, DEFAULT_MIN_BARS)
    d["stub"] = d["n_bars"] < thr
    d = d[~d["stub"]].sort_values("sdate").reset_index(drop=True)
    if len(d) < 60:
        return None
    d["range"] = d["high"] - d["low"]
    d["tr"] = true_range(d["high"].values, d["low"].values,
                         np.r_[d["close"].values[0], d["close"].values[:-1]])
    d["atr14"] = d["tr"].rolling(14, min_periods=5).mean()

    A = d.iloc[:-2].reset_index(drop=True)
    B = d.iloc[1:-1].reset_index(drop=True)
    C = d.iloc[2:].reset_index(drop=True)

    t = pd.DataFrame({
        "instrument": inst, "sessdef": sdef, "asset_class": ASSET_CLASS[inst],
        "A_date": A["sdate"], "B_date": B["sdate"], "C_date": C["sdate"],
        "B_wd": B["weekday"], "C_wd": C["weekday"],
        "year": pd.DatetimeIndex(B["sdate"]).year,
        "A_high": A["high"], "A_low": A["low"], "A_open": A["open"], "A_close": A["close"],
        "B_high": B["high"], "B_low": B["low"], "B_open": B["open"], "B_close": B["close"],
        "C_high": C["high"], "C_low": C["low"], "C_open": C["open"], "C_close": C["close"],
        "A_range": A["range"], "B_range": B["range"], "C_range": C["range"],
        "atr_at_B": B["atr14"],                       # uses data up to and including B
        "B_nbars": B["n_bars"], "C_nbars": C["n_bars"],
        "gapA": (B["sdate"] - A["sdate"]).dt.days,
        "gapB": (C["sdate"] - B["sdate"]).dt.days,
    })

    # ---- triggers ------------------------------------------------------
    t["trig_down"] = t["B_high"] < t["A_high"]          # literal: Friday fails Thursday high
    t["trig_down_incl"] = t["B_high"] <= t["A_high"]
    t["trig_up"] = t["B_low"] > t["A_low"]              # symmetric upside condition

    # ---- events --------------------------------------------------------
    t["touch_low"] = t["C_low"] <= t["B_low"]           # (A) binary touch
    t["touch_high"] = t["C_high"] >= t["B_high"]        # symmetric
    t["close_below"] = t["C_close"] < t["B_low"]
    t["gap_below"] = t["C_open"] < t["B_low"]

    # (B) penetration, normalised
    pen = t["B_low"] - t["C_low"]                       # >0 = traded through
    t["pen_abs"] = pen
    t["pen_frac_Brange"] = pen / t["B_range"].replace(0, np.nan)
    t["pen_frac_atr"] = pen / t["atr_at_B"].replace(0, np.nan)
    ex_up = t["C_high"] - t["B_high"]
    t["exup_frac_atr"] = ex_up / t["atr_at_B"].replace(0, np.nan)

    # distance from C open to each reference, in ATR
    t["dist_to_Blow_atr"] = (t["C_open"] - t["B_low"]) / t["atr_at_B"]
    t["dist_to_Bhigh_atr"] = (t["B_high"] - t["C_open"]) / t["atr_at_B"]
    t["dist_to_Ahigh_atr"] = (t["A_high"] - t["C_open"]) / t["atr_at_B"]

    # (C) directional excursion from C's open
    t["C_down_exc"] = t["C_open"] - t["C_low"]
    t["C_up_exc"] = t["C_high"] - t["C_open"]
    t["C_dir_down"] = t["C_down_exc"] > t["C_up_exc"]

    # ---- condition severity -------------------------------------------
    short = t["A_high"] - t["B_high"]
    t["shortfall_abs"] = short
    t["shortfall_atr"] = short / t["atr_at_B"].replace(0, np.nan)
    t["shortfall_Arange"] = short / t["A_range"].replace(0, np.nan)
    t["shortfall_Brange"] = short / t["B_range"].replace(0, np.nan)

    # ---- B (Friday) structure -----------------------------------------
    t["B_close_loc"] = (t["B_close"] - t["B_low"]) / t["B_range"].replace(0, np.nan)
    t["B_open_loc"] = (t["B_open"] - t["B_low"]) / t["B_range"].replace(0, np.nan)
    t["B_bear"] = t["B_close"] < t["B_open"]
    t["B_body_ratio"] = (t["B_close"] - t["B_open"]).abs() / t["B_range"].replace(0, np.nan)
    t["B_range_atr"] = t["B_range"] / t["atr_at_B"].replace(0, np.nan)
    t["B_below_Aclose"] = t["B_close"] < t["A_close"]
    t["B_below_Amid"] = t["B_close"] < (t["A_high"] + t["A_low"]) / 2
    t["B_took_Alow"] = t["B_low"] < t["A_low"]
    t["B_inside"] = (t["B_high"] < t["A_high"]) & (t["B_low"] > t["A_low"])
    # ---- A (Thursday) structure ---------------------------------------
    t["A_close_loc"] = (t["A_close"] - t["A_low"]) / t["A_range"].replace(0, np.nan)
    t["A_bear"] = t["A_close"] < t["A_open"]
    t["A_range_atr"] = t["A_range"] / t["atr_at_B"].replace(0, np.nan)
    # ---- C (Monday) open behaviour ------------------------------------
    t["C_gap_atr"] = (t["C_open"] - t["B_close"]) / t["atr_at_B"].replace(0, np.nan)
    t["C_open_in_Brange"] = (t["C_open"] <= t["B_high"]) & (t["C_open"] >= t["B_low"])
    return t


if __name__ == "__main__":
    (DERIVED / "triples").mkdir(parents=True, exist_ok=True)
    allt = []
    for inst in DUKA:
        for sdef in SESSION_DEFS:
            t = build(inst, sdef)
            if t is not None:
                allt.append(t)
    big = pd.concat(allt, ignore_index=True)
    big.to_parquet(DERIVED / "triples" / "triples_duka.parquet", index=False)
    print(len(big), "triples")
    print(big.groupby(["sessdef"])["instrument"].count())
    print(big[big.B_wd == 4].groupby("instrument").size())
