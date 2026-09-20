# Methods — everything needed to audit or reproduce the results

## 1. Data

**Primary.** Dukascopy 1-minute **bid** bars, from the canonical store at
`AI Lab/Data/Market Data/Canonical/1m/<INSTRUMENT>/BID/<version>/`. Timestamps are **UTC**;
each bar is labelled by its **open** and covers the half-open interval `[t, t+1min)`. The
store's own validation status for every series used is `PASS WITH EXPECTED CLOSURES`
(BTCUSD: `INVESTIGATE`). Ask-side series exist and were used only to measure spreads.

| | |
|---|---|
| Instruments | EURUSD, GBPUSD, AUDUSD, USDCAD, USDCHF, USDJPY (spot FX); XAUUSD, XAGUSD (spot metals); WTIUSD (CFD, Dukascopy `LIGHTCMDUSD`); NAS100 (CFD, `USATECHIDXUSD`); US500 (CFD, `USA500IDXUSD`); BTCUSD (crypto CFD) |
| Range | 2016-01-03 → 2026-09-15 (BTCUSD from 2017-05-07) |
| Rows | ≈3.2–4.0 M 1-minute bars per instrument |

**Replication.** Yahoo **daily** futures bars from
`Canonical/1d/YF_<SYM>/TRADE/` — ES, NQ (2000-09 → 2026-09), CL (2000-08 →), GC, SI
(2000-08 →). These are continuous back-adjusted series and are used only as a second,
independent-vendor replication set; no primary conclusion rests on them alone.

**Not in this repository.** The candle data itself. Everything here is aggregate. Source data
was opened read-only; nothing under `Market Data/` was modified.

## 2. Session construction

All five daily definitions are built from the same 1-minute UTC bars by mapping each bar to a
session label, then aggregating `open=first, high=max, low=min, close=last` in timestamp order
(`src/sessionlib.py`, `session_key()`):

| Name | Rule | Notes |
|---|---|---|
| `RTH` | 09:30–16:00 **America/New_York**, session dated by the NY date | **Hougaard's own definition.** Bars outside the window are dropped, not assigned elsewhere |
| `BROKER` | Dukascopy trading day. FX: 17:00 NY roll. Metals, WTI, index CFDs: 18:00 NY roll | implemented as NY-local time + 7 h (FX) or + 6 h (others), then `.normalize()` |
| `NYFX` | 17:00 NY roll for every instrument | identical to `BROKER` for FX by construction |
| `UTC` | 00:00–23:59 UTC calendar day | |
| `LONDON` | Europe/London local calendar day | |

**Timezone / DST.** Conversions use `pandas`/IANA tz databases (`tz_convert`), so US and UK
daylight-saving transitions are handled by the tz database rather than a fixed offset. The
roll-shift definitions are applied *after* conversion to local time, so a 17:00 NY roll stays
at 17:00 NY across DST changes — which is what the venue does. `LONDON` days are 23 or 25
hours on transition days, as they are on a London-local chart.

**Stub-session filter.** A session is dropped if it contains fewer than **300** 1-minute bars
(**200** for `RTH`). This removes the 2–3 hour Sunday-evening opening stub that `UTC` and
`LONDON` construction creates, the 1–11 Saturday fragments per instrument caused by DST
mismatches between Dukascopy and New York, and severely truncated holiday half-days. Without
this filter those stubs would enter the consecutive-session sequence as if they were trading
days. Sessions labelled Saturday or Sunday are excluded outright.

## 3. The triple table — the single object every test filters

`src/build_triples.py`. Sessions are restricted to weekday Mon–Fri, sorted ascending, and read
as overlapping consecutive triples:

```
A = session t-1     B = session t  ("Friday" slot)     C = session t+1  ("Monday" slot)
```

Because holidays simply do not appear as sessions, `B` = Friday implies `C` = Monday, or the
next trading session if Monday is a holiday — **which is exactly Hougaard's "asterisk"**. Both
readings are reported: `C_wd == 0` (strict Monday) and unrestricted (next session).
`gapB = (C_date − B_date).days` is retained so any other convention can be recovered.

Every weekday pair is produced by the same code path; `B_wd` selects which. This is what makes
the adjacent-weekday control an exact like-for-like comparison rather than a separate
implementation.

**ATR.** `atr14` is a 14-session simple average of the true range, computed on the session
series and read **at B** — it uses no information after Friday's close.

## 4. Definitions

**Trigger (literal).** `trig_down = B_high < A_high` (Friday's high strictly below Thursday's).
`trig_down_incl = B_high <= A_high` is also reported; it changes the hit rate by 0.001.
**Symmetric control.** `trig_up = B_low > A_low`.

