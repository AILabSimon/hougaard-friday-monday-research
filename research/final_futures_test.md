# Final futures/CFD economic test — the post-open-cross construction

Mandated as the **last** futures/CFD economic test for this hypothesis. Proceeds from
`d98f27e`. Scope: one strategy family, 2–3 coarse risk constructions, no parameter grid, no
filters, no threshold optimisation.

## Classification

> **Statistical Monday range-expansion phenomenon validated; no simple mechanically tradeable
> futures/CFD edge identified.**

The futures/CFD research branch for this hypothesis is **closed**.

---

## The construction

The only remaining justified entry, taken verbatim from the Cycle-3 closure:

```
A.  Monday first trades to +0.25 ATR or −0.25 ATR from its open        → leg direction, t0
B.  Price subsequently trades back THROUGH the Monday open             → cross, tc
C.  Enter at the open level in the direction of the cross:
        up leg   → cross down through open → SHORT
        down leg → cross up   through open → LONG
```

Regime trigger `H_FRI < H_THU` unchanged. No other Thursday/Friday/Monday filter.

**Causality.** Everything the rule uses — leg direction, leg extreme, the open level, the time
of the cross — is known at `tc`. Entry is a stop order resting at the Monday open, so the fill
is at that level by construction and cannot be a phantom fill (the defect that invalidated
Cycle 2's D3a). One trade per Monday: the first cross only. No overlapping positions. Session
close marks out anything unresolved.

**Frequency.** The signal fires on **48.0%** of triggered Mondays under RTH and **58.1%** on
the broker day (control: 44.5% / 48.3%) — 223 and 276 trades, about **10.1 and 12.5 trades per
instrument-year**. Frequency was never the problem.

## Risk constructions (3, chosen from the observed geometry)

| | stop | target | rationale |
|---|---|---|---|
| **S1** | beyond the initial-leg extreme (structural; mean 0.40–0.43 ATR) | 2R | the leg extreme is the natural invalidation and is known at entry |
| **S2** | 0.5 ATR (coarse) | 1R / 2R / 3R | round number near the observed leg size |
| **S3** | 0.5 ATR | 2R, break-even at +1R | the one management variant, justified by MFE/MAE |

Costs: Dukascopy 2024 median spread (NAS100 3.42, US500 0.51) plus one tick slippage per side,
charged on entry and exit, converted to R by each construction's own risk — median 0.041–0.063 R
per trade.

---

## Result: nothing is positive

| session | construction | N | trades/yr | win% | mean R | median R | 95% CI on mean R | p vs 0 |
|---|---|---|---|---|---|---|---|---|
| RTH | S1 structural, 2R | 223 | 10.1 | 12.6 | −0.045 | −0.184 | −0.207 … +0.113 | 0.60 |
| RTH | S2a 0.5 ATR, 1R | 223 | 10.1 | 27.8 | −0.048 | −0.103 | −0.170 … +0.072 | 0.42 |
| RTH | S2b 0.5 ATR, 2R | 223 | 10.1 | 6.3 | −0.062 | −0.175 | −0.206 … +0.078 | 0.38 |
| RTH | S2c 0.5 ATR, 3R | 223 | 10.1 | 1.8 | −0.058 | −0.186 | −0.204 … +0.104 | 0.47 |
| RTH | S3 BE at +1R | 223 | 10.1 | 6.3 | −0.042 | −0.111 | −0.184 … +0.093 | 0.52 |
| BROKER | S1 structural, 2R | 276 | 12.5 | 17.4 | +0.041 | −0.250 | −0.107 … +0.198 | 0.65 |
| BROKER | S2a 0.5 ATR, 1R | 276 | 12.5 | 30.4 | −0.036 | −0.064 | −0.144 … +0.074 | 0.51 |
| BROKER | S2b 0.5 ATR, 2R | 276 | 12.5 | 11.6 | −0.000 | −0.155 | −0.151 … +0.141 | 0.94 |
| BROKER | S2c 0.5 ATR, 3R | 276 | 12.5 | 5.1 | +0.029 | −0.161 | −0.145 … +0.192 | 0.74 |
| BROKER | S3 BE at +1R | 276 | 12.5 | 11.6 | +0.031 | −0.107 | −0.116 … +0.175 | 0.72 |

**No construction has a triggered mean R significantly above zero.** Every median R is
negative. Max drawdown runs 13.8–24.9 R on ~10–12 trades per instrument-year. Positive in
3–6 years of 11. Development (2016-20) and validation (2021-26) means flip sign in *opposite*
directions between the two session definitions — no stability.

The trigger does make the construction less bad: on the broker day S1 returns +0.041 triggered
against −0.216 for the control, a difference of +0.257 R (p = 0.009). But the triggered arm
itself is indistinguishable from zero (p = 0.65). This is the same pattern as every previous
cycle — the condition carries information, and the information is not worth money.

---

## Why: the distinction the mandate asked for

**"Post-cross movement is statistically larger" is true. "A trade entered at the cross can
capture it" is false, and the reason is arithmetic.**

The 0.445 ATR figure from Cycle 3 is a **maximum favourable excursion**. This test
re-derived it independently and reproduced it exactly — 0.446 ATR — which validates both
passes. But an MFE is not a realisable profit, and from the *same* entry:

| RTH | favourable (MFE) | **adverse (MAE)** | favourable − adverse |
|---|---|---|---|
| triggered | 0.446 ATR | **0.385 ATR** | **+0.061 ATR** |
| control | 0.278 ATR | 0.297 ATR | −0.019 ATR |

Broker day: triggered 0.508 vs 0.462 → +0.046; control 0.323 vs 0.348 → −0.024.

The trigger adds 0.168 ATR of favourable excursion — and 0.088 ATR of adverse excursion
alongside it. What is left is a mean margin of **+0.06 ATR of unrealisable maxima**, against a
round-trip cost of roughly 0.02 ATR and a stop that must survive a median adverse excursion of
0.27–0.31 ATR. The favourable and adverse distributions overlap heavily. No simple mechanically tradeable futures/CFD edge was found in the tested constructions, and the observed MFE/MAE geometry provides no evidence-based justification for further parameter search.

The R-attainment ladder says the same thing against the programme's 2R+ objective:

| | reaches 1R | reaches 2R | reaches 3R |
|---|---|---|---|
| RTH (0.5 ATR stop) | 30.5% | **8.1%** | 3.1% |
| broker day (0.5 ATR stop) | 34.1% | **13.0%** | 5.4% |
| RTH (structural stop) | 47.1% | 14.3% | 6.7% |

Median MFE is 0.69–0.96 R against median MAE of 0.54–0.74 R. On this evidence the geometry does
not support the 2R+ objective,
and manufacturing a high win rate at sub-1R (S2a: 27.8% win at 1R) does not rescue it either —
that construction is also negative.

---

## Status

- **VALIDATED (F-V1)** — the signal is frequent, causal and cleanly mechanical: 48–58% of
  triggered Mondays, ~10–12.5 trades per instrument-year, entry price available by construction.
- **VALIDATED (F-V2)** — the Cycle-3 post-cross MFE of 0.445 ATR is reproduced exactly (0.446)
  by an independent implementation.
- **FALSIFIED (F-F1)** — no risk construction converts it. All ten cells' confidence intervals
  span zero; all ten medians are negative.
- **FALSIFIED (F-F2)** — the 2R+ objective is unreachable: 8–14% of signals ever see 2R.
- **FALSIFIED (F-F3)** — break-even management at +1R does not change the answer
  (RTH −0.042, broker +0.031, both n.s.).
- **EXPLAINED (F-E1)** — the extra favourable excursion is accompanied by nearly equal extra
  adverse excursion; the residual margin is ~0.06 ATR of maxima that an exit rule cannot
  realise. No simple mechanically tradeable futures/CFD edge was found in the tested constructions, and the observed MFE/MAE geometry provides no evidence-based justification for further parameter search.

## Known approximation

The S3 break-even variant is resolved with a 0.25 ATR adverse grid level as the proxy for
"price returns to entry after +1R", because the entry level's own first-touch time is
degenerate (the open is touched at minute 0 by definition). This makes the BE stop fire
slightly *later* than a true break-even stop would, i.e. mildly generous to the strategy. S3 is
still not positive, so the approximation does not affect the conclusion.

## What is NOT concluded

- Nothing here overturns the validated range-expansion phenomenon (Cycle 2 C2-V4, Cycle 3
  C3-V1). It remains statistically real and well replicated.
- This closes the **futures/CFD** branch only. Whether the phenomenon is expressible in an
  instrument that pays for range rather than direction is untested, and by mandate was not
  begun.
