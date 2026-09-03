"""Authored documentation prose.

One entry per registered indicator. Everything mechanical — parameter tables,
output column names, example output — is derived by ``gen_docs.py`` from the
registry and from actually evaluating each example, so only genuine prose lives here.

``formula`` is the formula statement for the indicator implemented.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypedDict

import pandas as pd

import zeonta


class Doc(TypedDict):
    title: str
    formula: str
    about: str
    reading: str
    pitfalls: str
    example: list[Callable[[pd.DataFrame], Any]]


CONTENT: dict[str, Doc] = {
    "candles": {
        "title": "Candlestick Anatomy and Patterns",
        "formula": (
            "Body = |Close - Open|; bullish candle when Close > Open, bearish when Close < Open; "
            "Upper wick = High - max(Open, Close); Lower wick = min(Open, Close) - Low."
        ),
        "about": (
            "A candle compresses four numbers into one shape: where trading opened and closed "
            "(the body) and how far it strayed in between (the wicks). This function returns that "
            "geometry as plain columns, plus flags for the three patterns that show up most: the "
            "doji, the engulfing pair and the hammer/shooting-star."
        ),
        "reading": (
            "A long body means one side dominated the whole session; a long wick means a level was "
            "tested and rejected. `CDLDIR` gives direction, `CDLDOJI` marks indecision, `CDLENG` "
            "flags a reversal pair (+1 bullish, -1 bearish) and `CDLHAM` flags a rejection candle "
            "(+1 hammer, -1 shooting star)."
        ),
        "pitfalls": (
            "A pattern is a description of one or two bars, not a signal. A hammer in the middle "
            "of a range means nothing; the same hammer at a level that has already been tested "
            "twice is what traders act on. Always read patterns together with location."
        ),
        "example": [
            lambda df: zeonta.candles(df["open"], df["high"], df["low"], df["close"])[
                ["CDLBODY", "CDLDIR", "CDLDOJI", "CDLENG"]
            ].tail(3),
        ],
    },
    "support_resistance": {
        "title": "Support and Resistance",
        "formula": (
            "Pivot High(leftBars, rightBars) at bar i: High[i] > High[i-leftBars..i-1] and "
            "High[i] > High[i+1..i+rightBars] (local maximum). Pivot Low is the mirror. A price "
            "where multiple pivots cluster becomes a support/resistance level."
        ),
        "about": (
            "Support and resistance are not lines someone draws by eye — they are prices the "
            "market has already turned at. This function finds those turning points mechanically "
            "as swing pivots, then carries the most recent confirmed one forward as a usable level."
        ),
        "reading": (
            "`PIVOTHIGH` / `PIVOTLOW` mark where a swing actually formed. `RES` / `SUP` hold the "
            "most recent confirmed level and are the columns to trade against. Use `sr_levels()` "
            "when you want the clustered levels ranked by how many times each was touched."
        ),
        "pitfalls": (
            "A pivot cannot be known until `right` more bars have printed, so the `PIVOTHIGH` / "
            "`PIVOTLOW` columns contain look-ahead information — they place the pivot on the bar it "
            "occurred, not the bar you learned about it. Backtest against `RES` / `SUP`, which are "
            "already delayed by `right` bars."
        ),
        "example": [
            lambda df: zeonta.support_resistance(df["high"], df["low"], left=5, right=5)[
                ["RES_5_5", "SUP_5_5"]
            ].tail(3),
            lambda df: zeonta.sr_levels(df["high"], df["low"], left=5, right=5, max_levels=3),
        ],
    },
    "trend_channel": {
        "title": "Trend Basics and Trend Channels",
        "formula": (
            "Linear regression over length n bars (x = 0..n-1, y = close): slope b = "
            "(nSxy - SxSy) / (nSx^2 - (Sx)^2); intercept a = (Sy - bSx) / n; regression line = "
            "a + b*x. Channel bands = regression line +/- (multiplier x standard deviation of "
            "closes from the regression line)."
        ),
        "about": (
            '"Is this an uptrend?" is usually answered by eye. A least-squares fit answers it '
            "with a number: the slope. The channel bands around that fit show how tightly price "
            "has been hugging the trend."
        ),
        "reading": (
            "`LRCSLOPE` is the per-bar drift: positive is an uptrend, negative a downtrend, and its "
            "magnitude is the trend's steepness. Price near `LRCU` is extended relative to the "
            "trend; near `LRCL` it is lagging behind it. The band width is the scatter of price "
            "**about the fitted line**, not about its mean, so a cleanly trending market gives a "
            "narrow channel however steep it is."
        ),
        "pitfalls": (
            "The fit is recomputed every bar, so the channel repaints as new data arrives — the "
            "line you see today over past bars is not the line that existed back then. Also, a "
            "regression will happily fit a straight line through pure noise; check the slope "
            "against something like ADX before trusting it."
        ),
        "example": [
            lambda df: zeonta.trend_channel(df["close"], length=50).tail(3),
        ],
    },
    "relative_volume": {
        "title": "Volume Basics",
        "formula": (
            "Volume MA(n) = (1/n) x sum(Volume[i]) for the last n bars (a simple moving average "
            "applied to volume instead of price). Relative volume = current bar's Volume / "
            "Volume MA(n)."
        ),
        "about": (
            "Raw volume is close to meaningless on its own — a million shares is enormous for one "
            "ticker and a rounding error for another. Dividing by the recent average turns it into "
            "a number that means the same thing everywhere: how busy is this bar compared to normal?"
        ),
        "reading": (
            "`RVOL` of 1.0 is a perfectly ordinary bar; 2.0 is twice the recent norm. A breakout on "
            "high relative volume has participation behind it, while the same breakout on 0.5 is "
            "being made by very few people and tends not to hold."
        ),
        "pitfalls": (
            "Relative volume is distorted around scheduled events — index rebalances, options "
            "expiry and earnings all produce huge readings that say nothing about conviction. It "
            "also runs high at the open and close of every session, so compare like with like."
        ),
        "example": [
            lambda df: zeonta.relative_volume(df["volume"], length=20).tail(3),
        ],
    },
    "sma": {
        "title": "Simple Moving Average (SMA)",
        "formula": (
            "SMA(n) = (1/n) x sum(Close[i]) for the last n bars — an equally weighted average of "
            "the n most recent closes."
        ),
        "about": (
            "The simplest way to see a trend through the noise: average the last n closes and plot "
            "that instead of price. Every bar in the window counts the same, which makes the SMA "
            "smooth and predictable — and also means a single old bar dropping out of the window "
            "can move it."
        ),
        "reading": (
            "Price above a rising SMA is the textbook uptrend; price below a falling one is the "
            "downtrend. The 50 and 200 are watched far more than any other lengths, simply because "
            "so many people watch them."
        ),
        "pitfalls": (
            "An SMA lags by roughly half its length, so it confirms a turn well after it happened; "
            "it is a description of the past, not a forecast. In a sideways market price crosses it "
            "constantly, producing signals that are all noise."
        ),
        "example": [
            lambda df: zeonta.sma(df["close"], length=20).tail(3),
            lambda df: df.zta.sma(50).tail(3),
        ],
    },
    "ema": {
        "title": "Exponential Moving Average (EMA)",
        "formula": (
            "EMA(n) today = Close x k + EMA(n) yesterday x (1 - k), where k = 2 / (n + 1). Seed "
            "value: EMA(n) on the first available bar = SMA(n) of the first n closes."
        ),
        "about": (
            "The EMA fixes the SMA's biggest quirk: instead of every bar in a window counting "
            "equally and then abruptly dropping out, weight decays smoothly into the past. Recent "
            "bars matter most and old ones fade rather than fall off a cliff."
        ),
        "reading": (
            "Read it exactly like an SMA, but expect it to turn sooner. The gap between a fast and "
            "a slow EMA is the basis of MACD, and stacked EMAs of increasing length form the "
            "ribbon."
        ),
        "pitfalls": (
            "Faster response also means more false turns — the EMA reacts to a one-bar spike that "
            "an SMA would smooth away. Note also that different platforms seed the recursion "
            "differently; this library seeds with the SMA of the first n closes, so the first "
            "handful of values may not match a chart that seeds from the first close alone."
        ),
        "example": [
            lambda df: zeonta.ema(df["close"], length=20).tail(3),
        ],
    },
    "ma_cross": {
        "title": "Moving Average Crossovers",
        "formula": (
            "Bullish crossover (golden cross when fast=50, slow=200): fastMA[i-1] <= slowMA[i-1] "
            "and fastMA[i] > slowMA[i]. Bearish crossunder (death cross): fastMA[i-1] >= "
            "slowMA[i-1] and fastMA[i] < slowMA[i]."
        ),
        "about": (
            "Two averages of different lengths, and a signal whenever they swap places. The 50/200 "
            "pair has famous names — the golden cross and the death cross — and gets reported in "
            "the financial press, which is part of why it moves markets at all."
        ),
        "reading": (
            "The `cross` column is `1.0` on the bar the fast average crosses above the slow one, "
            "`-1.0` when it crosses below, and `0.0` otherwise. Many traders use the crossover as "
            "a regime filter — only take longs while the fast average is on top — rather than as "
            "an entry trigger."
        ),
        "pitfalls": (
            "Because both inputs lag, the crossover lags twice over: by the time a golden cross "
            "prints, a large part of the move is usually behind you. In a range the pair crosses "
            "back and forth repeatedly, and trading each one mechanically bleeds money."
        ),
        "example": [
            lambda df: (
                zeonta.ma_cross(df["close"], fast=20, slow=50).query("cross_20_50 != 0").tail(3)
            ),
        ],
    },
    "ema_ribbon": {
        "title": "EMA Ribbon",
        "formula": (
            "EMA Ribbon = 6 EMAs of increasing length plotted together, e.g. EMA(20), EMA(30), "
            "EMA(40), EMA(50), EMA(60), EMA(70) (or Fibonacci-like: 8, 13, 21, 34, 55, 89). Each "
            "EMA(n) = Close x k + previous EMA(n) x (1 - k), k = 2/(n+1)."
        ),
        "about": (
            "One EMA tells you the trend; six of them tell you how much agreement there is. When "
            "the whole fan points the same way and spreads apart, every timeframe in the ribbon "
            "agrees. When it knots together, none of them do."
        ),
        "reading": (
            "Widely spaced and correctly ordered (shortest on top in an uptrend) means a strong, "
            "well-established trend. Compressed and interleaved means the trend has stalled — "
            "often just before a decisive move in either direction."
        ),
        "pitfalls": (
            "The ribbon is six lagging indicators, not six independent opinions — they all come "
            'from the same closes, so their "agreement" is much weaker evidence than it looks. '
            "It is a visualisation aid more than a signal generator."
        ),
        "example": [
            lambda df: zeonta.ema_ribbon(df["close"], lengths=(8, 13, 21, 34, 55, 89)).tail(2),
        ],
    },
    "rsi": {
        "title": "Relative Strength Index (RSI)",
        "formula": (
            "RSI = 100 - 100 / (1 + RS), RS = AvgGain(14, Wilder-smoothed) / AvgLoss(14, "
            "Wilder-smoothed)"
        ),
        "about": (
            "RSI asks a narrow question: over the last n bars, how much of the total movement was "
            "upward? The answer is squeezed onto a 0-100 scale, which makes momentum comparable "
            "across symbols and timeframes."
        ),
        "reading": (
            'Above 70 is conventionally "overbought" and below 30 "oversold", but the more '
            "durable reading is the 50 line: RSI holding above 50 through pullbacks is a trend in "
            "good health. Divergence between RSI and price is the other classic use — see "
            "[divergence](divergence.md)."
        ),
        "pitfalls": (
            '"Overbought" does not mean "about to fall". In a strong trend RSI can sit above 70 '
            "for weeks, and shorting every such reading is one of the most reliable ways to lose "
            "money with this indicator. Treat 70/30 as a description of momentum, not an instruction."
        ),
        "example": [
            lambda df: zeonta.rsi(df["close"], length=14).tail(3),
        ],
    },
    "stoch": {
        "title": "Stochastic Oscillator",
        "formula": (
            "%K = 100 x (Close - LowestLow(n)) / (HighestHigh(n) - LowestLow(n)); %K(smoothed) = "
            "SMA(%K, smoothK); %D = SMA(%K smoothed, smoothD)"
        ),
        "about": (
            "Where did this bar close inside its recent range — at the top, the bottom, or the "
            "middle? That is the entire idea. Closing near the highs of the last n bars scores near "
            "100; closing near the lows scores near 0."
        ),
        "reading": (
            "Above 80 means closes are clustering at the top of the range, below 20 at the bottom. "
            "The `%D` line is the smoothed signal; `%K` crossing above `%D` from a low reading is "
            "the classic long trigger."
        ),
        "pitfalls": (
            "The stochastic is built for ranges, and in a trend it saturates: it pins near 100 for "
            "the whole of a strong advance, generating a stream of premature sell signals. Filter "
            "it with a trend measure such as ADX before acting on extremes."
        ),
        "example": [
            lambda df: zeonta.stoch(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "macd": {
        "title": "MACD (Moving Average Convergence Divergence)",
        "formula": (
            "MACD Line = EMA(12) - EMA(26); Signal Line = EMA(9) of MACD Line; Histogram = "
            "MACD Line - Signal Line"
        ),
        "about": (
            "MACD turns the distance between a fast and a slow EMA into its own series. That "
            "distance grows when a trend accelerates and shrinks when it tires, which makes MACD a "
            "momentum reading built entirely out of trend tools."
        ),
        "reading": (
            "The histogram is the part most people actually trade: it crosses zero exactly when the "
            "MACD line crosses its signal, and its height shows how fast the gap is changing. MACD "
            "above zero means the fast EMA is above the slow one — an uptrend by that definition."
        ),
        "pitfalls": (
            "MACD is unbounded and its values scale with price, so a reading of 3 means something "
            "entirely different on a $20 stock and a $2,000 one — never compare raw MACD across "
            "symbols. And as a doubly smoothed trend tool it whipsaws badly in a range."
        ),
        "example": [
            lambda df: zeonta.macd(df["close"]).tail(3),
        ],
    },
    "cci": {
        "title": "Commodity Channel Index (CCI)",
        "formula": (
            "TP = (High + Low + Close) / 3; CCI = (TP - SMA(TP, 20)) / (0.015 x "
            "MeanDeviation(TP, 20))"
        ),
        "about": (
            "CCI measures how far typical price has strayed from its own average, expressed in "
            "units of that period's normal deviation. Despite the name it has nothing to do with "
            "commodities specifically — it works on anything."
        ),
        "reading": (
            "The 0.015 constant is chosen so that roughly 70-80% of readings fall between -100 and "
            "+100. Moves outside that band mark unusual displacement: either an exhausted extreme "
            "or, in the trend-following reading, a breakout worth joining."
        ),
        "pitfalls": (
            'CCI is unbounded, so "+100 is overbought" is a convention, not a ceiling — strong '
            "trends routinely print +300. The two standard interpretations (fade the extreme vs. "
            "follow the breakout) are opposites, so decide which one you are using before you trade "
            "it."
        ),
        "example": [
            lambda df: zeonta.cci(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "bbands": {
        "title": "Bollinger Bands",
        "formula": (
            "Middle Band = SMA(Close, 20); Upper Band = Middle + 2 x StdDev(Close, 20); Lower Band "
            "= Middle - 2 x StdDev(Close, 20)"
        ),
        "about": (
            "A moving average with an envelope whose width is set by recent volatility. When the "
            "market gets quiet the bands squeeze in; when it gets violent they flare out. That "
            "self-adjusting width is the whole point."
        ),
        "reading": (
            "`BBB` (bandwidth) is the number to watch for compression — a multi-month low in "
            "bandwidth precedes most large moves. `BBP` (percent-B) locates price inside the bands: "
            "`0` sits on the lower band, `1` on the upper, and values outside `0..1` mean price has "
            "closed beyond them."
        ),
        "pitfalls": (
            'Touching the upper band is not a sell signal. In a strong trend price "walks the '
            'band", riding it for dozens of bars — Bollinger himself said the bands are a relative '
            "measure of high and low, not a trading system. Note also that the standard deviation "
            "here is the population one (`ddof=0`), matching charting platforms."
        ),
        "example": [
            lambda df: zeonta.bbands(df["close"], length=20, std=2).tail(3),
        ],
    },
    "atr": {
        "title": "Average True Range (ATR)",
        "formula": (
            "TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|); ATR = Wilder-smoothed "
            "average of TR over 14 periods (first ATR = SMA(TR,14), then ATR = (PrevATR x 13 + TR) "
            "/ 14)"
        ),
        "about": (
            "How far does this symbol typically move in one bar? ATR answers that in the "
            "instrument's own units. Because true range includes the gap from the previous close, "
            "it does not understate volatility on a market that jumps overnight."
        ),
        "reading": (
            "ATR is the standard way to size a position and place a stop: a stop at 2 x ATR is the "
            'same amount of "room" whether you are trading a quiet bond ETF or a volatile '
            "small-cap. Rising ATR means conditions are getting wider, not that price is going up."
        ),
        "pitfalls": (
            "ATR is directionless — a crash and a melt-up produce the same reading. It is also an "
            "absolute figure, so an ATR of 5 is meaningless without knowing the price; divide by "
            "close if you need to compare across symbols."
        ),
        "example": [
            lambda df: zeonta.atr(df["high"], df["low"], df["close"], length=14).tail(3),
        ],
    },
    "true_range": {
        "title": "True Range",
        "formula": "TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)",
        "about": (
            "The raw, unsmoothed bar range that ATR averages. Exposed on its own because building "
            "custom volatility logic almost always starts here rather than with a smoothed ATR."
        ),
        "reading": (
            "Each value is that single bar's full extent including any gap from the previous close. "
            "Spikes mark the individual bars where something happened."
        ),
        "pitfalls": (
            "The first bar has no previous close, so it falls back to `High - Low` rather than "
            "being `NaN`. That single value is slightly understated by construction."
        ),
        "example": [
            lambda df: zeonta.true_range(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "keltner": {
        "title": "Keltner Channels",
        "formula": (
            "Middle Line = EMA(Close, 20); Upper Band = Middle + 2 x ATR(10); Lower Band = Middle "
            "- 2 x ATR(10)"
        ),
        "about": (
            "The same idea as Bollinger Bands with one substitution: ATR instead of standard "
            "deviation. Since ATR reacts more slowly than standard deviation, Keltner Channels stay "
            "smoother through a shock — which is precisely what makes the pair useful together."
        ),
        "reading": (
            "A close outside the channel is a genuine breakout candidate, since the channel widens "
            "far less eagerly than a Bollinger band does. Comparing the two channels is the basis "
            "of [squeeze](squeeze.md)."
        ),
        "pitfalls": (
            "Implementations differ more than you would expect: some use SMA rather than EMA for "
            "the centre line, and older versions use a simple high-low range instead of ATR. Check "
            "the definition before comparing this output against a chart."
        ),
        "example": [
            lambda df: zeonta.keltner(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "squeeze": {
        "title": "The Squeeze (TTM Squeeze)",
        "formula": (
            "Squeeze ON when BB Upper < KC Upper AND BB Lower > KC Lower (Bollinger Bands "
            "compressed fully inside Keltner Channels); Momentum = LinReg(Close - "
            "Avg(HighestHigh(n), LowestLow(n), SMA(Close,n)), n)"
        ),
        "about": (
            "Two volatility measures that react at different speeds, compared against each other. "
            "When the faster one (Bollinger) contracts inside the slower one (Keltner), volatility "
            "has compressed unusually far — and compressed volatility tends to expand."
        ),
        "reading": (
            "`SQZ_ON` marks the compression; the bar traders actually act on is the release, when "
            "`SQZ_OFF` first turns on. The momentum histogram supplies the direction: rising bars "
            "above zero at the release point up, falling bars below zero point down."
        ),
        "pitfalls": (
            "The squeeze says a move is likely, never which way — trading it without the momentum "
            "read is a coin flip. Note also that widening `kc_multiplier` pushes the Keltner bands "
            "further out and therefore makes squeezes **more** frequent, not less — some casual "
            "descriptions of this indicator claim the opposite, but that claim doesn't follow from "
            "the formula itself, which this library follows. "
            "The momentum midline uses the published TTM *nested* average — "
            "`avg(avg(hh, ll), sma)`, weighting the range midpoint and the SMA at one half each — "
            "rather than an equal three-way mean, which some casual descriptions suggest instead; "
            "values here will differ from an implementation that follows that reading literally."
        ),
        "example": [
            lambda df: zeonta.squeeze(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "supertrend": {
        "title": "SuperTrend",
        "formula": (
            "Basic Upper Band = hl2 + multiplier x ATR(period); Basic Lower Band = hl2 - multiplier "
            "x ATR(period); Final Upper Band trails downward only, Final Lower Band trails upward "
            "only; SuperTrend = Final Lower Band while price closes above it (uptrend), Final Upper "
            "Band while price closes below it (downtrend); a flip occurs when close crosses to the "
            "opposite band"
        ),
        "about": (
            "A single line that sits under price in an uptrend and above it in a downtrend. Unlike "
            "a moving average it does not smooth price into a lagging curve — it builds a "
            "volatility-adjusted band and lets the trend ride one side of it until price forces a "
            "flip."
        ),
        "reading": (
            "`SUPERTd` is the regime: `1.0` long-biased, `-1.0` short-biased. The one-way ratchet "
            "means the line only ever moves in the trend's favour, which makes it a natural trailing "
            "stop. `SUPERTl` and `SUPERTs` are the line masked to each regime, ready to plot in two "
            "colours."
        ),
        "pitfalls": (
            "SuperTrend has no opinion about trend strength — it flips identically on a powerful "
            "move and a feeble one. In a range it flips repeatedly, and trading it mechanically as "
            "a stop-and-reverse system produces a string of small losses. Pair it with a strength "
            "filter such as [adx](adx.md)."
        ),
        "example": [
            lambda df: zeonta.supertrend(
                df["high"], df["low"], df["close"], length=10, multiplier=3
            )[["SUPERT_10_3.0", "SUPERTd_10_3.0"]].tail(3),
        ],
    },
    "adx": {
        "title": "ADX / DMI",
        "formula": (
            "+DM = up-move if up-move > down-move and up-move > 0, else 0; -DM = down-move if "
            "down-move > up-move and down-move > 0, else 0; +DI = 100 x WilderSmooth(+DM, period) / "
            "ATR(period); -DI = 100 x WilderSmooth(-DM, period) / ATR(period); DX = 100 x |+DI - "
            "-DI| / (+DI + -DI); ADX = WilderSmooth(DX, period)"
        ),
        "about": (
            "Wilder's answer to a question most indicators dodge: is there a trend here at all? ADX "
            "measures trend strength without caring about direction, while the +DI/-DI pair "
            "supplies the direction separately."
        ),
        "reading": (
            "Readings below 20 mean no usable trend, above 25 a trend worth following, and above 40 "
            "a strong one. Which DI line is on top tells you the direction: `DMP` above `DMN` is an "
            "uptrend. ADX is the classic filter for indicators that misbehave in ranges."
        ),
        "pitfalls": (
            'A rising ADX in a downtrend is still a rising ADX — it never says "bullish". Because '
            "it smooths an already-smoothed series it needs roughly `2 x length` bars before it "
            "produces anything, and it turns late by construction."
        ),
        "example": [
            lambda df: zeonta.adx(df["high"], df["low"], df["close"], length=14).tail(3),
        ],
    },
    "ichimoku": {
        "title": "Ichimoku",
        "formula": (
            "Tenkan-sen = (Highest High(9) + Lowest Low(9)) / 2; Kijun-sen = (Highest High(26) + "
            "Lowest Low(26)) / 2; Senkou Span A = (Tenkan-sen + Kijun-sen) / 2, plotted 26 periods "
            "ahead; Senkou Span B = (Highest High(52) + Lowest Low(52)) / 2, plotted 26 periods "
            "ahead; Chikou Span = Close, plotted 26 periods behind"
        ),
        "about": (
            "A complete system rather than a single indicator: five lines that between them give "
            "trend, momentum, and support and resistance in one glance. The cloud between the two "
            "Senkou spans is projected 26 bars into the future, which is what makes Ichimoku look "
            "unlike anything else on a chart."
        ),
        "reading": (
            "Price above the cloud is bullish, below it bearish, inside it undecided. A thick cloud "
            "is strong support or resistance; a thin one is easily cut through. This function "
            "returns two frames — the on-chart lines, and the part of the cloud that lands beyond "
            "the last bar."
        ),
        "pitfalls": (
            "The forward cloud is not a forecast: it is today's midpoints drawn 26 bars to the "
            "right, and it will not change when it gets there. Also, the default 9/26/52 settings "
            "come from a six-day Japanese trading week; they carry no special meaning on a "
            "five-day or 24/7 market."
        ),
        "example": [
            lambda df: zeonta.ichimoku(df["high"], df["low"], df["close"])[0].tail(2),
            lambda df: zeonta.ichimoku(df["high"], df["low"], df["close"])[1].head(2),
        ],
    },
    "donchian": {
        "title": "Donchian Channels",
        "formula": (
            "Upper Channel = Highest High(n); Lower Channel = Lowest Low(n); Middle Line = "
            "(Upper Channel + Lower Channel) / 2"
        ),
        "about": (
            "The simplest channel there is: the highest high and lowest low of the last n bars. Its "
            "simplicity is the point — the original Turtle Trading system was built almost entirely "
            "on breakouts of this channel."
        ),
        "reading": (
            "A close at the upper channel means this bar made the highest high of the last n bars — "
            "that statement *is* the breakout signal. The middle line is a common exit for a "
            "position entered on a breakout."
        ),
        "pitfalls": (
            'The channel includes the current bar, so price can never close outside it — "price '
            'broke above the channel" really means "price reached the channel". Compare against '
            "the previous bar's channel if you want a breakout that excludes the breaking bar."
        ),
        "example": [
            lambda df: zeonta.donchian(df["high"], df["low"], length=20).tail(3),
        ],
    },
    "vwap": {
        "title": "VWAP (Volume-Weighted Average Price)",
        "formula": (
            "Typical Price = (High + Low + Close) / 3; VWAP = sum(Typical Price x Volume) / "
            "sum(Volume), reset at each session open; Upper/Lower Band = VWAP +/- k x "
            "stdev(Typical Price, weighted by volume)"
        ),
        "about": (
            "The average price actually paid today, weighted by how much traded at each level. It "
            "is not a chart study so much as a benchmark: institutions are measured against VWAP, "
            "which is why price gravitates to it."
        ),
        "reading": (
            "Price above VWAP means buyers are paying up relative to the session's average. The "
            'bands mark statistically stretched levels within the session. Use `anchor="session"` '
            'on instruments with a real open, and `anchor="rolling"` on 24/7 markets like crypto.'
        ),
        "pitfalls": (
            "A VWAP that never resets is a different statistic entirely and loses the benchmark "
            "meaning — the reset is the point. Session anchoring needs a `DatetimeIndex` to find "
            "session boundaries; without one this function raises rather than silently computing "
            "the wrong thing."
        ),
        "example": [
            lambda df: zeonta.vwap(
                df["high"], df["low"], df["close"], df["volume"], anchor="rolling", length=20
            ).tail(3),
        ],
    },
    "fib_retracement": {
        "title": "Fibonacci Retracement",
        "formula": (
            "Ratios = 0.236, 0.382, 0.5, 0.618, 0.786 (derived from the Fibonacci sequence, 0.5 "
            "included by convention); after an uptrend, level = High - (High - Low) x ratio; after "
            "a downtrend, level = Low + (High - Low) x ratio; extensions use the same ratios beyond "
            "100% (127.2%, 161.8%, 261.8%) to project targets"
        ),
        "about": (
            "After a strong move, price rarely goes straight on — it gives some back. Fibonacci "
            "retracement marks the fractions of that move where the pullback most often stops. This "
            "implementation picks the swing automatically from a rolling window."
        ),
        "reading": (
            "The 0.382-0.618 zone is where most tradeable pullbacks end; 0.786 is the last level "
            "before the move is usually considered failed. `FIBDIR` tells you which way the swing "
            "ran, so you know whether levels are measured down from the high or up from the low."
        ),
        "pitfalls": (
            "Fibonacci levels work because enough traders draw the same lines, not because of "
            "anything physical. Two people picking different swings get different levels and both "
            'can be "right". Since the swing here is recomputed each bar, the levels repaint as '
            "new extremes print."
        ),
        "example": [
            lambda df: zeonta.fib_retracement(df["high"], df["low"], lookback=60)[
                ["FIB_0", "FIB_0.382", "FIB_0.618", "FIB_1", "FIBDIR"]
            ].tail(3),
        ],
    },
    "pivot_points": {
        "title": "Pivot Points",
        "formula": (
            "Classic: Pivot = (High + Low + Close) / 3; R1 = 2xPivot - Low; S1 = 2xPivot - High; "
            "R2 = Pivot + (High - Low); S2 = Pivot - (High - Low); R3 = Pivot + 2x(High - Low); "
            "S3 = Pivot - 2x(High - Low). Fibonacci: R1/S1 = Pivot +/- 0.382x(High - Low); R2/S2 = "
            "Pivot +/- 0.618x(High - Low); R3/S3 = Pivot +/- 1.0x(High - Low)"
        ),
        "about": (
            "A grid of levels for today, computed from yesterday's range before the market even "
            "opens. Floor traders used them precisely because they need no chart and no "
            "recalculation during the session."
        ),
        "reading": (
            "The central pivot is the day's reference: trading above it is a bullish session, below "
            "it bearish. R1/S1 are the levels reached on an ordinary day; R3/S3 only come into play "
            "on a big one. Feed daily bars for daily pivots, weekly bars for weekly ones."
        ),
        "pitfalls": (
            "Pivots are arithmetic, not analysis — they carry no information beyond the previous "
            "bar's range and work mainly as a shared reference grid. They are far less meaningful "
            "on instruments without a real session boundary. Classic R3/S3 has no single "
            "universally cited formula (StockCharts' own Classic page does not define R3/S3 at "
            "all); this library follows TradingView's own documented formula, confirmed "
            "empirically against a live reading."
        ),
        "example": [
            lambda df: zeonta.pivot_points(df["high"], df["low"], df["close"], kind="classic").tail(
                2
            ),
        ],
    },
    "divergence": {
        "title": "Divergences",
        "formula": (
            "Regular Bearish = price Higher High + oscillator Lower High; Regular Bullish = price "
            "Lower Low + oscillator Higher Low; Hidden Bearish = price Lower High + oscillator "
            "Higher High; Hidden Bullish = price Higher Low + oscillator Lower Low"
        ),
        "about": (
            "When price makes a new extreme but the oscillator does not, the move is being made "
            "with less force than the one before it. That disagreement — divergence — is one of the "
            "few genuinely forward-looking things in technical analysis."
        ),
        "reading": (
            "Regular divergence argues the trend is tiring and a reversal is closer. Hidden "
            "divergence argues the opposite: a pullback inside a trend is ending and the trend is "
            "about to resume. The default oscillator is RSI(14); pass any series via `oscillator`."
        ),
        "pitfalls": (
            "A divergence is a warning, not a signal — in a strong trend an oscillator can diverge "
            "three or four times while price keeps going, and each one looks convincing in "
            "hindsight. Wait for price confirmation. Note too that flags land on the pivot bar, "
            "which is only knowable `right` bars later: shift the output before backtesting."
        ),
        "example": [
            lambda df: zeonta.divergence(df["high"], df["low"], df["close"], left=5, right=5).sum(),
        ],
    },
    "momentum": {
        "title": "Momentum",
        "formula": "Momentum = Close - Close (n periods ago)",
        "about": (
            "The plainest possible momentum reading: how much has price moved, in its own units, "
            "over the last n bars? No smoothing, no normalisation — just today's close minus the "
            "close from n bars back."
        ),
        "reading": (
            "Above zero means price is higher than it was n bars ago (rising momentum); below zero "
            "means it is lower. The line's own slope — is momentum itself accelerating or fading — "
            "is usually more informative than the zero crossing alone."
        ),
        "pitfalls": (
            "Being expressed in raw price units means a Momentum reading of 2 means nothing without "
            "knowing the instrument's price level — never compare it across symbols. Use "
            "[roc](roc.md) instead when you need a percentage that is comparable across symbols or "
            "over a long history where the price level itself has changed a lot."
        ),
        "example": [
            lambda df: zeonta.momentum(df["close"], length=10).tail(3),
        ],
    },
    "roc": {
        "title": "Rate of Change (ROC)",
        "formula": "ROC = [(Close - Close n periods ago) / (Close n periods ago)] x 100",
        "about": (
            "The normalised sibling of [momentum](momentum.md): the same n-bars-back comparison, "
            "expressed as a percentage instead of a raw price difference. That one change makes it "
            "comparable across symbols and across price levels of the same symbol over time."
        ),
        "reading": (
            'ROC oscillates around zero the same way Momentum does, but a reading of "+5" always '
            "means the same thing — a 5% rise over the window — whether the symbol trades at $10 or "
            "$10,000. Sharp spikes away from zero mark unusually fast moves relative to the "
            "instrument's own recent pace."
        ),
        "pitfalls": (
            "ROC divides by the price n bars ago, so it is undefined (returned as `NaN`) on any bar "
            "whose reference close happened to be exactly zero — a real possibility on instruments "
            "quoted as a spread or a rate rather than a price. It also inherits Momentum's whipsaw "
            "behaviour in a range: a fast oscillation with no persistent trend behind it."
        ),
        "example": [
            lambda df: zeonta.roc(df["close"], length=12).tail(3),
        ],
    },
    "kalman_filter": {
        "title": "Kalman Filter",
        "formula": (
            "On log(Close): predict P = P_prev + process_variance; correct "
            "K = P / (P + measurement_variance), x = x_prev + K x (log(Close) - x_prev), "
            "P = (1 - K) x P; seeded x = log(Close[0]), P = 1.0; output = exp(x)"
        ),
        "about": (
            "The Kalman filter (Kalman, 1960) is the textbook recursive estimator for a hidden "
            "quantity observed through noise — used everywhere from spacecraft guidance to GPS. "
            "Applied to log(Close), it treats the 'true' price level as a random walk observed "
            "noisily bar by bar, and updates a minimum-mean-square-error estimate of it one bar "
            "at a time. There's no fixed window and no hand-picked smoothing constant like an "
            "EMA's `length` — the filter's own running confidence in its estimate (`P`) decides "
            "how much weight each new bar gets."
        ),
        "reading": (
            "Read it like any other adaptive moving average — trend direction, dynamic "
            "support/resistance. `process_variance`/`measurement_variance` set the "
            "smoothness/responsiveness trade-off the way `length` does for an EMA: smaller "
            "`process_variance` relative to `measurement_variance` trusts the running estimate "
            "more and produces a smoother, slower line."
        ),
        "pitfalls": (
            "There is no single 'correct' process_variance/measurement_variance pairing — unlike "
            "the filter's own update equations (a single, universally cited formulation), the "
            "noise variances are a tuning choice specific to the instrument and timeframe, the "
            "same way an EMA's `length` is. Filtering happens in log-price space specifically so "
            "the defaults stay roughly scale-free across instruments at very different price "
            "levels; passing raw non-log values elsewhere and comparing variances across two "
            "differently-scaled instruments directly would be a mismatch."
        ),
        "example": [
            lambda df: zeonta.kalman_filter(df["close"]).tail(3),
        ],
    },
    "kama": {
        "title": "Kaufman's Adaptive Moving Average (KAMA)",
        "formula": (
            "Efficiency Ratio ER = |Close - Close (n periods ago)| / Sum(|Close - Prior Close|, n); "
            "Smoothing Constant SC = [ER x (fastest SC - slowest SC) + slowest SC]^2, where fastest "
            "SC = 2/(fast+1) and slowest SC = 2/(slow+1); KAMA = Prior KAMA + SC x (Close - Prior KAMA)"
        ),
        "about": (
            "Every fixed-length moving average is a compromise: short enough to catch real moves, "
            "long enough to ignore noise, and wrong for whichever regime it wasn't tuned for. KAMA "
            "sidesteps the trade-off by measuring, bar by bar, how efficiently price is trending "
            "(the Efficiency Ratio) and using that to slide its own speed between a fast and a slow "
            "EMA automatically."
        ),
        "reading": (
            "Read it exactly like any other moving average — trend direction, support/resistance, "
            "crossovers — but trust it more through a regime change: it tightens onto price by "
            "itself when a clean trend starts and flattens out by itself when the market goes "
            "choppy, without you re-tuning a length."
        ),
        "pitfalls": (
            "KAMA is still reactive, not predictive — it adapts to a regime change after price has "
            "already started moving differently, the same lag every moving average has, just with a "
            "self-adjusting length. The Efficiency Ratio itself is noisy on short windows, so very "
            "small `length` values can make KAMA's speed jump around almost as much as price does."
        ),
        "example": [
            lambda df: zeonta.kama(df["close"], length=10, fast=2, slow=30).tail(3),
        ],
    },
    "parabolic_sar": {
        "title": "Parabolic SAR",
        "formula": (
            "Rising: Current SAR = Prior SAR + Prior AF x (Prior EP - Prior SAR); Falling: Current "
            "SAR = Prior SAR - Prior AF x (Prior SAR - Prior EP); AF starts at 0.02, increases by "
            "0.02 with each new extreme point, capped at 0.20; SAR cannot move above the prior two "
            "periods' lows in an uptrend, nor below the prior two periods' highs in a downtrend"
        ),
        "about": (
            "A series of dots that sit under price in an uptrend and above it in a downtrend, one "
            'step closer to price every bar. "Parabolic" describes the shape of that approach: the '
            "acceleration factor grows every time a new high (or low) prints, so the dots curve in "
            "toward price faster and faster the longer a trend runs."
        ),
        "reading": (
            "Most traders use it exactly as its name suggests: a stop that trails price and flips "
            'sides ("stop and reverse") the moment price crosses it. `PSARd` gives the regime '
            "directly (`1.0` long-biased, `-1.0` short-biased); `PSARl`/`PSARs` are the dots "
            "pre-split for two-colour plotting, matching [supertrend](supertrend.md)'s convention."
        ),
        "pitfalls": (
            "The accelerating AF is a double-edged sword: it rides a strong trend tightly, but it "
            "also means SAR gives back less and less room the longer a trend runs, so a normal "
            "pullback late in a trend can trigger a reversal that a wider stop would have survived. "
            "Like [supertrend](supertrend.md), it whipsaws repeatedly in a range and carries no "
            "opinion about trend strength — pair it with a filter such as [adx](adx.md)."
        ),
        "example": [
            lambda df: zeonta.parabolic_sar(df["high"], df["low"]).tail(3),
        ],
    },
    "obv": {
        "title": "On-Balance Volume (OBV)",
        "formula": (
            "If Close > Prior Close: OBV = Prior OBV + Volume; if Close < Prior Close: OBV = Prior "
            "OBV - Volume; if Close = Prior Close: OBV = Prior OBV (unchanged)"
        ),
        "about": (
            "The oldest and simplest way to combine volume with direction: add the bar's volume when "
            "price closed up, subtract it when price closed down, and run a cumulative total. The "
            "idea behind it — volume leads price — is what [divergence](divergence.md) between OBV "
            "and price is built to catch."
        ),
        "reading": (
            "The absolute level means nothing (it depends entirely on where the running total "
            "happened to start); what matters is its slope and whether that slope agrees with "
            "price's. OBV rising while price is flat or falling is read as accumulation building "
            "under the surface — the classic bullish divergence."
        ),
        "pitfalls": (
            "OBV treats every bar's entire volume as either fully bullish or fully bearish based on "
            "the close alone, ignoring how the bar actually traded intrabar — a bar that opened low, "
            "spiked high, and drifted back down to close marginally up still counts as 100% buying "
            "volume. [cmf](cmf.md) uses the bar's full range instead and is less crude on this point."
        ),
        "example": [
            lambda df: zeonta.obv(df["close"], df["volume"]).tail(3),
        ],
    },
    "cmf": {
        "title": "Chaikin Money Flow (CMF)",
        "formula": (
            "Money Flow Multiplier = ((Close - Low) - (High - Close)) / (High - Low); Money Flow "
            "Volume = Money Flow Multiplier x Volume; CMF = Sum(Money Flow Volume, n) / Sum(Volume, n)"
        ),
        "about": (
            "[obv](obv.md)'s more careful cousin: instead of asking only whether the close was up or "
            "down, CMF asks *where inside the bar's full range* the close landed, and weights that "
            "position by volume. A close pinned to the high of the range scores close to +1; a close "
            "pinned to the low scores close to -1."
        ),
        "reading": (
            "Sustained readings above zero over the window mean volume has concentrated on bars that "
            "closed strong — buying pressure. Traders often use the zero line itself as a trend "
            'filter ("only take longs while CMF is positive") rather than trading specific levels.'
        ),
        "pitfalls": (
            "A bar with a very narrow high-low range makes the Money Flow Multiplier's denominator "
            "tiny, so ordinary volume on a quiet bar can swing CMF sharply even though nothing much "
            "happened — this implementation defines that degenerate case as `0` rather than letting "
            "it blow up, but a run of narrow-range bars can still make CMF noisier than the price "
            "action underneath it would suggest."
        ),
        "example": [
            lambda df: zeonta.cmf(df["high"], df["low"], df["close"], df["volume"], length=20).tail(
                3
            ),
        ],
    },
    "mfi": {
        "title": "Money Flow Index (MFI)",
        "formula": (
            "Typical Price = (High + Low + Close) / 3; Raw Money Flow = Typical Price x Volume; "
            "Money Flow Ratio = Sum(Positive Money Flow, n) / Sum(Negative Money Flow, n); MFI = "
            "100 - 100 / (1 + Money Flow Ratio)"
        ),
        "about": (
            "Take [rsi](rsi.md)'s exact machinery — gains and losses summed over a window, squeezed "
            'onto a 0-100 scale — and replace "price change" with "typical price times volume". '
            "The result answers a question RSI cannot: was this move backed by real participation, "
            "or did it happen on thin volume?"
        ),
        "reading": (
            'Read the 0-100 scale exactly like RSI — above 80 conventionally "overbought", below '
            '20 "oversold" — but treat an MFI reading that disagrees with RSI as the more '
            "informative signal: it means the volume behind the move doesn't match its price action."
        ),
        "pitfalls": (
            "Unlike RSI's Wilder-smoothed averages, MFI sums positive and negative flow with a plain "
            "(unsmoothed) rolling window, so it can be noisier bar to bar than RSI at the same "
            'length. It also inherits RSI\'s core caution: "overbought" is a description of '
            "momentum, not an instruction to sell — a strong trend can hold MFI above 80 for weeks."
        ),
        "example": [
            lambda df: zeonta.mfi(df["high"], df["low"], df["close"], df["volume"], length=14).tail(
                3
            ),
        ],
    },
    "wma": {
        "title": "Weighted Moving Average (WMA)",
        "formula": (
            "WMA = (P1 x n + P2 x (n-1) + ... + Pn x 1) / (n + (n-1) + ... + 1), where P1 is the "
            "most recent close and Pn is the oldest close in the window"
        ),
        "about": (
            "Sits directly between `sma` and `ema` in how it treats the window: every bar still "
            "gets a fixed, predictable weight (unlike EMA's decay that technically never reaches "
            "zero), but that weight now favours recent bars in a straight line instead of treating "
            "the whole window equally like SMA does."
        ),
        "reading": (
            "Read it exactly like `sma` — trend direction, support, crossovers — but expect it to "
            "turn sooner after a reversal since the most recent bars carry more weight. It is also "
            "the building block several other moving averages (like the Hull Moving Average) chain "
            "together to cut lag further."
        ),
        "pitfalls": (
            "The linear taper is a much gentler lag reduction than EMA's exponential one — at the "
            "same length, WMA sits closer to SMA than to EMA in how much it lags. It also inherits "
            "every fixed-length moving average's core limitation: no length is right for both a "
            "trending and a choppy market, unlike the adaptive :func:`~zeonta.kama`."
        ),
        "example": [
            lambda df: zeonta.wma(df["close"], length=20).tail(3),
        ],
    },
    "smma": {
        "title": "Smoothed Moving Average (SMMA)",
        "formula": (
            "SMMA[t] = SMMA[t-1] + (Close[t] - SMMA[t-1]) / n, seeded by the plain SMA of the "
            "first n bars"
        ),
        "about": (
            "The exact recursion J. Welles Wilder used throughout *New Concepts in Technical "
            "Trading Systems* (1978) for `rsi`, `atr` and `adx`, exposed here as its own line "
            "instead of staying buried inside those three. Algebraically identical to `ema` with "
            "`alpha = 1/n` instead of `2/(n+1)` — the same shape of formula, just a gentler "
            "smoothing constant, which is why Wilder's tools all feel a step calmer than a plain "
            "EMA-based equivalent at the same length."
        ),
        "reading": (
            "Read it like any other moving average — trend direction, dynamic support/resistance "
            "— but expect it to lag noticeably more than an EMA of the same stated length, since "
            "`alpha=1/n` is always smaller than EMA's `2/(n+1)` for any n > 1. It also never fully "
            "forgets old prices the way `wma`'s hard window edge does; every bar since warm-up "
            "still carries a shrinking sliver of weight."
        ),
        "pitfalls": (
            "Neither StockCharts nor Wikipedia document SMMA as its own named indicator — it "
            "appears only embedded inside RSI/ATR/ADX on those sites. The default length here "
            "(9) follows TradingView's own dedicated Smoothed Moving Average page rather than "
            "Wilder's own convention of 14 used for RSI/ATR/ADX, since no single source states a "
            "canonical default for SMMA as a standalone indicator; the recursion itself was "
            "independently confirmed against MetaTrader's MQL5 documentation."
        ),
        "example": [
            lambda df: zeonta.smma(df["close"], length=9).tail(3),
        ],
    },
    "dema": {
        "title": "Double Exponential Moving Average (DEMA)",
        "formula": "DEMA = (2 x EMA1) - EMA2, where EMA1 = EMA(Close, n) and EMA2 = EMA(EMA1, n)",
        "about": (
            "A single EMA always lags, because it is, by construction, still catching up to "
            "price. DEMA estimates that lag by smoothing the EMA a second time — the gap between "
            "EMA1 and EMA2 tells you roughly how far behind EMA1 has fallen — then adds that gap "
            "back once to cancel most of it out."
        ),
        "reading": (
            "Read it exactly like `ema` — trend direction, support, crossovers — but expect "
            "turns sooner: on a straight-line move DEMA carries essentially zero lag, a property "
            "`ema` alone never has."
        ),
        "pitfalls": (
            "Cancelling lag also cancels some of the smoothing that made moving averages useful "
            "in the first place — DEMA overshoots and whips around real reversals more than `ema` "
            "does, especially at short lengths. It also needs roughly twice the warm-up of a plain "
            "EMA (`EMA2` needs a full window of already-warmed-up `EMA1` values)."
        ),
        "example": [
            lambda df: zeonta.dema(df["close"], length=20).tail(3),
        ],
    },
    "tema": {
        "title": "Triple Exponential Moving Average (TEMA)",
        "formula": (
            "TEMA = (3 x EMA1) - (3 x EMA2) + EMA3, where EMA1 = EMA(Close, n), EMA2 = EMA(EMA1, "
            "n) and EMA3 = EMA(EMA2, n)"
        ),
        "about": (
            "The same lag-cancelling idea as `dema`, carried one smoothing pass further. Where a "
            "straight price move already cancels almost perfectly under DEMA, TEMA's extra term "
            "keeps that cancellation working on *curved* moves — accelerations and decelerations — "
            "where DEMA itself starts to fall behind again."
        ),
        "reading": (
            "Read it like `dema` or `ema`, but trust it most exactly where DEMA starts to slip: a "
            "trend that is itself speeding up or slowing down, not just moving in a straight line."
        ),
        "pitfalls": (
            "Three layers of lag-cancelling means three layers of overshoot risk — TEMA reacts to "
            "noise even more eagerly than `dema` does, and needs roughly three times a plain EMA's "
            "warm-up (`EMA3` needs a full window of already-warmed-up `EMA2` values)."
        ),
        "example": [
            lambda df: zeonta.tema(df["close"], length=20).tail(3),
        ],
    },
    "hma": {
        "title": "Hull Moving Average (HMA)",
        "formula": (
            "Raw = (2 x WMA(Close, Integer(n/2))) - WMA(Close, n); HMA = WMA(Raw, "
            "Integer(sqrt(n))) — both intermediate lengths truncated toward zero, per Alan "
            "Hull's own formula, not rounded to the nearest whole number"
        ),
        "about": (
            "`wma` alone reduces lag only modestly next to `sma`. Hull's insight: take a fast "
            "half-length WMA, double it, and subtract the full-length WMA — this extrapolates "
            "*ahead* of the fast WMA rather than just averaging alongside it. That extrapolation "
            "is jumpy on its own, so one more short WMA smooths it back into a genuinely quick yet "
            "still-smooth line."
        ),
        "reading": (
            "Read it like any other moving average, but expect it to hug price far more closely "
            "than `sma`, `ema` or plain `wma` at the same length — and to occasionally overshoot a "
            "sharp turn before settling, a direct consequence of the extrapolation step."
        ),
        "pitfalls": (
            "The same extrapolation that cuts lag also means HMA can overshoot past the actual "
            "turning point on a sharp reversal, briefly pointing the wrong way before correcting — "
            "unlike `sma`/`wma`, which merely lag, never overshoot. It is also the most compute-"
            "heavy moving average in this library (three WMA passes per bar). Some secondary "
            "write-ups describe the two intermediate lengths as rounded rather than truncated; "
            "this implementation follows Alan Hull's own formula (truncation), confirmed both "
            "against his own site and empirically against a live TradingView reading."
        ),
        "example": [
            lambda df: zeonta.hma(df["close"], length=20).tail(3),
        ],
    },
    "t3": {
        "title": "T3 Moving Average (Tillson)",
        "formula": (
            "GD(x, v) = (1 + v) x EMA(x, n) - v x EMA(EMA(x, n), n); T3 = GD(GD(GD(Close)))"
        ),
        "about": (
            'Tim Tillson\'s "Generalized DEMA" blends a plain EMA and a full `dema` by the '
            "``volume_factor`` — at ``v=1`` GD is exactly `dema`'s own formula, so T3 is literally "
            "`dema` cascaded through itself three times at that setting. Tillson's recommended "
            "``v=0.7`` sits short of that, trading a little of `dema`/`tema`'s speed for "
            "meaningfully less overshoot on a sharp reversal."
        ),
        "reading": (
            "Read it like `dema`/`tema` — a fast-reacting trend line to hug price closely — but "
            "expect fewer of the sharp overshoot spikes those two produce on a sudden reversal, "
            "which is the entire reason Tillson built it."
        ),
        "pitfalls": (
            "Neither StockCharts nor Wikipedia document T3 — Tillson published it in *Technical "
            "Analysis of Stocks & Commodities*, January 1998, not through either of those "
            "channels. The default length here (5) follows an independently maintained reference "
            "implementation (Stock Indicators for .NET/Python); no source surveyed states one "
            "length as canonical the way Tillson's own 0.7 volume factor is agreed on everywhere."
        ),
        "example": [
            lambda df: zeonta.t3(df["close"]).tail(3),
        ],
    },
    "williams_r": {
        "title": "Williams %R",
        "formula": ("%R = (HighestHigh(n) - Close) / (HighestHigh(n) - LowestLow(n)) x -100"),
        "about": (
            "The same range-position idea as `stoch`, developed independently by Larry Williams "
            "and published first: where the close sits inside the recent high-low range. Williams "
            "just inverted and shifted the scale — literally `%R = %K - 100` for the unsmoothed "
            "`%K` — so it reads 0 to -100 instead of 0 to 100."
        ),
        "reading": (
            'Readings from -20 to 0 are conventionally "overbought", -80 to -100 "oversold" — '
            "the exact mirror of `stoch`'s 80/20. A cross above -50 signals price trading in the "
            "upper half of its recent range, below -50 the lower half."
        ),
        "pitfalls": (
            "Being mathematically identical to unsmoothed `stoch` minus 100, it inherits exactly "
            "the same weakness: it saturates in a trend, pinning near 0 or -100 for as long as the "
            "trend runs, generating premature reversal signals the whole way. Pair it with a trend "
            "filter before acting on the extremes."
        ),
        "example": [
            lambda df: zeonta.williams_r(df["high"], df["low"], df["close"], length=14).tail(3),
        ],
    },
    "stoch_rsi": {
        "title": "Stochastic RSI (StochRSI)",
        "formula": (
            "StochRSI = (RSI - LowestLow(RSI, n)) / (HighestHigh(RSI, n) - LowestLow(RSI, n))"
        ),
        "about": (
            "Takes `stoch`'s exact range-position formula and applies it to `rsi` instead of "
            "price — an oscillator of an oscillator. RSI alone measures momentum; StochRSI "
            "measures how extreme *that* momentum reading is relative to its own recent history, "
            "which makes it swing between its bounds far more often and far more sharply than RSI "
            "itself ever does."
        ),
        "reading": (
            'Above 80 conventionally "overbought", below 20 "oversold" — but because StochRSI '
            "is so much more volatile than RSI, it spends far more time near those extremes, so "
            "treat crossings of the 50 line or %K crossing %D as more useful signals than the "
            "extremes alone."
        ),
        "pitfalls": (
            "When RSI itself goes flat — most obviously when it is pinned at 100 or 0 through a "
            "strong trend — StochRSI's own high-low range collapses to zero and the indicator "
            "falls back to the midpoint (50) rather than staying at an extreme, which can look "
            "like a reversal signal that isn't one. It is also a doubly-derived indicator (RSI of "
            "price, then Stochastic of RSI), so treat single readings with real caution."
        ),
        "example": [
            lambda df: zeonta.stoch_rsi(df["close"]).tail(3),
        ],
    },
    "awesome_oscillator": {
        "title": "Awesome Oscillator (AO)",
        "formula": (
            "MedianPrice = (High + Low) / 2; AO = SMA(MedianPrice, 5) - SMA(MedianPrice, 34)"
        ),
        "about": (
            'Bill Williams\' momentum reading, built from the same "fast SMA minus slow SMA" '
            "shape as `macd`, but with two differences: it uses the bar's own midpoint rather than "
            "the close, and contrasts two plain SMAs instead of two EMAs, so it carries no memory "
            "beyond each window's own edge."
        ),
        "reading": (
            "Read the histogram like `macd`'s: positive and rising is strengthening upward "
            "momentum, a colour/sign change at the zero line marks a shift in which side (5-bar or "
            '34-bar) is currently dominant. A widely cited pattern ("saucer") looks for two or '
            "three consecutive bars getting shorter then one getting taller, all on the same side "
            "of zero."
        ),
        "pitfalls": (
            "Using the bar's midpoint instead of the close means AO can shift even on a bar that "
            "closed flat, purely from an intrabar wick — it is reading range, not just direction. "
            "Being unbounded and denominated in price units, it also can't be compared across "
            "symbols or price levels the way a 0-100 oscillator can."
        ),
        "example": [
            lambda df: zeonta.awesome_oscillator(df["high"], df["low"]).tail(3),
        ],
    },
    "aroon": {
        "title": "Aroon and the Aroon Oscillator",
        "formula": (
            "Aroon-Up = ((n - DaysSinceHighestHigh) / n) x 100; Aroon-Down = ((n - "
            "DaysSinceLowestLow) / n) x 100; Aroon Oscillator = Aroon-Up - Aroon-Down"
        ),
        "about": (
            "Where `donchian` marks *where* the n-bar high and low currently sit in price terms, "
            "Aroon marks *how long ago* they happened. A fresh high scores Aroon-Up at 100 no "
            "matter how far away it is in price; a high from `n` bars back scores 0 even if price "
            "is still sitting right next to it — the whole indicator is about recency, not level."
        ),
        "reading": (
            "Aroon-Up above 70 with Aroon-Down below 30 signals a strong uptrend (highs keep "
            "getting made, lows are stale); the mirror image signals a downtrend. The Aroon "
            "Oscillator condenses both into one line around zero: sustained positive readings mark "
            "an uptrend bias, sustained negative ones a downtrend bias."
        ),
        "pitfalls": (
            "Aroon-Up and Aroon-Down can both be high or both be low at once (a choppy market can "
            "make fresh highs and fresh lows in the same window), which the oscillator alone "
            "hides by netting them against each other — check the two raw lines, not just the "
            "oscillator, before concluding there is no trend. Ties for the extreme value within "
            "the window are broken toward the most recent occurrence, per the source's own "
            "convention."
        ),
        "example": [
            lambda df: zeonta.aroon(df["high"], df["low"]).tail(3),
        ],
    },
    "adl": {
        "title": "Accumulation/Distribution Line (ADL)",
        "formula": (
            "MFM = ((Close - Low) - (High - Close)) / (High - Low); MFV = MFM x Volume; ADL = "
            "Previous ADL + MFV"
        ),
        "about": (
            "Where `obv` only asks whether the close was up or down and assigns the *entire* bar's "
            "volume to one side or the other, ADL asks *where inside the bar's full range* the "
            "close landed and weights volume by that graded position instead — a bar that closed "
            "near, but not exactly at, the high contributes most (not all) of its volume "
            "positively. It is also the running-total version of `cmf`, which instead sums the "
            "same per-bar flow over a fixed window and divides by volume to get a bounded ratio."
        ),
        "reading": (
            "Read it exactly like `obv`: the absolute level is arbitrary (it depends on where the "
            "series happens to start), only its *slope* and its agreement or disagreement with "
            "price matter. ADL rising while price is flat or falling is read as accumulation "
            "building beneath the surface — the same bullish-divergence idea `obv` is used for, "
            "just with a more graded input."
        ),
        "pitfalls": (
            "A very narrow high-low range makes the Money Flow Multiplier's denominator tiny, so "
            "ordinary volume on a quiet bar can swing ADL sharply even though little actually "
            "happened — this implementation defines the exact zero-range case as contributing "
            "nothing rather than blowing up, but near-zero ranges are still noisy. Like `obv`, it "
            "is a running total with no natural reset point, so comparing absolute levels across "
            "two different time windows tells you nothing."
        ),
        "example": [
            lambda df: zeonta.adl(df["high"], df["low"], df["close"], df["volume"]).tail(3),
        ],
    },
    "chaikin_oscillator": {
        "title": "Chaikin Oscillator",
        "formula": "ChaikinOsc = EMA(ADL, fast) - EMA(ADL, slow)",
        "about": (
            "The same fast-EMA-minus-slow-EMA shape `macd` applies to price, applied here to "
            "`adl` instead. ADL itself only tells you the cumulative *level* of buying versus "
            "selling pressure; taking the difference of two EMAs of it turns that into a "
            "rate-of-change reading — whether accumulation/distribution is currently speeding up "
            "or slowing down, the same relationship `awesome_oscillator` has to raw price."
        ),
        "reading": (
            "Read it like any zero-centred momentum oscillator: crossing above zero signals ADL "
            "is accelerating upward (buying pressure building faster than its own recent average), "
            "crossing below signals the opposite. A divergence between the Chaikin Oscillator and "
            "price — price making a new high while the oscillator fails to — is read the same "
            "bearish-divergence way `macd` divergence is."
        ),
        "pitfalls": (
            "Inherits every caveat `adl` has: a very narrow high-low range makes the underlying "
            "Money Flow Multiplier noisy, and the whole thing is built on a running total with no "
            "natural reset point. Because it is the difference of two EMAs, it also inherits "
            "`macd`'s own lag — both EMAs react to the same underlying series, so the oscillator "
            "reflects a *change* in ADL's trend a few bars after it actually happens, not at the "
            "moment it happens."
        ),
        "example": [
            lambda df: zeonta.chaikin_oscillator(
                df["high"], df["low"], df["close"], df["volume"]
            ).tail(3),
        ],
    },
    "chandelier_exit": {
        "title": "Chandelier Exit",
        "formula": (
            "Long = HighestHigh(n) - ATR(n) x multiplier; "
            "Short = LowestLow(n) + ATR(n) x multiplier"
        ),
        "about": (
            "A volatility-anchored trailing stop, the same core idea `supertrend` and "
            "`parabolic_sar` use, but built differently: instead of ratcheting forward bar by bar, "
            "it is recomputed fresh from the last `n` bars' extreme and ATR every single time. "
            "That makes it simpler to reason about — no internal state to track — but it also "
            "means, unlike those two, the line itself can move against an open position from one "
            "bar to the next."
        ),
        "reading": (
            "Hold a long position above `CELONG`; a close below it is the exit signal. Hold a "
            "short position below `CESHORT`; a close above it is the exit signal. Which line is "
            "relevant depends entirely on the position actually held — the indicator itself has no "
            "opinion about which side you are on."
        ),
        "pitfalls": (
            "Because each bar recomputes the stop from scratch rather than ratcheting it, a fresh "
            "(lower) high combined with a wider ATR reading can pull the long stop *down* even "
            "while the trend is fully intact — a real retreat, not a bug. Some charting platforms "
            "add an optional one-way ratchet on top of the plain formula; this implementation "
            "follows the published formula exactly, with no ratchet."
        ),
        "example": [
            lambda df: zeonta.chandelier_exit(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "vortex": {
        "title": "Vortex Indicator",
        "formula": (
            "+VM = |High - PriorLow|; -VM = |Low - PriorHigh|; "
            "+VI = Sum(+VM, n) / Sum(TR, n); -VI = Sum(-VM, n) / Sum(TR, n)"
        ),
        "about": (
            "Each line measures how far the current bar's range stretched away from the *opposite* "
            "extreme of the prior bar, summed over a window and normalised by the same window's "
            "true range. +VI leads -VI in an uptrend and the two cross around trend changes — the "
            "same directional-pair relationship `adx`'s +DI/-DI lines have, though Vortex uses "
            "plain rolling sums throughout rather than Wilder smoothing, so it reacts faster and "
            "forgets old bars completely once they age out of the window."
        ),
        "reading": (
            "A crossover of +VI above -VI is read as a bullish signal, the reverse as bearish — "
            "the further apart the two lines sit, the stronger the implied trend. Because the "
            "lines use plain sums, they respond quickly to a fresh burst of directional movement, "
            "which also means more crossovers (and more false signals) in a genuinely choppy market "
            "than a Wilder-smoothed pair like ADX's DI lines would give."
        ),
        "pitfalls": (
            "Vortex has no fixed upper bound the way RSI or Stochastic do — both lines typically "
            "sit somewhere around 0.5 to 1.5, but a sharp enough move can push either one higher "
            "still, so treat the absolute level with caution and lean on the crossover and the gap "
            "between the two lines instead."
        ),
        "example": [
            lambda df: zeonta.vortex(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "ultimate_oscillator": {
        "title": "Ultimate Oscillator",
        "formula": (
            "BP = Close - Min(Low, PriorClose); TR = Max(High, PriorClose) - Min(Low, PriorClose); "
            "Average_n = Sum(BP, n) / Sum(TR, n); "
            "UO = 100 x (4xAverage_fast + 2xAverage_medium + Average_slow) / 7"
        ),
        "about": (
            "Developed by Larry Williams specifically to fix single-period oscillators' tendency "
            "to give false divergence signals: by blending three different look-backs (weighted "
            "4:2:1 toward the fastest) into one line, a bearish-looking divergence on the short "
            "window alone gets outvoted when the two longer windows disagree. Buying Pressure (BP) "
            "and True Range (TR) are both measured against the *prior* close rather than the "
            "current bar's own open, so a gap is counted as part of that bar's range instead of "
            "being invisible to it."
        ),
        "reading": (
            "Readings above 70 are considered overbought, below 30 oversold — the classic buy "
            "signal Williams himself described is a bullish divergence (price makes a lower low, "
            "UO does not) that then breaks back above 50, all three conditions together rather than "
            "any one alone."
        ),
        "pitfalls": (
            "The three windows must satisfy `fast < medium < slow`; passing them out of order "
            "raises `ValueError` rather than silently computing something meaningless. Like RSI "
            "and Stochastic, being at an overbought or oversold reading is not by itself a signal "
            "to act — Williams' own rule requires the divergence-plus-50-break combination, not "
            "the raw level alone."
        ),
        "example": [
            lambda df: zeonta.ultimate_oscillator(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "elder_ray": {
        "title": "Elder Ray (Bull Power / Bear Power)",
        "formula": "EMA = EMA(Close, length); Bull Power = High - EMA; Bear Power = Low - EMA",
        "about": (
            "Developed by Alexander Elder as a way to look inside each individual bar relative to "
            "the prevailing trend rather than only at where it closed. Bull Power reads how far "
            "buyers managed to push price above the EMA within the bar; Bear Power reads how far "
            "sellers pushed it below. Two numbers per bar instead of one closing-price comparison "
            "captures the tug-of-war that happened *during* the bar, which the close alone erases."
        ),
        "reading": (
            "In a healthy uptrend, Bull Power stays positive while Bear Power stays negative but "
            "shrinks toward zero bar by bar — sellers are losing their grip even during pullbacks. "
            "Bear Power turning positive, or Bull Power turning negative, while the EMA itself is "
            "still rising is the classic Elder Ray warning that the trend has lost control of the "
            "bar and a reversal may be near."
        ),
        "pitfalls": (
            "On a steady, non-accelerating trend, the EMA's own fixed lag can exceed the bar's "
            "high-low spread, which flips Bear Power positive (in an uptrend) or Bull Power "
            "negative (in a downtrend) even though nothing about the trend has actually changed — "
            "a real property of how far a lagging EMA sits behind price, not a signal of weakness. "
            "Elder's own rule reads the two lines *together* with the EMA's slope, never Bull or "
            "Bear Power in isolation."
        ),
        "example": [
            lambda df: zeonta.elder_ray(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "trix": {
        "title": "TRIX (Triple Exponential Average)",
        "formula": (
            "EMA1 = EMA(Close, n); EMA2 = EMA(EMA1, n); EMA3 = EMA(EMA2, n); "
            "TRIX = (EMA3[t] - EMA3[t-1]) / EMA3[t-1] x 100"
        ),
        "about": (
            "Three EMA passes before ever measuring a change is a deliberately heavier filter than "
            "`roc`'s single comparison against an older price, or `macd`'s single-pass EMA "
            "difference — the tradeoff for that extra noise reduction is proportionally more lag "
            "before TRIX actually turns."
        ),
        "reading": (
            "Read the zero line and the signal line the same way as `macd`: crossing above zero is "
            "bullish, crossing below is bearish, and a cross of TRIX above/below its own signal "
            "line (a 9-day EMA of TRIX) gives an earlier, noisier version of the same call."
        ),
        "pitfalls": (
            "The triple smoothing that makes TRIX quiet also makes it slow — on a fast-moving or "
            "short-lived trend it can still be turning while the move is already over. It is "
            "usually applied to longer time frames (weekly charts, or long daily lengths) for "
            "exactly this reason."
        ),
        "example": [
            lambda df: zeonta.trix(df["close"]).tail(3),
        ],
    },
    "ppo": {
        "title": "Percentage Price Oscillator (PPO)",
        "formula": (
            "PPO = (EMA(Close, fast) - EMA(Close, slow)) / EMA(Close, slow) x 100; "
            "Signal = EMA(PPO, signal); Histogram = PPO - Signal"
        ),
        "about": (
            "Exactly `macd`'s construction, divided by the slow EMA to turn an absolute price "
            "difference into a percentage. A PPO reading of 5 means the fast EMA sits 5% above the "
            "slow one regardless of whether the security trades at $5 or $500 — a comparison "
            "`macd`'s own raw output cannot make across symbols."
        ),
        "reading": (
            "Read it exactly like `macd`: signal-line crossovers, centerline crossovers and "
            "divergences all carry the same meaning, just on a percentage scale that stays "
            "comparable when screening across many different symbols."
        ),
        "pitfalls": (
            "Because it divides by the slow EMA, a security whose price (and therefore whose EMA) "
            "crosses through zero makes PPO briefly undefined or wildly scaled — this only matters "
            "for spread/synthetic series that can go negative, not for ordinary prices."
        ),
        "example": [
            lambda df: zeonta.ppo(df["close"]).tail(3),
        ],
    },
    "tsi": {
        "title": "True Strength Index (TSI)",
        "formula": (
            "PC = Close - Close[1 bar ago]; DoubleSmoothedPC = EMA(EMA(PC, long), short); "
            "DoubleSmoothedAbsPC = EMA(EMA(|PC|, long), short); "
            "TSI = 100 x DoubleSmoothedPC / DoubleSmoothedAbsPC; Signal = EMA(TSI, signal)"
        ),
        "about": (
            "William Blau's double smoothing operates on the raw price change itself, before any "
            "ratio is taken — the opposite order from `rsi`, which first turns gains/losses into "
            "separate averages and only then divides. TSI's double-EMA-first approach is meant to "
            "track the underlying trend closely while still filtering short-term noise."
        ),
        "reading": (
            "Overbought/oversold readings, centerline crossovers, signal-line crossovers and "
            "divergences all apply, the same vocabulary as `rsi` and `macd` combined — TSI is "
            "somewhat unusual in that its peaks and troughs often line up closely with price's own "
            "peaks and troughs, unlike oscillators that flatten out during a strong sustained move."
        ),
        "pitfalls": (
            "Neither StockCharts nor Fidelity's guide commits to one canonical default signal-line "
            "period — this implementation uses 7 alongside the (25, 13) core smoothing pair, the "
            "value repeated most often across independent sources, but TSI(25,13,13) and "
            "TSI(40,20,10) are both also in common use."
        ),
        "example": [
            lambda df: zeonta.tsi(df["close"]).tail(3),
        ],
    },
    "dpo": {
        "title": "Detrended Price Oscillator (DPO)",
        "formula": "DPO = Close[n/2 + 1 bars ago] - SMA(Close, n)",
        "about": (
            "Every other oscillator in this library compares the *current* price against a "
            "moving average or a prior value; DPO instead compares an *older* price against the "
            "*current* SMA. That inversion is deliberate — it removes the trend component so the "
            "leftover oscillation lines up with the market's actual cycle peaks and troughs, at "
            "the cost of the line no longer reacting to the most recent bars at all."
        ),
        "reading": (
            "Count the bars between successive DPO peaks (or troughs) to estimate the dominant "
            "cycle length in the data, then use that estimate to set lengths for other tools. This "
            "is a cycle-identification tool, not a momentum or trend signal — it should not be "
            "read the way `macd` or `rsi` are."
        ),
        "pitfalls": (
            "Because it is deliberately shifted left (using an older price), the most recent DPO "
            "value does not reflect the most recent bars — it lags by design and cannot be used "
            "for a real-time signal the way it might naively appear on a chart."
        ),
        "example": [
            lambda df: zeonta.dpo(df["close"]).tail(3),
        ],
    },
    "coppock_curve": {
        "title": "Coppock Curve",
        "formula": "Coppock = WMA(ROC(Close, long) + ROC(Close, short), wma_length)",
        "about": (
            "Edwin Coppock built the two `roc` periods (14 and 11) around how long, in his "
            "research, it took investor sentiment to recover from a loss — unconventional inputs "
            "for a technical indicator, but the result is a slow, heavily-smoothed long-term "
            "momentum line. Summing two `roc` readings before smoothing gives it a broader view of "
            "momentum than either period alone."
        ),
        "reading": (
            "Originally designed for monthly charts to call major market bottoms: a buy signal is "
            "the Coppock Curve turning up from below zero. It was never meant for everyday trading "
            "signals or for calling tops — Coppock built it specifically as a long-term, "
            "buy-side-only tool."
        ),
        "pitfalls": (
            "Applying Coppock's own (14, 11, 10) settings to daily charts (rather than the monthly "
            "charts it was designed for) produces a much noisier, faster-turning line that no "
            "longer behaves like the major-bottom-calling tool it was built to be."
        ),
        "example": [
            lambda df: zeonta.coppock_curve(df["close"]).tail(3),
        ],
    },
    "force_index": {
        "title": "Force Index",
        "formula": "FI(1) = (Close - PriorClose) x Volume; FI(n) = EMA(FI(1), n)",
        "about": (
            "Alexander Elder's combination of price direction, price magnitude and volume into one "
            "line — a bar that moves further on more volume produces a proportionally larger "
            "reading than the same move on light volume, something a pure price indicator like "
            "`momentum` cannot see. It is the same author's indicator as `elder_ray`, viewing "
            "buying/selling pressure through volume instead of through price relative to an EMA."
        ),
        "reading": (
            "A rising Force Index confirms an uptrend (price advancing on strong volume); a "
            "falling one during an uptrend, or a bearish divergence against price, warns that the "
            "advance is losing conviction. Elder himself used both a short unsmoothed version "
            "(``length=1``, or 2) for entry timing and the smoothed 13-period version for the "
            "underlying trend."
        ),
        "pitfalls": (
            "Like `obv` and `adl`, only its sign and slope are meaningful — the absolute level "
            "scales directly with the security's own typical share volume, so it cannot be "
            "compared across different symbols."
        ),
        "example": [
            lambda df: zeonta.force_index(df["close"], df["volume"]).tail(3),
        ],
    },
    "ease_of_movement": {
        "title": "Ease of Movement (EMV)",
        "formula": (
            "DistanceMoved = (High+Low)/2 - (PriorHigh+PriorLow)/2; "
            "BoxRatio = (Volume/100,000,000) / (High-Low); "
            "EMV(1) = DistanceMoved / BoxRatio; EOM = SMA(EMV(1), n)"
        ),
        "about": (
            "Richard Arms' box-ratio idea directly compares a bar's price movement against how "
            "much volume that movement needed — the same underlying question `chaikin_oscillator` "
            "and `mfi` ask, from a different angle. A large price move on light volume scores much "
            "higher than the same move on heavy volume."
        ),
        "reading": (
            "Sustained positive readings mean price is advancing easily — little volume is needed "
            "per unit of price movement, a healthy uptrend. Readings near or below zero mean price "
            "is struggling against volume to move at all, whether flat or actively declining."
        ),
        "pitfalls": (
            "A zero-range bar or a zero-volume bar makes the box ratio degenerate (a zero or "
            "infinite denominator); this implementation treats either case as contributing ``0`` "
            "to the raw EMV rather than raising or producing ``inf``/``NaN``, the same convention "
            "`cmf`'s Money Flow Multiplier uses for its own zero-range case."
        ),
        "example": [
            lambda df: zeonta.ease_of_movement(df["high"], df["low"], df["volume"]).tail(3),
        ],
    },
    "ulcer_index": {
        "title": "Ulcer Index",
        "formula": (
            "PercentDrawdown = (Close - HighestClose(n)) / HighestClose(n) x 100; "
            "UI = sqrt(mean(PercentDrawdown^2, n))"
        ),
        "about": (
            "Unlike `atr` or `bbands`, which measure movement in *either* direction, the Ulcer "
            "Index (Peter Martin, 1987) only measures how far price has fallen from its own recent "
            "high — squaring the drawdown before averaging means a single deep decline dominates "
            "the reading far more than several small ones of the same total size, mirroring how a "
            "real drawdown actually feels to hold through."
        ),
        "reading": (
            "Higher readings mean deeper, more sustained drawdowns — a security a risk-averse "
            "holder would find harder to sit through, even if its raw price swings (as measured by "
            "`atr`) are not especially large. Comparing the Ulcer Index across candidate "
            "investments is a way to rank them by how much drawdown pain they have historically "
            "caused, independent of their average return."
        ),
        "pitfalls": (
            "Originally designed with mutual funds in mind and focused purely on downside risk — "
            "it says nothing about upside potential, so it should complement a return measure, not "
            "replace one."
        ),
        "example": [
            lambda df: zeonta.ulcer_index(df["close"]).tail(3),
        ],
    },
    "linreg": {
        "title": "Linear Regression Slope & Forecast",
        "formula": (
            "Fits an ordinary-least-squares line y = mx + b to the last n closes; "
            "Slope = m; Forecast = the fitted line's value at the most recent bar"
        ),
        "about": (
            "StockCharts documents these as two separate indicators — Slope (default 20) and "
            "Linear Regression Forecast (default 14) — but both come from the exact same "
            "regression fit this library already computes inside `trend_channel` and `squeeze`, so "
            "they are exposed here as two columns from one call, sharing one length parameter, "
            "following the convention most platforms with a combined `LINEARREG` indicator family "
            "use."
        ),
        "reading": (
            "``LRSlope`` reads like any trend-strength measure: its sign gives direction, its "
            "magnitude gives steepness, directly comparable to `~zeonta.aroon`'s trend read from a "
            "completely different angle. ``LRForecast`` tracks price closely, like a smoothed "
            "moving average, but overshoots less on a sharp reversal since it fits a straight line "
            "rather than weighting recent bars more heavily."
        ),
        "pitfalls": (
            '"Forecast" describes what the line represents (StockCharts\' own name for it), not '
            "a claim about the future: ``LRForecast`` is the fitted value at the *current*, "
            "already-known bar, not a projection beyond it — using it as an actual price "
            "prediction is a misreading of the name."
        ),
        "example": [
            lambda df: zeonta.linreg(df["close"]).tail(3),
        ],
    },
    "fisher_transform": {
        "title": "Fisher Transform (Ehlers)",
        "formula": (
            "Position = (Price - LowestPrice(n)) / (HighestPrice(n) - LowestPrice(n)) - 0.5; "
            "Value1 = 0.33 x 2 x Position + 0.67 x Value1[t-1], clamped to +/-0.999; "
            "Fish = 0.5 x ln((1 + Value1) / (1 - Value1)) + 0.5 x Fish[t-1]"
        ),
        "about": (
            "Ordinary price data has a roughly uniform-to-bimodal distribution, not the Gaussian "
            "(bell-curve) one most statistical tools quietly assume. Ehlers' insight was to "
            "reshape a normalised price into something close to Gaussian — under that reshaping, "
            "large deviations become genuinely rare events instead of routine noise, which is "
            "exactly what makes the transform's turning points sharper and more decisive than an "
            "oscillator built directly from price."
        ),
        "reading": (
            "Read ``FISHERT``/``FISHERTs`` as a crossover pair the same way `macd`'s line and "
            "signal are read: the sharpness Ehlers built into this transform means the crossovers "
            "tend to occur right at genuine turning points rather than lagging behind them the "
            "way a rounded indicator like `macd` does."
        ),
        "pitfalls": (
            "The sharp, decisive turns are a direct consequence of amplifying values near the "
            "edge of the recent range — on a genuinely choppy, range-bound market this can mean "
            "more frequent, less meaningful crossovers rather than fewer, cleaner ones."
        ),
        "example": [
            lambda df: zeonta.fisher_transform(df["high"], df["low"]).tail(3),
        ],
    },
    "super_smoother": {
        "title": "Super Smoother Filter (Ehlers)",
        "formula": (
            "a1 = exp(-1.414 x pi / n); b1 = 2 x a1 x cos(1.414 x pi / n); "
            "c2 = b1; c3 = -a1^2; c1 = 1 - c2 - c3; "
            "SSF = c1 x (Close + Close[t-1]) / 2 + c2 x SSF[t-1] + c3 x SSF[t-2]"
        ),
        "about": (
            "A 2-pole digital low-pass filter, drawn from Ehlers' background in aerospace analog "
            "filter design rather than the classic finance literature: it removes the "
            "high-frequency jitter an ordinary moving average lets straight through, with "
            "meaningfully less lag than an EMA of the same critical period. Where `t3` cuts lag by "
            "cascading DEMA-style corrections, this cuts it by an entirely different route — "
            "genuine digital signal processing filter design."
        ),
        "reading": (
            "Read it exactly like any other moving average — trend direction, dynamic support and "
            "resistance, a baseline for a crossover system — but expect it to hug price noticeably "
            "more tightly, with less of the whipsaw jitter a plain `sma`/`ema` of the same length "
            "would show on choppy data."
        ),
        "pitfalls": (
            "``cos()``'s argument must be in radians; at least one popular open-source reference "
            "implementation keeps Ehlers' original EasyLanguage constant (``180``, meant for a "
            "degrees-based ``Cos()``) unconverted when porting to a radians-based language, which "
            "silently produces a different (wrong) filter — confirmed by inspecting that "
            "implementation's own source directly. This implementation uses the radians-consistent "
            "form throughout."
        ),
        "example": [
            lambda df: zeonta.super_smoother(df["close"]).tail(3),
        ],
    },
    "instantaneous_trendline": {
        "title": "Instantaneous Trendline (Ehlers)",
        "formula": (
            "IT = (a - a^2/4) x Close + 0.5 x a^2 x Close[t-1] - (a - 0.75 x a^2) x Close[t-2] "
            "+ 2 x (1-a) x IT[t-1] - (1-a)^2 x IT[t-2]"
        ),
        "about": (
            "Ehlers designed this second-order filter specifically to track the *trend* component "
            "of price while rejecting the *cyclic* component — an ordinary moving average passes "
            "both through together, which is why it lags: part of that lag is spent smoothing out "
            "a cycle that was never trend in the first place. `super_smoother` is a general-purpose "
            "low-pass filter; this one is purpose-built to isolate trend specifically."
        ),
        "reading": (
            "Read it as a smoothed trend line, similar in spirit to `super_smoother` or an EMA, "
            "but expect the reading to be genuinely flatter through a cyclical, range-bound stretch "
            "since that is precisely the component this filter is designed to reject."
        ),
        "pitfalls": (
            "Parameterised by ``alpha`` directly (Ehlers' own default is ``0.07``) rather than by "
            "a bar-count length the way most of this library's other filters are — a length-based "
            "wrapper is a natural extension some platforms add, but the primary source itself uses "
            "``alpha``, so that is what this implementation exposes."
        ),
        "example": [
            lambda df: zeonta.instantaneous_trendline(df["close"]).tail(3),
        ],
    },
    "hurst_exponent": {
        "title": "Hurst Exponent (Rescaled Range Analysis)",
        "formula": (
            "For each lag n: split the window's log returns into chunks of size n; "
            "R/S(n) = mean over chunks of range(cumulative mean-adjusted deviation) / "
            "std-dev(chunk); H = slope of log(R/S) regressed against log(n)"
        ),
        "about": (
            "Harold Hurst developed this while studying multi-year Nile River flood records in "
            "the 1950s, long before it was applied to markets; Rescaled Range (R/S) analysis is "
            "the classical estimator for it. Applied to a return series it measures *persistence* "
            "— whether a move tends to be followed by more of the same (trending) or by a reversal "
            "(mean-reverting) — a fundamentally different question from what any of this library's "
            "other indicators ask, which all measure price/momentum directly rather than the "
            "statistical character of the series generating it."
        ),
        "reading": (
            "``H ≈ 0.5``: a random walk with no memory — past moves say nothing about future ones. "
            "``H > 0.5``: trending/persistent — a move tends to be followed by more of the same. "
            "``H < 0.5``: mean-reverting/anti-persistent — a move tends to be followed by a "
            "reversal. Many traders use this as a *regime filter*: lean on trend-following tools "
            "when ``H`` is comfortably above 0.5, lean on oscillators/mean-reversion tools when it "
            "sits below."
        ),
        "pitfalls": (
            "R/S analysis is the classical (1951) estimator, not the only one — other methods "
            "(DFA, the generalized Hurst exponent) exist and do not always agree with R/S on the "
            "same data, so treat this as an estimate from one specific, standard method rather "
            "than a settled physical constant of the series. It is also, by a wide margin, the "
            "slowest indicator in this library (see its own docstring and `BENCHMARKS.md`) — a "
            "rolling regression over multiple lag values on every bar, not the single vectorised "
            "pass every other indicator here uses."
        ),
        "example": [
            lambda df: zeonta.hurst_exponent(df["close"]).tail(3),
        ],
    },
    "markov_regime_switching": {
        "title": "Markov Regime-Switching Probability",
        "formula": (
            "On each rolling window of log returns: fit y_t = mu_{S_t} + eps_t, "
            "eps_t ~ N(0, sigma_{S_t}^2), S_t in {0,1} a first-order Markov chain, by EM "
            "(Hamilton filter forward + Kim smoother backward per E-step; closed-form "
            "mu/sigma^2/transition updates per M-step); report the filtered probability "
            "P(S_t=high-variance | Y_1..t) for the window's last bar"
        ),
        "about": (
            "Hamilton's 1989 Markov-switching model treats a series as alternating between a "
            "small number of hidden 'regimes', each with its own statistical behaviour, and "
            "estimates both the regimes' parameters and which one is currently active at the "
            "same time. This implementation uses 2 states on log returns, distinguished purely "
            "by variance, so the output reads as a real-time estimate of 'is the market in its "
            "high- or low-volatility regime right now'. It is the only indicator in this "
            "library that fits an iterative statistical model (Expectation-Maximization) rather "
            "than evaluating a formula directly — every bar re-fits the model from scratch on "
            "its own trailing window, using nothing past that bar, so the output stays aligned "
            "and look-ahead free the same way every other indicator here is."
        ),
        "reading": (
            "Values near 1 mean the model is confident the current bar sits in the "
            "higher-variance of its two fitted regimes; values near 0 mean the lower-variance "
            "one. Traders use this as a regime filter the way `hurst_exponent` is used for "
            "trend/mean-reversion character: lean on breakout/momentum tooling when this is "
            "high (volatility expansion), lean on mean-reversion/range tooling when it is low. "
            "A rising value crossing through the middle of its range can flag the *start* of a "
            "volatility regime change before a fixed-window realized-volatility measure would "
            "clearly show it."
        ),
        "pitfalls": (
            "EM is not guaranteed to converge to the globally best fit — it can settle into "
            "different local optima depending on where it starts, which is why this "
            "implementation always seeds every window the same deterministic way (splitting the "
            "window's own returns at their median, self-transition probabilities seeded at 0.9) "
            "rather than randomly; that makes the output reproducible run to run, but does not "
            "make any one window's fit the unique correct answer — on a window with no real "
            "regime structure (constant volatility throughout), the 2-state fit can still find "
            "an arbitrary, unstable split of ordinary noise into two 'regimes'. `max_iterations` "
            "is a runtime safety valve, not a convergence guarantee: a window that has not "
            "converged when the cap is hit still reports its last iterate's estimate rather than "
            "`NaN`. And by far the most expensive indicator in this library — see its own "
            "docstring for the actual complexity — every bar re-runs up to `max_iterations` full "
            "forward/backward passes over its own window; `BENCHMARKS.md` does not cover it."
        ),
        "example": [
            lambda df: zeonta.markov_regime_switching(df["close"]).tail(3),
        ],
    },
    "wavelet_denoise": {
        "title": "Wavelet-Denoised Price (Discrete Wavelet Transform)",
        "formula": (
            "For each rolling window: DWT-decompose into an approximation band and `level` "
            "detail bands; sigma = MAD(finest detail band) / 0.6745; soft-threshold every "
            "detail band at sigma*sqrt(2*log(window)); reconstruct and keep only the "
            "window's last sample"
        ),
        "about": (
            "Wavelet transforms split a series into frequency bands the way a Fourier "
            "transform does, but — unlike Fourier — keep time localisation: they show *when* "
            "a frequency occurs, not just that it does. Academic work on wavelet-denoised "
            "technical indicators (e.g. de-noising return series before building new "
            "indicators on top of them) exploits exactly this to separate genuine price "
            "structure from noise without the lag an SMA/EMA adds. Classic wavelet denoising "
            "decomposes an entire series in a single pass, which is fine for an offline study "
            "but means every bar's value can depend on bars that come after it. This "
            "implementation instead re-runs the decomposition from scratch on every rolling "
            "`window`, using nothing past the current bar — see its own docstring for why "
            "that distinction matters for anything meant to generate live signals."
        ),
        "reading": (
            "This is a building block, not a finished signal: it returns a denoised price "
            "series meant to be fed into an existing indicator in place of raw `close` — e.g. "
            "`zeonta.rsi(zeonta.wavelet_denoise(df['close']))` or the same for `macd` — to get "
            "a lower-lag version of it. Used on its own as a trendline, it turns roughly the "
            "way a Super Smoother or Instantaneous Trendline does, but rejects noise by "
            "frequency-band thresholding rather than by a fixed recursive filter."
        ),
        "pitfalls": (
            "The rolling window means each bar re-decomposes from scratch rather than one "
            "vectorised pass — measure it on your own data before using it on a large "
            "history (see `BENCHMARKS.md`). The wavelet family and decomposition level are "
            "real choices, not defaults to ignore: `db4` at level 2 is what published work on "
            "wavelet-denoised indicators most often uses, but a different pairing changes the "
            "result. And because a longer lookback resolves lower frequencies at the cost of "
            "reacting more slowly, `window` is trading the same lag-versus-noise tradeoff "
            "every smoother in this library makes — just via a different mechanism."
        ),
        "example": [
            lambda df: zeonta.wavelet_denoise(df["close"]).tail(3),
        ],
    },
    "wavelet_variance": {
        "title": "Multi-Scale Wavelet Variance (MODWT)",
        "formula": (
            "For each rolling window: MODWT-decompose (norm=True, trim_approx=True) into "
            "`level` detail bands; WVAR_j = mean(detail_band_j ** 2) for each level j, "
            "1 (finest) through `level` (coarsest)"
        ),
        "about": (
            "atr() and a rolling standard deviation both answer 'how much did price move' "
            "with a single blended number. Percival & Walden's 'Wavelet Methods for Time "
            "Series Analysis' (2000) — the standard reference for this technique — splits "
            "that number apart by timescale using the Maximal Overlap DWT: because it is "
            "energy-conserving (unlike a plain DWT), the resulting per-scale variances are a "
            "genuine decomposition of total variance, not independent or overlapping "
            "readings. `wavelet_denoise` in this library uses an ordinary DWT to reconstruct "
            "a filtered price; this instead keeps the raw per-scale energy to describe the "
            "shape of the volatility itself."
        ),
        "reading": (
            "Each `WVAR_j` column covers a doubling band of bars (`WVAR_1` ~ 2-4 bars, "
            "`WVAR_2` ~ 4-8, and so on up to `WVAR_{level}`). A bar where the finest bands "
            "dominate is mostly high-frequency noise (thin books, HFT churn); one where the "
            "coarsest bands dominate reflects a genuine slower move — a distinction a single "
            "ATR reading cannot make since it always blends every timescale into one number. "
            "Traders use this as a regime read: which kind of volatility is currently driving "
            "the tape."
        ),
        "pitfalls": (
            "This uses the *biased* wavelet-variance estimator (average over every "
            "coefficient in the window) rather than Percival & Walden's *unbiased* one "
            "(which excludes boundary-affected coefficients) — simpler and always defined "
            "for any window/level pair, at the cost of a small bias the academic literature "
            "documents. `window` must be an exact multiple of `2**level`, a hard MODWT "
            "requirement, not a tunable default. And like `wavelet_denoise`, every bar "
            "re-runs its own decomposition rather than one pass over the whole series — "
            "measure it on your own data before a large history (see `BENCHMARKS.md`)."
        ),
        "example": [
            lambda df: zeonta.wavelet_variance(df["close"]).tail(3),
        ],
    },
    "ou_half_life": {
        "title": "Ornstein-Uhlenbeck Half-Life of Mean Reversion",
        "formula": (
            "Regress Close[t]-Close[t-1] against Close[t-1] over a rolling window "
            "(OLS); lambda = fitted slope; "
            "OUHL = -ln(2)/lambda if lambda < 0, else NaN"
        ),
        "about": (
            "The Ornstein-Uhlenbeck process is the standard continuous-time model "
            "for a mean-reverting series in quantitative finance; fitting it to price "
            "and converting the fitted mean-reversion speed into a half-life — how "
            "many bars until the gap between price and its own implied long-run level "
            "closes by half — is a widely used way to pick a *lookback length* for a "
            "mean-reversion strategy, rather than a signal read on its own. Unlike "
            "hurst_exponent, which asks whether a series is persistent or "
            "anti-persistent in general, this asks a narrower, more actionable "
            "question of a series already assumed to mean-revert: how fast."
        ),
        "reading": (
            "A short half-life (a handful of bars) means reversion happens fast — a "
            "mean-reversion entry can expect to be closed out soon. A long half-life "
            "means reversion is slow, if it is even reliably happening at all; `NaN` "
            "means the fitted `lambda` was >= 0 over that window — no mean reversion "
            "was detected there, so the whole premise of a mean-reversion trade does "
            "not currently hold. Traders commonly use the half-life value itself as "
            "the lookback/holding-period parameter for another indicator or strategy, "
            "rather than trading on it directly."
        ),
        "pitfalls": (
            "The fit assumes the series' mean-reversion behaviour is roughly stable "
            "over the whole rolling window — a regime change partway through the "
            "window (the series stops or starts mean-reverting) biases the estimate "
            "toward whichever behaviour dominates the window, not a clean split. And "
            "like `hurst_exponent`, this is one specific, standard estimation method "
            "(OLS on the discretised process), not the only one in the literature."
        ),
        "example": [
            lambda df: zeonta.ou_half_life(df["close"]).tail(3),
        ],
    },
    "dfa": {
        "title": "Detrended Fluctuation Analysis (DFA)",
        "formula": (
            "profile = cumsum(log_returns_window - mean(log_returns_window)); "
            "for each box size n: split profile into non-overlapping n-length boxes, "
            "detrend each with a local linear fit, pool squared residuals into "
            "F(n) = sqrt(mean(residual^2)); "
            "DFA = slope of log(F(n)) regressed against log(n)"
        ),
        "about": (
            "Peng et al. (1994) developed DFA to detect long-range correlations in "
            "DNA sequences without being fooled by the sequence's own local trends — "
            "the same non-stationarity problem a price series has. It estimates the "
            "same underlying quantity hurst_exponent's classical (1951) R/S analysis "
            "does, from the same rolling window of log returns, but by explicitly "
            "removing a local linear trend from every box before measuring "
            "fluctuation, rather than assuming the window is already trend-free."
        ),
        "reading": (
            "Same scale as hurst_exponent: ``alpha ~= 0.5`` random walk, "
            "``alpha > 0.5`` persistent/trending, ``alpha < 0.5`` "
            "anti-persistent/mean-reverting. Because DFA explicitly detrends each "
            "box, it stays reliable through a genuine trend or regime shift inside "
            "the window where R/S analysis can be pulled off by that trend alone — "
            "the two indicators are worth comparing on the same series precisely "
            "when they might disagree."
        ),
        "pitfalls": (
            "This is DFA1 (linear local detrending) — higher-order variants (DFA2, "
            "DFA3, quadratic/cubic local fits) exist and can differ on the same "
            "data, so treat this as one specific, standard order of the method, the "
            "same caveat hurst_exponent's own docstring gives for R/S versus other "
            "Hurst estimators. Like hurst_exponent, this is a per-bar rolling "
            "regression over several box sizes, not a single vectorised pass — "
            "measure it on your own data before a large history (see "
            "`BENCHMARKS.md`)."
        ),
        "example": [
            lambda df: zeonta.dfa(df["close"]).tail(3),
        ],
    },
    "sample_entropy": {
        "title": "Sample Entropy (SampEn)",
        "formula": (
            "Build every length-m and length-(m+1) template from the log-return "
            "window; B = count of length-m template pairs within tolerance "
            "r*std(window) (self-matches excluded); A = same count at length m+1; "
            "SampEn = -ln(A/B)"
        ),
        "about": (
            "Richman and Moorman (2000) built Sample Entropy to fix a specific "
            "flaw in the earlier Approximate Entropy (Pincus, 1991): ApEn counts a "
            "template as matching itself, which biases it — more so on shorter "
            "series — toward reading more regular than the data actually is. "
            "SampEn excludes self-matches entirely. It asks a different question "
            "from hurst_exponent/dfa: not whether a series trends or reverts, but "
            "how much it repeats its own short-term patterns at all, independent "
            "of which direction those patterns point."
        ),
        "reading": (
            "Low values (near 0) mean the window keeps repeating short patterns — "
            "regular, more predictable behaviour. High values mean little to no "
            "repeating structure — irregular, closer to noise. Unlike "
            "hurst_exponent/dfa, a high reading here does not say *which way* price "
            "is likely to move, only that its recent behaviour has been harder to "
            "characterise by a short repeating pattern."
        ),
        "pitfalls": (
            "By far the slowest indicator in this library — every bar compares "
            "every pair of templates in its own window (O(window^2)), not the "
            "single vectorised pass most indicators here use, and slower again "
            "than hurst_exponent/dfa's own per-bar loops (see `BENCHMARKS.md`). "
            "`m` and `r` are real choices, not defaults to ignore: Richman & "
            "Moorman's own examples use `m=2`, `r` between `0.1` and `0.25` of the "
            "window's standard deviation, and a different pairing changes the "
            "result — this is one specific, standard parameterisation, not the "
            "only one used in the literature."
        ),
        "example": [
            lambda df: zeonta.sample_entropy(df["close"]).tail(3),
        ],
    },
    "shannon_entropy": {
        "title": "Shannon Entropy",
        "formula": (
            "Bin a window's log returns into `bins` equal-width buckets spanning that window's "
            "own min-to-max range; H = -sum(p_i x log(p_i)) over buckets with p_i > 0, "
            "p_i = count_i / window; normalized result = H / log(bins)"
        ),
        "about": (
            "Shannon's 1948 entropy measures how uniformly a distribution's probability mass is "
            "spread across its possible outcomes. Applied to a rolling window of log returns, "
            "'outcomes' are equal-width return-size buckets: a window whose returns pile into one "
            "or two buckets (a quiet, directional stretch) has low entropy, one whose returns "
            "spread evenly across every bucket (no dominant move size) approaches the maximum, "
            "`log(bins)` — this indicator reports that ratio, so the result stays 0-1 regardless "
            "of `bins`. Unlike sample_entropy/approximate_entropy/permutation_entropy, it asks "
            "nothing about order or repetition — only how the move *sizes* are distributed."
        ),
        "reading": (
            "Low values mean recent returns have clustered around one typical size — often a "
            "quiet, low-volatility or persistently one-directional stretch. High values (near 1) "
            "mean return sizes have been spread out with no dominant scale — often choppier or "
            "more heterogeneous conditions. A sudden entropy drop or spike is sometimes read as a "
            "precursor to a volatility regime change, though this indicator only measures the "
            "current window's own spread, not what comes next."
        ),
        "pitfalls": (
            "`bins` is a real, tunable choice — like sample_entropy's `m`/`r` — not a value with "
            "one provably correct setting: more buckets resolve finer structure but need more "
            "bars per bucket to estimate each `p_i` reliably, so a small `window` with a large "
            "`bins` count produces a noisy estimate. A window whose returns are all identical "
            "(zero range) is defined as exactly `0.0` rather than left undefined."
        ),
        "example": [
            lambda df: zeonta.shannon_entropy(df["close"]).tail(3),
        ],
    },
    "emd_imf1": {
        "title": "Empirical Mode Decomposition — First IMF",
        "formula": (
            "Sift close within a rolling window: fit natural cubic splines through "
            "its local maxima and minima to form upper/lower envelopes, subtract "
            "their mean, repeat on the result until the Cauchy-type convergence "
            "measure SD < sd_threshold or max_iterations is reached; the result is "
            "the first Intrinsic Mode Function"
        ),
        "about": (
            "Huang et al. (1998) built EMD as an alternative to Fourier and wavelet "
            "analysis for signals that are non-stationary and nonlinear — a price "
            "series among them. Rather than projecting onto a fixed basis (sines, or "
            "a wavelet's fixed mother function), EMD derives its own basis functions "
            "directly from the data's local extrema. This library exposes only the "
            "first of what a full decomposition would produce: the fastest local "
            "oscillation, with slower components (later IMFs, and the residual trend "
            "a full decomposition ends with) left out, since a full decomposition's "
            "IMF count varies with the data and does not fit a fixed-column output."
        ),
        "reading": (
            "`close - zeonta.emd_imf1(close, window)` approximates the trend/cycle "
            "residual a full decomposition would isolate, though it is not exactly "
            "that residual — only one IMF has been removed, not the full recursive "
            "decomposition down to a monotonic trend. Used directly, IMF1 behaves "
            "like a cycle/noise extraction, similar in spirit to what "
            "`wavelet_denoise` removes but from the opposite direction: this keeps "
            "the fast component rather than filtering it out."
        ),
        "pitfalls": (
            "By far the most expensive indicator in this library to compute: every "
            "bar re-runs an iterative spline-fitting loop over its own window, not "
            "a single vectorised pass (see `BENCHMARKS.md`). Boundary handling is a "
            "known, real weak point of EMD in general — this implementation "
            "deliberately does not anchor the envelope splines to the window's own "
            "first/last sample (an earlier version did, and it turned out to force "
            "every sifted value at the boundary to exactly 0.0, caught by noticing "
            "a suspiciously exact zero rather than trusting the formula); letting "
            "the natural cubic spline extrapolate past the outermost real extremum "
            "instead avoids that specific artifact, but boundary bars are still the "
            "least reliable part of any EMD window for that reason."
        ),
        "example": [
            lambda df: zeonta.emd_imf1(df["close"]).tail(3),
        ],
    },
    "stddev": {
        "title": "Standard Deviation",
        "formula": "STDDEV = std(Close, n)",
        "about": (
            "The building block [bbands](bbands.md) plots as a band around price, exposed here on "
            "its own. Population standard deviation (`ddof=0`, matching charting-platform "
            "convention) unless you pass `ddof=1` for the sample estimate."
        ),
        "reading": (
            "A rising STDDEV means price has gotten choppier over the window; a falling one means "
            "it has calmed down — the same read [squeeze](squeeze.md) automates for a specific "
            "band-width comparison."
        ),
        "pitfalls": (
            "A raw price measure, not a percentage — a $5 standard deviation means something "
            "completely different for a $20 stock than for a $2,000 one. Compare across symbols "
            "using a percentage-based measure instead, or normalise it yourself."
        ),
        "example": [
            lambda df: zeonta.stddev(df["close"]).tail(3),
        ],
    },
    "variance": {
        "title": "Variance",
        "formula": "VAR = variance(Close, n) = STDDEV(Close, n) ^ 2",
        "about": (
            "[stddev](stddev.md) before the square root — computed directly here rather than by "
            "squaring it, but numerically the same relationship. Statistical work (variance is "
            "additive for independent series; standard deviation is not) reaches for this form; "
            "charting reaches for `stddev`, since it shares price's own units."
        ),
        "reading": "Same direction as `stddev`, just on a squared (and therefore larger) scale.",
        "pitfalls": (
            "Squared units — a variance of 4 for a price series in dollars is technically "
            "'dollars squared', not directly comparable to price itself the way `stddev` is."
        ),
        "example": [
            lambda df: zeonta.variance(df["close"]).tail(3),
        ],
    },
    "zscore": {
        "title": "Z-Score",
        "formula": "ZSCORE = (Close - SMA(Close, n)) / STDDEV(Close, n)",
        "about": (
            "The same mean and spread [bbands](bbands.md) plots as two lines around price, "
            "collapsed into a single number: how many standard deviations price currently sits "
            "from its own rolling mean."
        ),
        "reading": (
            "`|ZSCORE| > 2` is a common, if arbitrary, threshold for 'unusually far from the "
            "mean' — the same idea as touching a Bollinger Band, expressed as a number instead of "
            "a price level you have to compare visually against the close."
        ),
        "pitfalls": (
            "Assumes the window's distribution is roughly normal enough for 'standard deviations "
            "from the mean' to be a meaningful yardstick — a window dominated by one huge outlier "
            "bar distorts both the mean and the spread it is being measured against."
        ),
        "example": [
            lambda df: zeonta.zscore(df["close"]).tail(3),
        ],
    },
    "skewness": {
        "title": "Skewness",
        "formula": (
            "Adjusted Fisher-Pearson coefficient: G1 = (sqrt(n(n-1))/(n-2)) * (m3/m2^1.5), the "
            "same bias-adjusted formula pandas' own rolling .skew() uses"
        ),
        "about": (
            "A shape measure for the window's recent return distribution rather than a level or "
            "trend measure like most of this library: which side has the longer tail."
        ),
        "reading": (
            "Positive skew means the window had a longer right tail — a few outsized up-moves "
            "against an otherwise typical range, common in a slow grind higher punctuated by sharp "
            "rallies. Negative skew is the mirror image: a slow grind punctuated by sharp drops, "
            "the shape many equity indices show over the long run."
        ),
        "pitfalls": (
            "Needs a real spread to mean anything — `NaN` on a perfectly flat window, and noisy on "
            "a short one (a handful of points barely constrains a third-moment estimate)."
        ),
        "example": [
            lambda df: zeonta.skewness(df["close"]).tail(3),
        ],
    },
    "kurtosis": {
        "title": "Kurtosis",
        "formula": (
            "Adjusted Fisher-Pearson excess coefficient: G2 = ((n-1)/((n-2)(n-3))) * ((n+1)g2 + 6), "
            "g2 = m4/m2^2 - 3, the same bias-adjusted formula pandas' own rolling .kurt() uses"
        ),
        "about": (
            "[skewness](skewness.md)'s sibling shape measure: not which side has the longer tail, "
            "but how fat *both* tails are compared to a normal distribution — how much of the "
            "window's spread comes from a few extreme bars rather than being spread evenly."
        ),
        "reading": (
            "`0` reads like a normal distribution's tails. Positive (fat tails) means a few extreme "
            "bars dominate the window's spread — the pattern a market that is mostly quiet with "
            "occasional sharp shocks produces. Negative (thin tails) means moves have been unusually "
            "uniform in size."
        ),
        "pitfalls": (
            "Needs more points than `skewness` to be stable (a 4th-moment estimate is noisier "
            "still on a short window) and, like it, is `NaN` on a perfectly flat window."
        ),
        "example": [
            lambda df: zeonta.kurtosis(df["close"]).tail(3),
        ],
    },
    "mad": {
        "title": "Median Absolute Deviation (MAD)",
        "formula": "MAD = median(|Close - median(Close, n)|, n)",
        "about": (
            "A spread measure like [stddev](stddev.md), but built from medians instead of means "
            "and squares at every step — the same robust-to-outliers idea behind using a median "
            "instead of a mean in the first place, applied twice over."
        ),
        "reading": (
            "Reads the same direction as `stddev` — rising means the window has gotten choppier — "
            "but a single wild bar barely moves MAD, while it can dominate `stddev` outright."
        ),
        "pitfalls": (
            "Not the same thing as the mean absolute deviation [cci](cci.md) uses internally, "
            "despite the similar name — that one averages the deviations, this one takes their "
            "median, and the two disagree whenever the window has any outliers at all."
        ),
        "example": [
            lambda df: zeonta.mad(df["close"]).tail(3),
        ],
    },
    "log_return": {
        "title": "Logarithmic Return",
        "formula": "LOGRET = ln(Close[t] / Close[t-n])",
        "about": (
            "[roc](roc.md)'s statistical cousin: the same bar-lag comparison, expressed as a log "
            "ratio instead of a percentage. Log returns are additive across time (summing "
            "single-bar log returns over a window equals the log return over the whole window), "
            "which simple percentage change is not — the reason most statistical work on a return "
            "series (including this library's own `hurst_exponent`, `dfa` and `sample_entropy`) "
            "uses this form rather than `roc`."
        ),
        "reading": (
            "For everyday-sized moves, a log return and a simple percentage return are nearly "
            "identical (`ln(1.01) ~= 0.00995`); they diverge more visibly on a large single-bar move."
        ),
        "pitfalls": (
            "Requires strictly positive prices — `ln` of a zero or negative value is undefined, "
            "which surfaces here as `NaN` rather than an exception."
        ),
        "example": [
            lambda df: zeonta.log_return(df["close"]).tail(3),
        ],
    },
    "cumulative_return": {
        "title": "Cumulative Return",
        "formula": "CUMRET = (Close[t] / Close[0] - 1) * 100",
        "about": (
            "The odd one out among this library's indicators: every other one only ever looks "
            "back a fixed *length* of bars, so its value at bar N is stable no matter how much "
            "history you later add before it. This instead anchors to bar 0 of whatever series "
            "you pass in — the running percentage gain or loss since the very start of *that* "
            "series."
        ),
        "reading": (
            "A straightforward running total return line, the same shape an equity-curve chart "
            "plots — reads highest where price has run up the most since bar 0, lowest where it "
            "has run down the most."
        ),
        "pitfalls": (
            "Re-running this on a longer history changes *every* earlier value, since the anchor "
            "point (bar 0) moves with it — by design, since the question being asked is always "
            "'return since the start of this series', but a real surprise if you expected the same "
            "stability every other indicator here gives you."
        ),
        "example": [
            lambda df: zeonta.cumulative_return(df["close"]).tail(3),
        ],
    },
    "bop": {
        "title": "Balance of Power (BOP)",
        "formula": "BOP = (Close - Open) / (High - Low)",
        "about": (
            "Igor Livshin's 2001 measure of who won the bar outright: buyers pushed the close up "
            "from the open (positive), or sellers pushed it down (negative), scaled by how wide "
            "the bar's own range was. Similar in shape to [cmf](cmf.md)'s Money Flow Multiplier, "
            "but measured from the open rather than volume-weighted, and left as a raw per-bar "
            "ratio rather than summed over a window."
        ),
        "reading": (
            "Raw values are choppy bar to bar; many traders pipe this into `sma()` themselves for "
            "a smoother line, which is how StockCharts' own page presents it — this function "
            "returns the unsmoothed ratio to match TA-Lib's own zero-parameter convention."
        ),
        "pitfalls": (
            "Zero-range bars (`High == Low`) would divide by zero; treated as `0` rather than "
            "raising or producing a warning."
        ),
        "example": [
            lambda df: zeonta.bop(df["open"], df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "pvt": {
        "title": "Price Volume Trend (PVT)",
        "formula": (
            "PVT[0] = 0; PVT[i] = PVT[i-1] + Volume[i] * (Close[i] - Close[i-1]) / Close[i-1]"
        ),
        "about": (
            "[obv](obv.md)'s more graded cousin: OBV adds a bar's *entire* volume based only on "
            "which direction the close moved; PVT scales the volume it adds by *how much* the "
            "close moved as a percentage, so a 3% up day contributes three times as much as a 1% "
            "up day rather than the same full volume either way."
        ),
        "reading": (
            "Read the same way as OBV — a rising line alongside rising price confirms the trend "
            "with real participation behind it; a PVT that fails to make a new high alongside "
            "price is a classic bearish divergence warning."
        ),
        "pitfalls": (
            "A running total with an arbitrary starting level, like `obv`/`adl` — only its slope "
            "and its divergence from price carry meaning, never its absolute value."
        ),
        "example": [
            lambda df: zeonta.pvt(df["close"], df["volume"]).tail(3),
        ],
    },
    "nvi": {
        "title": "Negative Volume Index (NVI)",
        "formula": (
            "Starts at 1000. When Volume[i] < Volume[i-1]: "
            "NVI[i] = NVI[i-1] * (1 + (Close[i]-Close[i-1])/Close[i-1]); otherwise unchanged"
        ),
        "about": (
            "Paul Dysart's idea from the 1930s-40s, popularised by Norman Fosback: price moves on "
            "*quiet* (falling) volume days are more likely to reflect informed money moving "
            "without drawing a crowd, while moves on heavy volume days reflect crowd-driven "
            "activity. NVI only updates on the quiet days, holding flat through every heavy-volume "
            "bar — the mirror-image complement of [pvi](pvi.md)."
        ),
        "reading": (
            "StockCharts' own long-run study found the market was more often in a bull market "
            "when NVI sat above its own 255-day moving average than below it — used as a "
            "long-term, low-frequency regime read rather than a short-term signal."
        ),
        "pitfalls": (
            "The starting value of `1000` is a convention (StockCharts'), not a law of the "
            "formula — some other implementations start at `100` or `1`. Only ever compare an "
            "NVI series against itself (its own moving average, or its own history), never its "
            "absolute level against a different symbol's."
        ),
        "example": [
            lambda df: zeonta.nvi(df["close"], df["volume"]).tail(3),
        ],
    },
    "pvi": {
        "title": "Positive Volume Index (PVI)",
        "formula": (
            "Starts at 1000. When Volume[i] > Volume[i-1]: "
            "PVI[i] = PVI[i-1] * (1 + (Close[i]-Close[i-1])/Close[i-1]); otherwise unchanged"
        ),
        "about": (
            "The mirror-image complement of [nvi](nvi.md): only updates on a bar where volume "
            "*rose* versus the bar before it, holding flat through every quiet-volume bar. Built "
            "on the same Dysart/Fosback idea, from the opposite side — heavy volume days reflect "
            "crowd-driven activity rather than informed money."
        ),
        "reading": (
            "Read the opposite way from NVI in the classic Fosback framework: PVI is treated as "
            "the noisier, crowd-driven half of the pair, so less weight is typically put on it "
            "alone than on NVI's own long-run signal."
        ),
        "pitfalls": (
            "Same starting-value caveat as `nvi`: `1000` is StockCharts'/Fidelity's convention, "
            "not a universal constant — compare a PVI series only against itself."
        ),
        "example": [
            lambda df: zeonta.pvi(df["close"], df["volume"]).tail(3),
        ],
    },
    "vwma": {
        "title": "Volume-Weighted Moving Average (VWMA)",
        "formula": "VWMA = Sum(Close * Volume, n) / Sum(Volume, n)",
        "about": (
            "[sma](sma.md) treats every bar in the window equally regardless of how much traded "
            "on it; VWMA instead lets a heavy-volume bar pull the average toward its own close "
            "more than a quiet bar does — the same volume-weighting idea [vwap](vwap.md) uses, "
            "but over a fixed rolling window instead of resetting each session."
        ),
        "reading": (
            "Read the same way as any moving average — price crossing above/below it, or its own "
            "slope — with the difference that a break on unusually heavy volume shows up more "
            "prominently here than in a plain SMA of the same length."
        ),
        "pitfalls": (
            "`NaN` whenever the window's total volume is exactly `0` (no trading at all in that "
            "window) rather than an undefined division."
        ),
        "example": [
            lambda df: zeonta.vwma(df["close"], df["volume"]).tail(3),
        ],
    },
    "zlema": {
        "title": "Zero-Lag Exponential Moving Average (ZLEMA)",
        "formula": (
            "lag = floor((n-1)/2); data[t] = Close[t] + (Close[t] - Close[t-lag]); "
            "ZLEMA = EMA(data, n)"
        ),
        "about": (
            "Ehlers & Way's answer to [ema](ema.md)'s built-in lag: rather than changing the "
            "smoothing formula itself, they modify what goes *into* it — feeding the EMA a "
            "de-lagged version of price (today's close plus how far it has moved from `lag` bars "
            "ago) rather than the raw close."
        ),
        "reading": (
            "Read the same way as any EMA-family line — a faster-reacting alternative to `ema` of "
            "the same length, at the cost of overshooting more on a sharp reversal (removing lag "
            "makes the line more willing to move, in either direction)."
        ),
        "pitfalls": (
            "The lag-cancellation is exact only on a straight line; real price is not one, so some "
            "lag remains and the 'zero' in the name is aspirational rather than literal."
        ),
        "example": [
            lambda df: zeonta.zlema(df["close"]).tail(3),
        ],
    },
    "alma": {
        "title": "Arnaud Legoux Moving Average (ALMA)",
        "formula": (
            "m = floor(offset*(n-1)); s = n/sigma; w[j] = exp(-(j-m)^2/(2*s^2)) for j=0..n-1; "
            "ALMA = sum(w[j] * Close[t-n+1+j]) / sum(w[j])"
        ),
        "about": (
            "Where [wma](wma.md) weights the window linearly and [ema](ema.md) weights it "
            "exponentially, ALMA weights it with a Gaussian bell curve whose peak position "
            "(`offset`) and width (`sigma`) are both separately tunable — two independent knobs "
            "for the same lag-versus-smoothness tradeoff every moving average makes."
        ),
        "reading": (
            "Read the same way as any moving average. `offset` near `1` behaves more like a "
            "responsive EMA; `offset` near `0` behaves more like a smooth, centered average — "
            "`0.85` is a starting point tuned toward responsiveness, not a midpoint."
        ),
        "pitfalls": (
            "Two extra parameters beyond `length` (`offset`, `sigma`) that meaningfully change "
            "the result — treat the defaults as Legoux's own starting point, not universal "
            "constants, the same caveat this library gives Ehlers' own tunable filters."
        ),
        "example": [
            lambda df: zeonta.alma(df["close"]).tail(3),
        ],
    },
    "mcgd": {
        "title": "McGinley Dynamic",
        "formula": (
            "MD[0] = Close[0]; "
            "MD[i] = MD[i-1] + (Close[i] - MD[i-1]) / (N * (Close[i]/MD[i-1])^4), N = length"
        ),
        "about": (
            "John McGinley built this specifically to fix a complaint about ordinary moving "
            "averages: a fixed-period EMA/SMA lags badly in a fast market and whipsaws in a slow "
            "one, because its speed never changes. The `(Close/MD)^4` term makes McGinley Dynamic "
            "self-adjusting instead — it speeds up automatically whenever price pulls away from "
            "it, and slows back down once price and the average are close again."
        ),
        "reading": (
            "Read the same way as any moving average (price crossing it, its own slope) — "
            "McGinley's own pitch is that it needs less re-tuning across changing market "
            "conditions than a fixed-period EMA/SMA would, not that it reads differently."
        ),
        "pitfalls": (
            "The `(Close/MD)^4` term is exactly `0` when `Close` is `0`, which would divide by "
            "zero in the update step — held at the prior value for that one bar instead, since "
            "the formula has no real answer at that singular point."
        ),
        "example": [
            lambda df: zeonta.mcgd(df["close"]).tail(3),
        ],
    },
    "natr": {
        "title": "Normalized Average True Range (NATR)",
        "formula": "NATR = ATR(n) / Close * 100",
        "about": (
            "[atr](atr.md) reports a raw price amount — a $2 ATR is huge for a $10 stock and tiny "
            "for a $2,000 one. NATR expresses the same measurement as a percentage of price "
            "instead, so different symbols (or the same symbol at very different price levels "
            "over time) become directly comparable."
        ),
        "reading": (
            "Read the same way as ATR — rising means volatility is increasing — but compare its "
            "*level* across symbols or across a long price history the way you never would with "
            "raw ATR."
        ),
        "pitfalls": "`NaN` when `Close` is exactly `0`, rather than an undefined division.",
        "example": [
            lambda df: zeonta.natr(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "mass_index": {
        "title": "Mass Index",
        "formula": (
            "SingleEMA = EMA(High-Low, ema_length); DoubleEMA = EMA(SingleEMA, ema_length); "
            "Ratio = SingleEMA/DoubleEMA; MASS = Sum(Ratio, sum_length)"
        ),
        "about": (
            "Donald Dorsey built this entirely from the bar-to-bar *range*, not price direction: "
            "an EMA reacts faster than an EMA-of-that-EMA, so their ratio grows whenever the range "
            "is widening, whether that widening comes from an up move or a down move. Dorsey's own "
            "claim was that this range expansion tends to appear before a trend reversal, without "
            "saying which direction the reversal goes."
        ),
        "reading": (
            "Dorsey's own 'reversal bulge' threshold is a reading of 27 followed by a drop back "
            "below 26.5 — a specific level pattern to watch for, not a zero-line crossing or a "
            "bounded oscillator the way most indicators in this library work."
        ),
        "pitfalls": (
            "Reads in the mid-20s during ordinary conditions by construction (it is a 25-bar sum "
            "of a ratio that hovers near 1), so it needs its own specific threshold rather than a "
            "0/50/100-style intuition."
        ),
        "example": [
            lambda df: zeonta.mass_index(df["high"], df["low"]).tail(3),
        ],
    },
    "choppiness_index": {
        "title": "Choppiness Index (CHOP)",
        "formula": (
            "CHOP = 100 * log10(Sum(TrueRange, n) / (HighestHigh(n) - LowestLow(n))) / log10(n)"
        ),
        "about": (
            "E.W. Dreiss compares two ways of measuring the same window's movement: sum up every "
            "single bar's own range (a lot, if price zigzags back and forth all window long), "
            "versus the range of the window measured start to end (small, if all that zigzagging "
            "cancelled itself out). A high ratio between the two means most of the motion was "
            "wasted; a ratio close to 1 means the window's bars each contributed net progress in "
            "the same direction."
        ),
        "reading": (
            "Dreiss' own commonly cited reading: above `61.8` suggests consolidation, below `38.2` "
            "suggests a clean trend (Fibonacci numbers chosen for familiarity, not derived from "
            "the formula). Bounded to `[0, 100]` by construction, but says nothing about *which* "
            "direction a trend runs, the same caveat `atr` carries."
        ),
        "pitfalls": (
            "`NaN` on a perfectly flat window (both the numerator and denominator collapse to "
            "`0`) rather than an undefined division or a misleading number."
        ),
        "example": [
            lambda df: zeonta.choppiness_index(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "vertical_horizontal_filter": {
        "title": "Vertical Horizontal Filter (VHF)",
        "formula": ("VHF = (HighestClose(n) - LowestClose(n)) / Sum(|Close[i] - Close[i-1]|, n)"),
        "about": (
            "Adam White's version of the same comparison [choppiness_index](choppiness_index.md) "
            "makes, built the opposite way round and read the opposite direction: the numerator "
            "('vertical' movement) is the net distance the window's closing range covered; the "
            "denominator ('horizontal' movement) is the total bar-by-bar distance it took to get "
            "there."
        ),
        "reading": (
            "Higher means more trend (the opposite direction from CHOP, despite the similar "
            "construction) — little wasted motion getting from the window's start to its end. "
            "Lower means more whipsaw: a lot of bar-by-bar distance covered for little net "
            "progress."
        ),
        "pitfalls": (
            "`NaN` wherever the window's bar-to-bar movement summed to exactly `0` (a perfectly "
            "flat window), rather than an undefined division."
        ),
        "example": [
            lambda df: zeonta.vertical_horizontal_filter(df["close"]).tail(3),
        ],
    },
    "cmo": {
        "title": "Chande Momentum Oscillator (CMO)",
        "formula": "CMO = 100 * (SumUp(n) - SumDown(n)) / (SumUp(n) + SumDown(n))",
        "about": (
            "Built from the same up-move/down-move split as [rsi](rsi.md), but combined "
            "differently (a normalised difference rather than a ratio) and, unlike RSI, never "
            "smoothed — a gain or loss drops out of the window completely once it ages past "
            "`length` bars rather than fading gradually the way Wilder smoothing does."
        ),
        "reading": (
            "Reads on the same -100/+100 scale and the same overbought/oversold intuition as "
            "other bounded oscillators, but because it is never smoothed it reacts more abruptly "
            "than RSI to an old extreme move finally aging out of the window."
        ),
        "pitfalls": "`0` on a perfectly flat window (both sums are `0`), not an undefined `0/0`.",
        "example": [
            lambda df: zeonta.cmo(df["close"]).tail(3),
        ],
    },
    "drawdown": {
        "title": "Drawdown",
        "formula": "DD = (Close - CumMax(Close)) / CumMax(Close) * 100",
        "about": (
            "The running percentage decline from the series' own all-time high so far — the "
            "same idea [cumulative_return](cumulative_return.md) applies to total gain, applied "
            "here to loss from the peak instead."
        ),
        "reading": (
            "Always `<= 0`; `0` exactly at every new high. The most negative value reached over "
            "a history is its maximum drawdown — the standard way to describe how bad the worst "
            "stretch was, independent of when it happened."
        ),
        "pitfalls": (
            "Like `cumulative_return`, this looks back to the start of whatever series you pass "
            "in rather than a fixed length — prepending more history can only move the running "
            "peak higher, which can change every later value."
        ),
        "example": [
            lambda df: zeonta.drawdown(df["close"]).tail(3),
        ],
    },
    "trima": {
        "title": "Triangular Moving Average (TRIMA)",
        "formula": (
            "Even length: TRIMA = SMA(SMA(Close, n/2), n/2+1); "
            "Odd length: TRIMA = SMA(SMA(Close, (n+1)/2), (n+1)/2)"
        ),
        "about": (
            "An [sma](sma.md) of an [sma](sma.md), with the two window sizes chosen so the "
            "combined effect weights the middle of the window most heavily rather than every bar "
            "equally — a triangular weighting shape instead of `sma`'s rectangular one."
        ),
        "reading": (
            "Read the same way as any moving average. Smoother than an `sma` of the same "
            "length (the middle-weighting suppresses noise at both edges of the window), at the "
            "cost of a longer effective lag."
        ),
        "pitfalls": "No special edge cases — a plain double SMA pass.",
        "example": [
            lambda df: zeonta.trima(df["close"]).tail(3),
        ],
    },
    "vidya": {
        "title": "Variable Index Dynamic Average (VIDYA)",
        "formula": (
            "VIDYA = Close * F * |CMO/100| + VIDYA[-1] * (1 - F * |CMO/100|), F = 2/(length+1)"
        ),
        "about": (
            "An [ema](ema.md) whose smoothing constant is scaled by [cmo](cmo.md)'s momentum "
            "reading instead of staying fixed — freezing toward `0` (no update at all) when "
            "momentum is weak and choppy, and opening up toward the full EMA constant when "
            "momentum is strongly one-sided. A different self-adjusting idea from "
            "[kama](kama.md)'s Efficiency Ratio, but the same underlying motivation: don't use "
            "one fixed speed for every market condition."
        ),
        "reading": "Read the same way as any moving average — price crossing it, or its own slope.",
        "pitfalls": (
            "Two stacked parameters (`length` for the base EMA speed, `cmo_length` for the "
            "momentum reading driving it) that both meaningfully change the result — not a "
            "single-knob indicator the way `ema` is."
        ),
        "example": [
            lambda df: zeonta.vidya(df["close"]).tail(3),
        ],
    },
    "efficiency_ratio": {
        "title": "Kaufman's Efficiency Ratio (ER)",
        "formula": "ER = |Close - Close[n ago]| / Sum(|Close[i] - Close[i-1]|, n)",
        "about": (
            "The adaptive core [kama](kama.md) blends into its own smoothing constant, exposed "
            "here on its own: net movement over total movement, a direct measure of how much of "
            "a window's bar-to-bar churn actually went somewhere."
        ),
        "reading": (
            "`1` means the window trended in a straight line; near `0` means it churned in "
            "place. Often used as a regime filter feeding into another indicator's parameters, "
            "the way `kama` uses it internally, rather than traded on directly."
        ),
        "pitfalls": "`0` on a perfectly flat window rather than an undefined `0/0`.",
        "example": [
            lambda df: zeonta.efficiency_ratio(df["close"]).tail(3),
        ],
    },
    "center_of_gravity": {
        "title": "Center of Gravity Oscillator (CG)",
        "formula": (
            "Price = (High+Low)/2; "
            "CG = -sum((1+k)*Price[t-k], k=0..n-1) / sum(Price[t-k], k=0..n-1)"
        ),
        "about": (
            "John Ehlers' balance-point oscillator: treats the window's prices as weights along "
            "a beam and finds where it would balance, then inverts the sign since that balance "
            "point moves in exact opposition to price swings. The result is a smoothed "
            "oscillator with essentially zero lag, unlike a conventional smoothed indicator that "
            "trades lag for smoothness."
        ),
        "reading": (
            "Ehlers' own suggested signal is the crossover between CG and its own one-bar-"
            "delayed trigger line — the same pattern [fisher_transform](fisher_transform.md) "
            "uses. Ideally, `length` should be about half the market's dominant cycle length."
        ),
        "pitfalls": (
            "The scale is not comparable across different `length` values or to price itself — "
            "Ehlers' own paper notes only the *shape* of the curve matters."
        ),
        "example": [
            lambda df: zeonta.center_of_gravity(df["high"], df["low"]).tail(3),
        ],
    },
    "laguerre_rsi": {
        "title": "Laguerre RSI",
        "formula": (
            "4-stage Laguerre filter (L0..L3) replaces Wilder smoothing; "
            "CU/CD from stage-to-stage differences; LRSI = CU/(CU+CD)"
        ),
        "about": (
            "John Ehlers' fast-acting alternative to [rsi](rsi.md): rather than a full look-back "
            "window smoothed by Wilder's recursion, this runs price through a 4-stage all-pass "
            "filter cascade (a 'time warp' that delays low-frequency components more than high-"
            "frequency ones) and reads momentum from the relationships between the four stages."
        ),
        "reading": (
            "Same 0-1 scale and overbought/oversold intuition as RSI (Ehlers' own example uses "
            "20%/80% levels), but known for reacting much faster and often pinning near the "
            "extremes rather than drifting through the middle."
        ),
        "pitfalls": (
            "The filter starts from a zero initial state, so the first several bars are a "
            "warm-up transient rather than a meaningful reading — there is no fixed warm-up "
            "length the way a windowed indicator has, since the filter's own memory never fully "
            "clears, just fades."
        ),
        "example": [
            lambda df: zeonta.laguerre_rsi(df["close"]).tail(3),
        ],
    },
    "kst": {
        "title": "Pring's Know Sure Thing (KST)",
        "formula": (
            "KST = 1*SMA(ROC(roc1),sma1) + 2*SMA(ROC(roc2),sma2) "
            "+ 3*SMA(ROC(roc3),sma3) + 4*SMA(ROC(roc4),sma4)"
        ),
        "about": (
            "Martin Pring combines four separately smoothed [roc](roc.md) cycles into one line, "
            "weighting the longer cycles more heavily on the theory that they capture "
            "significant momentum shifts better than short-term noise does."
        ),
        "reading": (
            "Read like [macd](macd.md): the crossover between KST and its own signal line, or "
            "KST crossing its own zero line, are the two standard reads."
        ),
        "pitfalls": (
            "Nine parameters in total (four ROC lengths, four matching SMA lengths, one signal "
            "length) — Pring's own daily-chart defaults are widely used as-is rather than tuned "
            "per symbol."
        ),
        "example": [
            lambda df: zeonta.kst(df["close"]).tail(3),
        ],
    },
    "rvgi": {
        "title": "Relative Vigor Index (RVGI)",
        "formula": (
            "Body/Range each symmetrically weighted over 4 bars (1-2-2-1), "
            "then RVGI = SMA(Body, n) / SMA(Range, n)"
        ),
        "about": (
            "The same idea [bop](bop.md) measures raw — closing strength relative to the bar's "
            "own range — smoothed two ways at once: a 4-bar symmetric weighting on both the body "
            "and the range before an SMA of each, plus the same weighting again for its own "
            "signal line."
        ),
        "reading": (
            "The crossover between RVGI and its own signal line is the standard read — a "
            "smoother, less choppy version of watching raw BOP cross its own zero line."
        ),
        "pitfalls": (
            "Zero-range or zero-body bars are not specially guarded beyond the SMA smoothing "
            "itself — a long stretch of identical open/close or high/low bars can still produce "
            "an undefined `0/0` ratio, surfacing as `NaN`."
        ),
        "example": [
            lambda df: zeonta.rvgi(df["open"], df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "smi": {
        "title": "Stochastic Momentum Index (SMI)",
        "formula": (
            "Mid = (HH+LL)/2; SMI = 200 * EMA(EMA(Close-Mid,fast),slow) / EMA(EMA(HH-LL,fast),slow)"
        ),
        "about": (
            "William Blau's refinement of [stoch](stoch.md): instead of measuring where the "
            "close sits *within* the high-low range (0 to 100), it measures the close's distance "
            "from the range's *midpoint*, then double-smooths both that distance and the range "
            "itself with two EMA passes before dividing."
        ),
        "reading": (
            "Same overbought/oversold intuition as an ordinary stochastic (readings above +40 / "
            "below -40 are commonly cited), but because both the numerator and denominator are "
            "double-smoothed, SMI reaches its -100/+100 bounds far less abruptly than %K does."
        ),
        "pitfalls": (
            "Three separate smoothing periods (`length` for the range, `fast` and `slow` for the "
            "two EMA passes) stack together, so the effective lag is longer than any one of them "
            "alone suggests."
        ),
        "example": [
            lambda df: zeonta.smi(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "chaikin_volatility": {
        "title": "Chaikin Volatility (CVI)",
        "formula": "CVI = ROC(EMA(High - Low, n), n)",
        "about": (
            "Marc Chaikin's rate-of-change take on volatility: rather than reporting the typical "
            "range as a level the way [atr](atr.md) does, this smooths the range with an EMA "
            "and then reports the *percentage change* of that smoothed range over the same "
            "window — is the range widening or narrowing, not how large it currently is."
        ),
        "reading": (
            "Positive means the range has widened over the window (volatility picking up); "
            "negative means it has narrowed (volatility settling down) — often used to spot the "
            "quiet-before-the-storm setup a low, falling CVI can precede."
        ),
        "pitfalls": (
            "A rate of change of an already-smoothed quantity — expect more lag than `atr` "
            "itself, since this adds a second transformation on top of the EMA smoothing."
        ),
        "example": [
            lambda df: zeonta.chaikin_volatility(df["high"], df["low"]).tail(3),
        ],
    },
    "relative_volatility_index": {
        "title": "Relative Volatility Index (RVI)",
        "formula": (
            "SD = STDDEV(Close, stdev_length); U/D = SD split by up/down close; "
            "RVI = 100 * EMA(U) / (EMA(U) + EMA(D))"
        ),
        "about": (
            "Donald Dorsey's [rsi](rsi.md)-shaped take on volatility: the same up/down-split-"
            "then-smooth structure Wilder used for price change, applied to a rolling standard "
            "deviation instead — a volatility measure with *direction*, unlike [atr](atr.md)."
        ),
        "reading": (
            "Above 50 means recent volatility has shown up more on up bars than down bars; "
            "below 50 is the reverse. Often paired with a trend indicator: rising RVI alongside "
            "a confirmed uptrend supports the move, while rising RVI against the trend warns of "
            "a possible reversal."
        ),
        "pitfalls": (
            "Two stacked periods (`stdev_length`, `smooth_length`) rather than the single period "
            "`rsi` needs — both change the result meaningfully."
        ),
        "example": [
            lambda df: zeonta.relative_volatility_index(df["close"]).tail(3),
        ],
    },
    "klinger_volume_oscillator": {
        "title": "Klinger Volume Oscillator (KVO)",
        "formula": (
            "VF = 100 * Volume * Trend * |2*(dm/cm) - 1|, dm = High-Low, "
            "cm accumulates dm since the trend last flipped; KVO = EMA(VF,fast) - EMA(VF,slow)"
        ),
        "about": (
            "Stephen Klinger's more graded cousin of [obv](obv.md): rather than adding or "
            "subtracting a bar's entire volume by direction alone, the 'volume force' is scaled "
            "by how the bar's own range compares to the accumulated range since the trend last "
            "flipped — a half-hearted push contributes less than a bar where the range dominates "
            "the whole move."
        ),
        "reading": (
            "Read like [macd](macd.md): the crossover between KVO and its own signal line, or "
            "KVO crossing zero, confirming a price move with real volume conviction behind it."
        ),
        "pitfalls": (
            "The trend/cm bookkeeping means a single missing bar has more reach than a plain "
            "EMA gap would — a NaN bar breaks the trend comparison for the bar right after it "
            "too, recovering fully only once two consecutive clean bars are available."
        ),
        "example": [
            lambda df: zeonta.klinger_volume_oscillator(
                df["high"], df["low"], df["close"], df["volume"]
            ).tail(3),
        ],
    },
    "williams_ad": {
        "title": "Williams Accumulation/Distribution (WAD)",
        "formula": (
            "TRH = max(Close[-1], High); TRL = min(Close[-1], Low); "
            "WAD += (Close-TRL) if Close rose, (Close-TRH) if Close fell, else unchanged"
        ),
        "about": (
            "Larry Williams' predecessor to [adl](adl.md): where ADL weighs a bar by where the "
            "close sits inside *that bar's own* range, WAD anchors each bar against the *prior* "
            "close instead — a bar that gapped up only gets credit for the move above "
            "yesterday's close, not its own full range. No volume term, despite living in this "
            "category alongside ADL/OBV."
        ),
        "reading": (
            "Read the same way as `adl`/`obv` — a rising line alongside rising price confirms "
            "the trend; a failure to make a new high alongside price is a divergence warning."
        ),
        "pitfalls": (
            "A running total with an arbitrary starting level, like `adl`/`obv`/`pvt` — only "
            "its slope and its divergence from price carry meaning."
        ),
        "example": [
            lambda df: zeonta.williams_ad(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "heikin_ashi": {
        "title": "Heikin-Ashi Candles",
        "formula": (
            "HAclose=(O+H+L+C)/4; HAopen[0]=(O+C)/2 then (HAopen[-1]+HAclose[-1])/2; "
            "HAhigh=max(H,HAopen,HAclose); HAlow=min(L,HAopen,HAclose)"
        ),
        "about": (
            "'Average bar' — builds a second, smoothed OHLC series from the real one, where "
            "each bar's open folds in the *previous* bar's own smoothed open and close. The "
            "same kind of recursive, self-referencing smoothing [ema](ema.md) applies to a "
            "single price line, applied here to a whole candle."
        ),
        "reading": (
            "A run of same-direction candles with little or no opposite-colored wick is the "
            "classic read for a trend that has not shown genuine reversal pressure yet — noise "
            "a plain candle chart would still show bar to bar is filtered out here."
        ),
        "pitfalls": (
            "The recursive open means a single missing bar changes every later Heikin-Ashi "
            "value from that point on — there is no fixed window for the effect to age out of, "
            "unlike most indicators in this library."
        ),
        "example": [
            lambda df: zeonta.heikin_ashi(df["open"], df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "adxr": {
        "title": "ADX Rating (ADXR)",
        "formula": "ADXR = (ADX + ADX[length - 1 bars ago]) / 2",
        "about": (
            "A smoothed extension of [adx](adx.md): today's ADX averaged with its own "
            "value from ``length - 1`` bars ago. The same idea `trima`'s double-SMA pass "
            "applies to price, applied here to ADX instead — trading a bit more lag for "
            "fewer false tops and bottoms in the trend-strength reading."
        ),
        "reading": (
            "Read exactly like `adx` — a rising ADXR means the trend (whichever "
            "direction) is strengthening. Smoother than `adx` itself, so a change in "
            "ADXR's own direction is a steadier signal that trend strength has peaked or "
            "bottomed."
        ),
        "pitfalls": (
            "Needs roughly ``3 * length`` bars before it produces a value — `adx`'s own "
            "``2 * length``-bar warm-up, plus another ``length - 1`` bars for the lagged "
            "copy it averages against."
        ),
        "example": [
            lambda df: zeonta.adxr(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "qstick": {
        "title": "Qstick",
        "formula": "QS = SMA(Close - Open, length)",
        "about": (
            "Tushar Chande's simplest indicator: a moving average of each bar's own "
            "body (Close minus Open). Distinct from [bop](bop.md), which normalises the "
            "same close-minus-open difference by the bar's own high-low range instead of "
            "smoothing it directly."
        ),
        "reading": (
            "Positive means closes have consistently landed above opens over the window "
            "(bullish body bias); negative the mirror. A cross of Qstick's own zero line "
            "is the standard read."
        ),
        "pitfalls": "No special edge cases — a plain SMA of a simple bar-body difference.",
        "example": [
            lambda df: zeonta.qstick(df["open"], df["close"]).tail(3),
        ],
    },
    "accbands": {
        "title": "Acceleration Bands",
        "formula": (
            "Ratio = c*(High-Low)/(High+Low); "
            "Upper=SMA(High*(1+Ratio),n); Lower=SMA(Low*(1-Ratio),n); Middle=SMA(Close,n)"
        ),
        "about": (
            "Price Headley's volatility envelope: unlike [bbands](bbands.md) (which "
            "scales a fixed multiplier by *rolling* standard deviation), the widening "
            "here comes from each individual bar's *own* high-low range — a single big "
            "bar pushes the bands apart immediately, with no lag from a deviation window."
        ),
        "reading": (
            "Read like any envelope: a close outside the bands on a weekly or monthly "
            "chart is Headley's own preferred breakout signal; on shorter frames the "
            "bands double as dynamic support/resistance."
        ),
        "pitfalls": (
            "A zero-range-and-zero-price bar (High + Low == 0) leaves the ratio "
            "undefined; the bands fall back to `NaN` for that bar rather than dividing by "
            "zero."
        ),
        "example": [
            lambda df: zeonta.accbands(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "bias": {
        "title": "Bias",
        "formula": "BIAS = (Close - SMA(Close, length)) / SMA(Close, length) * 100",
        "about": (
            "A staple of Chinese/Taiwanese technical analysis: puts a number on how far "
            "price has stretched away from its own moving average. Where "
            "[efficiency_ratio](efficiency_ratio.md) or [choppiness_index](choppiness_index.md) "
            "describe how a *window* moved, Bias describes a single distance — price's "
            "current gap from its own average, nothing more."
        ),
        "reading": (
            'A large positive or negative reading is commonly read as "stretched too '
            'far" — a pullback toward the average (if positive) or a rebound away from '
            "it (if negative) becomes more likely the further Bias strays from zero."
        ),
        "pitfalls": "`NaN` wherever the window's SMA is exactly `0`, rather than an undefined division.",
        "example": [
            lambda df: zeonta.bias(df["close"]).tail(3),
        ],
    },
    "psl": {
        "title": "Psychological Line (PSL)",
        "formula": "PSL = (up-closing bars in the last n) / n * 100",
        "about": (
            "A pure vote-counting sentiment gauge: the share of bars in a rolling window "
            "where price closed above the prior close, as a percentage. Unlike every "
            "ratio-based oscillator in this library ([rsi](rsi.md), [cmo](cmo.md), ...), "
            "PSL only asks *how often* price rose, never *by how much*."
        ),
        "reading": (
            "Above 50 means more than half the window's bars closed up; below 50 the "
            "mirror. Readings above roughly 75 or below 25 are commonly read as "
            "overbought/oversold sentiment extremes."
        ),
        "pitfalls": "A flat close (unchanged from the prior bar) counts as *not* up, the same convention as most up/down-day counters.",
        "example": [
            lambda df: zeonta.psl(df["close"]).tail(3),
        ],
    },
    "cpr": {
        "title": "Central Pivot Range (CPR)",
        "formula": "Pivot=(H+L+C)/3; BC=(H+L)/2; TC=2*Pivot-BC",
        "about": (
            "The same classic pivot [pivot_points](pivot_points.md) computes, plus a "
            "width band (Bottom Central, Top Central) built from the same previous bar's "
            "range. The band's width is always exactly two-thirds of the distance "
            "between the previous close and the previous range's midpoint."
        ),
        "reading": (
            "A narrow CPR means the prior bar closed near the middle of its own range "
            "(indecision, often preceding a bigger move); a wide CPR means it closed near "
            "an extreme (a directional bar, often preceding continuation)."
        ),
        "pitfalls": (
            "Like `pivot_points`, levels are computed from the **previous** bar and "
            "apply to the current one — feed daily bars for daily CPR levels, weekly bars "
            "for weekly ones."
        ),
        "example": [
            lambda df: zeonta.cpr(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "vwmacd": {
        "title": "Volume-Weighted MACD",
        "formula": (
            "VWMACD = VWMA(fast) - VWMA(slow); Signal = EMA(VWMACD, signal); "
            "Histogram = VWMACD - Signal"
        ),
        "about": (
            "The same fast-minus-slow-then-signal shape as [macd](macd.md), but built "
            "from [vwma](vwma.md) instead of a plain EMA. Weighting the fast and slow "
            "lines by volume makes crossovers more representative of moves that traded "
            "heavily, rather than treating a thin, quiet bar the same as a heavily-traded "
            "one the way plain MACD does. The signal line stays a plain EMA — the MACD "
            "line itself already carries the volume weighting."
        ),
        "reading": "Read exactly like `macd` — the crossover between the line and its own signal, or the line crossing zero.",
        "pitfalls": "Inherits `vwma`'s own zero-total-volume edge case: `NaN` wherever a window's total volume is exactly `0`.",
        "example": [
            lambda df: zeonta.vwmacd(df["close"], df["volume"]).tail(3),
        ],
    },
    "kdj": {
        "title": "KDJ",
        "formula": (
            "RSV = 100*(Close-LL)/(HH-LL); K = Wilder(RSV, signal); "
            "D = Wilder(K, signal); J = 3*K - 2*D"
        ),
        "about": (
            "A stochastic variant popular in Chinese-market technical analysis. Starts "
            "from the same Raw Stochastic Value [stoch](stoch.md) calls `%K` before "
            "smoothing, then smooths it twice with Wilder's recursion (the same one "
            "[smma](smma.md) exposes) rather than a plain SMA. `J` extrapolates past the "
            "`K`/`D` move rather than averaging it, so it swings outside the usual 0-100 "
            "range — the point of it is to flag overbought/oversold conditions *before* "
            "`K` and `D` reach their own extremes."
        ),
        "reading": (
            "Read like `stoch`: crossovers between `K` and `D` signal momentum shifts, "
            "with `J` leading both — a `J` reading well above 100 or below 0 is the "
            "earliest warning of an extreme."
        ),
        "pitfalls": "`J` is unbounded by design — do not clamp it to 0-100 the way `K`/`D` naturally are.",
        "example": [
            lambda df: zeonta.kdj(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "qqe": {
        "title": "Quantitative Qualitative Estimation (QQE)",
        "formula": (
            "RsiMa = EMA(RSI, smooth); DeltaFastAtrRsi = EMA(EMA(|ΔRsiMa|, 2n-1), 2n-1)*factor; "
            "trailing band flips like a Supertrend built on RsiMa"
        ),
        "about": (
            "Smooths [rsi](rsi.md) with an EMA, measures that smoothed line's own "
            "bar-to-bar volatility (Wilder-smoothed twice), and uses it to build a "
            "trailing band around the smoothed RSI — the same one-way-ratchet, "
            "flip-on-cross construction [supertrend](supertrend.md) uses on price, "
            "applied to RSI instead. QQE has no single academic paper behind it — it "
            "originates as a MetaTrader community indicator — but its construction is "
            "precise and cross-confirmed identically across multiple independent "
            "implementations, unlike indicators this library has declined for lacking "
            "exactly that."
        ),
        "reading": (
            "The trailing line's own value is bullish support while price/RSI stays "
            "above it, and resistance while below — read the crossover between the "
            "smoothed RSI and the trailing line the way you would `supertrend`'s flips, "
            "or watch the smoothed RSI cross its own 50 midline."
        ),
        "pitfalls": (
            "Needs a long warm-up — the double-smoothed volatility term alone needs "
            "roughly `2*(2*length-1)` bars on top of RSI's own warm-up before it produces "
            "a value."
        ),
        "example": [
            lambda df: zeonta.qqe(df["close"]).tail(3),
        ],
    },
    "parkinson_volatility": {
        "title": "Parkinson Volatility",
        "formula": "PARKV = 100 * sqrt(mean(ln(High/Low)^2, length) / (4 * ln(2)))",
        "about": (
            "An extreme-value volatility estimator built from the high-low range alone, on the "
            "theory that the whole path a bar took — not just where it closed — carries "
            "information about its variance. The same idea [true_range](true_range.md)/"
            "[atr](atr.md) apply to range, applied here to variance instead."
        ),
        "reading": (
            "Read like any volatility measure: a rising value means the market's own bars are "
            "spanning more ground, falling means they're tightening up. Reported in percent, not "
            "annualized — multiply by `sqrt(periods_per_year)` if you want the conventional "
            "annualized figure."
        ),
        "pitfalls": (
            "Assumes zero drift and no opening jumps; a strongly trending or gapping series "
            "inflates this estimator. [rogers_satchell_volatility](rogers_satchell_volatility.md) "
            "and [yang_zhang_volatility](yang_zhang_volatility.md) correct for exactly that."
        ),
        "example": [
            lambda df: zeonta.parkinson_volatility(df["high"], df["low"]).tail(3),
        ],
    },
    "garman_klass_volatility": {
        "title": "Garman-Klass Volatility",
        "formula": (
            "GKV = 100 * sqrt(mean(0.5*ln(High/Low)^2 - (2*ln(2)-1)*ln(Close/Open)^2, length))"
        ),
        "about": (
            "Extends [parkinson_volatility](parkinson_volatility.md) with the open-close jump, "
            "using all four OHLC prices rather than the range alone for a more statistically "
            "efficient estimate at the same window length."
        ),
        "reading": (
            "Read the same way as `parkinson_volatility` — reported in percent, not annualized."
        ),
        "pitfalls": (
            "Still assumes zero drift and no opening jump, the same limitation "
            "`parkinson_volatility` has; [yang_zhang_volatility](yang_zhang_volatility.md) is the "
            "estimator in this family that corrects for both."
        ),
        "example": [
            lambda df: zeonta.garman_klass_volatility(
                df["open"], df["high"], df["low"], df["close"]
            ).tail(3),
        ],
    },
    "rogers_satchell_volatility": {
        "title": "Rogers-Satchell Volatility",
        "formula": (
            "RSV = 100 * sqrt(mean(ln(High/Close)*ln(High/Open) "
            "+ ln(Low/Close)*ln(Low/Open), length))"
        ),
        "about": (
            "An OHLC volatility estimator that, unlike "
            "[parkinson_volatility](parkinson_volatility.md) and "
            "[garman_klass_volatility](garman_klass_volatility.md), does not assume zero drift — "
            "it stays unbiased whether the market trended hard or went nowhere over the window."
        ),
        "reading": "Read the same way as the other estimators in this family — percent, not annualized.",
        "pitfalls": (
            "Drift-independent but still assumes no opening jump; "
            "[yang_zhang_volatility](yang_zhang_volatility.md) adds that correction on top of "
            "this estimator's own range term."
        ),
        "example": [
            lambda df: zeonta.rogers_satchell_volatility(
                df["open"], df["high"], df["low"], df["close"]
            ).tail(3),
        ],
    },
    "yang_zhang_volatility": {
        "title": "Yang-Zhang Volatility",
        "formula": (
            "YZV = 100 * sqrt(Var(overnight) + k*Var(open_close) "
            "+ (1-k)*mean(RogersSatchell_per_bar)), k = 0.34/(1.34+(n+1)/(n-1))"
        ),
        "about": (
            "Combines an overnight-gap variance term, an intraday open-to-close variance term, "
            "and [rogers_satchell_volatility](rogers_satchell_volatility.md)'s own drift-"
            "independent range term into the most statistically efficient of the four OHLC "
            "volatility estimators in this module, while staying unbiased under both drift and "
            "opening jumps."
        ),
        "reading": "Read the same way as the other estimators in this family — percent, not annualized.",
        "pitfalls": (
            "Needs `length >= 2` (the variance terms need at least two points), and the "
            "combining weight `k` is recomputed from `length` itself — it is not a universal "
            "constant."
        ),
        "example": [
            lambda df: zeonta.yang_zhang_volatility(
                df["open"], df["high"], df["low"], df["close"]
            ).tail(3),
        ],
    },
    "approximate_entropy": {
        "title": "Approximate Entropy",
        "formula": "ApEn = phi(m) - phi(m+1), phi(k) = mean(ln(C_i^k)) including self-matches",
        "about": (
            "[sample_entropy](sample_entropy.md)'s predecessor, and the whole reason Sample "
            "Entropy exists: it counts template matches the same way but counts a template as "
            "matching *itself*, which biases every count upward and makes the statistic depend "
            "more on window length than Sample Entropy does."
        ),
        "reading": (
            "Read like `sample_entropy` — low means the window keeps repeating short patterns, "
            "high means little structure at all. Kept here for the reader who specifically wants "
            "Pincus's original statistic; for new work, `sample_entropy` corrects this "
            "estimator's two known biases."
        ),
        "pitfalls": (
            "Same `O(window^2)` per-bar cost as `sample_entropy` — see `BENCHMARKS.md`. Never "
            "negative in this self-match-inclusive form, unlike `sample_entropy`, which can be "
            "undefined when a window's tightest tolerance finds no matches at all."
        ),
        "example": [
            lambda df: zeonta.approximate_entropy(df["close"], window=100).tail(3),
        ],
    },
    "permutation_entropy": {
        "title": "Permutation Entropy",
        "formula": "PERMEN = -sum(p_i * ln(p_i)) over each observed ordinal pattern i",
        "about": (
            "Reduces every overlapping slice of a rolling window to the *ordering* of its "
            "values — which of the possible orderings it matches, never their actual size — "
            "then takes the Shannon entropy of how often each ordering occurred. A different "
            "way of asking `sample_entropy`'s question, from shape rather than distance."
        ),
        "reading": (
            "A window that keeps repeating the same up/down shape has low permutation entropy; "
            "one with no preferred shape approaches `ln(order!)`, the maximum for that `order`."
        ),
        "pitfalls": (
            "Reported in nats (natural-log units), not the normalized 0-1 form some other "
            "software reports — divide by `ln(order!)` to get that. Ties within a window are "
            "broken by position, the conventional Bandt-Pompe rule, not treated as an error."
        ),
        "example": [
            lambda df: zeonta.permutation_entropy(df["close"], window=100, order=3).tail(3),
        ],
    },
    "connors_rsi": {
        "title": "Connors RSI",
        "formula": "CRSI = (RSI(Close) + RSI(Streak) + PercentRank(ROC(1))) / 3",
        "about": (
            "Averages three independent short-term readings of the same close series: an "
            "ordinary [rsi](rsi.md) on price, an `rsi` on the signed streak of consecutive "
            "up/down closes (is the current run itself unusually long?), and a percent-rank of "
            "the latest 1-bar return against its own recent history (a magnitude-aware read "
            "neither RSI term captures)."
        ),
        "reading": (
            "Ranges 0-100 like each of its three components; short-term mean-reversion traders "
            "commonly treat readings under 10-20 or over 80-90 as extremes."
        ),
        "pitfalls": (
            "Three separate lookbacks (`rsi_length`, `streak_length`, `rank_length`) stack "
            "together — changing any one changes the blend, not just one leg of it."
        ),
        "example": [
            lambda df: zeonta.connors_rsi(df["close"]).tail(3),
        ],
    },
    "ift_rsi": {
        "title": "Inverse Fisher Transform of RSI",
        "formula": (
            "v1 = 0.1*(RSI-50); v2 = WMA(v1, smooth); IFTRSI = (exp(2*v2)-1)/(exp(2*v2)+1)"
        ),
        "about": (
            "Rescales [rsi](rsi.md) toward zero, smooths it, and squashes the result through "
            "Ehlers' Inverse Fisher Transform — a curve that passes the middle of its input "
            "through almost unchanged but compresses everything else hard toward -1 or +1, "
            "trading RSI's gentle 0-100 curve for a near-binary reading."
        ),
        "reading": (
            "Readings pin close to -1 or +1 far more often than RSI pins near 0 or 100 — that "
            "compression is the entire point, giving very clear (if less nuanced) turning-point "
            "signals."
        ),
        "pitfalls": (
            "The compression means small, genuine changes in the underlying RSI can vanish "
            "once squashed toward an extreme — this trades resolution for clarity, not a free "
            "improvement on RSI."
        ),
        "example": [
            lambda df: zeonta.ift_rsi(df["close"]).tail(3),
        ],
    },
    "frama": {
        "title": "Fractal Adaptive Moving Average",
        "formula": (
            "D = (ln(N1+N2)-ln(N3))/ln(2); alpha = clip(exp(-4.6*(D-1)), 0.01, 1.0); "
            "FRAMA = alpha*Price + (1-alpha)*FRAMA[-1]"
        ),
        "about": (
            "An EMA whose smoothing constant adapts to price's own fractal dimension — the "
            "same self-adjusting idea [kama](kama.md) and [vidya](vidya.md) use, built from "
            "how rough the high-low range looks at two different window scales instead of "
            "Kaufman's Efficiency Ratio or Chande's CMO."
        ),
        "reading": (
            "Read like any moving average. At a fractal dimension of 1 (a straight trend) it "
            "moves as fast as price itself; at a fractal dimension of 2 (pure noise) it moves "
            "as slowly as a 200-bar SMA — rapidly following real moves while staying flat "
            "through congestion."
        ),
        "pitfalls": (
            "Outputs the midpoint price directly for the first `length` bars rather than `NaN` "
            "— there is no fixed-window warm-up the way `ema` has, since the adaptive recursion "
            "only starts once a full window exists to measure the fractal dimension from."
        ),
        "example": [
            lambda df: zeonta.frama(df["high"], df["low"]).tail(3),
        ],
    },
    "gmma": {
        "title": "Guppy Multiple Moving Average",
        "formula": "Two 6-line EMA groups: fast = EMA(3,5,8,10,12,15), slow = EMA(30,35,40,45,50,60)",
        "about": (
            "Two fixed six-line [ema_ribbon](ema_ribbon.md)s plotted together rather than one: "
            "a fast group standing in for short-term trader activity, and a slow group standing "
            "in for longer-term investor activity. Neither group's periods are tunable — the "
            "whole point of GMMA is this specific pair of period sets, not a generic ribbon."
        ),
        "reading": (
            "Compression *within* a group signals agreement among that group's own timescales; "
            "wide separation *between* the two groups signals a well-established trend. The "
            "fast group crossing the slow group is the classic entry signal, but reading the "
            "ribbons' own compression/expansion is the indicator's real purpose."
        ),
        "pitfalls": "Twelve EMA lines at once is a lot to plot — most charting tools shade each group as a ribbon rather than drawing all twelve individually.",
        "example": [
            lambda df: zeonta.gmma(df["close"]).tail(3),
        ],
    },
    "williams_fractals": {
        "title": "Williams Fractals",
        "formula": "Bearish: High[i] > 2 highs each side; Bullish: Low[i] < 2 lows each side",
        "about": (
            "Bill Williams' 5-bar pivot test — the same strict local-extremum check "
            "[support_resistance](support_resistance.md) builds on, at that indicator's own "
            "`left=right=2`."
        ),
        "reading": (
            "A confirmed fractal marks a potential reversal point; Williams' own methodology "
            "pairs it with the Alligator and Awesome Oscillator rather than trading fractals "
            "alone."
        ),
        "pitfalls": (
            "A fractal is only knowable 2 bars after it happened (the two right-side bars must "
            "exist first) — unlike `support_resistance`'s `RES`/`SUP` columns, this does not "
            "shift the flag forward, so a fractal shown at bar i was not actually confirmed "
            "until bar i+2. Look ahead of the marked bar, not at it, if trading the confirmation."
        ),
        "example": [
            lambda df: zeonta.williams_fractals(df["high"], df["low"]).tail(5),
        ],
    },
    "roofing_filter": {
        "title": "Roofing Filter",
        "formula": (
            "2-pole highpass(Close, hp_length) then SuperSmoother(., lp_length): "
            "keeps only cycles between lp_length and hp_length bars"
        ),
        "about": (
            "Removes both ends of the spectrum from price: a 2-pole high-pass removes cycles "
            "longer than `hp_length` (slow drift an oscillator shouldn't react to), and "
            "[super_smoother](super_smoother.md) then removes cycles shorter than `lp_length` "
            "(the aliasing noise a plain moving average lets through). What's left is only the "
            "band of cycles between the two."
        ),
        "reading": (
            "Ehlers designed this specifically to precede other oscillators — feeding this into "
            "[stoch](stoch.md) or [rsi](rsi.md) instead of raw price makes them react to genuine "
            "cycles rather than trend or noise."
        ),
        "pitfalls": (
            "Not an oscillator on its own — it has no fixed range and no natural zero line. It's "
            "a pre-processing filter meant to sit in front of one."
        ),
        "example": [
            lambda df: zeonta.roofing_filter(df["close"]).tail(3),
        ],
    },
    "even_better_sinewave": {
        "title": "Even Better Sinewave",
        "formula": (
            "HP = highpass(Close, hp_length); Filt = SuperSmoother(HP, lp_length); "
            "EBSW = mean(Filt,Filt[-1],Filt[-2]) / sqrt(mean(Filt^2,Filt[-1]^2,Filt[-2]^2))"
        ),
        "about": (
            "A highpass-then-smoothed cycle extraction, like [roofing_filter](roofing_filter.md), "
            "but divided by its own recent RMS amplitude so the result traces out an actual sine "
            'wave regardless of how big the underlying cycle currently is — the "even better" '
            "in the name is this self-normalization, versus Ehlers' earlier, unnormalized "
            "Sinewave Indicator."
        ),
        "reading": (
            "Ranges roughly -1 to 1 like a genuine sine wave; zero-line crossings and peaks/"
            "troughs mark the cycle's own turning points far more cleanly than an un-normalized "
            "oscillator would in a low-volatility stretch."
        ),
        "pitfalls": (
            "Exactly `0` (not `NaN`) wherever the filtered signal has been flat for three bars "
            "running — a degenerate but legal `0/0` case, not a division error."
        ),
        "example": [
            lambda df: zeonta.even_better_sinewave(df["close"]).tail(3),
        ],
    },
    "cyber_cycle": {
        "title": "Cyber Cycle",
        "formula": (
            "Smooth = (P+2P[-1]+2P[-2]+P[-3])/6; "
            "Cycle = (1-a/2)^2*(Smooth-2Smooth[-1]+Smooth[-2]) + 2(1-a)Cycle[-1] - (1-a)^2Cycle[-2]"
        ),
        "about": (
            "A 4-bar weighted smooth of the median price fed into a 2-pole highpass tuned by a "
            'fixed smoothing constant rather than a length in bars. Ehlers\' own "Adaptive" '
            "variant instead measures the market's own dominant cycle period (via a Hilbert "
            "Transform discriminator) and feeds that into the constant bar by bar — that "
            "measurement stage is the same dominant-cycle apparatus behind MAMA, an indicator "
            "this library has already declined, so only the fixed-constant form is implemented "
            "here."
        ),
        "reading": (
            "Oscillates around zero at the market's own dominant cycle rate; the crossover "
            "between `CYBERCYCLE` and its own one-bar-delayed trigger line is the standard read, "
            "the same pattern [fisher_transform](fisher_transform.md) uses."
        ),
        "pitfalls": (
            "A fixed smoothing constant means the filter is tuned for one cycle length — it "
            "will lag or overreact if the market's actual dominant cycle drifts far from what "
            "`alpha=0.07` implicitly assumes."
        ),
        "example": [
            lambda df: zeonta.cyber_cycle(df["high"], df["low"]).tail(3),
        ],
    },
    "voss_predictive_filter": {
        "title": "Voss Predictive Filter",
        "formula": (
            "Filt = BandPass(Close, period, bandwidth); "
            "Voss = ((3+order)/2)*Filt - sum((k+1)/order * Voss[-(order-k)], k=0..order-1)"
        ),
        "about": (
            "Band-limits price with a 2-pole bandpass filter, then runs it through a filter "
            "with *negative group delay* (Henning Voss' \"Universal Negative Group Delay Filter "
            'for the Prediction of Band-Limited Signals", adapted by Ehlers) to produce a '
            "second line that leads the bandpass output rather than lagging it."
        ),
        "reading": (
            "Plot `VOSS` against `VOSSFILT` — `VOSS` measurably precedes `VOSSFILT`'s own turns, "
            "so a crossover between the two at a peak or valley is Ehlers' own suggested signal."
        ),
        "pitfalls": (
            "This cannot see the future — the input must already be band-limited (which the "
            "bandpass stage guarantees only within its own passband), and a market that isn't "
            "currently cycling near `period` gives a `VOSS` line with nothing meaningful to lead."
        ),
        "example": [
            lambda df: zeonta.voss_predictive_filter(df["close"]).tail(3),
        ],
    },
    "reflex_trendflex": {
        "title": "Reflex and Trendflex",
        "formula": (
            "Filt = SuperSmoother(Close, length/2); "
            "Reflex = mean(Filt+k*Slope-Filt[-k]) / sqrt(MS); Trendflex = mean(Filt-Filt[-k]) / sqrt(MS)"
        ),
        "about": (
            "Both start from the same [super_smoother](super_smoother.md) pass at half `length`, "
            "then average that filtered line's own deviation from a reference over the full "
            "window — Reflex measures deviation from a straight line drawn across the window "
            "(stripping trend, isolating cycle swings), Trendflex measures deviation from the "
            "filtered line's *current* value (keeping trend in)."
        ),
        "reading": (
            'Both self-normalize against their own recent mean square, the same "divide by '
            'local RMS" idea [even_better_sinewave](even_better_sinewave.md) uses, so their '
            "scale stays comparable across different volatility regimes — read zero-line "
            "crossings and extremes the same way you would any zero-lag oscillator."
        ),
        "pitfalls": (
            "Reflex and Trendflex answer different questions from the same input — Reflex "
            "isolates the cycle, Trendflex keeps the trend — so reading one where you meant the "
            "other gives a misleading signal even though both are always well-defined together."
        ),
        "example": [
            lambda df: zeonta.reflex_trendflex(df["close"]).tail(3),
        ],
    },
    "higuchi_fractal_dimension": {
        "title": "Higuchi Fractal Dimension",
        "formula": (
            "For k = 1..k_max, resample the window every k-th point starting at each offset "
            "m = 1..k: L_m(k) = (N-1) / (floor((N-m)/k) x k^2) x "
            "sum |x(m+i x k) - x(m+(i-1) x k)|; L(k) = mean over m of L_m(k); "
            "HFD = slope of log(L(k)) regressed against log(1/k)"
        ),
        "about": (
            "Higuchi (1988) estimates a time series' fractal dimension directly from its own "
            "curve, without going through returns first the way hurst_exponent and dfa do: it "
            "measures how much shorter the window's own path gets when only every k-th point is "
            "kept, for several step sizes k, and reads the fractal dimension off how fast that "
            "shrinkage compounds. It is also a different construction from frama()'s internal "
            "box-counting dimension, which compares high-low range at two window halves rather "
            "than resampling the price path itself."
        ),
        "reading": (
            "Reads the same way as any box-counting fractal dimension: values near 1 describe a "
            "path close to a straight line (a strong, persistent trend); values near 2 describe "
            "a path that fills space as roughly as pure noise (choppy, directionless). Unlike "
            "hurst_exponent/dfa, there is no 0.5 'random walk' reference point built into the "
            "reading — 1 and 2 are the two ends of the scale here, not a midpoint split."
        ),
        "pitfalls": (
            "k_max is a free parameter the original paper does not pin to one value; 10 is the "
            "convention most secondary literature on this method has settled on, not something "
            "Higuchi's own paper mandates. A short or unusually smooth window can produce fewer "
            "than two usable (k, L(k)) pairs to regress against, in which case the result is "
            "NaN rather than an unreliable single-point slope."
        ),
        "example": [
            lambda df: zeonta.higuchi_fractal_dimension(df["close"]).tail(3),
        ],
    },
    "ffd": {
        "title": "Fixed-Width Window Fractional Differentiation",
        "formula": (
            "w_0 = 1, w_k = -w_{k-1} x (d-k+1)/k generated until |w_k| < threshold (l* weights "
            "kept); FFD[t] = sum(w_k x Close[t-k], k = 0..l*)"
        ),
        "about": (
            "Plain differencing (a 1-bar log_return or Close.diff()) makes a price series "
            "stationary but throws away all memory of its own level along with it. Lopez de "
            "Prado (2018) generalizes differencing to a fractional order d between 0 and 1 via "
            "the binomial series expansion of (1-B)^d, then truncates that expansion's weights "
            "to a fixed count once they fall below a threshold — the 'fixed-width window' this "
            "method is named for, as opposed to the same book's expanding-window variant, which "
            "reweights a series' entire history at every bar instead of a fixed trailing window."
        ),
        "reading": (
            "d close to 0 barely differences the series (it stays close to raw Close, and "
            "non-stationary); d close to 1 approaches plain first differencing (stationary, but "
            "memory-free). The book's own point is to search for the smallest d that a "
            "stationarity test (e.g. ADF) accepts, keeping as much memory as the transform "
            "allows — this function computes the transform for a d you choose, not that search."
        ),
        "pitfalls": (
            "threshold controls a real memory/window-length trade-off, not just a numerical "
            "nicety: the book's own default (1e-5) keeps several hundred weights even at "
            "d=0.5, which needs a correspondingly long history before the first output bar. "
            "This function defaults to a shorter, more usable 1e-3 instead — the weight "
            "recursion and truncation rule are unchanged from the book, only the default cutoff "
            "is this library's own choice, the same way many rolling-window defaults elsewhere "
            "here are a reasonable pick rather than something the source itself mandates."
        ),
        "example": [
            lambda df: zeonta.ffd(df["close"]).tail(3),
        ],
    },
    "amihud_illiquidity": {
        "title": "Amihud Illiquidity Ratio",
        "formula": "ILLIQ = mean(|R_t| / DollarVolume_t, length), R_t = (Close_t - Close_{t-1}) / Close_{t-1}, DollarVolume_t = Close_t x Volume_t",
        "about": (
            "Amihud (2002) proposes the simplest possible price-impact proxy available from "
            "daily bars alone: how far price moves, per dollar of volume that traded. A bar "
            "that swings a lot on thin dollar volume is illiquid — a small order was enough to "
            "move the price; a bar that barely moves on heavy dollar volume is liquid. Averaged "
            "over a window, this gives a rough, easily computed stand-in for the "
            "microstructure-level measures (quoted spreads, order-book depth) that need data "
            "most markets and most history don't have."
        ),
        "reading": (
            "Higher values mean less liquidity (more price impact per dollar traded); lower "
            "values mean more. Amihud's own paper uses ILLIQ cross-sectionally, ranking many "
            "stocks against each other and against their own history — the raw number is not "
            "comparable across instruments quoted in different currencies or at very different "
            "price and volume levels without further normalization."
        ),
        "pitfalls": (
            "A bar with zero dollar volume produces an undefined ratio (treated as NaN, not "
            "infinite), which only makes the windows still containing it NaN rather than "
            "corrupting the series from that point on. length=21 (roughly one trading month) is "
            "this library's own choice of averaging window, not something the 2002 paper "
            "prescribes — the paper's own cross-sectional study averages over a full year."
        ),
        "example": [
            lambda df: zeonta.amihud_illiquidity(df["close"], df["volume"]).tail(3),
        ],
    },
    "corwin_schultz_spread": {
        "title": "Corwin-Schultz Spread Estimator",
        "formula": (
            "beta = ln(H[t-1]/L[t-1])^2 + ln(H[t]/L[t])^2; "
            "gamma = ln(max(H[t-1],H[t]) / min(L[t-1],L[t]))^2; "
            "alpha = (sqrt(2 x beta) - sqrt(beta))/(3-2 x sqrt(2)) - sqrt(gamma/(3-2 x sqrt(2))); "
            "S = max(2 x (exp(alpha)-1) / (1+exp(alpha)), 0)"
        ),
        "about": (
            "Corwin & Schultz (2012) estimate a bid-ask spread from nothing but two consecutive "
            "bars' highs and lows — no trade or quote data at all. The insight: a bar's high is "
            "usually a buyer-initiated trade at the ask and its low a seller-initiated trade at "
            "the bid, so a bar's own high-low range carries both the day's price volatility and "
            "a fixed bid-ask-bounce contribution. Volatility grows with the length of the "
            "interval measured; the bounce does not, so writing down the expected squared range "
            "for one bar and for a two-bar window and solving that pair of equations together "
            "isolates the spread on its own."
        ),
        "reading": (
            "Read CS as a fraction of price — 0.01 is a 1% quoted spread. It is a liquidity-cost "
            "estimate, not a volatility measure in the usual sense: a wider CS means trading "
            "this instrument costs more of the price just to cross the spread, independent of "
            "how much the price itself is moving."
        ),
        "pitfalls": (
            "The closed-form estimate can come out negative on a bar pair whose combined 2-day "
            "range happens to be tighter than either single day's own range — the paper's own "
            "remedy, floored to zero here, is what this function applies rather than leaving a "
            "meaningless negative number or turning it into NaN. This implements the paper's "
            "core two-day estimator only, not its optional overnight-jump adjustment for cases "
            "where the previous close printed outside the current day's own high-low range."
        ),
        "example": [
            lambda df: zeonta.corwin_schultz_spread(df["high"], df["low"]).tail(3),
        ],
    },
    "abdi_ranaldo_spread": {
        "title": "Abdi-Ranaldo Spread Estimator",
        "formula": (
            "eta[t] = (ln(High[t]) + ln(Low[t])) / 2; "
            "S[t] = sqrt(max((ln(Close[t-1]) - eta[t-1]) x (ln(Close[t-1]) - eta[t]), 0))"
        ),
        "about": (
            "Abdi & Ranaldo (2017) combine corwin_schultz_spread's insight (a bar's high-low "
            "midrange is a better estimate of the efficient price than its close, because the "
            "bid-ask half-spreads on either side of the range cancel) with roll_spread's "
            "autocovariance construction, but applied to midrange-to-close-to-midrange instead "
            "of close-to-close. The result is a two-day, close/high/low-only spread estimator "
            "that behaves better than either building block alone on daily data."
        ),
        "reading": (
            "Read AR as a fraction of price — 0.01 is a 1% quoted spread, the same convention as "
            "corwin_schultz_spread. It is a liquidity-cost estimate, not a volatility measure: a "
            "wider AR means more of the price is spent just crossing the spread on a round trip."
        ),
        "pitfalls": (
            "The raw product inside the square root can come out negative, the same known "
            "limitation corwin_schultz_spread and roll_spread both have; the paper's own remedy, "
            "applied here, is to floor each single two-day estimate at zero rather than leave it "
            "negative or turn the whole bar into NaN. Only the first bar (no earlier bar to pair "
            "against) is genuinely undefined, and is NaN."
        ),
        "example": [
            lambda df: zeonta.abdi_ranaldo_spread(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "roll_spread": {
        "title": "Roll Spread Estimator",
        "formula": (
            "Scov[t] = Cov(r, r_lag1) over the trailing window; "
            "Spread[t] = 2 x sqrt(-Scov[t]) if Scov[t] < 0, else undefined"
        ),
        "about": (
            "Roll (1984) shows that in an efficient market, the bid-ask bounce alone — trades "
            "alternating between the bid and the ask with no new information moving the 'true' "
            "price at all — induces negative first-order serial covariance in successive "
            "returns. The size of that induced negative covariance identifies the spread "
            "directly, with no trade-direction data needed at all, only a return series."
        ),
        "reading": (
            "Read ROLL as a fraction of price. Unlike corwin_schultz_spread and "
            "abdi_ranaldo_spread, which use the high-low range and stay defined on almost every "
            "bar, Roll's estimator needs the return series' own serial covariance to be "
            "negative — something that is common at tick/trade frequency but frequently fails "
            "at daily frequency, especially for heavily traded instruments."
        ),
        "pitfalls": (
            "Whenever a window's serial covariance is non-negative, the estimator is genuinely "
            "undefined (NaN here) — not zero, and not a valid spread computed from a negative "
            "number under the square root. This is a well-documented limitation of the "
            "estimator itself (see Harris, 1990), not a bug: expect long stretches of NaN on "
            "daily bars for liquid instruments, where corwin_schultz_spread/abdi_ranaldo_spread "
            "stay defined far more often."
        ),
        "example": [
            lambda df: zeonta.roll_spread(df["close"]).tail(3),
        ],
    },
    "bipower_variation": {
        "title": "Realized Bipower Variation",
        "formula": "BV = (pi/2) x sum(|r[i-1]| x |r[i]|, i = 2..n) over a window of log returns",
        "about": (
            "Realized variance (the sum of squared log returns over a window) is a consistent "
            "estimator of total quadratic variation — both the continuous, diffusive part of "
            "price movement and any jumps. Barndorff-Nielsen & Shephard (2004, 2006) show that "
            "summing products of adjacent absolute returns instead, scaled by pi/2, estimates "
            "only the continuous part: a single large jump return inflates realized variance "
            "through its own squared value, but only enters bipower variation through two "
            "bounded cross-products with its ordinary-sized neighbours."
        ),
        "reading": (
            "BV reads on the same scale as a realized-variance-style estimate (log-return "
            "variance units, not annualized or square-rooted into a volatility). Comparing it "
            "to a same-window realized variance is this pair's own basis for detecting jumps: a "
            "realized variance well above bipower variation suggests a jump occurred, though the "
            "paper's full statistical test for that (its Z-statistic) needs a separate "
            "quarticity estimator this function does not compute."
        ),
        "pitfalls": (
            "This is the plain realized-BPV estimator from the paper's own equation, with no "
            "finite-sample bias correction (no n/(n-1) adjustment) — the paper itself states "
            "this estimator's consistency without one. window counts log returns, not close "
            "bars, so one extra close bar is needed beyond window to produce a value."
        ),
        "example": [
            lambda df: zeonta.bipower_variation(df["close"]).tail(3),
        ],
    },
    "realized_semivariance": {
        "title": "Realized Semivariance",
        "formula": (
            "RS+ = sum(r^2 : r > 0) over the window; RS- = sum(r^2 : r <= 0) over the window; "
            "RS+ + RS- = realized variance"
        ),
        "about": (
            "Barndorff-Nielsen, Kinnebrock & Shephard (2010) split realized variance — the sum "
            "of squared log returns over a window — into the part driven by up-moves and the "
            "part driven by down-moves. Ordinary realized variance cannot tell a volatile rally "
            "apart from a volatile selloff; the paper shows the downside half on its own carries "
            "real predictive power for future volatility that the symmetric total dilutes."
        ),
        "reading": (
            "RSPOS and RSNEG always sum to the same window's realized variance (sum of squared "
            "log returns) exactly — a useful sanity check on the two columns together. A window "
            "with RSNEG well above RSPOS reflects a period whose volatility was concentrated in "
            "down-moves, and vice versa."
        ),
        "pitfalls": (
            "length counts log returns, not close bars, so one extra close bar is needed beyond "
            "length to produce a value — the same convention bipower_variation uses. A bar with "
            "a non-positive close (making its log return NaN) poisons only the windows still "
            "containing it, the same self-recovering behaviour every rolling-window indicator "
            "in this library has."
        ),
        "example": [
            lambda df: zeonta.realized_semivariance(df["close"]).tail(3),
        ],
    },
    "multifractal_dfa": {
        "title": "Multifractal Detrended Fluctuation Analysis",
        "formula": (
            "F_q(n) = {mean over boxes of [F^2(n,box)]^(q/2)}^(1/q) for q != 0, or "
            "exp(mean(ln[F^2(n,box)])/2) for q = 0; "
            "h(q) = slope of log(F_q(n)) vs log(n); MFDFA = h(q_min) - h(q_max)"
        ),
        "about": (
            "dfa fits one scaling exponent to a return series, implicitly treating small and "
            "large fluctuations as scaling the same way. Kantelhardt et al. (2002) generalize "
            "DFA's fluctuation function with a q-th-power average over boxes instead of a plain "
            "RMS, reusing the exact same per-box detrended fluctuations dfa computes: negative q "
            "weights small fluctuations more heavily, positive q weights large ones. A "
            "monofractal series (small and large fluctuations scale identically, e.g. plain "
            "fractional Brownian motion) has h(q) essentially constant across q; a genuinely "
            "multifractal series has h(q) vary with q, and this function reports that variation "
            "as a single number, the width of the generalized-Hurst spectrum between two chosen "
            "q extremes."
        ),
        "reading": (
            "Near 0 describes a monofractal series (dfa's own single exponent already tells the "
            "whole story); larger describes a more strongly multifractal one, where small and "
            "large price swings genuinely follow different scaling laws. h(2) — the special case "
            "at q=2 this function does not expose on its own — reduces exactly to dfa's own "
            "exponent, so dfa and this function are checking related but different things."
        ),
        "pitfalls": (
            "q_min and q_max default to -5 and 5, the range most commonly scanned in the "
            "tutorial literature that has followed the original 2002 paper (e.g. Ihlen, 2012) — "
            "not something the paper itself mandates as the one correct choice. Like dfa, this "
            "divides each window into non-overlapping boxes counted from the start only, not "
            "also from the end as some MF-DFA implementations do, kept consistent with dfa's own "
            "existing convention in this library."
        ),
        "example": [
            lambda df: zeonta.multifractal_dfa(df["close"]).tail(3),
        ],
    },
    "cusum_filter": {
        "title": "CUSUM Filter",
        "formula": (
            "S+[t] = max(0, S+[t-1] + r[t]); S-[t] = min(0, S-[t-1] + r[t]); "
            "event = -1 and S- reset to 0 if S-[t] < -threshold; "
            "event = +1 and S+ reset to 0 if S+[t] > threshold; else event = 0"
        ),
        "about": (
            "Lopez de Prado's Symmetric CUSUM Filter tracks two running sums of log returns, "
            "one for upward drift and one for downward, each reset to zero the moment it "
            "crosses a fixed threshold. In the book it is used to sample bars for a downstream "
            "ML pipeline — only the bars where an event fires are kept. This library's "
            "aligned-per-bar contract has no place for dropping bars, so this function reports "
            "the discrete event flag itself at every bar instead, the same flag-column shape "
            "divergence already uses for events that only fire on some bars."
        ),
        "reading": (
            "A +1 means enough cumulative upward drift has built up since the last reset to "
            "cross threshold; -1 the same for downward drift; 0 means neither running sum has "
            "crossed yet. Because the running sums only reset on a crossing, the series will "
            "not fire repeatedly while hovering near the threshold — it takes a fresh, full run "
            "of drift to trigger the next event."
        ),
        "pitfalls": (
            "This is a genuinely stateful, whole-series recursion, not a fixed rolling window — "
            "like drawdown's running peak, prepending more history changes every later flag, "
            "since the running sums start accumulating from a different point. threshold is a "
            "fixed level in log-return units, not a multiple of a rolling volatility estimate; "
            "picking one that suits the instrument's typical volatility is left to the caller."
        ),
        "example": [
            lambda df: zeonta.cusum_filter(df["close"]).tail(3),
        ],
    },
    "multiscale_entropy": {
        "title": "Multiscale Entropy",
        "formula": (
            "y_j^(tau) = mean of log returns [(j-1)*tau+1 .. j*tau], j = 1..floor(window/tau); "
            "MSE(tau) = sample_entropy's own SampEn computed on y^(tau), for tau = 1..scales"
        ),
        "about": (
            "sample_entropy measures unpredictability at one, single time scale. Costa, "
            "Goldberger & Peng (2002) repeat that same measurement after coarse-graining the "
            "window at several scale factors — replacing every non-overlapping run of tau "
            "consecutive log returns with their own mean — and reuse sample_entropy's own "
            "template-matching machinery directly on each coarse-grained series rather than "
            "reimplementing it. Scale 1 (no coarse-graining) is exactly sample_entropy on the "
            "same window."
        ),
        "reading": (
            "A series with structure spread across multiple timescales keeps a roughly flat or "
            "rising entropy profile across scales; a series that is only complex at the finest "
            "scale (e.g. close to pure noise) has its entropy collapse quickly as tau grows, "
            "since averaging noise into blocks removes most of what made it unpredictable bar "
            "to bar. Comparing the whole profile, not just one scale, is the point of the method."
        ),
        "pitfalls": (
            "The tolerance r*std is fixed at scale 1's own standard deviation and reused, "
            "unchanged, at every coarser scale — the convention Costa et al.'s own papers and "
            "the PhysioNet MSE toolkit use, not a per-scale recomputation some later papers use "
            "instead. Same O(window^2) per-bar, per-scale cost as sample_entropy, now repeated "
            "once per scale."
        ),
        "example": [
            lambda df: zeonta.multiscale_entropy(df["close"], scales=3).tail(3),
        ],
    },
    "kl_divergence": {
        "title": "Kullback-Leibler Divergence",
        "formula": (
            "edges = bins equal-width buckets spanning the long window's own min..max; "
            "P_i = short window's fraction in bucket i; Q_i = long window's fraction in bucket i; "
            "KL = sum(P_i * ln(P_i / Q_i), over buckets with P_i > 0)"
        ),
        "about": (
            "Reuses shannon_entropy's own equal-width-bucket binning convention, applied to two "
            "nested windows ending on the same bar: a short, recent one and a long, older one "
            "that contains it. Because the short window is always the long window's own most "
            "recent trailing subset, its values are automatically bounded by the long window's "
            "own range, so both distributions can share one set of bin edges with no separate "
            "alignment convention to invent."
        ),
        "reading": (
            "KL is 0 when the recent return distribution looks just like the longer history it "
            "sits inside, and grows as the recent window's shape — not just its level — "
            "diverges from it: a recent stretch of unusually one-sided, narrow, or fat-tailed "
            "returns compared to the longer lookback reads as a large KL value."
        ),
        "pitfalls": (
            "`long` must exceed `short`. Because the short window is a literal trailing subset "
            "of the long window's own return array, every bucket the short distribution puts "
            "mass in is guaranteed to have some long-window mass too, so KL is always finite "
            "and well-defined here (unlike a KL divergence between two unrelated samples)."
        ),
        "example": [
            lambda df: zeonta.kl_divergence(df["close"]).tail(3),
        ],
    },
    "realized_skewness": {
        "title": "Realized Skewness",
        "formula": "RVar = sum(r_i^2); RSkew = sqrt(n) * sum(r_i^3) / RVar^1.5, over a window of n log returns",
        "about": (
            "skewness computes the adjusted Fisher-Pearson moment ratio directly on rolling "
            "price levels. Amaya, Christoffersen, Jacobs & Vasquez (2015) instead build a "
            "skewness measure from the window's own log returns, normalized by its own realized "
            "volatility rather than by a bias-adjustment factor — the same construction the "
            "high-frequency realized-variance literature (bipower_variation and "
            "realized_semivariance's own family) already uses, extended to the third moment."
        ),
        "reading": (
            "Negative means the window's return distribution has a fatter left (down-move) "
            "tail than right; positive the opposite — the same sign convention as skewness, on "
            "a differently normalized quantity. The paper finds a strong, robust negative "
            "relationship between a stock's realized skewness and its subsequent week's return "
            "in the cross-section."
        ),
        "pitfalls": (
            "length counts log returns, one more close bar than that is needed. The paper's own "
            "setting builds this from 5-minute intraday returns aggregated into a weekly "
            "statistic; this function applies the identical formula at whatever bar frequency "
            "close is sampled at, generalizing the estimator rather than the paper's specific "
            "data frequency. NaN wherever the window's realized variance is exactly 0."
        ),
        "example": [
            lambda df: zeonta.realized_skewness(df["close"]).tail(3),
        ],
    },
    "realized_kurtosis": {
        "title": "Realized Kurtosis",
        "formula": "RVar = sum(r_i^2); RKurt = n * sum(r_i^4) / RVar^2, over a window of n log returns",
        "about": (
            "realized_skewness's companion statistic from the same paper: the window's "
            "4th-power log returns rescaled by its own squared realized volatility rather than "
            "kurtosis's bias-adjustment factor applied to price levels."
        ),
        "reading": (
            "Always >= 0; larger means fatter tails relative to the window's own realized "
            "volatility. Unlike kurtosis, this is not excess kurtosis — there is no -3 term, so "
            "a normal-like return process reads near 3, not near 0. The paper finds a positive "
            "relationship between a stock's realized kurtosis and its subsequent week's return."
        ),
        "pitfalls": (
            "Same length/warm-up/NaN conventions as realized_skewness — see that indicator's "
            "own notes."
        ),
        "example": [
            lambda df: zeonta.realized_kurtosis(df["close"]).tail(3),
        ],
    },
    "cdar": {
        "title": "Conditional Drawdown at Risk (CDaR)",
        "formula": (
            "k = ceil((1-alpha)*length); CDaR = mean of the k largest drawdown magnitudes "
            "(-drawdown) in the rolling window"
        ),
        "about": (
            "The CVaR/Expected-Shortfall construction applied to a drawdown series instead of a "
            "return series, reusing drawdown rather than recomputing the running peak. "
            "Chekhlov, Uryasev & Zabarankin (2005) originally define this as a "
            "Rockafellar-Uryasev-style optimization, but their own Theorem 1 proves the optimum "
            "coincides exactly with the worst-fraction average implemented here — a closed-form "
            "equivalent, not an independent approximation."
        ),
        "reading": (
            "Reported as a positive percentage, like ulcer_index, not signed like drawdown "
            "itself — 8.0 reads as 'the expected worst-case drawdown magnitude over this window "
            "is about 8%'. alpha=0.95 (the default) means 'the average of the worst 5% of "
            "drawdowns in the window'."
        ),
        "pitfalls": (
            "CDaR contains the maximal drawdown (alpha -> 1, k -> 1) and the average drawdown "
            "(alpha -> 0, k -> length) as its two limiting cases — a useful sanity check when "
            "picking alpha. NaN for warm-up bars and any window containing a non-finite "
            "drawdown."
        ),
        "example": [
            lambda df: zeonta.cdar(df["close"]).tail(3),
        ],
    },
}
