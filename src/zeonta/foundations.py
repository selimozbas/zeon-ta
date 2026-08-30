"""Chart-reading fundamentals: candle anatomy, pivots, trend channels and volume.

These are the building blocks the rest of the library — and most discretionary
chart reading — sits on.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from ._core import (
    ArrayLike,
    Number,
    as_array,
    common_index,
    indicator,
    require_aligned_index,
    require_non_negative,
    require_same_length,
    rolling_linreg,
    rolling_mean,
    validate_length,
    validate_multiplier,
    wrap_frame,
)

__all__ = [
    "candles",
    "heikin_ashi",
    "relative_volume",
    "sr_levels",
    "support_resistance",
    "trend_channel",
    "williams_fractals",
]


def _pivot_flags(values: np.ndarray, left: int, right: int, high: bool) -> np.ndarray:
    """Boolean mask of strict local extrema with *left*/*right* bars on each side.

    Vectorised via a sliding window rather than a per-bar Python loop — at a
    million bars this is roughly 200x faster and produces bit-identical
    results (comparisons against a ``NaN`` neighbour or a ``NaN`` candidate
    are ``False`` either way, so a missing value excludes a bar from being a
    pivot exactly as the original per-bar ``continue`` did).
    """
    size = values.shape[0]
    flags = np.zeros(size, dtype=bool)
    window = left + right + 1
    if size < window:
        return flags
    windows = sliding_window_view(values, window)
    center = windows[:, left : left + 1]
    left_part = windows[:, :left]
    right_part = windows[:, left + 1 :]
    if high:
        confirmed = np.all(center > left_part, axis=1) & np.all(center > right_part, axis=1)
    else:
        confirmed = np.all(center < left_part, axis=1) & np.all(center < right_part, axis=1)
    flags[left : size - right] = confirmed
    return flags


@indicator(
    category="foundations",
    summary="Candle body/wick geometry plus doji, engulfing and hammer detection.",
    lesson="candlesticks",
    outputs=(
        "CDLBODY",
        "CDLUPPER",
        "CDLLOWER",
        "CDLRANGE",
        "CDLDIR",
        "CDLDOJI",
        "CDLENG",
        "CDLHAM",
    ),
)
def candles(
    open: ArrayLike,
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    doji_threshold: Number = 0.1,
    hammer_ratio: Number = 2.0,
) -> pd.DataFrame:
    """Candle anatomy and three classic single/double-bar patterns.

    ``Body = |Close - Open|``; a candle is bullish when ``Close > Open``.
    ``Upper wick = High - max(Open, Close)``; ``Lower wick = min(Open, Close) - Low``.

    Parameters
    ----------
    open, high, low, close:
        Price series of equal length.
    doji_threshold:
        A candle is a doji when its body is at most this fraction of its full range.
    hammer_ratio:
        Minimum wick-to-body ratio for a hammer or shooting star.

    Returns
    -------
    pandas.DataFrame
        ``CDLBODY``, ``CDLUPPER``, ``CDLLOWER``, ``CDLRANGE`` — raw geometry;
        ``CDLDIR`` — ``1.0`` bullish, ``-1.0`` bearish, ``0.0`` flat;
        ``CDLDOJI`` — ``1.0`` when the body is negligible;
        ``CDLENG`` — ``1.0`` bullish engulfing, ``-1.0`` bearish engulfing;
        ``CDLHAM`` — ``1.0`` hammer, ``-1.0`` shooting star.

    Notes
    -----
    A pattern is a *description of one or two bars*, not a signal on its own. A
    hammer in the middle of a range means nothing; the same hammer at a tested
    support level is what traders act on.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.candles([10, 9], [11, 11], [9, 8], [10.05, 10.5])
    >>> float(out['CDLDOJI'].iloc[0])
    1.0
    """
    threshold = validate_multiplier(doji_threshold, "doji_threshold")
    ratio = validate_multiplier(hammer_ratio, "hammer_ratio")

    require_aligned_index(open=open, high=high, low=low, close=close)
    open_values = as_array(open, "open")
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(open=open_values, high=high_values, low=low_values, close=close_values)

    body = np.abs(close_values - open_values)
    total_range = high_values - low_values
    upper_wick = high_values - np.maximum(open_values, close_values)
    lower_wick = np.minimum(open_values, close_values) - low_values
    direction = np.sign(close_values - open_values)

    with np.errstate(divide="ignore", invalid="ignore"):
        body_fraction = np.where(total_range > 0.0, body / total_range, 0.0)
    doji = (body_fraction <= threshold).astype("float64")

    previous_open = np.concatenate(([np.nan], open_values[:-1]))
    previous_close = np.concatenate(([np.nan], close_values[:-1]))
    bullish_engulf = (
        (previous_close < previous_open)
        & (close_values > open_values)
        & (close_values >= previous_open)
        & (open_values <= previous_close)
    )
    bearish_engulf = (
        (previous_close > previous_open)
        & (close_values < open_values)
        & (close_values <= previous_open)
        & (open_values >= previous_close)
    )
    engulfing = np.where(bullish_engulf, 1.0, np.where(bearish_engulf, -1.0, 0.0))
    engulfing[0] = np.nan

    significant = body > 0.0
    hammer = (significant & (lower_wick >= ratio * body) & (upper_wick <= body)).astype("float64")
    star = significant & (upper_wick >= ratio * body) & (lower_wick <= body)
    hammer[star] = -1.0

    order = [
        "CDLBODY",
        "CDLUPPER",
        "CDLLOWER",
        "CDLRANGE",
        "CDLDIR",
        "CDLDOJI",
        "CDLENG",
        "CDLHAM",
    ]
    columns = (body, upper_wick, lower_wick, total_range, direction, doji, engulfing, hammer)
    return wrap_frame(
        dict(zip(order, columns, strict=True)), common_index(open, high, low, close), order=order
    )


@indicator(
    category="foundations",
    summary="Confirmed swing pivots and the most recent support/resistance they mark.",
    lesson="support-resistance",
    outputs=("PIVOTHIGH", "PIVOTLOW", "RES", "SUP"),
)
def support_resistance(
    high: ArrayLike,
    low: ArrayLike,
    left: int = 10,
    right: int = 10,
) -> pd.DataFrame:
    """Swing pivots and the levels they establish.

    A pivot high at bar ``i`` requires ``High[i]`` to exceed every high in the
    ``left`` bars before and the ``right`` bars after it; a pivot low is the mirror.
    Prices where several pivots cluster are what traders call support or resistance.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    left, right:
        Bars required on each side of a pivot.

    Returns
    -------
    pandas.DataFrame
        ``PIVOTHIGH_{left}_{right}`` / ``PIVOTLOW_{left}_{right}`` hold the pivot
        price on pivot bars and ``NaN`` elsewhere. ``RES_...`` / ``SUP_...`` carry
        the most recent **confirmed** pivot forward, so they are safe to use in a
        backtest.

    Warning
    -------
    A pivot cannot be known until ``right`` further bars have printed. The
    ``PIVOTHIGH``/``PIVOTLOW`` columns place it on the bar it *occurred*, which is
    look-ahead information. The ``RES``/``SUP`` columns are already delayed by
    ``right`` bars — use those for anything that trades.

    Examples
    --------
    >>> import zeonta
    >>> highs = [1, 2, 5, 2, 1, 2, 1]
    >>> out = zeonta.support_resistance(highs, [h - 1 for h in highs], left=2, right=2)
    >>> float(out['PIVOTHIGH_2_2'].iloc[2])
    5.0
    """
    left = validate_length(left, "left")
    right = validate_length(right, "right")

    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    high_flags = _pivot_flags(high_values, left, right, high=True)
    low_flags = _pivot_flags(low_values, left, right, high=False)

    pivot_high = np.where(high_flags, high_values, np.nan)
    pivot_low = np.where(low_flags, low_values, np.nan)

    # A pivot at bar i is only knowable `right` bars later; shift it forward
    # by `right` bars, then carry the last known value forward (pandas
    # ffill) instead of a per-bar Python loop.
    resistance = np.full(size, np.nan, dtype="float64")
    support = np.full(size, np.nan, dtype="float64")
    if right < size:
        resistance[right:] = pivot_high[: size - right]
        support[right:] = pivot_low[: size - right]
    resistance = pd.Series(resistance).ffill().to_numpy()
    support = pd.Series(support).ffill().to_numpy()

    order = [
        f"PIVOTHIGH_{left}_{right}",
        f"PIVOTLOW_{left}_{right}",
        f"RES_{left}_{right}",
        f"SUP_{left}_{right}",
    ]
    return wrap_frame(
        dict(zip(order, (pivot_high, pivot_low, resistance, support), strict=True)),
        common_index(high, low),
        order=order,
    )


def sr_levels(
    high: ArrayLike,
    low: ArrayLike,
    left: int = 10,
    right: int = 10,
    max_levels: int = 5,
    tolerance: Number = 0.005,
) -> pd.DataFrame:
    """Cluster swing pivots into a ranked list of support/resistance levels.

    Pivots within ``tolerance`` (a fraction of price) of each other are merged;
    the resulting levels are ranked by how many pivots back them, because a level
    tested four times matters more than one touched once.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    left, right:
        Bars required on each side of a pivot.
    max_levels:
        Maximum number of levels to return.
    tolerance:
        Relative distance within which two pivots count as the same level.

    Returns
    -------
    pandas.DataFrame
        One row per level with columns ``level`` (the clustered price),
        ``touches`` (how many pivots formed it) and ``kind`` (``"resistance"``,
        ``"support"`` or ``"both"``), strongest first.

    Examples
    --------
    >>> import zeonta
    >>> highs = [1, 2, 5, 2, 1, 2, 5.01, 2, 1]
    >>> levels = zeonta.sr_levels(highs, [h - 1 for h in highs], left=2, right=2, tolerance=0.01)
    >>> int(levels.iloc[0]['touches'])
    2
    """
    left = validate_length(left, "left")
    right = validate_length(right, "right")
    max_levels = validate_length(max_levels, "max_levels")
    tolerance = validate_multiplier(tolerance, "tolerance")

    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    require_same_length(high=high_values, low=low_values)

    points: list[tuple[float, str]] = []
    high_pivots = high_values[_pivot_flags(high_values, left, right, high=True)]
    low_pivots = low_values[_pivot_flags(low_values, left, right, high=False)]
    points += [(float(value), "resistance") for value in high_pivots]
    points += [(float(value), "support") for value in low_pivots]
    points.sort(key=lambda item: item[0])

    clusters: list[list[tuple[float, str]]] = []
    for price, kind in points:
        if clusters and abs(price - clusters[-1][-1][0]) <= tolerance * abs(clusters[-1][-1][0]):
            clusters[-1].append((price, kind))
        else:
            clusters.append([(price, kind)])

    rows: list[tuple[float, int, str]] = []
    for cluster in clusters:
        kinds = {kind for _, kind in cluster}
        rows.append(
            (
                float(np.mean([price for price, _ in cluster])),
                len(cluster),
                "both" if len(kinds) > 1 else next(iter(kinds)),
            )
        )
    # Strongest level first: most touches wins, ties broken by price for stable output.
    rows.sort(key=lambda row: (-row[1], row[0]))
    return pd.DataFrame(rows[:max_levels], columns=["level", "touches", "kind"])


@indicator(
    category="foundations",
    summary="Linear-regression trend line with standard-deviation channel bands.",
    lesson="trend-basics",
    outputs=("LRCM", "LRCU", "LRCL", "LRCSLOPE"),
)
def trend_channel(
    close: ArrayLike,
    length: int = 100,
    multiplier: Number = 2.0,
) -> pd.DataFrame:
    """Linear-regression trend channel.

    Fits ``y = a + b*x`` over the last ``length`` closes (``x = 0..n-1``) and
    places bands at ``+/- multiplier`` standard deviations **of the residuals**
    around the fitted line. The slope sign is the objective answer to "is this an
    uptrend?".

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Number of bars in the regression window.
    multiplier:
        Standard-deviation multiplier for the channel width.

    Returns
    -------
    pandas.DataFrame
        ``LRCM_{length}`` — the regression value at the current bar;
        ``LRCU_...`` / ``LRCL_...`` — the channel bands;
        ``LRCSLOPE_...`` — slope per bar, positive in an uptrend.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.trend_channel([float(i) for i in range(50)], length=10)
    >>> round(float(out['LRCSLOPE_10'].iloc[-1]), 6)
    1.0
    """
    length = validate_length(length, minimum=2)
    factor = validate_multiplier(multiplier)

    values = as_array(close, "close")
    fit = rolling_linreg(values, length)
    slope, endpoint = fit.slope, fit.endpoint
    # Scatter is measured about the fitted line, not about the window mean: in a
    # steep trend the deviation about the mean is mostly the trend itself, which
    # would inflate the channel exactly when price is behaving most predictably.
    deviation = fit.residual_std

    order = [f"LRCM_{length}", f"LRCU_{length}", f"LRCL_{length}", f"LRCSLOPE_{length}"]
    columns = (endpoint, endpoint + factor * deviation, endpoint - factor * deviation, slope)
    return wrap_frame(dict(zip(order, columns, strict=True)), common_index(close), order=order)


@indicator(
    category="foundations",
    summary="Volume moving average and relative volume (today versus normal).",
    lesson="volume-basics",
    outputs=("VOLMA", "RVOL"),
)
def relative_volume(volume: ArrayLike, length: int = 20) -> pd.DataFrame:
    """Volume moving average and relative volume.

    ``VolumeMA(n) = (1/n) * sum(Volume)``; ``RVOL = Volume / VolumeMA(n)``.

    Raw volume is close to meaningless across symbols and eras — a million shares
    is enormous for one ticker and a rounding error for another. Relative volume
    normalises it: ``2.0`` means twice the recent norm, whatever the symbol.

    Parameters
    ----------
    volume:
        Traded volume per bar.
    length:
        Look-back window for the average.

    Returns
    -------
    pandas.DataFrame
        Columns ``VOLMA_{length}`` and ``RVOL_{length}``.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value, which has no meaning for a
        traded quantity.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.relative_volume([100] * 19 + [200], length=20)
    >>> round(float(out['RVOL_20'].iloc[-1]), 4)
    1.9048
    """
    length = validate_length(length)
    values = as_array(volume, "volume")
    require_non_negative(volume=values)
    average = rolling_mean(values, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(average > 0.0, values / average, np.nan)

    order = [f"VOLMA_{length}", f"RVOL_{length}"]
    return wrap_frame(
        dict(zip(order, (average, ratio), strict=True)), common_index(volume), order=order
    )


@indicator(
    category="foundations",
    summary="Recursively smoothed candles that filter noise from the price bars themselves.",
    reference="https://www.babypips.com/learn/forex/how-to-calculate-heikin-ashi",
    outputs=("HAopen", "HAhigh", "HAlow", "HAclose"),
)
def heikin_ashi(open: ArrayLike, high: ArrayLike, low: ArrayLike, close: ArrayLike) -> pd.DataFrame:
    """Heikin-Ashi Candles ("average bar" in Japanese).

    Builds a second, smoothed OHLC series from the real one::

        HAclose[i] = (Open[i] + High[i] + Low[i] + Close[i]) / 4
        HAopen[0]  = (Open[0] + Close[0]) / 2
        HAopen[i]  = (HAopen[i-1] + HAclose[i-1]) / 2
        HAhigh[i]  = max(High[i], HAopen[i], HAclose[i])
        HAlow[i]   = min(Low[i], HAopen[i], HAclose[i])

    Because ``HAopen`` folds in the *previous* bar's own smoothed values,
    every bar carries a trace of the whole history before it — the same
    kind of recursive smoothing :func:`~zeonta.ema` uses, applied to a
    full candle instead of a single price line. A run of same-direction
    Heikin-Ashi candles with little or no opposite-colored wick is the
    classic read for "this trend has not shown genuine reversal pressure
    yet", filtered from noise a plain candle would still show bar to bar.

    Parameters
    ----------
    open, high, low, close:
        Series of equal length.

    Returns
    -------
    pandas.DataFrame
        Columns ``HAopen``, ``HAhigh``, ``HAlow``, ``HAclose``. Never
        ``NaN`` for finite input — ``HAopen`` is always seeded from bar 0
        itself, unlike a fixed-window indicator's warm-up.

    Notes
    -----
    ``HAopen``'s recursion means a single missing bar changes every later
    Heikin-Ashi value from that point on (there is no fixed window for
    the effect to age out of) — clean the input first if your feed has
    gaps, rather than relying on this to recover the way a windowed
    indicator would.

    Examples
    --------
    >>> import zeonta
    >>> open_ = [10.0, 11.0, 10.5, 12.0]
    >>> high = [12.0, 13.0, 11.5, 14.0]
    >>> low = [9.0, 10.0, 9.5, 11.0]
    >>> close = [11.0, 10.5, 11.2, 13.5]
    >>> out = zeonta.heikin_ashi(open_, high, low, close)
    >>> [round(v, 5) for v in out["HAclose"]]
    [10.5, 11.125, 10.675, 12.625]

    References
    ----------
    https://www.babypips.com/learn/forex/how-to-calculate-heikin-ashi
    """
    require_aligned_index(open=open, high=high, low=low, close=close)
    open_values = as_array(open, "open")
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(
        open=open_values, high=high_values, low=low_values, close=close_values
    )

    ha_close = (open_values + high_values + low_values + close_values) / 4.0
    ha_open = np.full(size, np.nan, dtype="float64")
    ha_open[0] = (open_values[0] + close_values[0]) / 2.0
    for i in range(1, size):
        previous = ha_open[i - 1] + ha_close[i - 1]
        ha_open[i] = previous / 2.0 if np.isfinite(previous) else ha_open[i - 1]

    ha_high = np.maximum(high_values, np.maximum(ha_open, ha_close))
    ha_low = np.minimum(low_values, np.minimum(ha_open, ha_close))

    order = ["HAopen", "HAhigh", "HAlow", "HAclose"]
    return wrap_frame(
        dict(zip(order, (ha_open, ha_high, ha_low, ha_close), strict=True)),
        common_index(open, high, low, close),
        order=order,
    )


@indicator(
    category="foundations",
    summary="Bill Williams' 5-bar pivot: a high or low with two lower/higher bars on each side.",
    outputs=("FRACTALB", "FRACTALU"),
    reference="https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals",
)
def williams_fractals(high: ArrayLike, low: ArrayLike) -> pd.DataFrame:
    """Williams Fractals (Bill Williams).

    The same strict local-extremum test :func:`support_resistance` builds
    on, at that indicator's own ``left=right=2`` — the classic 5-bar
    window: a bearish fractal is a high exceeding the two highs on each
    side of it, a bullish fractal a low below the two lows on each side.

    Parameters
    ----------
    high, low:
        Price series of equal length.

    Returns
    -------
    pandas.DataFrame
        ``FRACTALB`` (bearish, the confirmed high) and ``FRACTALU``
        (bullish, the confirmed low) — each ``NaN`` except at a
        confirmed fractal bar, where it holds that bar's own high/low.

    Notes
    -----
    Unlike :func:`support_resistance`'s ``RES``/``SUP`` columns, this
    does **not** shift the flag forward or hold it until the next pivot —
    a fractal is only knowable 2 bars after it happened (the two
    right-side bars must exist first), so a fractal shown at bar ``i``
    was not actually confirmed until bar ``i + 2``. Look ahead of the
    marked bar, not at it, if trading the confirmation.

    Examples
    --------
    >>> import zeonta
    >>> high = [10.0, 11.0, 15.0, 11.0, 10.0]
    >>> low = [8.0, 7.0, 6.0, 7.0, 8.0]
    >>> out = zeonta.williams_fractals(high, low)
    >>> float(out['FRACTALB'].iloc[2])
    15.0
    >>> float(out['FRACTALU'].iloc[2])
    6.0

    References
    ----------
    https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals
    """
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    require_same_length(high=high_values, low=low_values)

    high_flags = _pivot_flags(high_values, 2, 2, high=True)
    low_flags = _pivot_flags(low_values, 2, 2, high=False)
    bearish = np.where(high_flags, high_values, np.nan)
    bullish = np.where(low_flags, low_values, np.nan)

    order = ["FRACTALB", "FRACTALU"]
    return wrap_frame(
        dict(zip(order, (bearish, bullish), strict=True)),
        common_index(high, low),
        order=order,
    )
