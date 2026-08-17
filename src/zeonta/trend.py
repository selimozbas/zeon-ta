"""Trend systems: SuperTrend, ADX/DMI, Ichimoku, Donchian and Parabolic SAR.

SuperTrend, ADX, Ichimoku and Donchian follow the TA 101 *Trend Systems*
module. Parabolic SAR is outside that curriculum; see its own ``References``
section for its source.

SuperTrend, ADX and Parabolic SAR are the only genuinely sequential indicators
in the library: their bands ratchet in one direction and depend on the
previous bar's state, so they cannot be expressed as a pure window reduction.
All three keep a single readable pass over the data rather than an obscure
vectorised trick.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    Number,
    as_array,
    common_index,
    first_full_window,
    indicator,
    require_aligned_index,
    require_same_length,
    rolling_max,
    rolling_min,
    validate_length,
    validate_multiplier,
    wilder_values,
    wrap_frame,
)
from .volatility import _true_range_values

__all__ = ["adx", "donchian", "ichimoku", "parabolic_sar", "supertrend"]


@indicator(
    category="trend",
    summary="ATR-based trailing line that flips between support and resistance.",
    lesson="supertrend",
    outputs=("SUPERT", "SUPERTd", "SUPERTl", "SUPERTs"),
)
def supertrend(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 10,
    multiplier: Number = 3.0,
) -> pd.DataFrame:
    """SuperTrend.

    Starting from ``hl2 = (High + Low) / 2``:

    * ``Basic Upper = hl2 + multiplier * ATR(length)``
    * ``Basic Lower = hl2 - multiplier * ATR(length)``

    The final upper band may only move **down** while price stays below it, and
    the final lower band may only move **up** while price stays above it. This
    one-way ratchet is what keeps the line from reacting to every small pullback.
    A flip happens when the close crosses to the opposite band.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        ATR period. Shorter reacts faster and flips more often.
    multiplier:
        ATR multiplier. Lower hugs price and flips frequently; higher gives the
        trend more room.

    Returns
    -------
    pandas.DataFrame
        ``SUPERT_{length}_{multiplier}`` — the plotted line;
        ``SUPERTd_...`` — direction, ``1.0`` uptrend / ``-1.0`` downtrend;
        ``SUPERTl_...`` / ``SUPERTs_...`` — the line masked to long-only and
        short-only bars, which is what you plot in two colours.

    Notes
    -----
    SuperTrend is not a leading indicator and carries no opinion about trend
    strength — it flips identically on a powerful move and a feeble one. In a
    range it will flip repeatedly. Pairing it with :func:`adx` is the usual fix.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.supertrend([2] * 30, [1] * 30, [1.5] * 30)
    >>> float(out['SUPERTd_10_3.0'].iloc[-1])
    1.0

    References
    ----------
    https://ta.cognicode.org/learn/supertrend
    """
    length = validate_length(length)
    factor = validate_multiplier(multiplier)

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(high=high_values, low=low_values, close=close_values)

    ranges = wilder_values(_true_range_values(high_values, low_values, close_values), length)
    midpoint = (high_values + low_values) / 2.0
    basic_upper = midpoint + factor * ranges
    basic_lower = midpoint - factor * ranges

    line = np.full(size, np.nan, dtype="float64")
    direction = np.full(size, np.nan, dtype="float64")
    final_upper = np.full(size, np.nan, dtype="float64")
    final_lower = np.full(size, np.nan, dtype="float64")

    start = first_full_window(ranges, 1)
    if start < 0:
        columns = (line, direction, line.copy(), line.copy())
    else:
        final_upper[start] = basic_upper[start]
        final_lower[start] = basic_lower[start]
        direction[start] = 1.0
        line[start] = final_lower[start]

        for i in range(start + 1, size):
            previous_upper = final_upper[i - 1]
            previous_lower = final_lower[i - 1]

            # The upper band ratchets down; it may only widen once price closes above it.
            final_upper[i] = (
                basic_upper[i]
                if (basic_upper[i] < previous_upper or close_values[i - 1] > previous_upper)
                else previous_upper
            )
            # The lower band ratchets up; it may only widen once price closes below it.
            final_lower[i] = (
                basic_lower[i]
                if (basic_lower[i] > previous_lower or close_values[i - 1] < previous_lower)
                else previous_lower
            )

            if direction[i - 1] > 0:
                direction[i] = -1.0 if close_values[i] < final_lower[i] else 1.0
            else:
                direction[i] = 1.0 if close_values[i] > final_upper[i] else -1.0

            line[i] = final_lower[i] if direction[i] > 0 else final_upper[i]

        long_line = np.where(direction > 0, line, np.nan)
        short_line = np.where(direction < 0, line, np.nan)
        columns = (line, direction, long_line, short_line)

    suffix = f"{length}_{factor}"
    order = [f"SUPERT_{suffix}", f"SUPERTd_{suffix}", f"SUPERTl_{suffix}", f"SUPERTs_{suffix}"]
    return wrap_frame(
        dict(zip(order, columns, strict=True)), common_index(high, low, close), order=order
    )


@indicator(
    category="trend",
    summary="Wilder's directional movement system: trend strength (ADX) and direction (DI).",
    lesson="adx-dmi",
    outputs=("ADX", "DMP", "DMN"),
)
def adx(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 14,
) -> pd.DataFrame:
    """Average Directional Index with the +DI / -DI pair.

    ``+DM`` is the up-move when it exceeds the down-move and is positive, else 0;
    ``-DM`` is the mirror. Both are Wilder-smoothed and normalised by ATR::

        +DI = 100 * WilderSmooth(+DM, n) / ATR(n)
        -DI = 100 * WilderSmooth(-DM, n) / ATR(n)
        DX  = 100 * |+DI - -DI| / (+DI + -DI)
        ADX = WilderSmooth(DX, n)

    ADX measures trend **strength only** — it rises in strong downtrends just as
    it does in strong uptrends. Direction comes from which DI line is on top.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Wilder smoothing period.

    Returns
    -------
    pandas.DataFrame
        Columns ``ADX_{length}``, ``DMP_{length}`` (+DI) and ``DMN_{length}`` (-DI).
        Because ADX smooths an already-smoothed series it needs roughly
        ``2 * length`` bars before it produces a value.

    Examples
    --------
    >>> import zeonta
    >>> prices = [float(i) for i in range(1, 60)]
    >>> out = zeonta.adx(prices, [p - 1 for p in prices], prices)
    >>> bool(out['ADX_14'].iloc[-1] > 90)
    True

    References
    ----------
    https://ta.cognicode.org/learn/adx-dmi
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(high=high_values, low=low_values, close=close_values)

    up_move = np.diff(high_values, prepend=np.nan)
    down_move = -np.diff(low_values, prepend=np.nan)

    plus_dm = np.where((up_move > down_move) & (up_move > 0.0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0.0), down_move, 0.0)
    plus_dm[0] = np.nan
    minus_dm[0] = np.nan

    ranges = wilder_values(_true_range_values(high_values, low_values, close_values), length)
    smoothed_plus = wilder_values(plus_dm, length)
    smoothed_minus = wilder_values(minus_dm, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        plus_di = 100.0 * smoothed_plus / ranges
        minus_di = 100.0 * smoothed_minus / ranges
        total = plus_di + minus_di
        dx = 100.0 * np.abs(plus_di - minus_di) / total
    # A flat market gives no directional movement at all; DX is zero, not NaN.
    dx = np.where(np.isfinite(total) & (total == 0.0), 0.0, dx)
    plus_di = np.where(np.isfinite(ranges) & (ranges == 0.0), 0.0, plus_di)
    minus_di = np.where(np.isfinite(ranges) & (ranges == 0.0), 0.0, minus_di)

    adx_values = np.full(size, np.nan, dtype="float64")
    adx_values[1:] = wilder_values(dx[1:], length)

    order = [f"ADX_{length}", f"DMP_{length}", f"DMN_{length}"]
    return wrap_frame(
        dict(zip(order, (adx_values, plus_di, minus_di), strict=True)),
        common_index(high, low, close),
        order=order,
    )


@indicator(
    category="trend",
    summary="Five-line Japanese system giving trend, momentum and support in one view.",
    lesson="ichimoku",
    outputs=("ITS", "IKS", "ISA", "ISB", "ICS"),
    returns_frame=True,
)
def ichimoku(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    tenkan: int = 9,
    kijun: int = 26,
    senkou: int = 52,
    displacement: int = 26,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ichimoku Kinko Hyo.

    ``Tenkan-sen = (HighestHigh(9) + LowestLow(9)) / 2``;
    ``Kijun-sen = (HighestHigh(26) + LowestLow(26)) / 2``;
    ``Senkou Span A = (Tenkan + Kijun) / 2`` plotted 26 bars **ahead**;
    ``Senkou Span B = (HighestHigh(52) + LowestLow(52)) / 2`` plotted 26 bars ahead;
    ``Chikou Span = Close`` plotted 26 bars **behind**.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    tenkan, kijun, senkou:
        Conversion, base and leading-span-B look-backs.
    displacement:
        How far the cloud is projected forward and Chikou is pushed back.

    Returns
    -------
    (pandas.DataFrame, pandas.DataFrame)
        The first frame is aligned to the input bars and holds
        ``ITS_{tenkan}``, ``IKS_{kijun}``, ``ISA_{tenkan}_{kijun}``,
        ``ISB_{senkou}`` and ``ICS_{displacement}``.

        The second frame is the part of the cloud that lands **beyond the last
        bar** — ``displacement`` rows of ``ISA``/``ISB`` that have no price to sit
        next to yet. It is returned separately rather than silently discarded,
        because that forward cloud is precisely what traders read for future
        support and resistance. When the input carries a ``DatetimeIndex`` with
        a regular frequency, this frame's index continues as real future dates
        (so it concatenates directly onto a date-indexed chart); otherwise it
        falls back to a plain integer continuation of the input's length.

    Examples
    --------
    >>> import zeonta
    >>> prices = [float(i) for i in range(1, 120)]
    >>> visible, forward = zeonta.ichimoku(prices, [p - 1 for p in prices], prices)
    >>> len(forward)
    26

    References
    ----------
    https://ta.cognicode.org/learn/ichimoku
    """
    tenkan = validate_length(tenkan, "tenkan")
    kijun = validate_length(kijun, "kijun")
    senkou = validate_length(senkou, "senkou")
    displacement = validate_length(displacement, "displacement")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(high=high_values, low=low_values, close=close_values)

    def midpoint(window: int) -> np.ndarray:
        combined = rolling_max(high_values, window) + rolling_min(low_values, window)
        return np.asarray(combined / 2.0, dtype="float64")

    conversion = midpoint(tenkan)
    base = midpoint(kijun)
    span_a = (conversion + base) / 2.0
    span_b = midpoint(senkou)

    def shift_forward(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Split a forward-shifted series into its on-chart and beyond-chart parts."""
        visible = np.full(size, np.nan, dtype="float64")
        keep = max(size - displacement, 0)
        visible[displacement:] = values[:keep]
        return visible, values[keep:]

    span_a_visible, span_a_forward = shift_forward(span_a)
    span_b_visible, span_b_forward = shift_forward(span_b)

    lagging = np.full(size, np.nan, dtype="float64")
    if size > displacement:
        lagging[:-displacement] = close_values[displacement:]

    index = common_index(high, low, close)
    names = (
        f"ITS_{tenkan}",
        f"IKS_{kijun}",
        f"ISA_{tenkan}_{kijun}",
        f"ISB_{senkou}",
        f"ICS_{displacement}",
    )
    visible_frame = wrap_frame(
        dict(zip(names, (conversion, base, span_a_visible, span_b_visible, lagging), strict=True)),
        index,
        order=list(names),
    )

    forward_frame = pd.DataFrame(
        {names[2]: span_a_forward, names[3]: span_b_forward},
        index=_forward_index(index, size, span_a_forward.shape[0]),
    )
    return visible_frame, forward_frame


def _forward_index(index: pd.Index | None, size: int, count: int) -> pd.Index:
    """Continue *index* for ``count`` more steps, for the part of the cloud that
    projects beyond the last input bar.

    ``size`` is the number of input bars, independent of whether an index was
    given at all — a plain RangeIndex fallback must still start at ``size``,
    not at 0.

    A ``DatetimeIndex`` with a regular frequency continues as real future
    dates, so the forward cloud can be concatenated onto a date-indexed chart
    directly. Anything else (no index, or a frequency that cannot be inferred
    from as few as two bars) falls back to a plain integer continuation.
    """
    if isinstance(index, pd.DatetimeIndex) and size >= 2:
        freq = index.freq or pd.infer_freq(index)
        if freq is not None:
            start = index[-1] + pd.tseries.frequencies.to_offset(freq)
            return pd.date_range(start=start, periods=count, freq=freq)
    return pd.RangeIndex(size, size + count)


@indicator(
    category="trend",
    summary="Highest high and lowest low over n bars — the classic breakout channel.",
    lesson="donchian-channels",
    outputs=("DCL", "DCM", "DCU"),
)
def donchian(high: ArrayLike, low: ArrayLike, length: int = 20) -> pd.DataFrame:
    """Donchian Channels.

    ``Upper = HighestHigh(n)``; ``Lower = LowestLow(n)``;
    ``Middle = (Upper + Lower) / 2``.

    Note the channel *includes* the current bar, so price touching the upper
    channel is the same statement as "this bar made the highest high of the last
    n bars". Compare against the previous bar's channel if you want a breakout
    that excludes the breaking bar itself.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    length:
        Look-back window.

    Returns
    -------
    pandas.DataFrame
        Columns ``DCL_{length}``, ``DCM_{length}``, ``DCU_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.donchian([3, 4, 5], [1, 2, 3], length=2).iloc[-1].tolist()
    [2.0, 3.5, 5.0]

    References
    ----------
    https://ta.cognicode.org/learn/donchian-channels
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    require_same_length(high=high_values, low=low_values)

    upper = rolling_max(high_values, length)
    lower = rolling_min(low_values, length)
    middle = (upper + lower) / 2.0

    order = [f"DCL_{length}", f"DCM_{length}", f"DCU_{length}"]
    return wrap_frame(
        dict(zip(order, (lower, middle, upper), strict=True)), common_index(high, low), order=order
    )


@indicator(
    category="trend",
    summary="Trailing stop-and-reverse dots that accelerate the longer a trend runs.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-overlays/parabolic-sar"
    ),
    outputs=("PSAR", "PSARd", "PSARl", "PSARs"),
)
def parabolic_sar(
    high: ArrayLike,
    low: ArrayLike,
    start: Number = 0.02,
    increment: Number = 0.02,
    max_af: Number = 0.2,
) -> pd.DataFrame:
    """Parabolic SAR (Stop And Reverse).

    In an uptrend: ``SAR = PriorSAR + AF * (EP - PriorSAR)``. In a downtrend
    the sign flips: ``SAR = PriorSAR - AF * (PriorSAR - EP)``. ``EP`` (Extreme
    Point) is the highest high seen since the last reversal in an uptrend, or
    the lowest low in a downtrend. ``AF`` (Acceleration Factor) starts at
    ``start``, grows by ``increment`` every time a new EP is recorded, and is
    capped at ``max_af`` — the longer a trend runs unbroken, the faster SAR
    accelerates toward price. SAR is additionally clamped so it never sits
    above the prior two bars' lows in an uptrend, nor below the prior two
    bars' highs in a downtrend; a reversal fires the moment price crosses the
    (clamped) SAR, at which point SAR jumps to the old EP, AF resets to
    ``start``, and a fresh EP starts tracking the new direction.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    start:
        Initial acceleration factor.
    increment:
        How much the acceleration factor grows each time a new extreme point
        is recorded.
    max_af:
        Acceleration factor ceiling.

    Returns
    -------
    pandas.DataFrame
        ``PSAR_{start}_{increment}_{max_af}`` — the dot; ``PSARd_...`` —
        direction, ``1.0`` uptrend / ``-1.0`` downtrend; ``PSARl_...`` /
        ``PSARs_...`` — the dot masked to long-only and short-only bars,
        ready to plot in two colours (the same convention as
        :func:`supertrend`).

    Notes
    -----
    There is no "prior SAR" for the very first bar, so bars 0 and 1 are
    ``NaN``; the initial trend direction for bar 1 is bootstrapped by
    comparing bar 1's midpoint (``(high + low) / 2``) against bar 0's, since
    this function takes no ``close`` to compare instead.

    Like :func:`supertrend`, this is a trailing stop with no opinion about
    trend strength, and whipsaws in a range as the acceleration factor keeps
    resetting to ``start``. Unlike SuperTrend it actively accelerates the
    longer a trend runs, which tightens it aggressively into extended moves —
    useful when riding a trend, a liability if it means giving back less room
    than the market's ordinary noise.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.parabolic_sar([2] * 30, [1] * 30)
    >>> float(out['PSARd_0.02_0.02_0.2'].iloc[-1])
    1.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/parabolic-sar
    """
    af0 = validate_multiplier(start, "start")
    step = validate_multiplier(increment, "increment")
    af_max = validate_multiplier(max_af, "max_af")

    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    sar = np.full(size, np.nan, dtype="float64")
    direction = np.full(size, np.nan, dtype="float64")

    if size >= 2:
        trend_up = bool(high_values[1] + low_values[1] >= high_values[0] + low_values[0])
        extreme = high_values[1] if trend_up else low_values[1]
        af = af0
        sar[1] = low_values[0] if trend_up else high_values[0]
        direction[1] = 1.0 if trend_up else -1.0

        for i in range(2, size):
            prior_sar = sar[i - 1]
            if trend_up:
                candidate = prior_sar + af * (extreme - prior_sar)
                candidate = min(candidate, low_values[i - 1], low_values[i - 2])
                if low_values[i] < candidate:
                    trend_up = False
                    candidate = extreme
                    extreme = low_values[i]
                    af = af0
                elif high_values[i] > extreme:
                    extreme = high_values[i]
                    af = min(af + step, af_max)
            else:
                candidate = prior_sar - af * (prior_sar - extreme)
                candidate = max(candidate, high_values[i - 1], high_values[i - 2])
                if high_values[i] > candidate:
                    trend_up = True
                    candidate = extreme
                    extreme = high_values[i]
                    af = af0
                elif low_values[i] < extreme:
                    extreme = low_values[i]
                    af = min(af + step, af_max)

            sar[i] = candidate
            direction[i] = 1.0 if trend_up else -1.0

    long_line = np.where(direction > 0, sar, np.nan)
    short_line = np.where(direction < 0, sar, np.nan)

    suffix = f"{af0}_{step}_{af_max}"
    order = [f"PSAR_{suffix}", f"PSARd_{suffix}", f"PSARl_{suffix}", f"PSARs_{suffix}"]
    return wrap_frame(
        dict(zip(order, (sar, direction, long_line, short_line), strict=True)),
        common_index(high, low),
        order=order,
    )
