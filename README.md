# Hougaard Friday → Monday research

Independent quantitative test of the market behaviour attributed to Tom Hougaard.

## Research question

> **"If Friday's high does not reach or exceed Thursday's high, does Monday chase Friday's low?"**

Formally: given `H_FRI < H_THU`, does Monday trade to or through `L_FRI` more often than
ordinary Monday behaviour would produce anyway?

## Current status

**AWAITING INDEPENDENT REVIEW.** First-pass evidence package complete: literal hypothesis,
controls, geometric and permutation tests, cross-market and cross-vendor replication, session
and temporal robustness, frozen dev/validation split, Monday path anatomy, and a first round of
economic tests. No further hypothesis expansion or strategy optimisation until review.

## Data universe

| | |
|---|---|
| **Primary source** | Dukascopy 1-minute bid bars, canonicalised (`AI Lab/Data/Market Data/Canonical`), UTC, bar labelled by open |
| **Instruments** | EURUSD, GBPUSD, AUDUSD, USDCAD, USDCHF, USDJPY, XAUUSD, XAGUSD, WTIUSD, NAS100 (Nasdaq-100 CFD), US500 (S&P 500 CFD), BTCUSD |
| **Range** | 2016-01-03 → 2026-09-15 (≈2 760 sessions per instrument) |
| **Replication source** | Yahoo daily futures bars: ES, NQ, CL, GC, SI — **2000-08 → 2026-09** (26 years, independent vendor, independent session convention) |
| **Weekly / intraday scales** | weekly bars aggregated from broker days; Asia / London / New York UTC session blocks, built from the same 1m data |
| **Session definitions tested** | `RTH` 09:30–16:00 New York (**Hougaard's own definition**), `BROKER` (Dukascopy CFD/FX day: 17:00 NY roll for FX, 18:00 NY for metals/WTI/indices), `NYFX` (17:00 NY roll), `UTC` 00:00–23:59, `LONDON` local calendar day (DST-aware) |
| **Not uploaded** | the candle data itself. Everything here is aggregate. |

## Current headline result

**Partially supported, and only in one place — and it is not tradeable as stated.**

1. **The literal hypothesis is directionally true everywhere but nowhere near the claimed
   strength.** Pooled over 12 instruments, `P(Monday low ≤ Friday low | H_FRI < H_THU)` is
   **44–50%**, against an unconditional Monday rate of 37–43%. Hougaard's own quoted figures
   (>90%, 95%, and latterly 62%) are not reproduced under any legitimate construction.
2. **For every asset class except US equity indices the apparent edge is a geometric
   artefact.** A failed Friday high selects Fridays that *closed near their low*; a nearby
   level is touched more often. Once Friday's close-within-range is controlled for, the
   logistic coefficient on the trigger collapses to ≈0 (FX: β = −0.01, z = −0.18). A placebo
   that destroys the temporal pairing while preserving all marginals **reproduces the whole FX
   effect** (observed uplift 0.141 vs placebo 0.159, p = 0.91).
3. **US equity indices are the exception and the effect is real** (though the replication is
   less independent than it looks — NAS100/US500/ES/NQ outcomes correlate ≈0.75–0.79 on the same
   Monday, so this is close to one bet on the US equity complex; the real replication is
   temporal). After the same control the
   trigger keeps β ≈ 0.42–0.44 (OR ≈ 1.52–1.55, z ≈ 3.0) on Dukascopy NAS100/US500 and
   β = 0.36 (z = 3.67) on 26 years of ES/NQ. It beats its placebo (p < 0.001), it is positive
   in 11/11 Dukascopy years and 26/27 Yahoo years, and it **survives a frozen
   dev(2000-2015) → validation(2016-2026) split on two independent data sources**.
4. **Hougaard's own >90% is reproducible only at a "double bottom" tolerance of ~0.75 ATR —
   at which point the opposite condition also scores 83.5%** and the Thursday/Friday comparison
   has stopped carrying information. This appears to be the explanation for the gap between his
   figures and every systematic test, his own included (he has since revised to 62%).
5. **Friday is only modestly special.** The identical construction on Mon→Tue … Thu→Fri also
   produces large raw uplifts; after control, only the US-index Friday→Monday cell stays
   clearly significant, at roughly 3× the coefficient of the other weekday pairs.
6. **The simple trade constructions tested were not economically viable.** Of 40 triggered
   construction-cells, none showed positive expectancy; 11 were significantly negative and the
   rest were indistinguishable from zero. Three structural features explain why: even in
   triggered weeks Monday reaches Friday's *high* more often than its *low* (53.5% vs 46.5%,
   RTH) and the low is reached *first* only 41% of the time; 76% of the touches that do happen
   occur inside the first hour, mostly at the open; and the trigger systematically selects the
   *worst* payoff geometry — median reward:risk available at Friday's close is **0.75R** versus
   2.60R for non-triggered Fridays. **This is not a claim that no tradeable exploitation
   exists** — only directional short constructions were tested.

