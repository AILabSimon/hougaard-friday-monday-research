# Cycle 3 — Range-expansion topology and the last simple futures test

Mandate: GitHub Issue #2, reviewed commit `84bdb0a`. Central question: given
`H_FRI < H_THU`, what is the intraday topology of Monday's validated range expansion
(C2-V4), and does that topology support one simple futures/CFD construction Cycle 2 did not
test?

## Classification: **Outcome 1 — range expansion is statistically real, but intraday
topology provides no simple futures/CFD edge. Stop futures/CFD exploitation of this
hypothesis.**

No new construction was tested. Stage A/B evidence — most of it already sitting in Cycle 1/2
artifacts and re-read here specifically against Cycle 3's question — closes off every
construction family the mandate suggested before Stage C could start, and the mandate is
explicit: *"If no sequence has enough post-signal movement, do not manufacture a strategy. End
the cycle there."* That is what happened.

---

## A necessary caveat, stated before the findings

**This cycle could not execute a fresh, literal Stage A/B run.** The mandate assumes access to
the per-Monday derived data (`derived/c2_monday_path.parquet`, `derived/c2_grid.parquet`) and,
if required, the canonical 1-minute store — both of which `README.md`/`METHODS.md` describe as
held only on the researcher's own machine and are excluded from the repository by
`.gitignore` (`*.parquet`, `derived/`, `**/Canonical/**`). The execution environment this cycle
ran in is a clean checkout of the git repository with **no access to that machine, no access to
the canonical store, and no outbound network** to substitute a new data pull (confirmed: the
sandbox has no local `derived/` directory and blocks the shell tools that would be needed to
fetch or compute against raw data). Rebuilding years of NAS100/US500/ES/NQ 1-minute history from
a public API was not attempted — it is not possible within the mandate's "keep compute light",
"reuse existing derived data" instructions even where it is technically possible at all (Yahoo
serves ~30 days of 1-minute ES/NQ history; see C2 corrections §1).

