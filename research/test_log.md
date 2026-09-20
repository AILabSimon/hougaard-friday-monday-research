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
