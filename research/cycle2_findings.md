# Cycle 2 — can the surviving US-index effect be converted into a mechanical setup?

Proceeds from reviewed commit `97fca1c`. Central question:

> When Friday fails to reach or breach Thursday's high, is there a simple, mechanically
> identifiable change in **Monday's path** in US equity indices that can be exploited
> economically?

**Answer: no. Outcome B — STATISTICAL EFFECT ONLY.**

The Thursday→Friday condition is confirmed to carry real information about *where Monday
ends up relative to Friday's low*. It carries essentially none about *how Monday gets there*.
Under Hougaard's own session definition the effect is delivered by the weekend gap and is
already resolved at the opening bell.

Intraday evidence is NAS100/US500 only, 2016–2026 (ES/NQ are daily bars in this library).
All inference below is **week-clustered** so that instrument-observations sharing a Monday
move together.

---

## VALIDATED

### C2-V1 — The effect survives dependence-aware inference, with materially wider intervals
Week-cluster bootstrap (2 000 reps) on the controlled logistic coefficient.
Cluster SEs are only **1.22–1.27×** the Cycle-1 naive SEs — the inflation is modest because,
as Cycle 1 already found, the real replication is temporal, not cross-sectional.

| Sample | n | weeks | β ctrl | cluster 95% CI | p |
|---|---|---|---|---|---|
| Dukascopy NAS100+US500 RTH 2016-26 | 1036 | 528 | 0.420 | 0.071 – 0.767 | **0.012** |
| Dukascopy NAS100+US500 BROKER | 1076 | 538 | 0.442 | 0.087 – 0.785 | **0.015** |
| Yahoo ES+NQ daily 2000-26 | 2369 | 1194 | 0.360 | 0.118 – 0.596 | **0.003** |
| NAS100 alone (no cross-instrument dependence) | 527 | 527 | 0.453 | 0.048 – 0.856 | **0.028** |
| US500 alone | 509 | 509 | 0.387 | −0.026 – 0.789 | 0.062 |
| ES alone | 1188 | 1188 | 0.377 | 0.122 – 0.644 | **0.005** |
| NQ alone | 1181 | 1181 | 0.341 | 0.054 – 0.609 | **0.021** |
| DEV Yahoo 2000-2015 | 1405 | 712 | 0.407 | 0.109 – 0.731 | **0.009** |
| VAL Yahoo 2016-2026 | 964 | 482 | 0.344 | −0.023 – 0.724 | 0.071 |
| VAL Dukascopy RTH 2016-2026 | 1036 | 528 | 0.420 | 0.075 – 0.770 | **0.021** |
| CONTROL Yahoo Mon–Thu→next | 10481 | 1356 | 0.129 | 0.020 – 0.230 | 0.020 |

The decision does not change: the effect is real. But it is **weaker than Cycle 1's naive
z-values implied**. The frozen Yahoo validation window alone is p = 0.071, and by regime —
2000-07 p = 0.095, 2008-12 p = 0.345, 2013-19 p = 0.018, 2020-26 p = 0.260 — only one of four
sub-periods is individually significant, though all four point estimates are positive
(0.369 / 0.267 / 0.555 / 0.263). The honest reading is *a modest effect, consistently signed,
not established within any individual regime*. Evidence: `results/stageA_dependence.csv`,
`charts/c2_03_dependence.png`.

### C2-V2 — The effect is a LEVEL-POSITION effect, not a path effect
The decisive decomposition. Under RTH:

| | triggered | opposite | Δ | p (week-clustered) |
|---|---|---|---|---|
| Monday touches Friday's low | 0.465 | 0.293 | **+0.171** | <0.001 |
| …because Monday **opened below** Friday's range (level already gone) | 0.233 | 0.100 | **+0.133** | <0.001 |
| …because Monday **travelled** to it during the session | 0.231 | 0.193 | +0.038 | **0.225 — n.s.** |

**Roughly four-fifths of the conditional uplift under Hougaard's own definition is the level
being gone before the session starts.** The component a trader could act on shows no
significant conditional uplift at all.