What follows is therefore a **second-pass synthesis of evidence already computed and committed
in Cycle 1/2** (`results/*.csv`), read specifically against Cycle 3's central question, not a
new frozen statistical run. Every number below cites the existing file it comes from. Where the
mandate's Stage A/B items need genuinely new joint per-Monday measures that aren't recoverable
from the committed marginal/conditional tables (the co-occurrence of both-sides-threshold
crossing, the exact ratio of smaller-to-larger excursion per session, minute-exact ordering of
Monday's *own* high and low), that is stated explicitly as unanswered rather than guessed at.
A literal Stage A/B run remains possible — the scripts already exist
(`src/build_paths_c2.py`, `src/build_grid_c2.py`, `src/stageB_structure.py`,
`src/stageC_path.py`) — but need to run on the researcher's machine, where the derived data
lives.

---

## Stage A — joint excursion topology (from existing marginal/conditional evidence)

### A1 — The expansion is two-sided in magnitude, but the two sides are not equally reliable

Re-reading `results/stageC_path.csv` and `results/c2_decomposition_tradeable.csv` side by side,
split by session window and by whether Monday's open still has the level in play
("tradeable state" = opens at/above Friday's low):

| cut | n trig/opp | Δ mfe_down (ATR) | Δ mfe_up (ATR) | verdict |
|---|---|---|---|---|
| RTH, unconditional | 467/569 | **+0.146**, p<0.001 | **+0.074**, p=0.015 | both sides up, down ~2× the size |
| RTH, **tradeable state** | 358/512 | **+0.117**, p=0.001 | +0.041, p=0.128 (n.s.) | up-side effect **disappears** once the gap-consumed cases are excluded |
| BROKER, unconditional | 475/601 | **+0.176**, p<0.001 | **+0.114**, p=0.001 | both sides up, more evenly |
| BROKER, tradeable state | 959* | **+0.149**, p=0.003 | **+0.097**, p=0.001 | both sides survive (C2-V4) |

*BROKER tradeable-state row is quoted from `research/cycle2_findings.md` C2-V4 (the
`c2_range_effect.csv` breakdown); the equivalent per-side split wasn't re-extracted from a raw
CSV this cycle, only the combined total (`c2_range_expansion.csv`, diff 0.246 = 0.149+0.097,
which reconciles exactly).

**This directly extends C2-V2/C2-V6's "the session window decides the answer" theme to the
topology question itself.** In the 6.5-hour RTH window, once you strip out cases where the
extra down-reach was already baked in at the open, the residual up-side expansion is not
distinguishable from control — the surviving effect is downside-tilted. In the 23-hour broker
window, both sides remain significant even in the tradeable state. Net (down − up) excursion at
5/15/30/60 minutes is **flat in every cut** (`stageC_path.csv`, `net5/15/30/60_atr` rows,
p = 0.59–0.98) — there is no persistent one-sided drift over the session, in either window.

### A2 — Marginal magnitude data cannot by itself settle "same-day two-sided" vs "cross-day
averaging of random one-sided expansion"

This is the mandate's central methodological point, and it needs to be conceded directly: if
half of triggered Mondays expanded only upward and half only downward (a coin-flip per Monday,
no genuine two-sidedness within any single session), the *average* up-excursion and *average*
down-excursion across the whole triggered sample would **still both come out elevated** versus
control — because the "up" Mondays inflate the up-average and the "down" Mondays inflate the
down-average. Distinguishing the two readings needs a **joint, per-session** measure (smaller
side / larger side ratio, or the fraction of sessions where *both* sides cross a threshold) —
exactly what `c2_monday_path.parquet` was built to hold and exactly what this environment cannot
reach. **This is the one genuinely open item from Stage A** — flagged, not guessed at.

### A3 — Indirect evidence leans toward "tilted, not cleanly one-sided or fully symmetric"

Two things the committed data *do* show, that a purely random-direction one-sided story would
not easily produce:

- `results/stageD4_nondirectional.csv` (Cycle 2, HF-118): an OCO straddle placed at the open with
  a symmetric ±k·ATR trigger has a **54–56% long fill share** in every parameter cell — i.e.
  whichever side gets hit first is close to a coin flip, not concentrated on one side. If the
  expansion were reliably one specific direction (down) rather than genuinely contested, the
  straddle's fill side would be lopsided, and it isn't.
- But `results/stageC_path.csv` `touch_Bhigh` (touches Friday's high) falls, not rises, when
  triggered on the broker day (52.0% vs 61.4%, diff **−9.4pp**, p = 0.015, survives BH) and is
  flat on RTH (53.5% vs 59.4%, n.s.) — i.e. the specific, far-away reference level (Friday's
  high, which sits further from a weak Friday close) is touched *no more, or less* often, even
  though the *average size* of the up-move grew. The two are compatible: a broad, moderate
  increase in typical up-wobble that usually doesn't travel far enough to reach a specific
  distant level, next to a down-move increase large enough to reliably cross the (nearer)
  Friday-low level. HF-110 (`test_log.md`) points the same way: the `low_only` sequence label
  (touches Friday's low, never Friday's high) rises from 23.9% to 36.4% when triggered — the
  *qualitative* level-touching outcome shifts toward single-sided-down, even while excursion
  *size* rises on both sides.

**Read together: same-day two-sidedness in magnitude, with a reliability tilt toward the
downside for actually crossing a specific level — not the "genuinely symmetric, contested
two-sided battle" that would make a straddle-style construction work, and not a clean one-sided
story either.** This is consistent with, and explains, why D4 (the symmetric straddle, C2-F7)
failed despite the range effect being real: the two sides are unequal in a way a symmetric
OCO can't exploit, but the magnitude data can't tell us, session by session, which specific
Mondays will be lopsided which way.

---

## Stage B — sequence anatomy

The mandate asks for four exact sequences. Three are already answered by existing Cycle 1/2
work; the fourth needs data this environment doesn't have.

| sequence | existing evidence | verdict |
|---|---|---|
| open → first leg → cross back through open → opposite extension | not directly measured; closest proxy is `bounce_after_Blow_atr` (retracement *after the Friday-low touch specifically*, not after a generic first leg) | `stageC_path.csv`: RTH diff −0.011 (p=0.848), BROKER diff +0.070 (p=0.147) — **no evidence of extra bounce-back when triggered, in either window** |
| open → first leg → retracement of 50%/100% of first leg | same limitation as above (would need `c2_monday_path.parquet`'s explicit retracement columns) | **not computable from committed artifacts — OPEN** |
| first 15/30/60m extreme → later break of the opposite side | `high_then_low` sequence label (rally first, reverse down) | **C2-F1, already falsified**: 5.4% of triggered Mondays vs 2.6% of control — real but ~25 events per instrument in ten years, too rare to trade. The complementary `low_then_high` frequency is not quoted anywhere in the committed record and could not be recomputed here — also **OPEN**. |
| first meaningful extreme → session opposite extreme | `mon_high_before_low` (does Monday's *own* high precede Monday's *own* low) | `stageC_path.csv`: 44.8% vs 43.1% (RTH, n.s.), 47.2% vs 40.6% (BROKER, n.s.) — **the ordering of Monday's own extremes is not affected by the trigger** |

**Conclusion for Stage B:** where it can be checked, the reversal/traversal shape the mandate's
Stage C examples need (a first leg that reliably gives back ground, or a first extreme that
reliably gets broken by the opposite side later) is either too rare to trade (C2-F1) or not
present at all (bounce-after-touch, ordering of Monday's own extremes). What is *not* rare — the
elevated average down-excursion — arrives largely in the **first 60 minutes** (`Blow_by15/30/60`,
`stageC_path.csv`: RTH +12.3/+13.5/+13.2pp, BROKER +11.5/+12.1/+12.5pp, all p<0.001) and,
in the RTH window specifically, is dominated by the weekend gap rather than intraday travel
(C2-V2/HF-106). This is a front-loaded, largely-already-resolved-at-or-near-the-open effect, not
a slow-building, tradeable-mid-session sequence.

---

## Stage C — is a new construction justified?

**No.** Walking through the mandate's own example families against what Stage A/B established:

- **"First-leg exhaustion → trade back through the open"** (a reversal/fade). Requires a
  reliable retracement after the initial move. `bounce_after_Blow_atr` shows no such thing
  (n.s. in both windows). The specific rally-then-reverse-down shape is real but too rare to
  trade (C2-F1, 5.4%/2.6%). **Rejected on the evidence.**
- **"Open-cross after an initial ≥k ATR excursion → target opposite excursion."** Same
  objection: no elevated bounce/reversal magnitude once a move has happened; the up-side
  magnitude increase exists but doesn't reliably reach a specific opposite reference level
  (`touch_Bhigh` flat-to-negative). **Rejected on the evidence.**
- **"Confirmed early expansion → continuation, with a trailing/BE mechanism."** The plain
  continuation version of this is exactly D1 (short at the open) and D3b (short the break of
  Friday's low), both already tested in Cycle 2 and both negative-to-flat after costs
  (`results/stageD_entries.csv`, `results/c2_economics_full.csv`; HF-112–115). The mandate
  permits a trailing/BE variant only "if justified by MFE/MAE/path" — but
  `results/c2_economics_full.csv` (HF-122) shows **median MAE meets or exceeds median MFE in
  every reported cell** (e.g. RTH D1 stop-0.5: MFE 0.64R vs MAE 0.73R; BROKER D3b stop-0.5: MFE
  0.80R vs MAE 1.25R) — trades are typically more underwater than they are ever in profit before
  resolving, which is the opposite of what would justify moving a stop to break-even from
  +1R. **Rejected on the mandate's own justification bar.**
- **The one non-directional construction expressible with futures/CFDs, the OCO straddle, was
  already tested exhaustively (D4, C2-F7)** across both trigger widths and three targets, in
  both session windows: every cell's triggered-minus-control difference spans zero
  (`results/stageD4_nondirectional.csv`). Stage A2/A3 above explains *why* it failed even though
  the range effect is real: the two sides are unequal in a way a symmetric OCO can't capture,
  but not unequal in a way that is knowable at the open, session by session.

Every family the mandate suggests, and the two obvious alternatives to it, are either already
tested and falsified (Cycle 1's E1–E3, Cycle 2's D1/D2/D3a/D3b/D4 — 20 + 60 construction-cells
combined) or ruled out by the sequence evidence gathered above before a single new backtest cell
was run. Per the mandate: **no sequence has enough distinct, untested, post-observation
movement to justify a fresh construction. Stage C is not run.** No parameters were searched, no
strategy was manufactured to force a result.

This also directly answers Cycle 2's own open question 4 ("Is D4 the right non-directional test?
... Is there a better futures-expressible test we have missed?", `cycle2_findings.md` §Questions
for independent review): **no** — not one that the available topology evidence supports.

---

## Stage D — decision gate

**Outcome 1: Range expansion is statistically real but intraday topology provides no simple
futures/CFD edge — stop futures/CFD exploitation of this hypothesis.**

Recommendation: **archive the hypothesis as statistically interesting but non-tradeable with
current instruments.** The range-expansion finding (C2-V4) remains the strongest-evidenced
result in the whole programme — significant in every cut, both vendors, both session windows,
development and validation separately — but three cycles and roughly 90 construction-cells
across five entry families (E1–E3, D1–D4, and the topology-based elimination in this cycle) have
found no way to convert it into a futures/CFD position with a definable edge. The topology work
in this cycle explains *why*: the two-sidedness is real in magnitude but structurally unequal
in reliability, front-loaded near the open, largely already resolved by the time an RTH trader
can act, and shows no dependable reversal or continuation shape once a first leg has happened.

**Options/volatility remains the only unexplored avenue** consistent with what this cycle found
— a conditional realised-range expansion with no reliable directional or sequencing edge is
structurally a statement about implied volatility, not about price direction. This is not begun
here, per the mandate ("Do not source options data in this cycle") and per C2-O1.

**Open item for anyone continuing this thread:** the one piece of Stage A/B genuinely not
answered here (A2 above — the joint, same-session two-sidedness question, and the two Stage B
sequences marked OPEN) needs the per-Monday derived data or the canonical store, neither of
which this execution environment can reach. If the programme wants that settled beyond
reasonable doubt before treating Outcome 1 as final, `src/build_paths_c2.py` /
`src/build_grid_c2.py` / `src/stageB_structure.py` already exist and would need to be re-run
where the data lives; no new code is needed for that, only the data access this run didn't have.

---

## Research-discipline compliance

No broad census restart; no FX/commodity/crypto rescue; no Thursday/Friday filter stacking; no
large parameter search (zero new construction-cells were run); no attempt to optimise win rate;
all existing negative findings (Cycle 1 E1–E3, Cycle 2 D1–D4, C2-F1/F6/F7) preserved and cited,
not re-litigated; no derived data or canonical store was rebuilt; compute stayed light — no code
was executed this cycle, this is a re-reading of already-computed artifacts. Cycle 4 was not
started.
