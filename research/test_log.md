# Test log

`Confirmatory` = specified before results were seen. `Control` = pre-specified control.
`Exploratory` = relationship examined after seeing results. `Validation` = run on data not
used to select the relationship.

| ID | Question | Type | Status | Result | Evidence |
|---|---|---|---|---|---|
| HF-001 | Literal: Fri high < Thu high → Monday low ≤ Fri low | Confirmatory | COMPLETE | TRUE but weak. 44–50% pooled, 46.5% under Hougaard's RTH definition. Not the claimed 90/95/62%. | `results/core_results.csv` |
| HF-002 | Unconditional base rate of Monday reaching Friday's low | Control | COMPLETE | 37–43% depending on session/asset. Uplift +2 to +21 pp. | `results/core_results.csv` |
| HF-003 | Opposite condition (Fri high ≥ Thu high) | Control | COMPLETE | 28–42%. Trigger beats it everywhere except crypto. | `results/core_results.csv` |
| HF-004 | Upside symmetry: Fri low > Thu low → Monday takes Fri high | Control | COMPLETE | Equal or **stronger** than the downside version at every weekday and asset class. Effect is symmetric, not directional. | `results/controls.csv` |
| HF-005 | Placebo, wrong direction: does the failed-high trigger predict Monday taking Friday's *high*? | Control | COMPLETE | Negative uplift (−0.04 to −0.15). Trigger does carry directional content. | `results/controls.csv` |
| HF-006 | Adjacent weekday triples (Mon→Tue … Thu→Fri) | Control | COMPLETE | Same raw effect on every pair. Friday not special on raw numbers; ~3× on controlled β for US indices only. | `results/controls.csv`, `charts/02` |
| HF-007 | Session-definition sensitivity (RTH / BROKER / NYFX / UTC / LONDON) | Confirmatory | COMPLETE | US-index controlled β = 0.42/0.44/0.44/0.44/0.44 — invariant. FX β ≈ 0 under all five. Result is **not** session-dependent. | `results/core_results.csv` |
| HF-008 | Cross-market: 12 instruments, 4 asset classes | Confirmatory | COMPLETE | Effect concentrated entirely in US equity indices. | `results/core_results.csv` |
| HF-009 | Mechanism: control for Friday's close location within its range | Confirmatory | COMPLETE | **Kills the effect everywhere except US equity indices.** FX β 0.584 → −0.009. | `results/controls.csv`, `mechanism_logit` rows |
| HF-010 | Path-shuffle placebo (1000 reps, within instrument × year) | Control | COMPLETE | FX p = 0.91 (artefact). US indices p < 0.001 (real). Random-trigger sanity = 0.000. | `results/controls.csv`, `charts/03` |
| HF-011 | Condition severity: does the size of the high shortfall matter? | Confirmatory | COMPLETE | **FALSIFIED.** Flat across quintiles of shortfall/ATR. | `results/severity.csv` |
| HF-012 | Year-by-year stability | Confirmatory | COMPLETE | US indices positive in 11/11 (Duka) and 26/27 (YF) years. | `results/robustness.csv`, `charts/04` |
| HF-013 | Frozen dev(2000-2015) → validation(2016-2026) split | Validation | COMPLETE | Held: β 0.408 → 0.343 (YF val) and 0.420 (independent Dukascopy val). | `results/robustness.csv` |
| HF-014 | Independent second data source (Yahoo daily futures 2000–2026) | Validation | COMPLETE | Replicates: US-index β 0.360 (z 3.67); commodities β 0.057 (n.s.), matching Dukascopy. | `results/core_results.csv` |
| HF-015 | Weekly analogue (week fails prior week's high → next week takes this week's low) | Control | COMPLETE | **FALSIFIED after control.** Raw +0.08 to +0.22, controlled β ≈ 0 in 12/12. | `results/controls.csv` |
| HF-016 | Intraday session analogue (Asia→London→NY) | Control | COMPLETE | **FALSIFIED after control.** 2 of 16 cells marginal, both index. | `results/controls.csv` |
| HF-017 | Event-definition ladder: touch / penetration / close-below / gap-below / directional | Confirmatory | COMPLETE | Relative uplift preserved or amplified for US indices under stricter definitions. `dir_down` barely moves (0.463 vs 0.436) — the trigger is not a direction signal. | `results/event_ladder.csv` |
| HF-018 | First arrival: does Monday reach Friday's low before Friday's high? | Confirmatory | COMPLETE | **No.** High reached more often (53.5% vs 46.5%); low-first in only 41.1% of triggered Mondays. | `charts/06` |
| HF-019 | Time-to-event distribution | Confirmatory | COMPLETE | 76% of touches inside the first 60 min of RTH; median at the open. | `charts/05` |
| HF-020 | Is the residual a weekend-gap effect? | Exploratory | COMPLETE | **No.** Trigger does not predict the gap (p = 0.94/0.31/0.12); controlling for Monday's open does not remove the residual. | `mechanism` output |
| HF-021 | E1 — short at Friday close, TP Friday low, SL Friday high | Confirmatory | COMPLETE | 41.1% TP / 48.8% SL; median R available 0.75; median R −0.52. **Mean R unusable**: risk denominator unbounded below, max single-trade R = 1321. See METHODS §7. | `results/strategy_expectancy.csv` |
| HF-022 | E2 — short at Monday open, TP Friday low, SL Friday high | Confirmatory | COMPLETE | Mean R = −0.115 (US idx RTH), 95% CI (−0.31, +0.08) — negative point estimate, not significantly so. Same denominator caveat as HF-021. | `results/strategy_expectancy.csv` |
| HF-023 | E3 — short at Monday open, fixed ATR stop / 1–3R target | Confirmatory | COMPLETE | Mean R = −0.03 to −0.10 triggered; −0.10 to −0.18 non-triggered. Negative point estimate in all 12 US-index cells, 95% CI strictly below zero in 3. **The construction the tradeability conclusion rests on.** | `results/strategy_expectancy.csv`, `charts/07` |
| HF-024 | Hougaard variants: `<` vs `≤`; Monday-only vs next-session (holiday asterisk) | Confirmatory | COMPLETE | Immaterial. ≤ changes hit rate by 0.001; the holiday asterisk *reduces* uplift 0.171 → 0.160. | `research/provenance.md` |
| HF-025 | Provenance: what did Hougaard actually claim? | — | COMPLETE | Dow cash, RTH only, "retested / seen again / at least a double bottom". Own figures 20/21 (N=21, one year) and latterly 62%. | `research/provenance.md` |
| HF-025b | Monday path anatomy: first arrival, time-to-touch, MFE/MAE | Confirmatory | COMPLETE | Fri high reached more often than Fri low even when triggered; low reached first 41%; 76% of touches inside 60 min; median MAE before touch 0.07 ATR. | `results/monday_path.csv`, `charts/05`, `charts/06` |
| HF-026 | Is the US-index residual monetisable in a non-directional form? | Exploratory | **NOT STARTED** — deliberately not expanded pending review | — | — |
| HF-028 | Entries inside Monday's first 30 minutes, where most of the measured movement occurs | Exploratory | **NOT STARTED** | — | — |
| HF-027 | Dow Jones cash replication | — | **BLOCKED** | No DJIA series in the data library. | — |

