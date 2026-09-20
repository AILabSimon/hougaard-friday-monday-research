"""Session-bar construction from canonical 1m UTC bars.

Source data is READ-ONLY: we only read Market Data/Canonical.
Bars are labelled by OPEN time, interval [t, t+1min).
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
import pandas as pd

MD = Path(os.environ.get("MARKET_DATA_ROOT",
          Path.home() / "mnt" / "Data" / "Market Data"))
CANON = MD / "Canonical"
PROJ = Path(__file__).resolve().parents[1]
DERIVED = PROJ / "derived"
OUT = PROJ / "outputs"

# instrument -> broker-day shift in hours applied to NY local time
# FX weekly/daily roll 17:00 NY  -> +7h ; metals/WTI/US index CFD roll 18:00/16:15 NY -> +6h
BROKER_SHIFT = {
    "EURUSD": 7, "GBPUSD": 7, "AUDUSD": 7, "USDCAD": 7, "USDCHF": 7, "USDJPY": 7,
    "XAUUSD": 6, "XAGUSD": 6, "WTIUSD": 6, "NAS100": 6, "US500": 6, "BTCUSD": 0,
}
ASSET_CLASS = {
    "EURUSD": "FX", "GBPUSD": "FX", "AUDUSD": "FX", "USDCAD": "FX",
    "USDCHF": "FX", "USDJPY": "FX",
    "XAUUSD": "METAL", "XAGUSD": "METAL",
    "WTIUSD": "ENERGY", "NAS100": "INDEX", "US500": "INDEX", "BTCUSD": "CRYPTO",
}
DUKA = list(ASSET_CLASS)

SESSION_DEFS = ["UTC", "LONDON", "NYFX", "BROKER", "RTH"]


def current_version(tf, inst, side):
    p = CANON / tf / inst / side / "CURRENT"
    return p.read_text().strip()


def manifest(tf, inst, side):
    v = current_version(tf, inst, side)
    return json.loads((CANON / tf / inst / side / v / "MANIFEST.json").read_text()), v


def year_files(tf, inst, side):
    man, v = manifest(tf, inst, side)
    base = CANON / tf / inst / side
    return [(f["year"], base / f["path"]) for f in sorted(man["files"], key=lambda x: x["year"])]


def read_year(tf, inst, side, year):
    for y, p in year_files(tf, inst, side):
        if y == year:
            return pd.read_parquet(p)
    return None


def session_key(ts_utc: pd.DatetimeIndex, inst: str, sdef: str):
    """Return (session_date as datetime64[ns] normalised, mask of in-session bars)."""
    n = len(ts_utc)
    if sdef == "UTC":
        return ts_utc.tz_convert("UTC").normalize().tz_localize(None), np.ones(n, bool)
    if sdef == "LONDON":
        loc = ts_utc.tz_convert("Europe/London").tz_localize(None)
        return pd.DatetimeIndex(loc).normalize(), np.ones(n, bool)
    if sdef == "NYFX":
        loc = ts_utc.tz_convert("America/New_York")
        shifted = pd.DatetimeIndex(loc.tz_localize(None)) + pd.Timedelta(hours=7)
        return shifted.normalize(), np.ones(n, bool)
    if sdef == "BROKER":
        h = BROKER_SHIFT.get(inst, 7)
        if h == 0:
            return ts_utc.tz_convert("UTC").normalize().tz_localize(None), np.ones(n, bool)
        loc = ts_utc.tz_convert("America/New_York")
        shifted = pd.DatetimeIndex(loc.tz_localize(None)) + pd.Timedelta(hours=h)
        return shifted.normalize(), np.ones(n, bool)
    if sdef == "RTH":
        loc = ts_utc.tz_convert("America/New_York")
        naive = pd.DatetimeIndex(loc.tz_localize(None))
        mins = naive.hour * 60 + naive.minute
        mask = (mins >= 9 * 60 + 30) & (mins < 16 * 60)
        return naive.normalize(), mask
    raise ValueError(sdef)


AGG = {"open": "first", "high": "max", "low": "min", "close": "last",
       "volume": "sum", "timestamp": ["min", "max", "count"]}


def agg_chunk(df: pd.DataFrame, inst: str, sdef: str) -> pd.DataFrame:
    ts = pd.DatetimeIndex(df["timestamp"])
    key, mask = session_key(ts, inst, sdef)
    d = df.loc[mask].copy()
    d["sdate"] = key[mask]
    d = d.sort_values("timestamp")
    g = d.groupby("sdate", sort=True)
    out = pd.DataFrame({
        "open": g["open"].first(),
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "volume": g["volume"].sum(),
        "first_ts": g["timestamp"].min(),
        "last_ts": g["timestamp"].max(),
        "n_bars": g["timestamp"].count(),
    }).reset_index()
    return out


def combine(parts: list[pd.DataFrame]) -> pd.DataFrame:
    """Combine per-year partial session aggregates (sessions may straddle year ends)."""
    df = pd.concat(parts, ignore_index=True).sort_values(["sdate", "first_ts"])
    g = df.groupby("sdate", sort=True)
    out = pd.DataFrame({
        "open": g["open"].first(),      # already sorted by first_ts
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "volume": g["volume"].sum(),
        "first_ts": g["first_ts"].min(),
        "last_ts": g["last_ts"].max(),
        "n_bars": g["n_bars"].sum(),
    }).reset_index()
    return out


def build_sessions(inst: str, side: str = "BID", sdefs=SESSION_DEFS, tf="1m") -> dict:
    res = {s: [] for s in sdefs}
    for y, p in year_files(tf, inst, side):
        df = pd.read_parquet(p, columns=["timestamp", "open", "high", "low", "close", "volume"])
        for s in sdefs:
            res[s].append(agg_chunk(df, inst, s))
        del df
    return {s: combine(v) for s, v in res.items()}