**Final classification: PARTIALLY SUPPORTED.** Statistically supported for US equity indices,
Friday → Monday, at roughly a fifth of the claimed magnitude; not supported for any other
market, scale or weekday; and **not yet demonstrated to provide an economically tradeable
implementation** — 20 directional short constructions were tested and none showed positive
expectancy, but the search was deliberately not expanded beyond them.

## Most important evidence

| What | File |
|---|---|
| Literal hypothesis by instrument / session / dataset | [`results/core_results.csv`](results/core_results.csv) |
| Base rate, opposite condition, upside symmetry, adjacent weekdays, weekly & intraday analogues, placebo | [`results/controls.csv`](results/controls.csv) |
| Year-by-year, session definitions, frozen dev/validation | [`results/robustness.csv`](results/robustness.csv) |
| Monday intraday path: first arrival, time-to-touch, MFE/MAE | [`results/monday_path.csv`](results/monday_path.csv) |
| Strategy expectancy by construction | [`results/strategy_expectancy.csv`](results/strategy_expectancy.csv) |
| Tolerance ladder — where ">90%" comes from | [`results/tolerance_ladder.csv`](results/tolerance_ladder.csv) |
| Effective independence of the replication | [`results/independence.csv`](results/independence.csv) |
| **Principal research report** | [`research/REPORT.md`](research/REPORT.md) |
| **Methods — data, sessions, DST, definitions, statistics, reproduction** | [`research/METHODS.md`](research/METHODS.md) |
| Full interpretation, by evidence status | [`research/current_findings.md`](research/current_findings.md) |
| What was tested and what happened | [`research/test_log.md`](research/test_log.md) |
| Provenance of the claim (what Hougaard actually said) | [`research/provenance.md`](research/provenance.md) |

Charts: [`charts/`](charts/) — conditional vs base rate, adjacent-weekday comparison, placebo,
year-by-year, time-to-touch, first arrival, strategy expectancy, payoff geometry.

## Current unresolved questions

- Effective sample size. Four US index series behave as roughly one. The evidence rests on 26
  years of time-series replication, not on four independent markets.
- We do **not** have the Dow Jones cash index, which is the only instrument Hougaard says he
  tested. NAS100/US500 CFDs and ES/NQ futures are the closest available proxies.
- The surviving US-index effect has no established mechanism. Weekend news flow, options
  positioning and Monday-open liquidity are candidates; none is tested here.
- The effect is measured on CFD/futures proxies; a cash-index test would settle whether the
  RTH result is a property of the index or of the derivative.

## Next analytical step

**None — the package is submitted for independent review.** Research is paused pending that
review. Candidates for a subsequent mandate, not yet begun: source a Dow cash series to test
Hougaard's exact instrument; test whether the US-index residual is monetisable in any
non-directional form; test entries inside the first 30 minutes of Monday, where most of the
measured movement occurs.