Note the weekend gap *itself* is unchanged (gap/ATR: 0.026 vs 0.029, p = 0.92 — Cycle 1's
finding reconfirmed). What changes is the *starting position relative to Friday's low*: a
triggered Friday closes nearer its low, so the same-sized gap lands below it.

Under the 24-hour BROKER day the travelled component *is* significant (0.347 vs 0.215,
p < 0.001) — but under that construction "travelled" includes the Sunday-evening and Asian
sessions, i.e. the same overnight repricing, relocated from a gap into the interior of the
candle. It is the same phenomenon relabelled by candle construction, not a second effect.
Evidence: `results/stageC_path.csv`, `charts/c2_01_gap_vs_travelled.png`.

### C2-V3 — Conditional on the level still being reachable, almost nothing about Monday changes
Restricting to Mondays that open at or above Friday's low (n_trig = 358), only 2 of 16 path
measures differ at p < 0.05:

| survives | | | fails |
|---|---|---|---|
| touches Friday's low | +0.087 (0.014–0.161) p=0.017 | | low before high, p=0.17 |
| max down-excursion | +0.117 ATR (0.049–0.190) p<0.001 | | low touched by 30 min, p=0.41 |
| | | | low touched by 60 min, p=0.44 |
| | | | 15-min opening range breaks down, p=0.79 |
| | | | 30-min opening range breaks down, p=0.73 |
| | | | first 0.25-ATR move is down, p=0.29 |
| | | | net (down−up) excursion 30 / 60 min, p=0.90 / 0.73 |
| | | | Monday close − open, p=0.21 |
| | | | penetration past the low, p=0.17; bounce off it, p=0.90 |

So the trigger lengthens Monday's eventual downside *reach* by about a tenth of an ATR, and
does not change when, in what order, or in which direction Monday moves. There is no opening
behaviour to trade. Evidence: `results/stageC_conditional.csv`, `charts/c2_02_tradeable_state.png`.

