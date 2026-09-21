# Cycle 3 closure — same-Monday joint excursion topology

Requested by the independent review of Cycle 2 (Issue #1 comment, 2026-09-21) and by Issue #2
Stage A. The GitHub Actions runner that executed Issue #2 could not reach the per-Monday
derived parquet or the 1-minute store — both are gitignored and local — so it flagged the
central Stage A question **OPEN**. This is that measurement, run locally against the data the
runner could not see. Scope is deliberately narrow: the closure experiment only. No new
constructions, no strategy work, no options data, no earlier work repeated.

Data: NAS100 + US500, 1-minute, 2016-2026, RTH and broker day, 2 112 Mondays
(467/475 triggered). Uncertainty is week-clustered throughout, as in Cycle 2.
New derived set: `c3_topology.parquet` (132 columns), built by `src/cycle3_topology.py`.

---

## The question

> Is the validated Monday range expansion genuinely **two-sided within the same session**, or is
> it cross-day averaging of random **one-sided** expansion?

It has a decisive local test. If expansion were one-sided in a random direction, the **larger**
side would grow and the **smaller** side would not, so the smaller/larger ratio would fall. If
it is genuinely two-sided, the smaller side grows too and the ratio holds.

## Answer — proportional scaling of the whole excursion envelope

| measure | RTH trig | RTH opp | Δ | p | BROKER Δ | p |
|---|---|---|---|---|---|---|
| larger-side excursion | 0.743 | 0.567 | **+0.176** | <0.001 | **+0.235** | <0.001 |
| **smaller-side excursion** | 0.196 | 0.152 | **+0.043** | **0.001** | **+0.055** | **<0.001** |
| smaller / larger ratio | 0.348 | 0.339 | +0.008 | **0.690** | −0.003 | **0.907** |
| total range | 0.939 | 0.720 | +0.220 | <0.001 | +0.290 | <0.001 |

**Both sides expand and the ratio is unchanged.** So it is neither of the two hypotheses the
review posed. It is not one-sided random expansion — the smaller side grows, significantly, in
both session definitions. It is not a shift toward balanced two-sidedness either — the ratio
would have risen. The trigger scales the entire excursion envelope up by roughly a quarter,
preserving its shape.

The shape it preserves is strongly one-side-dominant: the smaller side is about **35%** of the
larger, in triggered and control weeks alike.

## Same-session two-sided threshold crossing

| threshold | P(both sides), RTH trig | RTH opp | Δ | p |
|---|---|---|---|---|
| 0.25 ATR | 0.285 | 0.169 | **+0.116** | <0.001 |
| 0.50 ATR | 0.051 | 0.021 | **+0.030** | 0.039 |
| 0.75 ATR | 0.015 | 0.004 | +0.012 | 0.109 |
| 1.00 ATR | 0.004 | 0.000 | +0.004 | 0.263 |

Broker day is the same shape and slightly stronger (0.25 ATR: +0.153, p<0.001; 0.50: +0.042,
p=0.004). Same-session two-sided expansion is real and measurable at 0.25 ATR, rare at 0.5 ATR,
and effectively absent at 0.75 ATR and beyond.

### Joint versus independence
`P(both) ÷ [P(up)·P(down)]` — 1.0 would mean the two sides are independent:

| threshold | RTH triggered | RTH opposite | BROKER triggered | BROKER opposite |
|---|---|---|---|---|
| 0.25 | 0.78 | 0.62 | 0.80 | 0.66 |
| 0.50 | 0.43 | 0.33 | 0.48 | 0.35 |
| 0.75 | 0.45 | 0.30 | 0.49 | 0.33 |

Every value is well below 1: on any given Monday the two sides are strongly negatively
dependent, which is simply the statement that most days trend. Triggered Mondays sit
**closer to independence** than control Mondays at every threshold — they are relatively less
one-sided — but they remain a long way from genuinely two-sided.

## Direction is not predictable

| measure | RTH Δ | p | BROKER Δ | p |
|---|---|---|---|---|
| larger side is the UP side | −0.027 | 0.46 | −0.030 | 0.43 |
| first side to reach 0.25 ATR is UP | −0.032 | 0.37 | +0.009 | 0.78 |
| session high before session low | +0.017 | 0.66 | +0.066 | 0.074 |

## Timing — the expansion starts earlier

| measure | RTH trig | RTH opp | Δ (min) | p |
|---|---|---|---|---|
| time of first 0.25 ATR excursion | 41.4 | 66.0 | **−24.6** | <0.001 |
| time of first 0.50 ATR excursion | 126.7 | 142.1 | −15.5 | 0.167 |

Broker day: −128.8 min (p<0.001) and −125.2 min (p<0.001). This is new and was not visible in
Cycle 2's marginal statistics: triggered Mondays reach their first meaningful excursion
substantially sooner.

## First-leg sequences

Definitions are mechanical and free of look-ahead: the first leg is the first touch of
±k·ATR from the open; retracement levels are measured against **that threshold**, not against
the eventual extreme; "opposite" means reaching ∓k·ATR *after* the open has been re-crossed.

| RTH, k = 0.25 | trig | opp | Δ | p |
|---|---|---|---|---|
| leg → retrace 50% of the leg | 0.707 | 0.704 | +0.002 | 0.98 |
| leg → cross back through the open | 0.517 | 0.502 | +0.015 | **0.69** |
| full sequence: leg → open cross → opposite 0.25 ATR | 0.285 | 0.169 | +0.116 | <0.001 |
| opposite-side movement available after the cross (ATR) | 0.445 | 0.272 | **+0.173** | <0.001 |

At k = 0.5 the full sequence occurs on 5.1% vs 2.1% of Mondays (p = 0.027) with 0.636 vs 0.309
ATR available afterwards (p = 0.005), but on only 57 triggered observations.

**The retracement itself is not elevated** (p = 0.69). What is elevated is the extension after
it — which is range expansion restated, not a reversal tendency. The trigger does not make
Monday more likely to turn around; it makes the move that follows a turn bigger.

---

## Status

- **VALIDATED (C3-V1)** — the range expansion is a same-session, shape-preserving proportional
  scaling: both sides grow, the ratio is unchanged, and days remain one-side-dominant.
- **VALIDATED (C3-V2)** — two-sided crossing is real at 0.25 ATR (+11.6 / +15.3 pp) and dies out
  by 0.75 ATR.
- **VALIDATED (C3-V3)** — the expansion starts earlier: first 0.25 ATR excursion ~25 minutes
  sooner under RTH, ~2 hours sooner on the broker day.
- **FALSIFIED (C3-F1)** — the trigger does not make the first leg more likely to retrace or to
  cross back through the open (p = 0.69). Reversal-shape constructions have no conditional
  support.
- **FALSIFIED (C3-F2)** — direction remains unpredictable on every measure tested.
- **OPEN** — whether ~0.45 ATR of post-cross opposite-side movement on 28.5% of triggered
  Mondays is enough to build Issue #2's Stage C family on. **Not tested here:** this closure
  was scoped to measurement only. It is the reviewer's decision whether Stage C is now
  warranted or whether Outcome 1 stands.

## Defect found and fixed during this work

The first implementation computed post-leg extremes from the **session-wide** running
accumulators (`np.minimum.accumulate(low)` over the whole day) rather than accumulating
**from the first-leg index**. Because the session-wide running minimum already contains the
open, every "retracement to the open" tested true: `retr100` came out at 1.000 for every
Monday in both groups, and `opp` silently degenerated into "did the session ever reach ∓k·ATR"
— which made the full-sequence frequency identical to the both-sides-crossed frequency. Fixed
in `src/cycle3_topology.py` (the fix is commented in place); every sequence number above comes
from the corrected pass. The uncorrected run was never reported.

## Relationship to the CI runner's Cycle 3

The runner's synthesis (branch `claude/issue-2-20260921-0716`, commit `e1dff68`, not merged)
reached Outcome 1 from marginal statistics and correctly flagged this question as unresolved.
Its Stage A/B reasoning stands except that it could not measure same-session jointness, which
is now measured. Its conclusion that reversal constructions lack support is **confirmed here
directly** (C3-F1) rather than inferred.
