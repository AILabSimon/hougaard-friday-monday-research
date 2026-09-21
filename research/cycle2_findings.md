# Cycle 2 — Thursday→Friday failure and the Monday executable path

Mandate: GitHub Issue #1. Starting commit `97fca1c` (confirmed as `origin/main` HEAD at start).
Sequence preserved throughout: **Thursday high → Friday fails it → Friday structure/close →
weekend/Monday open → Monday path → Friday-level interaction → possible trade.**

## Classification: **2 — statistical effect survives, no simple executable manifestation found**

> **Accepted by independent review** (Issue #1, 2026-09-21). The review's follow-up question —
> is the expansion same-session two-sided or cross-day averaging of one-sided expansion? — is
> answered in [`cycle3_closure.md`](cycle3_closure.md): shape-preserving proportional scaling,
> both sides expanding, ratio unchanged.

The Thursday→Friday condition survives dependence-aware confirmation, it is the strongest of
the five weekday pairs, and it carries a large, robust, twice-validated signal about Monday.
But that signal is about **how far Monday reaches in both directions**, not about which way it
goes. Four entry families, 60 construction-cells, none reached positive expectancy after costs.

---

## Corrections to the Cycle-2 interim record (recorded, not silently amended)

1. **ES/NQ intraday exists but is one month long.** The library holds 1m/5m/15m/1h for ES, NQ
   and the micros, but Yahoo serves only ~30 days of 1-minute history: 2026-08-19 → 2026-09-17,
   ≈4 Mondays. Minute-level path work on ES/NQ is therefore impossible, and an earlier
   statement that "ES/NQ are daily bars in this library" was wrong in detail though right in
   consequence. Daily-resolution decomposition on ES/NQ **is** possible and is reported below.
2. **"The effect is the weekend gap, not Monday's path" was an RTH-only statement and was
   wrongly generalised.** It is session-window dependent — see C2-V2. On the mandate's primary
   instruments the travelled component dominates.
3. **Friday was under-credited.** Under identical week-clustered treatment Friday→Monday is the
   only weekday pair significant in all three datasets, and has the largest coefficient in each.

---

## VALIDATED

### C2-V1 — Survives dependence-aware confirmation, with wider intervals
Week-cluster bootstrap (2 000 reps; the cluster is the calendar week, so NAS100 and US500 on
the same Monday move together). Cluster SEs are **1.22–1.27×** the naive SEs.

| Sample | n | weeks | β ctrl | cluster 95% CI | p |
|---|---|---|---|---|---|
| Dukascopy NAS100+US500 RTH | 1036 | 528 | 0.420 | 0.071 – 0.767 | **0.012** |
| Dukascopy NAS100+US500 BROKER | 1076 | 538 | 0.442 | 0.087 – 0.785 | **0.015** |
| Yahoo ES+NQ daily 2000-2026 | 2369 | 1194 | 0.360 | 0.118 – 0.596 | **0.003** |
| NAS100 alone | 527 | 527 | 0.453 | 0.048 – 0.856 | **0.028** |
| US500 alone | 509 | 509 | 0.387 | −0.026 – 0.789 | 0.062 |
| ES alone | 1188 | 1188 | 0.377 | 0.122 – 0.644 | **0.005** |
| NQ alone | 1181 | 1181 | 0.341 | 0.054 – 0.609 | **0.021** |
| DEV Yahoo 2000-2015 | 1405 | 712 | 0.407 | 0.109 – 0.731 | **0.009** |
| VAL Yahoo 2016-2026 | 964 | 482 | 0.344 | −0.023 – 0.724 | 0.071 |
| VAL Dukascopy RTH 2016-2026 | 1036 | 528 | 0.420 | 0.075 – 0.770 | **0.021** |

Caveat kept in view: the frozen Yahoo validation window alone is p = 0.071, and by regime only
1 of 4 sub-periods is individually significant (2000-07 p = 0.095, 2008-12 p = 0.345,
2013-19 p = 0.018, 2020-26 p = 0.260), though all four point estimates are positive.
Evidence: `results/stageA_dependence.csv`, `charts/c2_03_dependence.png`.

### C2-V2 — Gap or travel is decided by the session window, not by the market
The decisive decomposition, now run on all three datasets:

| dataset | total uplift | already gone at the open | travelled to during the session |
|---|---|---|---|
| NAS100/US500 **RTH** (6.5h cash window) | +0.171 | **+0.133** (p<0.001) | +0.038 (**p = 0.231**) |
| NAS100/US500 **broker day** (23h) | +0.206 | +0.073 (p<0.001) | **+0.133** (p<0.001) |
| **ES + NQ futures day, 2000-2026** | +0.192 | +0.052 (p<0.001) | **+0.140** (p<0.001) |

The weekend gap *itself* is unchanged in every dataset (gap/ATR p = 0.95 / 0.43 / 0.17). What
changes is the starting position relative to Friday's low, because a triggered Friday closes
nearer its low.

So: a trader restricted to New York cash hours mostly finds the level already gone at the bell.
A futures or CFD trader whose session opens Sunday evening sees most of the same move happen
while the market is open. Same phenomenon, different window. On ES/NQ — the mandate's primary
instruments, 26 years — the travelled component is 73% of the total and highly significant.
Evidence: `results/c2_decomposition.csv`, `charts/c2_05_decomposition_by_session.png`.

### C2-V3 — Friday→Monday is the strongest weekday pair under identical treatment
Same clustered logit, every adjacent pair:

| day whose high failed | NAS100/US500 RTH | NAS100/US500 broker | ES+NQ daily |
|---|---|---|---|
| Mon | 0.05 (p=0.78) | 0.32 (p=0.084) | 0.26 (**p=0.025**) |
| Tue | 0.16 (p=0.34) | −0.25 (p=0.16) | −0.08 (p=0.44) |
| Wed | 0.18 (p=0.27) | 0.04 (p=0.81) | 0.14 (p=0.20) |
| Thu | 0.24 (p=0.16) | 0.29 (p=0.12) | 0.22 (p=0.051) |
| **Fri** | **0.39 (p=0.017)** | **0.50 (p=0.003)** | **0.36 (p=0.003)** |

Friday is the only pair significant in all three, and the largest in each (OR 1.48 / 1.65 /
1.43). Cycle 1's "Friday is not special" applied to *raw* uplifts; with the geometry control
and clustered inference, it is. Evidence: `results/c2_weekday_pairs.csv`, `charts/c2_06_weekday_pairs.png`.

### C2-V4 — The surviving mechanism is RANGE EXPANSION, and it is two-sided
This is the substantive Cycle-2 discovery. Monday's total excursion (down + up, ATR units),
regressed on the trigger with Friday's range/ATR, Friday's close-in-range and instrument fixed
effects, week-clustered:

| sample | n | β (ATR) | 95% CI | p | uplift |
|---|---|---|---|---|---|
| NAS100/US500 RTH | 1036 | 0.176 | 0.105 – 0.244 | <0.001 | **+24%** |
| NAS100/US500 RTH, tradeable state | 870 | 0.134 | 0.067 – 0.205 | 0.001 | +19% |
| NAS100/US500 broker day | 1076 | 0.230 | 0.158 – 0.299 | <0.001 | **+28%** |
| NAS100/US500 broker, tradeable | 959 | 0.208 | 0.136 – 0.287 | <0.001 | +26% |
| **ES+NQ daily 2000-2026** | 2369 | 0.160 | 0.115 – 0.207 | <0.001 | **+18%** |
| ES+NQ **DEV 2000-2015** | 1405 | 0.121 | 0.064 – 0.179 | <0.001 | +13% |
| ES+NQ **VAL 2016-2026** | 964 | 0.218 | 0.140 – 0.294 | <0.001 | +25% |
| ES alone / NQ alone | 1188 / 1181 | 0.171 / 0.150 | both exclude 0 | <0.001 | +20% / +17% |

Significant in **every** cut, in both vendors, in each instrument alone, in development and in
validation, before and after restricting to the tradeable state. When Friday fails Thursday's
high, Monday's realised range is **13–28% larger** than otherwise, over and above what Friday's
own range and close location predict.

It is symmetric: in the tradeable state on the broker day, max down-excursion +0.149 ATR
(p = 0.003) **and** max up-excursion +0.097 ATR (p = 0.001). Evidence:
`results/c2_range_effect.csv`, `results/c2_range_expansion.csv`, `charts/c2_07_range_expansion.png`.

### C2-V5 — Direction, return and opening-range behaviour are unchanged
In the tradeable state, across both session definitions: Monday close − open p = 0.21–0.56;
up-after-60-min p = 0.13–0.91; first 0.25-ATR move down p = 0.29–0.40; 15-min opening range
breaks down p = 0.23–0.79; 30-min opening range breaks down p = 0.08–0.73 — and where it moves
at all it moves the *wrong* way (broker day, opens-inside subset: 38.8% down vs 48.8%,
p = 0.020, i.e. triggered Mondays break the opening range downward *less* often).

The one asymmetry that does appear on the broker day is timing: Friday's low touched within
30 min +5.8pp and within 60 min +6.3pp (both p < 0.001) — but from a low base (8.2% vs 2.3%),
and it does not appear under RTH (p = 0.41 / 0.44).
Evidence: `results/stageC_path.csv`, `results/stageC_conditional.csv`, `charts/c2_02_tradeable_state.png`.

### C2-V6 — No Thursday or Friday structural state explains the heterogeneity
Sixteen mechanical variables × six Monday outcomes, week-clustered, Benjamini–Hochberg 5%.
Raw association is strong for Friday close-in-range (ρ = −0.37), when Friday made its high
(ρ = −0.28) and Friday's last-hour return (ρ = −0.23). After controlling for close-in-range and
range/ATR, **1 of 168 survives** and fails to replicate across session definitions. Thursday
contributes nothing on any measure; the ATR-normalised shortfall contributes nothing
(confirming Cycle 1 F6). Note that when Friday fails Thursday's high, Friday's closest approach
to that high *is* Friday's high — those two variables are identical by construction.
**No filter is justified, and none was built.** Evidence: `results/stageB_structure.csv`,
`results/stageB_partial.csv`.

### C2-V7 — No entry construction reaches positive expectancy after costs
Four families, 60 construction-cells, all week-clustered, all net of costs (Dukascopy 2024
median spread 3.42 pts NAS100 / 0.51 pts US500 plus one tick slippage per side).

| family | definition | result (triggered, net) |
|---|---|---|
| **D1** | short at Monday's open; stop 0.5/0.75/1.0 ATR; target 0.5–2.0 ATR | mean R −0.05 to −0.16; 8 of 12 cells' CI excludes zero negatively |
| **D2** | short on a limit 0.25/0.5 ATR above the open | mean R −0.02 to −0.10; fill rate 30–65%; none positive |
| **D3b** | short the break of Friday's low (genuine intraday crosses only) | mean R −0.16 to +0.04; every CI spans zero |
| **D4** | OCO straddle at the open, ±0.25/0.5 ATR, stop = opposite level, target 0.5–1.5 ATR | mean R −0.084 to +0.013; every CI spans zero; long share 54–56% |

**Zero constructions have a triggered mean R significantly above zero, and no construction's
triggered-minus-control difference is significant.** The 2R+ objective is never approached:
median MFE 0.32–0.80 R, median MAE 0.36–1.25 R — adverse excursion exceeds favourable in most
cells — with 2R attainment 2–15% and 3R attainment 0–8%. Positive in 3–6 of 11 years.
Evidence: `results/stageD_entries.csv`, `results/stageD4_nondirectional.csv`,
`results/c2_economics_full.csv`, `charts/c2_04_stageD.png`.

**Why D4 fails despite C2-V4 being true:** a breakout monetises range only when the move is
directional and sustained. The extra range is distributed on *both* sides, so the wider
Monday stops out the straddle's losing leg about as often as it pays the winning one.

---

## PROVISIONAL

### C2-P1 — The tradeable-state touch effect is concentrated in 2021–2026
Adversarial check run in the *rescue* direction, eight pre-chosen subsets, all reported.
Under RTH, the tradeable-state touch uplift is +3.1pp (p = 0.59) in 2016–2020 and +13.5pp
(p = 0.008) in 2021–2026; the down-reach uplift +0.066 ATR (p = 0.21) versus +0.159 ATR
(p = 0.001). Two of eight subsets reach 5% on the travelled component against ~0.4 expected.
The effect is strengthening rather than decaying, which is not the signature of a decaying
artefact — but it rests on six years of two correlated series. Note this does **not** apply to
C2-V4, which is significant in DEV and VAL separately and in both vendors.
Evidence: `results/stageE_rescue.csv`.

---

## ARTEFACT / DEFECT

### C2-A1 — D3 produced a large false positive via a phantom fill
Entering on the *touch* of Friday's low looked excellent: mean R **+0.81** at a 0.25-ATR stop,
cluster CI 0.38–1.26, p < 0.001. Win rate was only 29% — inconsistent with that mean.

Cause: 23.3% of triggered Mondays open *below* Friday's low, where "entry at Friday's low" is
unfillable. Monday opens a median **0.306 ATR below** the level — at a 0.25-ATR stop, **1.23 R
of free, unattainable profit per trade**. Those 109 observations carried mean R +1.58 and
generated the whole result. Restricted to genuine intraday crosses (n = 108 fills), the same
construction returns **−0.16 to +0.04 with every interval spanning zero**. Both versions are
retained in the CSV as `D3a INVALID (incl. gap-through)` and `D3b` so the contrast is auditable.

---

## FALSIFIED

- **C2-F1** — "Triggered Mondays rally first, then reverse to Friday's low." The `high_then_low`
  sequence is 5.4% of triggered vs 2.6% of opposite Mondays — ~25 events per instrument in ten
  years. Too rare to trade.
- **C2-F2** — Opening-range break direction is unchanged, and where it moves it moves against
  the hypothesis (C2-V5).
- **C2-F3** — Monday's direction and return are unchanged.
- **C2-F4** — The trigger does not predict the weekend gap. Reconfirmed in all three datasets.
- **C2-F5** — Thursday structure is uninformative on every measure tested.
- **C2-F6** — Deeper penetration past Friday's low after a touch (+0.23 ATR, p = 0.008 in the
  full sample) does not survive restriction to the tradeable state under RTH (+0.08, p = 0.17).
  It survives on the broker day (+0.175, p = 0.009) but does not convert (D3b).