### C2-V4 — No Thursday or Friday structural state explains the heterogeneity
Sixteen candidate variables (Thursday range, close location and direction; ATR-normalised
shortfall; when and how closely Friday approached Thursday's high; Friday range, close
location, body ratio, last-hour return, inside day, took-Thursday's-low) × 6 Monday outcomes,
week-clustered, Benjamini–Hochberg at 5%.

Raw association is strong for the usual suspects — Friday close-in-range (ρ = −0.37 on
"low before high"), when Friday made its high (ρ = −0.28), Friday's last-hour return
(ρ = −0.23). **But once Friday's close-in-range and range/ATR are controlled for, only one
variable survives in one session definition** (Friday body ratio → touch, BROKER only), and
it does not replicate under RTH. Thursday contributes nothing anywhere. Severity of the
failure contributes nothing (confirming Cycle 1 F6).

Two useful specifics: when Friday fails Thursday's high, Friday's closest approach to that
high **is** Friday's high, so those two variables are identical by construction — they are not
independent evidence. And the only variable that does add information is `open_to_Blow_atr`,
which is Monday's opening distance to Friday's low — a Monday-time variable included as a
machinery sanity check, not a Friday-close-time filter.

**No filter is justified.** Evidence: `results/stageB_structure.csv`, `results/stageB_partial.csv`.

### C2-V5 — No entry construction reaches positive expectancy after costs
Three families, 42 construction-cells, all week-clustered, all net of costs (Dukascopy 2024
median spread 3.42 pts NAS100 / 0.51 pts US500, plus one tick slippage per side).

| Family | Result (triggered, RTH, net) |
|---|---|
| **D1** short at Monday's open, ATR stop 0.5/0.75/1.0, target 0.5–2.0 ATR | mean R −0.07 to −0.16; 8 of 12 cells' CI excludes zero on the negative side |
| **D2** short on a limit 0.25/0.5 ATR above the open | mean R −0.02 to −0.10; none positive; fill rate 30–65% |
| **D3b** short the break of Friday's low (genuine intraday cross only) | mean R −0.16 to +0.04, every CI spans zero |

**Zero constructions have a triggered mean R significantly above zero.** No construction's
triggered-minus-opposite difference is significant either — the trigger adds nothing to the
economics of any of them. Evidence: `results/stageD_entries.csv`, `charts/c2_04_stageD.png`.

### C2-V6 — The headline effect is not carried by any single year
Year by year (RTH, all Mondays): positive in **11 of 11** years, 2016–2026. Worst
leave-one-year-out pooled uplift **+0.137** (against a full-sample +0.171). No year carries it.
Evidence: `results/stageE_year_by_year.csv`.

---

## PROVISIONAL

### C2-P1 — The tradeable component is period-dependent, and recent
Because Cycle 2's conclusion is negative, the adversarial check was run in the *rescue*
direction: is the tradeable component significant in any defensible subset? Eight pre-chosen
subsets, all reported so the multiplicity is visible.

| test | subset | n trig | Δ | 95% CI | p |
|---|---|---|---|---|---|
| travelled to Friday's low | all | 467 | +0.038 | −0.022 – 0.099 | 0.231 |
| | 2016-2020 | 215 | −0.018 | −0.105 – 0.074 | 0.685 |
| | **2021-2026** | 252 | **+0.085** | 0.005 – 0.168 | **0.041** |
| | **opens inside Friday's range** | 247 | **+0.095** | 0.002 – 0.185 | **0.049** |
| | NAS100 / US500 / lower half / high-range | | +0.054 / +0.021 / +0.005 / +0.070 | | 0.12 / 0.57 / 0.89 / 0.09 |
| tradeable-state touch rate | 2016-2020 | 162 | +0.031 | −0.079 – 0.135 | 0.588 |
| | **2021-2026** | 196 | **+0.135** | 0.038 – 0.231 | **0.008** |
| tradeable-state max down-reach | 2016-2020 | 162 | +0.066 ATR | −0.034 – 0.174 | 0.215 |
| | **2021-2026** | 196 | **+0.159 ATR** | 0.073 – 0.251 | **0.001** |

Two of eight subsets reach 5% on the travelled component, against ~0.4 expected by chance —
suggestive but not decisive. More materially, **the one surviving path feature (C2-V3) is
concentrated entirely in 2021–2026**: in 2016–2020 the tradeable-state touch uplift is +3.1pp
(p = 0.59) and the down-reach uplift +0.066 ATR (p = 0.21); in 2021–2026 they are +13.5pp
(p = 0.008) and +0.159 ATR (p = 0.001).

This cuts both ways and both should be stated. Against the finding: the tradeable path effect
is not present in the first half of the only intraday sample we have, so C2-V3 rests on six
years of two correlated instruments. For it: the effect is *strengthening*, not decaying,
which is not the signature of a decaying artefact — and it is the later period, so it cannot
be dismissed as stale.

It does not change the Cycle-2 verdict, because even in 2021–2026 nothing about Monday's
timing, direction, sequencing or opening-range behaviour changes, and no entry construction
was profitable. But it is the single most promising thread for a later cycle and must not be
quietly dropped. Evidence: `results/stageE_rescue.csv`.

---

## ARTEFACT / DEFECT

### C2-A1 — D3 "break of Friday's low" produced a large false positive via a phantom fill
Worth recording in full, because it is the exact failure mode the adversarial check exists for.

Entering on the *touch* of Friday's low looked excellent: mean R **+0.81** at a 0.25-ATR stop,
week-clustered CI 0.38–1.26, p < 0.001, and the triggered-vs-opposite difference significant
at p = 0.047. Win rate, however, was only 29% — inconsistent with that mean.

Cause: 23.3% of triggered Mondays **open below Friday's low**. For those, "entry at Friday's
low" is unfillable — Monday opens a median **0.306 ATR below** the level, which at a 0.25-ATR
stop is **1.23 R of free, unattainable profit per trade**. Those 109 observations carried a
mean R of +1.58 and were generating the entire result.

Restricted to Mondays where the cross is genuine (price opens at/above the low and trades down
through it, n = 108 fills), the same construction returns **−0.16 to +0.04 mean R with every
interval spanning zero**. The CSV retains both as `D3a INVALID (incl. gap-through)` and
`D3b short break of Friday low` so the contrast is auditable.

---

## FALSIFIED

- **C2-F1** — "Triggered Mondays rally first and then reverse to Friday's low" (entry family
  C/D). The `high_then_low` sequence occurs on 5.4% of triggered vs 2.6% of opposite Mondays
  — ~25 occurrences per instrument in ten years. Too rare to trade even if real.
- **C2-F2** — Opening-range break direction is unchanged. 15-min: 43.9% down triggered vs
  42.7% opposite. 30-min: 40.0% vs 41.8% — very slightly *less* bearish when triggered.
- **C2-F3** — Monday direction is unchanged: close−open p = 0.21, up-after-60-min p = 0.91,
  first 0.25-ATR move down p = 0.055 (all Mondays) and p = 0.29 (tradeable state).
- **C2-F4** — The trigger does not predict the weekend gap. Reconfirmed, p = 0.92.
- **C2-F5** — Thursday structure is uninformative on every measure tested.
- **C2-F6** — Deeper penetration past Friday's low after a touch (+0.23 ATR, p = 0.008 in the
  full sample) does **not** survive restriction to the tradeable state (+0.08, p = 0.17). It
  was a gap-through artefact.