**Events.**

| Name | Definition |
|---|---|
| `touch_low` (primary) | `C_low <= B_low` — Monday trades **to or through** Friday's low |
| `touch_high` (symmetric) | `C_high >= B_high` |
| penetration | `(B_low − C_low) / B_range > k` for k ∈ {0.05, 0.25}; and `/ATR14 > 0.25` |
| `close_below` | `C_close < B_low` |
| `gap_below` | `C_open < B_low` |
| `C_dir_down` | `(C_open − C_low) > (C_high − C_open)` — directional excursion from Monday's own open |
| tolerance ladder | `C_low <= B_low + tol × ATR14`, tol ∈ {0, .05, .10, .25, .50, .75, 1.0} — the "double bottom" reading |

**Severity.** `shortfall = (A_high − B_high)`, normalised by ATR14, by Thursday's range and by
Friday's range; analysed in quintiles.

## 5. Controls

| Control | Definition | File |
|---|---|---|
| Unconditional base rate | `touch_low` over **all** eligible Fridays, triggered or not | `core_results.csv` → `base_rate_all` |
| Opposite condition | `touch_low` given `B_high >= A_high` | `core_results.csv` → `opposite_rate` |
| Upside symmetry | `trig_up` → `touch_high`, same code path | `controls.csv` → `control = upside_symmetry` |
| Wrong-direction placebo | `trig_down` → `touch_high` (should be ≤ base) | `controls.csv` → `placebo_wrong_direction` |
| Adjacent weekdays | identical construction with `B_wd` ∈ {Mon…Fri} | `controls.csv` → `adjacent_weekday_down` |
| Weekly analogue | weeks aggregated from BROKER days (≥4 days/week) | `controls.csv` → `weekly_analogue` |
| Intraday session analogue | UTC blocks Asia 00–07, London 07–13, NY 13–21; ≥60 bars | `controls.csv` → `intraday_session_analogue` |
| **Geometric / close-location** | logistic regression, below | `mechanism_logit.csv` |
| **Path-shuffle placebo** | permutation, below | `placebo.csv` |
| Random-trigger sanity | trigger vector permuted, 200 reps | `placebo.csv` → `randtrig_mean` |

### 5.1 The geometric control
The trigger is strongly correlated with Friday closing near its low, and a nearby level is
touched more often for purely geometric reasons. The control is a logistic regression of
`touch_low` on:

```
trig_down  +  (B_close − B_low)/ATR14  +  B_range/ATR14  +  instrument fixed effects
```

fitted by Newton–IRLS with ridge 1e-4 (`src/mechanism.py::logit_fit`; standard errors from the
inverse observed information). The reported quantity is the coefficient on `trig_down`, raw and
controlled. This is the single most consequential test in the study, and it is the one most
open to the charge of over-controlling — which is why §5.2 exists.

### 5.2 The path-shuffle placebo
Assumption-free counterpart to §5.1. For each observation, Monday's behaviour is reduced to
three ATR-normalised quantities: the gap `(C_open − B_close)/ATR`, the up-excursion
`(C_high − C_open)/ATR` and the down-excursion `(C_open − C_low)/ATR`. Those three are
**permuted jointly** across observations **within instrument × calendar year**, and the touch
indicator is re-derived. Every marginal distribution is preserved; only the actual pairing
between a given Friday and its own Monday is destroyed. 1 000 replications; the observed uplift
is compared with the resulting null distribution. Reconstruction of `touch_low` from the three
normalised quantities is ≥99.9% exact, so the machinery introduces no error of its own.
`src/placebo.py`, seed 20260920.

## 6. Statistics

- Proportions: **Wilson** score intervals.
- Difference of proportions: **Newcombe** method 10.
- Significance of a 2×2 table: **Fisher exact**; effect size: **Cohen's h**.
- Regression: logistic, Newton–IRLS, ridge 1e-4, instrument fixed effects.
- Mean R per trade: normal-approximation 95% interval on the mean, `± 1.96·sd/√n`. Given the
  skew documented in §7 this interval is indicative only for the structural constructions.
- Correlated observations are **not** treated as independent evidence; see
  `results/independence.csv` and finding V9.

## 7. Economic tests — exact definitions

All constructions are **shorts**, because that is what the hypothesis implies. All are resolved
from 1-minute bars. All figures are **gross of costs**.

