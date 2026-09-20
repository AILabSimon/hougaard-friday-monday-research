# The Hougaard Thursday → Friday → Monday hypothesis

**A falsification study.** 20 September 2026.

> *"If Friday's high does not reach or exceed Thursday's high, Monday will chase Friday's low."*

---

## 1. Executive conclusion

**The behaviour exists. It is roughly a quarter as strong as claimed, it is not specific to
Friday except in US equity indices, and it cannot be traded in the form implied.**

Across 12 instruments of Dukascopy 1-minute data (2016–2026) and five Yahoo daily futures
series (2000–2026), under five legitimate daily-session constructions, the conditional
probability that Monday trades to or through Friday's low after a failed Friday high is
**44–55%**, against an unconditional Monday rate of 37–45%. The uplift is real and highly
significant in aggregate. It is also, for almost every market tested, **a geometric artefact**:
a failed Friday high selects Fridays that closed near their low, and a nearby level is touched
more often. When that is controlled for — by regression, and independently by a placebo that
destroys the temporal pairing while preserving every marginal distribution — the effect
disappears in FX (placebo p = 0.91), in metals, in energy, in crypto, at the weekly scale, and
at the intraday-session scale.

It does **not** disappear in US equity indices on Friday → Monday. There it survives every
control, replicates on an independent vendor's data over 26 years, is invariant to session
definition, is positive in 11/11 and 26/27 individual years, and passes a frozen
development/validation split. That is a genuine conditional regularity, and to that extent
Hougaard is right about the market he trades.

But we could not turn it into money. Twenty directional short constructions were tested across
three families; none showed positive expectancy, eleven of forty triggered construction-cells
were significantly negative, and the rest were indistinguishable from zero. Three structural
features explain the failure: even in triggered weeks Monday reaches Friday's **high** more
often than its **low** (53.5% vs 46.5%) and reaches the low *first* only 41% of the time;
three quarters of the touches that do occur happen inside the first hour, most at the open;
and the trigger systematically selects the setups with the *worst* payoff geometry — median
reward-to-risk available at Friday's close is 0.75R against 2.60R for non-triggered Fridays.
That is a strong argument that this particular trade does not work. It is **not** a proof that
no exploitation of the residual exists, and this report does not make that claim.

Finally, the study offers a specific explanation for the gap between Hougaard's figures and
every systematic test including his own later one. His loosest wording — *"or at least making a
double bottom"* — corresponds to a tolerance of about 0.75 ATR around Friday's low. At that
tolerance the triggered rate is **92.1%**, matching his ">90%" almost exactly. At that same
tolerance the **opposite** condition scores **83.5%**. The number is real; the conditionality
is not.

**Final classification: PARTIALLY SUPPORTED.**
Statistically supported for US equity indices, Friday → Monday, at roughly a fifth of the
claimed magnitude. Not supported for any other market, scale or weekday. Not yet demonstrated
to provide an economically tradeable implementation — the directional short constructions
tested all failed, and the strategy search was deliberately not expanded beyond them.

---

## 2. What Hougaard actually claimed

Testing the right claim matters, and the popular restatement has drifted from the original.
From his own words (full sourcing in [`provenance.md`](provenance.md)):

- **Instrument: the Dow Jones cash index only.** *"if you're looking at the Dow Jones index
  where this research is done"*. He says he assumes the S&P behaves similarly; he did not test
  it. No Nasdaq or DAX test, despite trading both.
- **Session: US regular trading hours, 09:30–16:00 ET, overnight explicitly excluded.** Every
  third-party implementation we found uses 24-hour bars instead.
- **Event: a retest.** *"whatever low we made on the Friday will be seen again on Monday"*,
  and at its loosest *"surpassed or at least making a double bottom"*. He never says "close
  below" and never says "gap down" — the "gap down" phrasing originates in a third-party
  paraphrase and is materially stricter than what he said.
