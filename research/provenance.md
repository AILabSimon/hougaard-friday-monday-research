# Provenance of the claim — what Tom Hougaard actually said

Compiled from primary sources (his own videos and talk) and credible secondary sources.
Transcripts were obtained via a transcript mirror because youtube.com blocks automated
fetching. Quotes are reproduced as the transcripts render them.

## The claim in his own words

**Source A — "V58 – Thursday Friday Monday Pattern" (YouTube, `euebIz4Mf4A`)** — the most
detailed statement:

> "If Friday is unable to trade above the high of Thursday, then the odds are high, I argue,
> that whatever low we made on the Friday will be seen again on Monday."

Instrument and session, same source:

> "if you're looking at the Dow Jones index where this research is done, and you only look in
> what we call regular trading hours. You don't look at the overnight range."
> "It goes from 09:30 Eastern time to 4:00 p.m. Eastern time."

His statistics in that video: 188 occurrences over ~10 years on the Dow; a recent sample of 52
with **62%** meeting the objective; an 85% sub-period that then deteriorated. His own verdict:

> "a pattern that has a 62% success rate and no real setup is more like a pattern rather than
> an entry technique."

**Source B — "Trader Tom Live Trading – Thursday, Friday, and Monday Scenario" (`Ecm3IC7GxH4`)**
— the >90% version, and the loosest definition of the event:

> "the odds were more than 90% that during the following Monday, whatever low was made on the
> Friday, would be retested on the Monday."
> "the lows of Friday should be surpassed **or at least making a double bottom**."

Also, explicitly ruling out any Friday-close condition:

> "wherever you closed that Friday"

**Source C — Trading Psychology Talk, London 2020 (`sg_OTc0lRko`)** — the origin of the 95%
figure:

> "there were 21 instances where the price action on Friday was unable to trade above the
> highest point of the previous day which was Thursday … 20 out of 21 times based on the last
> 252 trading days … the market has traded low on the Monday"

**Source D — his 2019 book, *What I Wish Someone Had Told Me 20 Years Ago*, p. 110ff** (quoted
second-hand; the primary PDF was unreachable):

> "I was surprised to find that on 20 out of the 21 occurrences, the Dow traded lower on
> Monday, **often** lower than Friday's low."

This is the load-bearing sentence. In the book the 20/21 statistic attaches to *"traded lower
on Monday"* — a directional statement — and only "often" to *below Friday's low*. Every
downstream restatement collapses those two into one.

## What this means for the test design

| Dimension | Hougaard | Popular restatement | What we tested |
|---|---|---|---|
| Instrument | **Dow cash only**; he says he assumes S&P behaves similarly but did not test it | instrument-agnostic; applied to DAX, Nasdaq, FX | NAS100, US500, ES, NQ (no DJIA available) + 10 other instruments |
| Session | **US RTH 09:30–16:00 ET**, overnight explicitly excluded | 24-h daily bars (every TradingView implementation found) | both, plus three more definitions |
| Event | "retested" / "seen again" / "traded below" / "or at least a double bottom" | "chase", "gap down", "trade below" | touch, penetration (0.05R/0.25R/0.25 ATR), close-below, gap-below, directional excursion |
| Trigger | Friday RTH high < Thursday RTH high; Friday's close irrelevant | same | `<` and `≤` both tested |
| Holidays | counts Tuesday fulfilment when Monday is a holiday ("asterisk") | usually silent | Monday-only **and** next-session both tested |
| Own numbers | 20/21 (95%, N=21, one year); ">90%"; latterly 62% of 52 | usually only the 90–95% figure repeated | — |

Two provenance points matter for fairness to him:

1. **"Gap down" is not his.** It originates in the Whitebox docs' paraphrase
   (docs.whitebox.so/trader-tom/scenario-strategy) and is a materially stricter condition than
   "retested".
2. **He has walked the number down himself**, from >90% in 2019–20 to 62% recently, and now
   describes it as a pattern rather than a setup. Our results (46.5% RTH / 55.0% on 24-h
   futures bars) are lower still, but the direction of his own revision is the same as ours.

## Independent tests by others

- **Whitebox docs** — restates the rule, adds "gap down", supplies no statistics, and states
  explicitly that Hougaard specifies no entry or exit.
- **TradingView "Friday/Monday Pattern Backtest [Market Rebellion]"** — uses 24-h daily bars,
  reports no statistics, claims only an "overwhelming tendency".
- **TradingView "Tom Hougaard MWF Situational Theory Pro"** — bolts an EMA trend filter and R
  targets onto the name; none of that machinery traces to Hougaard. No statistics.
- **time-price-research-astrofin.blogspot.com (Aug 2025)** — the only quantified third-party
  test located: 2003–2025, S&P 500 48.94% (472 setups), Nasdaq 55.46% (449), **DJIA 48.69%
  (458)**, Russell 2000 55.60% (464). Construction (RTH vs 24-h, touch vs close) is not
  stated. The DJIA number — no edge on Hougaard's own index — is broadly consistent with our
  finding that the *absolute* rate is near a coin flip, while their Nasdaq/Russell numbers are
  close to our US-index figures.

## Sources

- https://www.youtube.com/watch?v=euebIz4Mf4A (transcript via youtubetotranscript.com)
- https://www.youtube.com/watch?v=Ecm3IC7GxH4 (transcript via youtubetotranscript.com)
- https://www.youtube.com/watch?v=sg_OTc0lRko (transcript via youtubetotranscript.com)
- https://docs.whitebox.so/trader-tom/scenario-strategy
- https://time-price-research-astrofin.blogspot.com/2025/08/the-thursday-friday-monday-pattern-tom.html
- https://in.tradingview.com/script/lsT7w9Wm-Tom-Hougaard-MWF-Situational-Theory-Pro-KG/
- https://it.tradingview.com/script/5lqfNJVa-Friday-Monday-Pattern-Backtest-Market-Rebellion