| ID | Entry | Target | Invalidation | Resolution |
|---|---|---|---|---|
| **E1** | Friday's close | Friday's low | Friday's high | first-touch minute of the low vs the high; unresolved marked to Monday's close |
| **E2** | Monday's open (skipped when Monday opens below Friday's low, or above Friday's high) | Friday's low | Friday's high | as E1 |
| **E3** | Monday's open | `k_t × ATR14` below the open, k_t ∈ {0.5, 1.0, 1.5, 2.0} | `k_s × ATR14` above the open, k_s ∈ {0.5, 0.75, 1.0} | first-touch minute on a grid of levels `open ± k·ATR`, k from −3 to +3 in 0.25 steps (`src/path_grid.py`) |

`R` is profit divided by the entry-to-invalidation distance. Every construction is run for
triggered **and** non-triggered Fridays; the non-triggered column is the control, and the
difference between them is the only thing the hypothesis can claim.

**Known pathology in E1/E2 — read before using their mean R.** The risk denominator is
`Friday high − entry`, which is *unbounded below*: when Friday closes at or near its high the
denominator can be under 0.01 ATR, producing single-trade R values above 100 (max observed:
1321). The mean R of E1 is therefore dominated by a handful of observations and is **not a
usable expectancy estimate**. The CSV carries `mean_R_trim5` (mean after dropping the top 5% of
R), `max_R` and `risk_atr_p05` so this is visible. Trimmed means are negative in 14 of 16 E1
cells; medians are negative in 15 of 16. E3 exists precisely because it floors the stop
distance, which is what a trader would actually do — and E3's expectancy is negative
throughout. **Conclusions about tradeability rest on E3 and on the structural evidence in
`monday_path.csv`, not on E1's mean R.**

**Costs.** Measured, not modelled: Dukascopy 2024 median ask−bid is 3.42 index points on
NAS100 (median RTH ATR14 = 252) and 0.51 on US500 (ATR14 = 49) — about **2–3% of a 0.5-ATR
stop** per round trip. Not applied to the tables, because no construction reached positive
expectancy before costs.

## 8. Confirmatory / exploratory / frozen

- **Confirmatory** (specified before results were seen): HF-001 … HF-003, HF-007 … HF-009,
  HF-011, HF-012, HF-017 … HF-019, HF-021 … HF-024.
- **Control** (pre-specified): HF-004 … HF-006, HF-010, HF-015, HF-016.
- **Exploratory** (examined after seeing results): HF-020 (gap decomposition), HF-026.
  The asset-class breakdown was pre-specified as a robustness dimension, but the decision to
  *focus* on US equity indices followed the results and should be read as exploratory
  selection — which is why it was then frozen and validated (below).
- **Frozen validation** (HF-013): the rule and all controls were fixed on Yahoo ES+NQ
  **2000–2015**, then applied unchanged to Yahoo **2016–2026** and, separately, to Dukascopy
  NAS100/US500 RTH **2016–2026**. No parameter was re-tuned between development and validation;
  there is no parameter to tune — the trigger is `B_high < A_high`.
- **Multiplicity.** The asset-class × session-definition grid is 4 × 5 = 20 cells. The
  US-index result is significant in all five session definitions and in both vendors, which is
  not independent replication (V9) but does rule out cell-shopping across session definitions.
  A reviewer may still wish to apply a multiplicity discount to the asset-class selection; see
  question 5 in `current_findings.md`.

## 9. Reproducing the results

The scripts expect the canonical store and are run in this order. They write to
`<project>/derived/` and `<project>/outputs/`; only `outputs/` is copied into this repository.

```
python src/build_all_sessions.py     # 1m -> session bars, all 5 definitions, 12 instruments
python src/build_triples.py          # session bars -> the (A,B,C) triple table
python src/build_yf_triples.py       # Yahoo daily futures -> triples
python src/census.py                 # first-pass census (superseded by finalise.py)
python src/mechanism.py              # geometric control, severity, event ladder
python src/htf_placebo.py            # weekly and intraday-session analogues
python src/placebo.py                # path-shuffle placebo (1000 reps, seed 20260920)
python src/path_intraday.py          # Monday 1m path: first arrival, time-to-touch, MFE/MAE
python src/path_grid.py NAS100 US500 EURUSD GBPUSD   # ATR level grid for E3
python src/economics.py              # monday_path.csv + strategy_expectancy.csv
python src/finalise.py               # core_results / controls / robustness + charts 1-6
python src/strategy_chart.py         # charts 7-8
python src/final_challenge.py        # tolerance ladder, independence + chart 9
python src/chart02_fix.py            # chart 2 with confidence intervals
```

Requirements: python ≥3.10, pandas, numpy, pyarrow, scipy, matplotlib. No other dependencies.
`MARKET_DATA_ROOT` overrides the canonical store location.
