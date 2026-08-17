"""Chart-reading fundamentals: candle anatomy, pivots, trend channels and volume.

Formulas follow the TA 101 *Foundations* module. These are the building blocks
the rest of the library — and most discretionary chart reading — sits on.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    Number,
    as_array,
    common_index,
    indicator,
    require_same_length,
    rolling_linreg,
    rolling_mean,
    validate_length,
    validate_multiplier,
    wrap_frame,
)

__all__ = ["candles", "relative_volume", "sr_levels", "support_resistance", "trend_channel"]


def _pivot_flags(values: np.ndarray, left: int, right: int, high: bool) -> np.ndarray:
    """Boolean mask of strict local extrema with *left*/*right* bars on each side."""
    size = values.shape[0]
    flags = np.zeros(size, dtype=bool)
    if size < left + right + 1:
        return flags
    for i in range(left, size - right):
        pivot = values[i]
        if not np.isfinite(pivot):
            continue
        window_left = values[i - left : i]
        window_right = values[i + 1 : i + 1 + right]
        if high:
            flags[i] = bool(np.all(pivot > window_left) and np.all(pivot > window_right))
        else:
            flags[i] = bool(np.all(pivot < window_left) and np.all(pivot < window_right))
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

    References
    ----------
    https://ta.cognicode.org/learn/candlesticks
    """
    threshold = validate_multiplier(doji_threshold, "doji_threshold")
    ratio = validate_multiplier(hammer_ratio, "hammer_ratio")

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

    References
    ----------
    https://ta.cognicode.org/learn/support-resistance
    """
    left = validate_length(left, "left")
    right = validate_length(right, "right")

    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    high_flags = _pivot_flags(high_values, left, right, high=True)
    low_flags = _pivot_flags(low_values, left, right, high=False)

    pivot_high = np.where(high_flags, high_values, np.nan)
    pivot_low = np.where(low_flags, low_values, np.nan)

    resistance = np.full(size, np.nan, dtype="float64")
    support = np.full(size, np.nan, dtype="float64")
    last_high = np.nan
    last_low = np.nan
    for i in range(size):
        # Shift by `right` bars: that is when the pivot actually became knowable.
        confirmed = i - right
        if confirmed >= 0:
            if high_flags[confirmed]:
                last_high = high_values[confirmed]
            if low_flags[confirmed]:
                last_low = low_values[confirmed]
        resistance[i] = last_high
        support[i] = last_low

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

    References
    ----------
    https://ta.cognicode.org/learn/trend-basics
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

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.relative_volume([100] * 19 + [200], length=20)
    >>> round(float(out['RVOL_20'].iloc[-1]), 4)
    1.9048

    References
    ----------
    https://ta.cognicode.org/learn/volume-basics
    """
    length = validate_length(length)
    values = as_array(volume, "volume")
    average = rolling_mean(values, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(average > 0.0, values / average, np.nan)

    order = [f"VOLMA_{length}", f"RVOL_{length}"]
    return wrap_frame(
        dict(zip(order, (average, ratio), strict=True)), common_index(volume), order=order
    )
