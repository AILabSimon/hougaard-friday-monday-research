# Current findings

> **Cycle 3 is complete (Issue #2).** This document is the Cycle-1 record and remains valid
> except where the blocks below say otherwise. The current interpretation lives in
> [`cycle3_findings.md`](cycle3_findings.md) (Cycle 3: Outcome 1 — range expansion real, no
> simple futures/CFD edge; stop futures/CFD exploitation of this hypothesis), which builds on
> [`cycle2_findings.md`](cycle2_findings.md) below.
>
> **Cycle 2 classification: 2 — statistical effect survives, no simple executable manifestation found.**
>
> What Cycle 2 changed in this document:
> - **V6 ("the behaviour is scale-invariant and symmetric, which argues against a Friday-specific
>   mechanism") is partially superseded.** That conclusion compared *raw* uplifts. Under the
>   geometry control with week-clustered inference, Friday→Monday is the only adjacent weekday
>   pair significant in all three datasets and has the largest coefficient in each
>   (C2-V3). Both statements are correct as stated; the raw comparison does not separate the
>   pairs, the controlled one does.
> - **V3 is confirmed under dependence-aware inference** but with wider intervals: cluster SEs
>   are 1.22–1.27× the naive ones used here, the frozen Yahoo validation window alone is
>   p = 0.071, and only 1 of 4 regime sub-periods is individually significant (C2-V1).
> - **V7's structural obstacles are refined.** "Monday reaches Friday's high more often than its
>   low" and "76% of touches occur in the first hour" are RTH-window statements. On the futures
>   session the level is travelled to rather than gapped through (C2-V2).
> - **A new validated finding supersedes nothing but outranks everything here in strength:**
>   the trigger predicts a **13–28% expansion in Monday's realised range**, significant in every
>   cut, both vendors, and in development and validation separately (C2-V4). It is two-sided,
>   which is why no directional construction in either cycle captured it.
> - Everything classified FALSIFIED or ARTEFACT below stands. Nothing has been reinstated.


Last updated: 2026-09-20. Primary data 2016–2026 (Dukascopy 1m, 12 instruments);
replication 2000–2026 (Yahoo daily futures ES/NQ/CL/GC/SI).

---

## VALIDATED

### V1 — The literal hypothesis is directionally true, and far weaker than claimed
`P(Monday low ≤ Friday low | Friday high < Thursday high)`, pooled:

| Session def | Asset group | N trig | hit rate | 95% CI | unconditional | opposite cond. | uplift vs opposite (95% CI) |
|---|---|---|---|---|---|---|---|
| RTH | US indices | 467 | **0.465** | 0.420–0.510 | 0.371 | 0.293 | **+0.171** (0.112–0.229) |
| RTH | FX | 1685 | 0.441 | 0.417–0.465 | 0.431 | 0.420 | +0.021 (−0.013–0.054) |
| RTH | Commodities | 767 | 0.459 | 0.424–0.494 | 0.425 | 0.393 | +0.066 (0.017–0.114) |
| BROKER | US indices | 475 | **0.497** | 0.452–0.542 | 0.382 | 0.291 | **+0.206** (0.147–0.262) |
| BROKER | FX | 1761 | 0.497 | 0.474–0.520 | 0.431 | 0.356 | +0.141 (0.107–0.174) |
| YF daily | ES+NQ 2000–2026 | 1096 | **0.550** | 0.521–0.579 | 0.447 | 0.358 | **+0.192** (0.152–0.231) |

No construction anywhere in this study reaches Hougaard's 90–95%. His later 62% figure is
approached only by the 24-hour futures bar (55%), not by his own stated RTH definition (46.5%).
Evidence: `results/core_results.csv`, `charts/01_conditional_vs_base.png`.

### V2 — Outside US equity indices, the effect is a geometric artefact
The trigger is a proxy for "Friday closed near its low". Controlling for
`(Friday close − Friday low) / ATR14` and `Friday range / ATR14` in a logistic model:

| Group | raw β (z) | controlled β (z) | controlled OR |
|---|---|---|---|
| FX, BROKER, Fri→Mon | 0.584 (8.19) | **−0.009 (−0.11)** | 0.99 |
| FX, RTH, Fri→Mon | 0.088 (1.25) | −0.116 (−1.58) | 0.89 |
| Commodities, BROKER | 0.529 (5.20) | −0.050 (−0.42) | 0.95 |
| Commodities, YF 2000–2026 | 0.512 (6.77) | 0.057 (0.68) | 1.06 |
| All 12 instruments, BROKER | 0.596 (11.65) | 0.063 (1.07) | 1.07 |

Independently confirmed by the path-shuffle placebo (V4). Evidence:
`results/controls.csv` (`control = placebo_path_shuffle`), `charts/03_placebo.png`.

### V3 — US equity indices carry a genuine residual, Friday→Monday specifically
Same control, same model:

| Dataset | scope | n | controlled β | z | OR |
|---|---|---|---|---|---|
| Dukascopy NAS100+US500 RTH | Fri→Mon | 1036 | 0.420 | 2.95 | 1.52 |
| Dukascopy NAS100+US500 BROKER | Fri→Mon | 1076 | 0.442 | 3.02 | 1.56 |
| Dukascopy NAS100+US500 UTC | Fri→Mon | 1076 | 0.439 | 3.04 | 1.55 |
| Dukascopy NAS100+US500 LONDON | Fri→Mon | 1076 | 0.441 | 3.04 | 1.55 |
| Yahoo ES+NQ daily 2000–2026 | Fri→Mon | 2369 | 0.360 | 3.66 | 1.43 |
| Dukascopy NAS100+US500 BROKER | **Mon–Thu→next** | 4424 | 0.091 | 1.28 | 1.10 |
| Yahoo ES+NQ daily | **Mon–Thu→next** | 10481 | 0.129 | 2.78 | 1.14 |

The coefficient is essentially **invariant to session definition** (0.42–0.44 across five
legitimate day constructions) and roughly **3× larger on Friday→Monday than on other weekday
pairs**. Controlling additionally for Monday's *open* does not remove it (β rises to 0.47–0.60),
and the trigger does **not** predict the weekend gap (p = 0.94 / 0.31 / 0.12), so it is not a
gap effect.

### V4 — It beats its placebo only for US equity indices
Placebo: keep Friday's geometry, give Monday a randomly drawn other Monday's normalised
behaviour (gap, up-excursion, down-excursion in ATR), resampled within instrument × year,
1 000 replications. This preserves every marginal distribution and destroys only the temporal
pairing. Reconstruction accuracy of the touch indicator ≥ 99.9%.

| Dataset | observed uplift | placebo mean ± sd | p |
|---|---|---|---|
| Dukascopy US indices RTH | 0.171 | 0.084 ± 0.028 | **0.001** |
| Dukascopy US indices BROKER | 0.206 | 0.114 ± 0.026 | **<0.001** |
| Yahoo ES+NQ | 0.192 | 0.108 ± 0.018 | **<0.001** |
| Dukascopy FX BROKER | 0.141 | 0.159 ± 0.014 | 0.91 — **fully explained** |
| Dukascopy US indices, Mon–Thu | 0.117 | 0.094 ± 0.013 | 0.056 |

A random-trigger control returns 0.000 ± 0.02–0.03 everywhere (machinery sanity check).

### V5 — The US-index effect survives a frozen out-of-sample test
Rule fixed on Yahoo ES+NQ 2000–2015, then applied unchanged:

| Sample | n | trigger hit | opposite | uplift (95% CI) | controlled β (z) |
|---|---|---|---|---|---|
| DEV — YF ES+NQ 2000–2015 | 1405 | 0.577 | 0.392 | +0.185 (0.133–0.236) | 0.408 (3.15) |
| VAL — YF ES+NQ 2016–2026 | 964 | 0.511 | 0.308 | +0.203 (0.141–0.263) | 0.343 (2.24) |
| VAL — Dukascopy NAS100+US500 RTH 2016–2026 (**different vendor, different instrument, different session**) | 1036 | 0.465 | 0.293 | +0.171 (0.112–0.229) | 0.420 (2.95) |

Year-by-year: positive uplift in **11/11** Dukascopy years and **26/27** Yahoo years
(only 2025 negative, −0.031). Evidence: `results/robustness.csv`,
`charts/04_year_by_year.png`.

### V6 — The behaviour is scale-invariant and symmetric, which argues against a Friday-specific mechanism
The identical "failed high → next bar seeks this bar's low" construction produces large raw
uplifts at every scale tested — Asia→London→NY session blocks (+0.06 to +0.18), weekly bars
(+0.08 to +0.22), and every adjacent weekday pair (+0.05 to +0.22). After the close-in-range
control, essentially all of these collapse to ≈0. The **mirror** condition ("failed low → next
bar seeks this bar's high") is equally strong or stronger everywhere (e.g. BROKER FX Friday:
down +0.143 vs up +0.186). A directional mechanism specific to Fridays is not what the data
looks like. Evidence: `results/controls.csv`, `charts/02_adjacent_weekday.png`.

### V7 — The simple trade constructions tested were not economically viable, and there are structural reasons why
This is a narrower claim than "the phenomenon is not tradeable", and the distinction matters.
What the evidence establishes is: (a) three families of construction, 20 variants, all shorts,
all failed; and (b) three structural features that explain why and that would obstruct most
similar constructions. It does **not** establish that no exploitation of the residual exists.

**The structural obstacles** (`results/monday_path.csv`):
- **First arrival.** On triggered Mondays (RTH, US indices, n = 467) Friday's **high** is
  reached 53.5% of the time and Friday's **low** 46.5%. The low is reached *first* in only
  41.1%; the high first in 48.8%. Given both are reached, the low comes first 46.8% of the
  time. The hypothesis names the less likely destination.
- **Timing.** Of the Mondays that do touch, **76.5% touch within 60 minutes** of the RTH open
  and 70% within 30; the median touch is at the open itself. Median MAE before the touch is
  0.07 ATR — the move is essentially already complete when it starts.
- **Payoff geometry.** Because the trigger selects Fridays that closed near their low, median
  reward:risk available at Friday's close (target Friday low, invalidation Friday high) is
  **0.75R** for triggered weeks against **2.60R** for non-triggered. The setup self-selects the
  worst-shaped trades. `charts/08_payoff_geometry.png`

**The constructions** (`results/strategy_expectancy.csv`, definitions in `METHODS.md` §7):

| | US indices RTH, triggered | 95% CI on mean R |
|---|---|---|
| E1 short Friday close → Friday low, stop Friday high | mean +0.26, **median −0.52**, trimmed mean −0.31 | (−0.05, +0.58) |
| E2 short Monday open → Friday low, stop Friday high | mean −0.115, median −0.49 | (−0.31, +0.08) |
| E3 short Monday open, 0.5 ATR stop / 0.5 ATR target | mean −0.096 | (−0.172, −0.020) |
| E3, 0.5/1.0 ATR (2R) | mean −0.054 | (−0.147, +0.038) |
| E3, 0.75/1.5 ATR (2R) | mean −0.030 | (−0.101, +0.041) |
| E3, 1.0/2.0 ATR (2R) | mean −0.039 | (−0.095, +0.018) |

**Stated precisely:** of 40 triggered construction-cells across all asset classes, 23 have a
negative point estimate and **11 have a 95% interval strictly below zero**; none of the 16
US-index triggered cells has an interval above zero, 14 of 16 have negative point estimates,
and 3 are significantly negative. So the correct statement is *no construction tested showed
positive expectancy, several were significantly negative, and the rest were indistinguishable
from zero* — not *every construction is a proven loser*.

The triggered constructions are consistently **less bad** than their non-triggered
counterparts, which is the conditional information of V3 showing up in P&L. It is not enough
to flip expectancy positive in anything tested.

**A defect in our own E1/E2 test, recorded rather than buried.** Their risk denominator
(`Friday high − entry`) is unbounded below: when Friday closes near its high it can be under
0.01 ATR, producing single-trade R values above 100 (max observed 1321). E1's *mean* R is
therefore dominated by a handful of observations and is not a usable expectancy estimate —
dropping the top 5% turns RTH FX from +0.55 to −0.17. Two cells (RTH FX and RTH commodities,
E1 triggered) show a mean R whose CI excludes zero on the positive side; both have negative
medians, both are outlier-driven, both sit in asset classes where the trigger carries **no**
information (V2), and in both the *non-triggered* version scores higher still. They are
artefacts of the normalisation, not edges. `mean_R_trim5`, `max_R` and `risk_atr_p05` are now
carried in the CSV so this is visible. E3 floors the stop distance and is the construction the
tradeability conclusion actually rests on.

### V8 — The ">90%" is reachable, but only at a tolerance that destroys the information
Hougaard's own loosest wording is *"the lows of Friday should be surpassed **or at least making
a double bottom**"*. Testing that literally — event = `Monday low ≤ Friday low + tol × ATR14`:

| tolerance (ATR14) | triggered | opposite | uplift |
|---|---|---|---|
| 0.00 (strict touch) | 0.550 | 0.358 | **+0.192** |
| 0.10 | 0.617 | 0.428 | +0.189 |
| 0.25 | 0.718 | 0.554 | +0.164 |
| 0.50 | 0.842 | 0.705 | +0.137 |
| **0.75** | **0.921** | **0.835** | +0.086 |
| 1.00 | 0.963 | 0.919 | +0.044 |

(Yahoo ES+NQ 2000–2026; Dukascopy RTH and BROKER give the same shape.)

**This is the single best explanation of the discrepancy between his numbers and ours.** A
"double bottom" tolerance of about three quarters of a daily ATR reproduces his >90% almost
exactly — but at that tolerance the *opposite* condition also scores 83.5%, so the
Thursday/Friday comparison has stopped carrying information. Eyeballing charts for "did Monday
come back near Friday's low" will produce >90% on almost any sample, whatever Thursday did.
Evidence: `results/tolerance_ladder.csv`, `charts/09_tolerance_ladder.png`.

### V9 — The replication is far less independent than the instrument count suggests
Outcome correlation on the *same* Monday:

| pair | n | corr(touch) | corr(trigger) | agreement |
|---|---|---|---|---|
| NAS100 vs US500 (Dukascopy RTH) | 508 | 0.753 | 0.770 | 88.4% |
| ES vs NQ (Yahoo daily) | 1175 | 0.760 | 0.681 | 88.1% |
| NAS100 CFD vs NQ futures (**cross-vendor**) | 479 | 0.793 | 0.782 | — |
| EURUSD vs GBPUSD | 552 | 0.510 | 0.587 | 76.1% |
| EURUSD vs USDJPY | 552 | −0.234 | −0.207 | 39.9% |

Four US-index series are **not** four independent tests — they are close to one bet on the US
equity complex, and the cross-vendor comparison is a data-quality check rather than
independent evidence. The genuine replication in this study is **temporal**
(2000–2015 → 2016–2026, V5), not cross-sectional. Pooled N of 2 369 should be read as an
effective N several times smaller. Evidence: `results/independence.csv`.

---

## PROVISIONAL

- **P0 — Whether the US-index residual can be monetised at all is OPEN, not settled.** V7
  establishes that three families of directional short failed and gives structural reasons.
  It does not establish that no construction works. Untested: anything non-directional, any
  entry inside the first 30 minutes of Monday (where most of the movement happens), options
  structures, and use of the trigger as a filter on an unrelated strategy rather than as a
  signal in itself.
- **P1 — The US-index residual is a downside-reach effect, not a return effect.** Conditional
  on the trigger, Monday's net excursion (down-from-open minus up-from-open) is 0.07 ATR more
  negative (p ≈ 0.08 RTH, 0.14 YF) but Monday's *close-to-open return* is not significantly
  different (p = 0.12–0.62). The trigger shifts how far Monday probes down, not where it ends.
  Whether that is exploitable in a non-directional form (range/volatility filter, option
  structure) has not been tested.
- **P2 — Event-definition ladder.** Stricter definitions preserve the *relative* uplift for US
  indices: touch 0.465 vs 0.293; penetration > 0.25 × Friday range 0.366 vs 0.199; close below
  0.248 vs 0.144; gap below 0.233 vs 0.100. The 2.3× relative on "gap below" deserves its own
  test but is based on 109 events.

---

## FALSIFIED

- **F1 — "Monday chases Friday's low" as a high-probability event (>90%, 95%, or even 62%) is
  not reproducible.** Maximum observed under any legitimate construction: 55.0% (Yahoo ES+NQ
  24-h bars). Under Hougaard's own stated RTH definition: 46.5%.
- **F2 — The effect in FX is not an effect.** Placebo p = 0.91; controlled β = −0.009.
- **F3 — The effect in commodities and metals is not an effect.** Controlled β ≈ −0.05 to +0.07
  in every dataset and session definition.
- **F4 — The weekly analogue is not an effect.** Raw uplift +0.08 to +0.22 and significant in
  all 12 instruments; controlled β ≈ 0 or negative in 8 of 12 and never significant.
- **F5 — The intraday session analogue is not an effect.** Raw uplift +0.06 to +0.18 in all 16
  asset × session-pair cells; controlled β significant in only 2 of 16 (both index cells,
  z ≈ 2.1).
- **F6 — Severity carries no information.** Monday's touch rate is flat across quintiles of
  `(Thursday high − Friday high)/ATR`: US indices RTH 0.436 / 0.484 / 0.419 / 0.505 / 0.479.
  A marginal miss behaves like a substantial failed attempt. `results/severity.csv`
- **F7 — Hougaard's variants do not matter.** `<` vs `≤` on the highs changes the hit rate by
  0.001. Allowing Tuesday fulfilment when Monday is a holiday (his "asterisk") changes it by
  0.002 and *reduces* the uplift from 0.171 to 0.160.
- **F8 — Every short construction tested (E1, E2, E3 — 20 variants) failed to show positive
  expectancy.** See V7 for the precise statement and for a defect in E1/E2's R-normalisation.

---

## ARTEFACT / DEFECT

- **A1 — Sunday/Saturday stub sessions.** Under `UTC` and `LONDON` day construction the FX week
  opens with a 2–3 hour Sunday stub, and DST mismatches create 1–11 Saturday stubs per
  instrument. These are excluded by a minimum-bar filter (≥300 bars for 24-h definitions,
  ≥200 for RTH) before any triple is formed. Without the filter they would corrupt the
  adjacent-session sequence. `src/build_triples.py`
- **A2 — US index CFD regime change.** Dukascopy's US index CFDs had no overnight session
  between 2015-04-18 and 2018-04-12. Our window starts 2016-01, so 2016–early 2018 index
  "BROKER/UTC days" are day-session-only. The RTH results are unaffected; the RTH and 24-h
  results agree closely (β 0.420 vs 0.442), which is itself evidence this is not driving
  anything.
- **A3 — Yahoo daily futures are continuous back-adjusted series.** Roll artefacts can create
  spurious highs/lows. They are used only as a *replication* set; the primary result does not
  depend on them, and the two sources agree.
- **No defect has invalidated a reported result to date.**

---

## OPEN

- **O1 — Dow Jones cash.** Hougaard's research is Dow-only, RTH-only. We have no DJIA series.
  NAS100/US500/ES/NQ are proxies. A third-party backtest reports 48.7% over 458 DJIA setups
  (2003–2025), i.e. no edge on his own index — consistent with our finding that the absolute
  rate is near a coin flip, though we cannot verify their construction.
- **O2 — Mechanism.** Why US equity indices and not FX, metals or oil? Weekend information
  flow, index options expiry/positioning, and Monday-open auction liquidity are untested
  candidates.
- **O3 — Spread/commission.** Measured, not modelled in depth: Dukascopy 2024 median spread is
  3.42 index points on NAS100 (median RTH ATR14 = 252) and 0.51 on US500 (ATR14 = 49), i.e.
  **≈2–3% of a 0.5-ATR stop** per round trip. Immaterial next to the −3% to −18% of R by which
  the constructions already fail. Costs only widen the negative.

---

## QUESTIONS FOR INDEPENDENT REVIEW

1. **Is the close-in-range control the right one?** We control for
   `(Friday close − Friday low)/ATR14` and `Friday range/ATR14`. The trigger and the control
   are correlated by construction (a failed high often implies a weak close). Is this
   over-controlling — i.e. are we partialling out part of the very phenomenon Hougaard
   describes? Our defence is the placebo (V4), which needs no regression assumptions and gives
   the same answer. Is that defence sound?
2. **Is the path-shuffle placebo valid?** We resample Monday's `(gap, up-excursion,
   down-excursion)` triplet jointly within instrument × year and re-derive the touch. Does
   within-year resampling leave enough residual dependence (volatility clustering) to bias the
   placebo distribution upward, which would make us *too conservative* for FX?
3. **Does the surviving US-index residual justify further work given V7?** The statistical
   effect is robust across two vendors, 26 years, five session definitions and a frozen
   validation split — but every directional construction loses money. Is there a construction
   we have not considered that exploits a downside-*reach* shift without taking a directional
   short?
4. **Adjacent-weekday comparison.** We treat "the same effect exists on other weekday pairs" as
   evidence against Friday being special. But the US-index Friday coefficient is ~3× the other
   days'. Is that difference itself the finding, and are we under-weighting it?
5. **Is the economic conclusion stated at the right strength?** We have narrowed it from "not
   tradeable" to "the 20 directional short constructions tested showed no positive expectancy,
   and three structural features explain why". Is that still too strong given that 29 of 40
   triggered cells have confidence intervals spanning zero? Conversely, is it too weak given
   the first-arrival and payoff-geometry evidence, which is structural rather than statistical?
6. **The E1 denominator defect.** We flagged it ourselves rather than dropping the test. Is
   reporting `mean_R_trim5` alongside `mean_R` the right treatment, or should E1/E2 be removed
   from the evidence base entirely as unidentified?
7. **Multiple testing.** Confirmatory tests were specified before results (HF-001…HF-008 in
   `test_log.md`). The asset-class split that produced the US-index finding was pre-specified
   as a robustness dimension, not chosen after seeing results — but there are 4 asset groups ×
   5 session definitions. Is the US-index result adequately protected by the frozen validation
   split and the second data source, or should it carry an explicit multiplicity discount?
