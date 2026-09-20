# Current findings

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

### V7 — The phenomenon is not tradeable in the form implied
- **First arrival.** On triggered Mondays (RTH, US indices) Monday reaches Friday's **high**
  53.5% of the time and Friday's **low** 46.5%. Low-first only 41.1%. Given both are reached,
  the low comes first in 46.8% of cases — a coin flip. `charts/06_first_arrival.png`
- **Timing.** Of the Mondays that do touch, **76% touch within the first 60 minutes** and 70%
  within 30 minutes; the median touch occurs at the very open. The information is consumed
  before it can be acted on. `charts/05_time_to_touch.png`
- **Payoff geometry.** Because the trigger selects Fridays that closed near their low, the
  median reward:risk available at Friday's close (target = Friday low, invalidation = Friday
  high) is only **0.75R** for triggered weeks, against 2.60R for non-triggered weeks. The
  trigger systematically picks the worst-shaped trades. `charts/08_payoff_geometry.png`
- **Expectancy.** Shorting at Friday's close with TP = Friday low and SL = Friday high wins
  41.1% and loses 48.8% (RTH, US indices). Every fixed-R construction (stop 0.5/0.75/1.0 ATR,
  target 1–3R) shorting Monday's open has **negative mean R before costs**, triggered
  (−0.03 to −0.10) or not (−0.10 to −0.18). Triggered is *less bad* than non-triggered — the
  conditional information is real — but "less bad at shorting an uptrend" is not an edge.
  `results/strategy_expectancy.csv`, `charts/07_strategy_expectancy.png`


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
- **F8 — Shorting the setup is not profitable.** See V7.

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
5. **Multiple testing.** Confirmatory tests were specified before results (HF-001…HF-008 in
   `test_log.md`). The asset-class split that produced the US-index finding was pre-specified
   as a robustness dimension, not chosen after seeing results — but there are 4 asset groups ×
   5 session definitions. Is the US-index result adequately protected by the frozen validation
   split and the second data source, or should it carry an explicit multiplicity discount?