---

## OPEN

- **C2-O1** — The effect is real but its mechanism is unidentified. It behaves like a
  *position* effect: a triggered Friday closes nearer its low, so the same overnight
  repricing lands below the level more often. Whether anything beyond that remains is
  unresolved; the residual after controlling for close-in-range says something does.
- **C2-O2** — Intraday evidence is two correlated CFD series over ten years. ES/NQ intraday
  history would roughly triple the independent time span for the path analysis.
- **C2-O3** — Does the 2021–2026 concentration of the tradeable path effect (C2-P1) reflect a
  regime change, or is it selection across eight subsets? A pre-registered test on 2027+ data,
  or on ES/NQ intraday history if it can be sourced, would settle it.
- **C2-O4** — Untested by design: non-directional constructions (volatility/range), and any
  use of the trigger as a filter on an unrelated strategy rather than as a signal. The
  +0.117 ATR down-reach with unchanged up-reach in the tradeable state is the only surviving
  hook.
- **C2-O5** — The Dow cash series is still absent (Cycle 1 O1).

---

## QUESTIONS FOR INDEPENDENT REVIEW

1. **Is the gap/travelled split the right decomposition?** We define "already gone" as Monday
   opening below Friday's low. A Monday that opens 0.01 ATR above the low and touches it in
   the first minute is counted as "travelled" but is economically identical to a gap-through.
   Would a tolerance band change the conclusion, or does the tradeable-state analysis
   (C2-V3) already answer that?
2. **Is the week the right cluster?** It makes NAS100 and US500 on the same Monday move
   together, which is the dependence Cycle 1 flagged. It does not address serial correlation
   across adjacent weeks. Is a block bootstrap over longer blocks warranted, and would it
   change a decision that already rests on p = 0.012–0.003?
3. **Regime instability.** Only 1 of 4 regime sub-periods is individually significant. Is
   "consistently signed, individually underpowered" the right characterisation, or should the
   effect be downgraded?
4. **Have we tested the right entry families?** Stage C gave us almost nothing to work with,
   so Stage D is deliberately thin. Is there a family implied by "+0.117 ATR of extra
   down-reach with no timing or direction change" that we have not considered?
5. **D3a.** We caught the phantom fill because the win rate was inconsistent with the mean R.
   Is there an equivalent leak in D1/D2 that we have not caught? Both enter at prices that
   are definitionally available (the open, or a limit above it), which we believe closes that
   route — but a second opinion is worth having.