- **No other condition.** *"wherever you closed that Friday"* explicitly rules out a
  Friday-close filter. Holidays get an asterisk: he counts Tuesday fulfilment when Monday is a
  holiday.
- **His own numbers have moved:** 20/21 = 95% (N = 21, one year, 2019–20) → ">90%" → **62%**
  of 52 recently, at which point he describes it as *"more like a pattern rather than an entry
  technique"*.

We do not have a Dow cash series. NAS100 and US500 CFDs and ES/NQ futures are the closest
available proxies, and we test his RTH definition explicitly alongside four others.

---

## 3. Method

**Data.** Canonical Dukascopy 1-minute bid bars, UTC, bar labelled by open interval `[t, t+1m)`
— EURUSD, GBPUSD, AUDUSD, USDCAD, USDCHF, USDJPY, XAUUSD, XAGUSD, WTIUSD, NAS100, US500,
BTCUSD, 2016-01-03 → 2026-09-15. Replication set: Yahoo daily futures ES, NQ, CL, GC, SI,
2000-08 → 2026-09. Source data was read only; all derived sets live in the project folder.

**Session definitions.** `RTH` 09:30–16:00 America/New_York (Hougaard's); `BROKER` the
Dukascopy trading day (17:00 NY roll for FX, 18:00 NY for metals, WTI and index CFDs);
`NYFX` 17:00 NY roll; `UTC` calendar day; `LONDON` local calendar day, DST-aware. Sessions with
fewer than 300 bars (200 for RTH) are dropped, which removes the Sunday-evening stub and the
DST Saturday fragments that would otherwise corrupt the day sequence.

**Construction.** Everything downstream is a filter on one table of consecutive-session triples
`(A, B, C)` restricted to Monday–Friday sessions, so that `B` = Friday implies `C` = Monday, or
the next trading session when Monday is a holiday — which is exactly Hougaard's asterisk, and is
tested both ways. Trigger `B.high < A.high` (and `≤`). Events: touch `C.low ≤ B.low`;
penetration at 0.05R / 0.25R / 0.25 ATR; close below; gap below; directional excursion; and a
tolerance ladder `C.low ≤ B.low + tol × ATR14`.

**Controls, all pre-specified.** Unconditional base rate; the opposite condition; the mirror
condition (failed low → next session seeks the high); a wrong-direction placebo; the same
construction on every other adjacent weekday pair; the same construction at the weekly scale
and across Asia → London → New York session blocks; a random-trigger sanity check; and the
path-shuffle placebo described below.

**The mechanism control.** Logistic regression of the touch indicator on the trigger, with
`(B.close − B.low)/ATR14` and `B.range/ATR14` as controls and instrument fixed effects. This
asks: given how far Friday closed above its own low, does the Thursday comparison still tell
you anything?

**The placebo.** For each observation, keep Friday's geometry, but give Monday a randomly drawn
*other* Monday's normalised behaviour — its gap, up-excursion and down-excursion in ATR units —
resampled jointly within instrument and year, 1 000 replications. Every marginal distribution is
preserved; only the actual temporal pairing is destroyed. Reconstruction of the touch indicator
from the normalised quantities is ≥ 99.9% accurate, so the machinery is exact. If the observed
uplift sits inside the placebo distribution, the "effect" is level geometry and nothing else.

---

## 4. Results

### 4.1 The literal hypothesis

| Session | Group | N trig | hit rate | 95% CI | unconditional | opposite | uplift (95% CI) |
|---|---|---|---|---|---|---|---|
| RTH | US indices | 467 | 0.465 | 0.420–0.510 | 0.371 | 0.293 | +0.171 (0.112–0.229) |
| RTH | FX | 1685 | 0.441 | 0.417–0.465 | 0.431 | 0.420 | +0.021 (−0.013–0.054) |
| RTH | Commodities | 767 | 0.459 | 0.424–0.494 | 0.425 | 0.393 | +0.066 (0.017–0.114) |
| BROKER | US indices | 475 | 0.497 | 0.452–0.542 | 0.382 | 0.291 | +0.206 (0.147–0.262) |
| BROKER | FX | 1761 | 0.497 | 0.474–0.520 | 0.431 | 0.356 | +0.141 (0.107–0.174) |
| YF daily | ES + NQ, 2000–2026 | 1096 | 0.550 | 0.521–0.579 | 0.447 | 0.358 | +0.192 (0.152–0.231) |

Under Hougaard's own RTH definition the answer to "will Monday chase Friday's low" is **46.5%**
— slightly worse than a coin flip. No construction in this study reaches his 90%, 95%, or even
his revised 62%, except the 24-hour futures bar at 55%.

### 4.2 Symmetry and control — the effect contains no information beyond Friday's close

| Group / scope | raw β (z) | controlled β (z) | OR |
|---|---|---|---|
| FX, BROKER, Fri→Mon | 0.584 (8.19) | **−0.009 (−0.11)** | 0.99 |
| Commodities, BROKER, Fri→Mon | 0.529 (5.20) | −0.050 (−0.42) | 0.95 |
| Commodities, YF 2000–2026 | 0.512 (6.77) | 0.057 (0.68) | 1.06 |
| All 12 instruments, BROKER, Fri→Mon | 0.596 (11.65) | 0.063 (1.07) | 1.07 |
| **US indices, RTH, Fri→Mon** | 0.737 (5.64) | **0.420 (2.95)** | **1.52** |
| **US indices, BROKER, Fri→Mon** | 0.877 (6.83) | **0.442 (3.02)** | **1.56** |
| **US indices, YF daily, Fri→Mon** | 0.782 (9.27) | **0.360 (3.67)** | **1.43** |
| US indices, BROKER, Mon–Thu→next | 0.473 (7.70) | 0.091 (1.28) | 1.10 |

The mirror condition (failed low → next session seeks the high) is **equal or stronger than the
downside version at every weekday and in every asset class**. A mechanism that is specific to
Fridays and specific to the downside is not what the data looks like.

### 4.3 The placebo settles it

| Dataset | observed uplift | placebo mean ± sd | p |
|---|---|---|---|
| Dukascopy US indices RTH | 0.171 | 0.084 ± 0.028 | **0.001** |
| Dukascopy US indices BROKER | 0.206 | 0.114 ± 0.026 | **<0.001** |
| Yahoo ES+NQ 2000–2026 | 0.192 | 0.108 ± 0.018 | **<0.001** |
| **Dukascopy FX BROKER** | **0.141** | **0.159 ± 0.014** | **0.91 — fully explained** |
| Dukascopy US indices, Mon–Thu | 0.117 | 0.094 ± 0.013 | 0.056 |

Random-trigger control: 0.000 ± 0.02–0.03 everywhere.

### 4.4 Robustness of the surviving US-index effect

- **Session definition:** controlled β = 0.420 / 0.442 / 0.441 / 0.439 / 0.441 for
  RTH / BROKER / NYFX / UTC / LONDON. Essentially invariant. **Not** a candle-construction
  artefact.
- **Time:** positive uplift in 11/11 Dukascopy years and 26/27 Yahoo years (2025 the only
  negative, −0.031).
- **Frozen split:** developed on Yahoo ES+NQ 2000–2015 (β = 0.408), validated unchanged on
  Yahoo 2016–2026 (β = 0.343) and on Dukascopy NAS100/US500 RTH 2016–2026 (β = 0.420).
- **Severity does not matter:** touch rate is flat across quintiles of
  `(Thursday high − Friday high)/ATR` (0.436 / 0.484 / 0.419 / 0.505 / 0.479). A marginal miss
  behaves exactly like a large failed attempt, which argues against a "rejection" narrative.
- **Not a gap effect:** the trigger does not predict the weekend gap (p = 0.94 / 0.31 / 0.12),
  and controlling for Monday's open leaves the coefficient intact or larger.
- **Honest caveat:** NAS100/US500/ES/NQ outcomes correlate 0.75–0.79 on the same Monday. This
  is close to *one* bet on the US equity complex. The real replication here is temporal, not
  cross-sectional.

### 4.5 It is a general phenomenon, not a Friday phenomenon

The identical construction produces large raw uplifts on every adjacent weekday pair
(+0.05 to +0.22), at the weekly scale (+0.08 to +0.22, significant in 12/12 instruments), and
across Asia → London → New York session blocks (+0.06 to +0.18, significant in 16/16 cells).
After the close-in-range control, essentially all of them collapse to zero: weekly β ≈ 0 in
12/12; intraday β significant in only 2/16. The only asset class in which anything survives is
US equity indices. Within it, weekday by weekday (controlled β, 95% CI): Mon 0.32 (0.03–0.60),
Tue −0.25 (−0.53–0.03), Wed 0.04 (−0.25–0.32), Thu 0.29 (0.01–0.57), **Fri 0.50 (0.22–0.78)**.
Friday is the largest and the cleanest, but Monday and Thursday are marginally positive as
well; the pooled Mon–Thu coefficient (0.091, z = 1.28) is small only because Tuesday and
Wednesday offset them. So Friday is *the strongest* case of a US-equity-index effect, not the
*only* one.

So Outcome E of the original brief is the right description of the general case — this is a
failed-extreme/next-bar continuation *appearance* that is mostly tautological — with Outcome D
applying narrowly to US equity indices.

### 4.6 Monday's anatomy, and why the trades tested fail

- **First arrival.** On triggered Mondays (RTH, US indices) Friday's **high** is reached 53.5%
  of the time and Friday's **low** 46.5%. The low is reached *first* in only 41.1% of triggered
  Mondays. Given both are reached, the low comes first 46.8% of the time. The hypothesis names
  the less likely destination.
- **Timing.** Of Mondays that do touch, **70% touch within 30 minutes and 76% within an hour**;
  the median touch occurs at the open itself. Under the 24-hour definition the median touch
  falls in the Asian/European session. The information is consumed before New York opens.
- **Payoff geometry.** Because the trigger selects Fridays that closed near their low, the
  median reward:risk available at Friday's close (target Friday low, invalidation Friday high)
  is **0.75R** for triggered weeks versus **2.60R** for non-triggered weeks. The setup
  self-selects the worst-shaped trades.
- **Expectancy.** Short at Friday's close, TP Friday low, SL Friday high: 41.1% TP, 48.8% SL,
  at 0.75R, median R −0.52. Short at Monday's open with the same levels: mean −0.115R
  (95% CI −0.31 to +0.08). Short at Monday's open with ATR stops of 0.5/0.75/1.0 and targets of
  1R–3R: mean −0.03R to −0.10R triggered, −0.10R to −0.18R untriggered. Across all asset
  classes, 23 of 40 triggered cells have negative point estimates and 11 have 95% intervals
  strictly below zero; none has an interval above zero except two E1 cells that are artefacts
  (below). Costs add another 2–3% of a 0.5-ATR stop per round trip.
- **A defect in our own test, recorded not buried.** E1 and E2 divide profit by
  `Friday high − entry`, which is unbounded below; when Friday closes near its high the
  denominator can be under 0.01 ATR and a single trade returns R > 100 (max observed 1321).
  E1's *mean* R is therefore not a usable expectancy estimate — trimming the top 5% turns RTH
  FX from +0.55 to −0.17, and medians are negative in 15 of 16 cells. The two cells whose mean
  R is significantly positive (RTH FX and RTH commodities, triggered) sit in asset classes
  where the trigger carries no information at all, and their non-triggered counterparts score
  higher still. The tradeability conclusion rests on E3, which floors the stop distance, and on
  the structural evidence above.

The trigger is genuinely informative — triggered shorts lose less than untriggered shorts — but
being less bad at shorting a rising market is not an edge, and nothing tested converted the
information into positive expectancy.

### 4.7 The strongest possible reading of the claim, and why it fails too

Event = `Monday low ≤ Friday low + tol × ATR14` (Yahoo ES+NQ 2000–2026):

| tolerance | triggered | opposite | uplift |
|---|---|---|---|
| 0.00 | 0.550 | 0.358 | +0.192 |
| 0.25 | 0.718 | 0.554 | +0.164 |
| 0.50 | 0.842 | 0.705 | +0.137 |
| **0.75** | **0.921** | **0.835** | +0.086 |
| 1.00 | 0.963 | 0.919 | +0.044 |

His ">90%" is exactly reproducible at a "double bottom" tolerance of about 0.75 ATR. At that
tolerance the opposite condition scores 83.5%. Chart-eye assessment of "did Monday come back to
Friday's low" will return >90% on almost any sample regardless of what Thursday did. This is,
in our view, the most likely explanation of the original observation — and it is consistent with
him revising the figure down to 62% once he counted more carefully.

---

## 5. Failed ideas, recorded so they are not recycled

| Idea | Outcome |
|---|---|
| Friday/Monday is a special weekday pair | Only for US indices, and only ~3× the others; raw effect is identical on all pairs |
| The size of the high shortfall predicts the outcome | Flat across quintiles. No relationship |
| The effect is a weekend-gap phenomenon | Trigger does not predict the gap (p ≥ 0.12) |
| The effect works at the weekly scale | Vanishes under control in 12/12 instruments |
| The effect works across intraday sessions | Vanishes under control in 14/16 cells |
| FX / metals / oil / crypto versions | Fully reproduced by the placebo. Artefact |
| `≤` instead of `<` on the highs | Changes the hit rate by 0.001 |
| Hougaard's holiday asterisk (allow Tuesday) | *Reduces* the uplift, 0.171 → 0.160 |
| Short at Friday's close to Friday's low | 0.75R available, 41% hit, median R −0.52. Mean R unusable — see the E1 denominator defect |
| Short at Monday's open, structural stop | −0.115R |
| Short at Monday's open, fixed ATR stop, 1–3R | Negative point estimate in all 12 cells; significantly negative in 3 |

---

## 6. If you disagree with this conclusion

The places this study could be wrong, in order of how much they would change the answer:

1. **We do not have the Dow cash index.** Hougaard's research is Dow-only and RTH-only. If the
   Dow behaves unlike the Nasdaq-100, the S&P 500, ES and NQ, this study has not tested his
   claim. We consider that unlikely, and the one quantified third-party DJIA backtest we found
   reports 48.69% over 458 setups — no edge — which is if anything worse than what we measure.
2. **The close-in-range control could be over-controlling.** The trigger and the control are
   correlated by construction. This is why the placebo exists: it needs no regression
   assumptions, and it gives the same answer.
3. **Session and DST handling.** All five constructions are DST-aware and built from the same
   1-minute UTC bars; the stub-session filter is documented; the five definitions agree to
   within β = 0.02 on the surviving result. A timezone error would not survive that agreement.
4. **Effective sample size.** The four US index series are ≈0.75 correlated. Read the pooled N
   as substantially smaller than it appears.

5. **The strategy search was narrow, deliberately.** Three families of directional short, 20
   variants. The brief's instruction was not to expand the search in order to defend a negative,
   so we did not. Nothing here rules out a non-directional construction, an entry inside
   Monday's first 30 minutes, or use of the trigger as a filter on some other strategy.

If none of those overturns it, the conclusion stands: the behaviour is real in US equity
indices, roughly a fifth as strong as advertised, not specific to Friday in any other market,
and not exploitable by any of the simple Monday-short constructions tested here.