## Cycle 2 (from commit 97fca1c)

| ID | Question | Type | Status | Result | Evidence |
|---|---|---|---|---|---|
| HF-101 | Does the US-index residual survive week-clustered inference? | Confirmatory | COMPLETE | YES, with wider intervals. Cluster SE = 1.22-1.27x naive. Pooled RTH p=0.012; ES+NQ p=0.003; NAS100 alone p=0.028; US500 alone p=0.062. | `results/stageA_dependence.csv` |
| HF-102 | Does it survive per-regime? | Confirmatory | COMPLETE | **Only 1 of 4 regimes individually significant** (2013-19 p=0.018); all four point estimates positive. Frozen Yahoo validation window alone p=0.071. | `results/stageA_dependence.csv` |
| HF-103 | Do Thursday structure variables explain Monday heterogeneity? | Exploratory | COMPLETE | **FALSIFIED.** Nothing from Thursday survives, raw or controlled. | `results/stageB_structure.csv` |
| HF-104 | Do Friday structure / Friday-vs-Thursday interaction variables add information beyond close-in-range? | Exploratory | COMPLETE | **FALSIFIED.** 1 of 168 associations survives BH and does not replicate across session definitions. No filter justified. | `results/stageB_partial.csv` |
| HF-105 | Does the trigger change Monday's opening location? | Confirmatory | COMPLETE | YES but via geometry: opens below Friday's range 23.3% vs 10.0% (p<0.001) while the gap ITSELF is unchanged (p=0.92). | `results/stageC_path.csv` |
| HF-106 | Gap-consumed vs travelled-to decomposition | Confirmatory | COMPLETE | **The central Cycle-2 result.** RTH: total +0.171, gap-consumed +0.133 (p<0.001), travelled-to +0.038 (**p=0.225, n.s.**). | `results/stageC_path.csv`, `charts/c2_01` |
| HF-107 | Does the trigger change Monday's direction? | Confirmatory | COMPLETE | **NO.** close-open p=0.21; up-after-60m p=0.91; first 0.25-ATR move down p=0.29 (tradeable state). | `results/stageC_conditional.csv` |
| HF-108 | Does it change opening-range break direction? | Confirmatory | COMPLETE | **NO.** OR15 down 43.9% vs 42.7%; OR30 40.0% vs 41.8%. | `results/stageC_path.csv` |
| HF-109 | Does it change timing of the Friday-low touch, in the tradeable state? | Confirmatory | COMPLETE | **NO.** by-30-min p=0.41, by-60-min p=0.44. | `results/stageC_conditional.csv` |
| HF-110 | Does it change path sequencing? | Confirmatory | COMPLETE | Marginally: low_only 36.4% vs 23.9%. But `high_then_low` (the retracement path an entry would need) is 5.4% vs 2.6% - too rare to trade. | `results/stageC_path.csv` |
| HF-111 | What survives in the tradeable state (opens at/above Friday's low)? | Confirmatory | COMPLETE | Only 2 of 16: touch rate +0.087 (p=0.017) and max down-excursion +0.117 ATR (p<0.001). | `results/stageC_conditional.csv`, `charts/c2_02` |
| HF-112 | D1 - short at Monday's open, ATR stop/target | Confirmatory | COMPLETE | Negative after costs, mean R -0.07 to -0.16; 8/12 cells significantly negative. | `results/stageD_entries.csv` |
| HF-113 | D2 - short on a limit above the open | Confirmatory | COMPLETE | Negative to zero, mean R -0.02 to -0.10, none positive. | `results/stageD_entries.csv` |
| HF-114 | D3 - short the break of Friday's low | Confirmatory | COMPLETE | **ARTEFACT then FALSIFIED.** Looked strong (+0.81R, p<0.001) via a phantom fill on gap-through Mondays; corrected version -0.16 to +0.04, all CIs span zero. | `results/stageD_entries.csv`, cycle2_findings C2-A1 |
| HF-115 | Is the trigger's economic contribution (triggered - opposite) significant anywhere? | Confirmatory | COMPLETE | **NO.** No construction's difference is significant. | `results/stageD_entries.csv` |
| HF-116 | Adversarial RESCUE check: is the tradeable component significant in any subset? | Exploratory | COMPLETE | **PROVISIONAL.** 2 of 8 pre-chosen subsets reach 5% (2021-2026 p=0.041; opens-inside-range p=0.049). The tradeable-state path effect is concentrated entirely in 2021-2026 (p=0.008 vs p=0.59 in 2016-2020). Does not change the verdict; flagged as the best thread for a later cycle. | `results/stageE_rescue.csv` |
| HF-117 | Is any single year carrying the headline effect? | Control | COMPLETE | **NO.** Positive in 11/11 years; worst leave-one-year-out pooled uplift +0.137 vs +0.171 full sample. | `results/stageE_year_by_year.csv` |
| HF-118 | D4 - OCO straddle at Monday's open (non-directional) | Confirmatory | COMPLETE | **FALSIFIED.** Mean R -0.084 to +0.013, every CI spans zero, long share 54-56%. Range expansion is real but a breakout does not capture it. | `results/stageD4_nondirectional.csv` |
| HF-119 | Fri->Mon vs every adjacent weekday pair under the SAME week-clustered treatment | Confirmatory | COMPLETE | **Friday is the only pair significant in all three datasets** and the largest in each (OR 1.48/1.65/1.43; p=0.017/0.003/0.003). Partially supersedes Cycle-1 V6. | `results/c2_weekday_pairs.csv` |
| HF-120 | ES/NQ daily gap-vs-travel decomposition, 2000-2026 | Confirmatory | COMPLETE | **Reverses the RTH conclusion.** Travelled component +0.140 of +0.192 total (73%), p<0.001. The split is decided by the session window, not the market. | `results/c2_decomposition.csv` |
| HF-121 | Does the trigger predict Monday RANGE EXPANSION? | Exploratory -> Confirmatory | COMPLETE | **VALIDATED.** +13% to +28%, beta 0.12-0.23 ATR, p<0.001 in every cut incl. DEV and VAL separately and each instrument alone. Survives Friday range/close-location control. Two-sided. | `results/c2_range_effect.csv` |
| HF-122 | Full economics reporting set (trades/year, 1R/2R/3R, MFE/MAE, year, dev/val) | Confirmatory | COMPLETE | 2R+ never approached: median MAE exceeds median MFE in most cells; 2R attainment 2-15%, 3R 0-8%; positive in 3-6 of 11 years. | `results/c2_economics_full.csv` |
| HF-123 | Non-directional exploitation via options | Exploratory | **BLOCKED** - no options data in the library | - | - |

## Cycle 3 closure (review of Cycle 2 → Issue #2 Stage A, run locally)

| ID | Question | Type | Status | Result | Evidence |
|---|---|---|---|---|---|
| HF-301 | Is the Monday range expansion same-session two-sided, or cross-day averaging of random one-sided expansion? | Confirmatory | COMPLETE | **Neither.** Both sides expand (smaller side +0.043/+0.055 ATR, p=0.001/<0.001) and the smaller/larger ratio is unchanged (p=0.69/0.91) - a shape-preserving proportional scaling of the excursion envelope. | `results/c3_stageA_topology.csv`, `charts/c3_01` |
| HF-302 | Both-side threshold crossing on the same Monday | Confirmatory | COMPLETE | Real at 0.25 ATR (+0.116 RTH / +0.153 BROKER, p<0.001), marginal at 0.5 (+0.030, p=0.039), absent by 0.75. | `results/c3_stageA_topology.csv` |
| HF-303 | Joint vs independence of the two sides | Confirmatory | COMPLETE | Lift 0.43-0.80, always below 1: days stay one-side-dominant. Triggered Mondays are closer to independence than control at every threshold. | `results/c3_joint_independence.csv` |
| HF-304 | Smaller-side / larger-side excursion ratio | Confirmatory | COMPLETE | Flat: +0.008 (p=0.69) RTH, -0.003 (p=0.91) BROKER. Smaller side is ~35% of larger in both groups. | `results/c3_stageA_topology.csv` |
| HF-305 | First-leg ordering and direction | Confirmatory | COMPLETE | **FALSIFIED as a signal.** Larger side up p=0.46; first side up p=0.37/0.78; high-before-low p=0.66. | `results/c3_stageA_topology.csv` |
| HF-306 | Does the first leg retrace / cross back through the open more often when triggered? | Confirmatory | COMPLETE | **FALSIFIED.** 50% retrace p=0.98; open cross 51.7% vs 50.2%, p=0.69. No conditional reversal tendency. | `results/c3_stageB_sequences.csv`, `charts/c3_02` |
| HF-307 | Complementary sequence: first leg -> open cross -> opposite side | Confirmatory | COMPLETE | Frequency 28.5% vs 16.9% (p<0.001) at 0.25 ATR, with 0.445 vs 0.272 ATR available after the cross (p<0.001). But this is range expansion restated, not a reversal effect - the cross itself is not elevated. | `results/c3_stageB_sequences.csv` |
| HF-308 | Timing of the expansion | Exploratory | COMPLETE | **NEW.** First 0.25 ATR excursion arrives 24.6 min earlier (RTH, p<0.001) and 129 min earlier (broker day, p<0.001). Not visible in Cycle 2's marginals. | `results/c3_stageA_topology.csv` |
| HF-309 | DEFECT: post-leg extremes read from session-wide running accumulators | Artefact | FIXED | Made every retracement trivially true (retr100 = 1.000 for all) and collapsed the full sequence onto both-sides-crossed. Fixed to accumulate from the first-leg index; uncorrected run never reported. | `src/cycle3_topology.py` |
| HF-310 | Issue #2 Stage C construction family | - | **NOT RUN** - closure scoped to measurement only; Stage C is the reviewer's decision | - | - |

## Final futures/CFD economic test (post-open-cross construction)

| ID | Question | Type | Status | Result | Evidence |
|---|---|---|---|---|---|
| HF-401 | Does the post-open-cross signal fire often enough to matter? | Confirmatory | COMPLETE | Yes. 48.0% of triggered Mondays (RTH) / 58.1% (broker); 223 / 276 trades; ~10.1 / 12.5 per instrument-year. Frequency was never the constraint. | `results/postcross_economics.csv` |
| HF-402 | S1 - structural stop beyond the initial-leg extreme, target 2R | Confirmatory | COMPLETE | **FALSIFIED.** RTH mean R -0.045 (CI -0.207..+0.113); broker +0.041 (CI -0.107..+0.198). Medians -0.18 / -0.25. | `results/postcross_economics.csv` |
| HF-403 | S2 - coarse 0.5 ATR stop, targets 1R / 2R / 3R | Confirmatory | COMPLETE | **FALSIFIED.** Six cells, mean R -0.062 to +0.029, every CI spans zero, every median negative. | `results/postcross_economics.csv` |
| HF-404 | S3 - 0.5 ATR stop, 2R target, break-even at +1R | Confirmatory | COMPLETE | **FALSIFIED.** RTH -0.042, broker +0.031, both n.s. Management does not rescue it. | `results/postcross_economics.csv` |
| HF-405 | Is the 2R+ programme objective reachable from this entry? | Confirmatory | COMPLETE | **NO.** 2R attainment 8.1% (RTH) / 13.0% (broker) at a 0.5 ATR stop, 14.3% with the structural stop. Median MFE 0.69-0.96 R vs median MAE 0.54-0.74 R. | `results/postcross_economics.csv`, `charts/c4_01` |
| HF-406 | Does the trigger add value relative to the control on this construction? | Control | COMPLETE | Partially: broker S1 +0.041 triggered vs -0.216 control, diff +0.257 R (p=0.009). But the triggered arm is itself indistinguishable from zero (p=0.65). Informative, not profitable - the pattern of every prior cycle. | `results/postcross_economics.csv` |
| HF-407 | Reconciliation: is 0.445 ATR of post-cross movement capturable? | Confirmatory | COMPLETE | **NO, and this is the key result.** The figure is a maximum favourable excursion, reproduced exactly here (0.446). From the SAME entry the adverse excursion is 0.385 ATR. Margin = +0.061 ATR of unrealisable maxima vs ~0.02 ATR costs; control margin -0.019. No simple mechanically tradeable futures/CFD edge was found in the tested constructions, and the observed MFE/MAE geometry provides no evidence-based justification for further parameter search. | `results/postcross_geometry.csv`, `charts/c4_01` |
| HF-408 | Year and DEV/VAL consistency | Confirmatory | COMPLETE | Positive in 3-6 of 11 years; DEV/VAL means flip sign in OPPOSITE directions between RTH and broker day. No stability. Max drawdown 13.8-24.9 R. | `results/postcross_economics.csv` |
| HF-409 | Known approximation: BE-at-+1R resolution | Artefact | DOCUMENTED | The entry level's own first-touch is degenerate (open touched at minute 0), so BE is proxied by the 0.25 ATR adverse level - mildly generous to the strategy. S3 is negative anyway. | `research/final_futures_test.md` |