- **C2-F7** — The non-directional straddle (D4). Range expansion is real; a breakout does not
  capture it.

---

## OPEN

- **C2-O1** — The range-expansion effect (C2-V4) is the strongest surviving result in the whole
  programme and has **not** been tested in the instrument class that naturally expresses it.
  A conditional +13–28% range with no directional bias is an options statement, not a futures
  statement. Nothing in this library prices options, so this is untestable here.
- **C2-O2** — Mechanism unidentified. The effect behaves like conditional volatility: a failed
  Friday high marks an unresolved test of a reference level, and unresolved tests resolve
  violently. Untested.
- **C2-O3** — ES/NQ intraday history is one month. Sourcing real ES/NQ minute history would
  roughly triple the independent span available for path work and let Stage D be run on the
  mandate's primary instruments directly.
- **C2-O4** — Whether the trigger is useful as a *filter* on an unrelated Monday strategy
  (position sizing, stop width, session selection) rather than as a signal. Not tested.
- **C2-O5** — The Dow cash series is still absent (Cycle 1 O1).

---

## QUESTIONS FOR INDEPENDENT REVIEW

1. **Is C2-V4 the right place to take this?** A conditional range expansion that is significant
   in every cut, both vendors, DEV and VAL separately, is a better-evidenced finding than
   anything in Cycle 1 — but it is not tradeable with the instruments in this library. Is
   sourcing options data a sanctioned direction, or is that out of scope?
2. **Is the session-window framing of C2-V2 correct?** We argue the gap/travel split is an
   artefact of the observation window rather than two different phenomena. The counter-argument
   is that an RTH trader genuinely cannot trade the overnight move, so for *that* trader the
   gap interpretation is the operative one. Which framing should the record carry?
3. **Does C2-V3 overturn Cycle 1's "Friday is not special"?** Cycle 1 compared raw uplifts and
   concluded not special. Cycle 2 compares controlled coefficients under clustered inference and
   finds Friday the only pair significant in all three datasets. We believe both are correct as
   stated; is that reconciliation acceptable?
4. **Is D4 the right non-directional test?** An OCO straddle is the only non-directional
   construction expressible with futures/CFD data. Its failure does not show the range effect is
   unexploitable — only that a breakout does not capture it. Is there a better futures-expressible
   test we have missed?
5. **C2-A1** — we caught the phantom fill because the win rate was inconsistent with the mean R.
   D1/D2/D4 enter at prices definitionally available (the open, a limit above it, a stop beyond
   it), which we believe closes that route. A second opinion on whether any equivalent leak
   remains would be valuable.
