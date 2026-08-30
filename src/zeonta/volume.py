"""Volume-based indicators.

On-Balance Volume, Accumulation/Distribution Line, Chaikin Money Flow, Money
Flow Index, and the Chaikin Oscillator.

Each function's own ``References`` section cites the external source its
formula was verified against. These sit apart from :func:`zeonta.relative_volume`
(which normalises raw volume against its own recent average) and
:func:`zeonta.vwap` (which weights *price* by volume) — this module instead
combines volume with price *direction* to build a running measure of buying
versus selling pressure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    as_array,
    common_index,
    ema_values,
    indicator,
    require_aligned_index,
    require_non_negative,
    require_same_length,
    rolling_mean,
    rolling_sum,
    validate_length,
    wrap_frame,
    wrap_series,
)
from .moving_averages import vwma

__all__ = [
    "adl",
    "bop",
    "chaikin_oscillator",
    "cmf",
    "ease_of_movement",
    "force_index",
    "klinger_volume_oscillator",
    "mfi",
    "nvi",
    "obv",
    "pvi",
    "pvt",
    "vwmacd",
    "williams_ad",
]


def _money_flow_multiplier(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """Money Flow Multiplier: ``((Close-Low)-(High-Close))/(High-Low)``.

    ``+1`` at the high, ``-1`` at the low; a zero-range bar carries no
    information and is treated as ``0``.
    """
    span = high - low
    with np.errstate(divide="ignore", invalid="ignore"):
        multiplier = ((close - low) - (high - close)) / span
    return np.where(span == 0.0, 0.0, multiplier)


def _adl_values(
    high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray
) -> np.ndarray:
    """Cumulative Money Flow Volume — the shared core of :func:`adl` and :func:`chaikin_oscillator`.

    A bar with an unknown high, low, close or volume contributes nothing to
    the running total rather than corrupting every bar after it via ``NaN``
    propagating through ``cumsum``, the same convention :func:`obv` uses.
    """
    money_flow_volume = _money_flow_multiplier(high, low, close) * volume
    money_flow_volume = np.where(np.isfinite(money_flow_volume), money_flow_volume, 0.0)
    return np.cumsum(money_flow_volume)


@indicator(
    category="volume",
    summary="Cumulative volume, added on up closes and subtracted on down closes.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv"
    ),
    outputs=("OBV",),
)
def obv(close: ArrayLike, volume: ArrayLike) -> pd.Series:
    """On-Balance Volume.

    ``OBV[0] = 0``; for every following bar, ``Volume[i]`` is added when
    ``Close[i] > Close[i-1]``, subtracted when ``Close[i] < Close[i-1]``, and
    ignored on a flat close. Unlike :func:`relative_volume`, which only looks
    at how large today's volume is, OBV cares which direction it traded in —
    it is a running tally of buying pressure minus selling pressure.

    Parameters
    ----------
    close, volume:
        Series of equal length.

    Returns
    -------
    pandas.Series
        Named ``OBV``. Never ``NaN`` — this is a running total, not a
        windowed statistic, so there is no warm-up period. The absolute level
        is arbitrary (it depends on where the series happens to start);
        only its *slope* and its divergence from price are meaningful.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value, which has no meaning for a
        traded quantity.

    Notes
    -----
    A bar with an unknown close or volume (``NaN``) contributes nothing to the
    running total rather than corrupting every bar after it — a single bad
    tick in the middle of an otherwise clean feed does not erase months of
    accumulated OBV. Direction for the bar right after a gap is measured
    against the last *known* close, not the missing one, so OBV picks back up
    correctly once real data resumes.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.obv([10, 11, 10, 10], [100, 50, 80, 20]).tolist()
    [0.0, 50.0, -30.0, -30.0]

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv
    """
    require_aligned_index(close=close, volume=volume)
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    # Compare each bar against the last *known* close (forward-filled) rather
    # than the immediately preceding raw one, so a gap doesn't corrupt the
    # direction reading for the bar where real data resumes.
    filled_close = pd.Series(close_values).ffill().to_numpy()
    direction = np.sign(np.diff(filled_close, prepend=filled_close[0]))
    signed_volume = direction * volume_values

    # A bar with an unknown close or volume contributes nothing — held flat —
    # instead of poisoning every bar after it via NaN propagating through
    # cumsum. Bar 0 has no prior bar to compare against, so it is always flat.
    gap = ~np.isfinite(close_values) | ~np.isfinite(volume_values) | ~np.isfinite(signed_volume)
    signed_volume = np.where(gap, 0.0, signed_volume)
    signed_volume[0] = 0.0

    result = np.cumsum(signed_volume)

    return wrap_series(result, common_index(close, volume), "OBV")


@indicator(
    category="volume",
    summary="Running total of volume weighted by where the close sits in its own range.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line"
    ),
    outputs=("ADL",),
)
def adl(high: ArrayLike, low: ArrayLike, close: ArrayLike, volume: ArrayLike) -> pd.Series:
    """Accumulation/Distribution Line.

    ``MFM = ((Close - Low) - (High - Close)) / (High - Low)`` — the Money Flow
    Multiplier, ``+1`` when the close sits at the top of the bar's range,
    ``-1`` at the bottom; ``MFV = MFM * Volume``; ``ADL = Previous ADL + MFV``.
    Where :func:`obv` only asks whether the close was up or down, ADL asks
    *where inside the bar's full range* the close landed and weights that by
    volume — a more graded read on the same buying-versus-selling idea. It is
    also the running-total version of :func:`cmf`, which instead sums ``MFV``
    over a fixed window and divides by volume to get a bounded ratio.

    Parameters
    ----------
    high, low, close, volume:
        Series of equal length.

    Returns
    -------
    pandas.Series
        Named ``ADL``. Never ``NaN`` — a running total, not a windowed
        statistic. Like OBV, the absolute level is arbitrary; only its slope
        and its divergence from price are meaningful.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value, which has no meaning for a
        traded quantity.

    Notes
    -----
    A bar with an unknown high, low, close or volume (``NaN``) contributes
    nothing to the running total rather than corrupting every bar after it —
    a single bad tick in the middle of an otherwise clean feed does not erase
    months of accumulated ADL, the same convention :func:`obv` uses. Unlike
    OBV, ADL has no day-to-day comparison to re-anchor, so no special
    handling is needed for the bar right after a gap.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.adl([11, 12], [9, 10], [11, 12], [100, 100]).tolist()
    [100.0, 200.0]

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line
    """
    require_aligned_index(high=high, low=low, close=close, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(high=high_values, low=low_values, close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    result = _adl_values(high_values, low_values, close_values, volume_values)

    return wrap_series(result, common_index(high, low, close, volume), "ADL")


@indicator(
    category="volume",
    summary="MACD's fast-EMA-minus-slow-EMA shape applied to the A/D Line instead of price.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/chaikin-oscillator"
    ),
    outputs=("ADOSC",),
)
def chaikin_oscillator(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    volume: ArrayLike,
    fast: int = 3,
    slow: int = 10,
) -> pd.Series:
    """Chaikin Oscillator.

    ``ChaikinOsc = EMA(ADL, fast) - EMA(ADL, slow)`` — the same fast-EMA-minus-
    slow-EMA shape as :func:`macd`, but applied to :func:`adl` instead of raw
    price. Where ADL tracks the cumulative level of buying versus selling
    pressure, this measures whether that pressure is currently accelerating
    or decelerating — a rate-of-change read on ADL, the same relationship
    :func:`awesome_oscillator` has to price.

    Parameters
    ----------
    high, low, close, volume:
        Series of equal length.
    fast, slow:
        EMA lengths applied to the A/D Line; ``fast`` must be smaller than
        ``slow``.

    Returns
    -------
    pandas.Series
        Named ``ADOSC_{fast}_{slow}``. Like ADL itself, only its sign and
        slope are meaningful — the absolute level depends on where the
        underlying ADL happens to sit.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value, or if ``fast`` is not
        smaller than ``slow``.

    Examples
    --------
    >>> import zeonta
    >>> highs = [11.0, 12.0, 11.5, 13.0, 12.5]
    >>> lows = [9.0, 10.0, 9.5, 11.0, 10.5]
    >>> closes = [10.5, 11.5, 10.0, 12.5, 11.0]
    >>> volumes = [100.0, 120.0, 90.0, 150.0, 110.0]
    >>> float(zeonta.chaikin_oscillator(highs, lows, closes, volumes, fast=2, slow=3).iloc[-1])
    -0.6944444444444429

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")

    require_aligned_index(high=high, low=low, close=close, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(high=high_values, low=low_values, close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    adl_values = _adl_values(high_values, low_values, close_values, volume_values)
    result = ema_values(adl_values, fast) - ema_values(adl_values, slow)

    return wrap_series(result, common_index(high, low, close, volume), f"ADOSC_{fast}_{slow}")


@indicator(
    category="volume",
    summary="Volume-weighted measure of where price closed within its own range.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf"
    ),
    outputs=("CMF",),
)
def cmf(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    volume: ArrayLike,
    length: int = 20,
) -> pd.Series:
    """Chaikin Money Flow.

    ``MFM = ((Close - Low) - (High - Close)) / (High - Low)`` — the Money Flow
    Multiplier, ``+1`` when the close sits at the top of the bar's range,
    ``-1`` at the bottom. ``MFV = MFM * Volume``;
    ``CMF = Sum(MFV, n) / Sum(Volume, n)``.

    Parameters
    ----------
    high, low, close, volume:
        Series of equal length.
    length:
        Look-back window for both sums.

    Returns
    -------
    pandas.Series
        Named ``CMF_{length}``, ranging roughly -1 to +1 (a bar that closed at
        one extreme of its range on every bar in the window pushes it toward
        the corresponding boundary; ordinary mixed closes keep it well inside).

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value, which has no meaning for a
        traded quantity.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.cmf([11, 12], [9, 10], [11, 12], [100, 100], length=2).iloc[-1])
    1.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf
    """
    length = validate_length(length)

    require_aligned_index(high=high, low=low, close=close, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(high=high_values, low=low_values, close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    multiplier = _money_flow_multiplier(high_values, low_values, close_values)
    money_flow_volume = multiplier * volume_values
    sum_volume = rolling_sum(volume_values, length)
    sum_flow = rolling_sum(money_flow_volume, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        result = sum_flow / sum_volume
    result = np.where(sum_volume == 0.0, 0.0, result)
    result = np.where(np.isfinite(sum_volume), result, np.nan)

    return wrap_series(result, common_index(high, low, close, volume), f"CMF_{length}")


@indicator(
    category="volume",
    summary='"Volume-weighted RSI" — momentum measured through money flow instead of price.',
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi"
    ),
    outputs=("MFI",),
)
def mfi(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    volume: ArrayLike,
    length: int = 14,
) -> pd.Series:
    """Money Flow Index.

    ``TP = (High + Low + Close) / 3``; ``RawFlow = TP * Volume``. Each bar's
    raw flow is classified positive when ``TP`` rose from the previous bar and
    negative when it fell; ``MFR = Sum(PositiveFlow, n) / Sum(NegativeFlow, n)``;
    ``MFI = 100 - 100 / (1 + MFR)``. The structure mirrors :func:`rsi` exactly,
    with typical-price-times-volume standing in for a plain price change — and
    unlike RSI's Wilder smoothing, MFI's sums are plain (unsmoothed) totals.

    Parameters
    ----------
    high, low, close, volume:
        Series of equal length.
    length:
        Look-back window for both money-flow sums.

    Returns
    -------
    pandas.Series
        Named ``MFI_{length}``, ranging 0-100.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value, which has no meaning for a
        traded quantity.

    Examples
    --------
    >>> import zeonta
    >>> prices = [float(i) for i in range(2, 20)]
    >>> out = zeonta.mfi(prices, [p - 1 for p in prices], prices, [100.0] * 18, length=14)
    >>> float(out.iloc[-1])
    100.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi
    """
    length = validate_length(length)

    require_aligned_index(high=high, low=low, close=close, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    size = require_same_length(
        high=high_values, low=low_values, close=close_values, volume=volume_values
    )
    require_non_negative(volume=volume_values)

    typical = (high_values + low_values + close_values) / 3.0
    raw_flow = typical * volume_values

    change = np.diff(typical, prepend=np.nan)
    positive_flow = np.where(np.isfinite(change) & (change > 0.0), raw_flow, 0.0)
    negative_flow = np.where(np.isfinite(change) & (change < 0.0), raw_flow, 0.0)
    positive_flow[0] = np.nan
    negative_flow[0] = np.nan

    sum_positive = np.full(size, np.nan, dtype="float64")
    sum_negative = np.full(size, np.nan, dtype="float64")
    sum_positive[1:] = rolling_sum(positive_flow[1:], length)
    sum_negative[1:] = rolling_sum(negative_flow[1:], length)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = sum_positive / sum_negative
        result = 100.0 - 100.0 / (1.0 + ratio)

    # No negative flow at all -> ratio is infinite -> MFI is 100; both zero -> flat -> 50.
    result = np.where((sum_negative == 0.0) & np.isfinite(sum_positive), 100.0, result)
    flat = (sum_negative == 0.0) & (sum_positive == 0.0)
    result = np.where(flat, 50.0, result)
    result = np.where(np.isfinite(sum_positive) & np.isfinite(sum_negative), result, np.nan)

    return wrap_series(result, common_index(high, low, close, volume), f"MFI_{length}")


@indicator(
    category="volume",
    summary="Volume-weighted price change: Elder's Force Index.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/force-index"
    ),
    outputs=("FI",),
)
def force_index(close: ArrayLike, volume: ArrayLike, length: int = 13) -> pd.Series:
    """Force Index.

    ``FI(1) = (Close - PriorClose) * Volume``; ``FI(n) = EMA(FI(1), n)``.
    Alexander Elder's combination of price direction, price magnitude and
    volume into one line — a bar that moves further on more volume produces
    a proportionally larger reading than the same move on light volume,
    something a pure price indicator like :func:`~zeonta.momentum` cannot see.

    Parameters
    ----------
    close, volume:
        Series of equal length.
    length:
        EMA smoothing period. ``length=1`` returns the unsmoothed raw
        1-bar Force Index.

    Returns
    -------
    pandas.Series
        Named ``FI_{length}``. Only its sign and slope are meaningful, not
        its absolute level, since that scales directly with the security's
        own share volume.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.force_index([10, 11, 10, 12], [100, 100, 100, 100], length=1).tolist()
    [nan, 100.0, -100.0, 200.0]

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index
    """
    length = validate_length(length)
    require_aligned_index(close=close, volume=volume)
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    raw = np.diff(close_values, prepend=np.nan) * volume_values
    result = ema_values(raw, length)

    return wrap_series(result, common_index(close, volume), f"FI_{length}")


@indicator(
    category="volume",
    summary="How much price moves per unit of volume — Arms' Ease of Movement.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv"
    ),
    outputs=("EOM",),
)
def ease_of_movement(
    high: ArrayLike, low: ArrayLike, volume: ArrayLike, length: int = 14
) -> pd.Series:
    """Ease of Movement (EMV).

    ``DistanceMoved = (High+Low)/2 - (PriorHigh+PriorLow)/2``;
    ``BoxRatio = (Volume/100,000,000) / (High-Low)``;
    ``EMV(1) = DistanceMoved / BoxRatio``; ``EOM = SMA(EMV(1), n)``. Richard
    Arms' box-ratio idea directly compares a bar's price movement against
    how much volume that movement needed — the same underlying question
    :func:`chaikin_oscillator` and :func:`mfi` ask, from a different angle.

    Parameters
    ----------
    high, low, volume:
        Series of equal length.
    length:
        SMA smoothing period applied to the raw 1-bar EMV.

    Returns
    -------
    pandas.Series
        Named ``EOM_{length}``. Positive readings mean price is advancing
        easily (little volume needed per unit of price movement); readings
        near zero mean price is struggling against volume to move at all.

    Raises
    ------
    ValueError
        If ``volume`` contains a negative value.

    Notes
    -----
    A zero-range bar (``High == Low``) or a zero-volume bar makes the box
    ratio degenerate (a zero or infinite denominator); either case is
    treated as contributing ``0`` to the raw EMV rather than raising or
    producing ``inf``/``NaN``, the same convention :func:`cmf`'s Money Flow
    Multiplier uses for its own zero-range case.

    Examples
    --------
    >>> import zeonta
    >>> high = [11.0, 12.0, 13.0]
    >>> low = [9.0, 10.0, 11.0]
    >>> volume = [100_000_000.0, 100_000_000.0, 200_000_000.0]
    >>> zeonta.ease_of_movement(high, low, volume, length=1).tolist()
    [nan, 2.0, 1.0]

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    volume_values = as_array(volume, "volume")
    require_same_length(high=high_values, low=low_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    midpoint = (high_values + low_values) / 2.0
    prior_midpoint = np.concatenate(([np.nan], midpoint[:-1]))
    distance_moved = midpoint - prior_midpoint
    span = high_values - low_values

    with np.errstate(divide="ignore", invalid="ignore"):
        box_ratio = (volume_values / 100_000_000.0) / span
        raw_emv = distance_moved / box_ratio
    degenerate = (span == 0.0) | (volume_values == 0.0)
    raw_emv = np.where(degenerate & np.isfinite(distance_moved), 0.0, raw_emv)

    result = rolling_mean(raw_emv, length)

    return wrap_series(result, common_index(high, low, volume), f"EOM_{length}")


@indicator(
    category="volume",
    summary="Where the close landed between open and the bar's range, unweighted by volume.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/balance-of-power-bop"
    ),
    outputs=("BOP",),
)
def bop(open: ArrayLike, high: ArrayLike, low: ArrayLike, close: ArrayLike) -> pd.Series:
    """Balance of Power (Igor Livshin, 2001).

    ``BOP = (Close - Open) / (High - Low)`` — ``+1`` when the close sits at
    the top of the bar's own open-to-range move, ``-1`` at the bottom.
    Similar in shape to :func:`~zeonta.cmf`'s Money Flow Multiplier, but
    measured from the *open* rather than volume-weighted, and returned raw
    per bar rather than summed over a window.

    Left unsmoothed to match the plain per-bar ratio most implementations
    (including TA-Lib's) use; StockCharts' own page describes smoothing it
    with a moving average for a less choppy line — pipe the result into
    :func:`~zeonta.sma` yourself if you want that.

    Parameters
    ----------
    open, high, low, close:
        Series of equal length.

    Returns
    -------
    pandas.Series
        Named ``BOP``. ``0`` on a zero-range bar (``High == Low``), rather
        than an undefined division.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.bop([10.0], [12.0], [9.0], [11.0]).tolist()
    [0.3333333333333333]

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop
    """
    require_aligned_index(open=open, high=high, low=low, close=close)
    open_values = as_array(open, "open")
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(open=open_values, high=high_values, low=low_values, close=close_values)

    span = high_values - low_values
    with np.errstate(divide="ignore", invalid="ignore"):
        result = (close_values - open_values) / span
    result = np.where(span == 0.0, 0.0, result)

    return wrap_series(result, common_index(open, high, low, close), "BOP")


@indicator(
    category="volume",
    summary="Running total of volume-scaled percentage price change.",
    reference="https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/",
    outputs=("PVT",),
)
def pvt(close: ArrayLike, volume: ArrayLike) -> pd.Series:
    """Price Volume Trend.

    ``PVT[0] = 0``; for every following bar,
    ``PVT[i] = PVT[i-1] + Volume[i] * (Close[i] - Close[i-1]) / Close[i-1]``.
    Where :func:`~zeonta.obv` adds or subtracts a bar's *entire* volume
    based only on which direction the close moved, PVT scales the volume
    it adds by *how much* the close moved (as a percentage) — a 3% up day
    contributes three times as much as a 1% up day, rather than the same
    full volume either way.

    Parameters
    ----------
    close, volume:
        Series of equal length.

    Returns
    -------
    pandas.Series
        Named ``PVT``. Never ``NaN`` — a running total, not a windowed
        statistic. The absolute level is arbitrary; only its slope and its
        divergence from price are meaningful.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.pvt([10.0, 11.0, 10.0], [100.0, 200.0, 150.0]).tolist()
    [0.0, 20.0, 6.363636363636363]

    References
    ----------
    https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/
    """
    require_aligned_index(close=close, volume=volume)
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    with np.errstate(divide="ignore", invalid="ignore"):
        percent_change = np.diff(close_values, prepend=close_values[0]) / np.concatenate(
            ([np.nan], close_values[:-1])
        )
        raw_contribution = percent_change * volume_values
    # A missing close or volume anywhere in the pair must not poison every
    # later bar the way an unguarded NaN would once it hits cumsum (the
    # exact bug adl() was fixed for) — held at 0 for that one bar instead.
    contribution = np.where(np.isfinite(raw_contribution), raw_contribution, 0.0)
    contribution[0] = 0.0
    result = np.cumsum(contribution)

    return wrap_series(result, common_index(close, volume), "PVT")


def _volume_conditioned_index(close: np.ndarray, volume: np.ndarray, *, rises: bool) -> np.ndarray:
    """Shared engine for :func:`nvi`/:func:`pvi`.

    Starts at ``1000`` (StockCharts' convention); on a bar where *volume*
    moved in the direction *rises* asks for relative to the bar before it,
    scales by that bar's percentage price change; otherwise carries the
    previous value forward unchanged.
    """
    size = close.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    result[0] = 1000.0
    for i in range(1, size):
        moved = volume[i] > volume[i - 1] if rises else volume[i] < volume[i - 1]
        if not moved or close[i - 1] == 0.0 or not np.isfinite(close[i - 1] + close[i]):
            result[i] = result[i - 1]
        else:
            result[i] = result[i - 1] * (1.0 + (close[i] - close[i - 1]) / close[i - 1])
    return result


@indicator(
    category="volume",
    summary="Cumulative index that only moves on a bar where volume fell versus the prior bar.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi"
    ),
    outputs=("NVI",),
)
def nvi(close: ArrayLike, volume: ArrayLike) -> pd.Series:
    """Negative Volume Index.

    Starts at ``1000``. On a bar where ``Volume`` *fell* versus the bar
    before it, ``NVI[i] = NVI[i-1] * (1 + (Close[i]-Close[i-1])/Close[i-1])``;
    otherwise ``NVI[i] = NVI[i-1]`` unchanged. Built on the idea (Paul
    Dysart, 1930s-40s; popularised by Norman Fosback) that price moves on
    *quiet* volume days carry more informed-money signal than moves on
    heavy, crowd-driven volume days — the mirror-image complement of
    :func:`pvi`.

    Parameters
    ----------
    close, volume:
        Series of equal length.

    Returns
    -------
    pandas.Series
        Named ``NVI``, starting at ``1000``. Never ``NaN`` past the first
        bar — a running index, not a windowed statistic.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.nvi([10.0, 11.0, 9.0, 9.5], [100.0, 80.0, 120.0, 90.0]).tolist()
    [1000.0, 1100.0, 1100.0, 1161.111111111111]

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi
    """
    require_aligned_index(close=close, volume=volume)
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    result = _volume_conditioned_index(close_values, volume_values, rises=False)
    return wrap_series(result, common_index(close, volume), "NVI")


@indicator(
    category="volume",
    summary="Cumulative index that only moves on a bar where volume rose versus the prior bar.",
    reference=(
        "https://www.fidelity.com/learning-center/trading-investing/technical-analysis/"
        "technical-indicator-guide/positive-volume-index"
    ),
    outputs=("PVI",),
)
def pvi(close: ArrayLike, volume: ArrayLike) -> pd.Series:
    """Positive Volume Index.

    Starts at ``1000``. On a bar where ``Volume`` *rose* versus the bar
    before it, ``PVI[i] = PVI[i-1] * (1 + (Close[i]-Close[i-1])/Close[i-1])``;
    otherwise ``PVI[i] = PVI[i-1]`` unchanged — the mirror-image complement
    of :func:`nvi`, built on the idea that price moves on *heavy* volume
    days reflect crowd-driven rather than informed-money activity.

    Parameters
    ----------
    close, volume:
        Series of equal length.

    Returns
    -------
    pandas.Series
        Named ``PVI``, starting at ``1000``. Never ``NaN`` past the first
        bar — a running index, not a windowed statistic.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.pvi([10.0, 11.0, 9.0, 9.5], [100.0, 80.0, 120.0, 90.0]).tolist()
    [1000.0, 1000.0, 818.1818181818181, 818.1818181818181]

    References
    ----------
    https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index
    """
    require_aligned_index(close=close, volume=volume)
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    result = _volume_conditioned_index(close_values, volume_values, rises=True)
    return wrap_series(result, common_index(close, volume), "PVI")


@indicator(
    category="volume",
    summary="Difference of two EMAs of a trend-and-range-scaled volume force.",
    reference="https://tulipindicators.org/kvo",
    outputs=("KVO", "KVOs"),
)
def klinger_volume_oscillator(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    volume: ArrayLike,
    fast: int = 34,
    slow: int = 55,
    signal_length: int = 13,
) -> pd.DataFrame:
    """Klinger Volume Oscillator (Stephen Klinger).

    Builds a "volume force" that signs each bar's volume by trend and
    scales it by how the bar's own range compares to the accumulated
    range since the trend last flipped, then takes the difference of two
    EMAs of that force::

        HLC = High + Low + Close
        Trend = +1 if HLC rose vs. the prior bar, -1 if it fell, else carried forward
        dm = High - Low
        cm = dm[-1] + dm if Trend flipped, else cm[-1] + dm
        VF = 100 * Volume * Trend * |2*(dm/cm) - 1|
        KVO = EMA(VF, fast) - EMA(VF, slow)

    with an EMA of ``KVO`` as its own signal line. Where :func:`obv` signs
    a bar's *entire* volume by direction alone, Klinger's volume force is
    scaled down when a bar's own range is small relative to the
    accumulated move (a half-hearted push) and scaled up when the range
    dominates it (full commitment behind the move).

    Parameters
    ----------
    high, low, close, volume:
        Series of equal length.
    fast, slow:
        EMA periods for the volume force. Klinger's own commonly cited
        defaults are ``34`` and ``55``.
    signal_length:
        EMA period for the signal line. Klinger's own default is ``13``.

    Returns
    -------
    pandas.DataFrame
        Columns ``KVO_{fast}_{slow}`` and ``KVOs_{fast}_{slow}`` (the
        signal line).

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.0, 11.0, 14.0, 15.0, 13.5, 16.0]
    >>> low = [10.0, 11.0, 9.0, 12.0, 13.0, 11.5, 14.0]
    >>> close = [11.0, 12.5, 10.0, 13.5, 14.5, 12.5, 15.5]
    >>> volume = [100.0, 150.0, 200.0, 120.0, 180.0, 90.0, 210.0]
    >>> out = zeonta.klinger_volume_oscillator(high, low, close, volume, fast=3, slow=5)
    >>> round(float(out.iloc[-1, 0]), 6)
    -463.888889

    References
    ----------
    https://tulipindicators.org/kvo
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    signal_length = validate_length(signal_length, "signal_length")
    require_aligned_index(high=high, low=low, close=close, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    size = require_same_length(
        high=high_values, low=low_values, close=close_values, volume=volume_values
    )
    require_non_negative(volume=volume_values)

    hlc = high_values + low_values + close_values
    dm = high_values - low_values

    trend = np.zeros(size, dtype="float64")
    cm = np.zeros(size, dtype="float64")
    if size > 0:
        trend[0] = 1.0
        cm[0] = dm[0]
    for i in range(1, size):
        if not np.isfinite(hlc[i] - hlc[i - 1]):
            trend[i] = trend[i - 1]
        elif hlc[i] > hlc[i - 1]:
            trend[i] = 1.0
        elif hlc[i] < hlc[i - 1]:
            trend[i] = -1.0
        else:
            trend[i] = trend[i - 1]
        cm[i] = (dm[i - 1] + dm[i]) if trend[i] != trend[i - 1] else (cm[i - 1] + dm[i])

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(cm != 0.0, dm / cm, 0.0)
    volume_force = 100.0 * volume_values * trend * np.abs(2.0 * ratio - 1.0)
    volume_force = np.where(np.isfinite(hlc) & np.isfinite(volume_values), volume_force, np.nan)

    short_ema = ema_values(volume_force, fast)
    long_ema = ema_values(volume_force, slow)
    result = short_ema - long_ema
    signal = ema_values(result, signal_length)

    order = [f"KVO_{fast}_{slow}", f"KVOs_{fast}_{slow}"]
    return wrap_frame(
        dict(zip(order, (result, signal), strict=True)),
        common_index(high, low, close, volume),
        order=order,
    )


@indicator(
    category="volume",
    summary="Running total gated by whether today extended a rising or falling close.",
    reference="https://tulipindicators.org/wad",
    outputs=("WAD",),
)
def williams_ad(high: ArrayLike, low: ArrayLike, close: ArrayLike) -> pd.Series:
    """Williams Accumulation/Distribution (Larry Williams).

    ``WAD[0] = 0``; for every following bar::

        TRH = max(Close[i-1], High[i])
        TRL = min(Close[i-1], Low[i])
        WAD[i] = WAD[i-1] + (Close[i] - TRL)   if Close[i] > Close[i-1]
        WAD[i] = WAD[i-1] + (Close[i] - TRH)   if Close[i] < Close[i-1]
        WAD[i] = WAD[i-1]                      if Close[i] == Close[i-1]

    Unlike :func:`adl` (which weighs every bar by where the close sits in
    *that bar's own* range), WAD anchors each bar against the *prior
    close* — a bar that gapped up still only gets credit for the move
    above yesterday's close, not its own full range. No volume term
    despite the name and the category it sits in; it is purely a price
    construction, predating :func:`adl`.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.

    Returns
    -------
    pandas.Series
        Named ``WAD``. Never ``NaN`` — a running total, not a windowed
        statistic. The absolute level is arbitrary; only its slope and
        its divergence from price are meaningful.

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.0, 11.0, 14.0, 15.0]
    >>> low = [10.0, 11.0, 9.0, 12.0, 13.0]
    >>> close = [11.0, 12.5, 10.0, 13.5, 14.5]
    >>> zeonta.williams_ad(high, low, close).tolist()
    [0.0, 1.5, -1.0, 2.5, 4.0]

    References
    ----------
    https://tulipindicators.org/wad
    """
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(high=high_values, low=low_values, close=close_values)

    result = np.zeros(size, dtype="float64")
    for i in range(1, size):
        previous_close = close_values[i - 1]
        current_close = close_values[i]
        if not np.isfinite(previous_close + current_close + high_values[i] + low_values[i]):
            result[i] = result[i - 1]
            continue
        true_range_high = max(previous_close, high_values[i])
        true_range_low = min(previous_close, low_values[i])
        if current_close > previous_close:
            result[i] = result[i - 1] + (current_close - true_range_low)
        elif current_close < previous_close:
            result[i] = result[i - 1] + (current_close - true_range_high)
        else:
            result[i] = result[i - 1]

    return wrap_series(result, common_index(high, low, close), "WAD")


@indicator(
    category="volume",
    summary="MACD built from Volume-Weighted Moving Averages instead of EMAs.",
    outputs=("VWMACD", "VWMACDs", "VWMACDh"),
    reference="https://vectoralpha.dev/projects/ta/indicators/vwmacd/",
)
def vwmacd(
    close: ArrayLike,
    volume: ArrayLike,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Volume-Weighted MACD (Buff Dormeier, 2000).

    The same fast-minus-slow-then-signal shape as :func:`macd`, but built
    from :func:`vwma` instead of a plain EMA::

        VWMACD = VWMA(Close, fast) - VWMA(Close, slow)
        Signal = EMA(VWMACD, signal)
        Histogram = VWMACD - Signal

    Weighting the fast and slow lines by volume makes crossovers more
    representative of moves that traded heavily, rather than treating a
    thin, quiet bar the same as a heavily-traded one the way plain MACD
    does. The signal line stays a plain EMA — the MACD line itself
    already carries the volume weighting.

    Parameters
    ----------
    close, volume:
        Series of equal length.
    fast, slow:
        VWMA lengths; ``fast`` must be smaller than ``slow``.
    signal:
        EMA length of the signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``VWMACD_{f}_{s}_{sig}``, ``VWMACDs_{f}_{s}_{sig}``,
        ``VWMACDh_{f}_{s}_{sig}``.

    Examples
    --------
    >>> import zeonta
    >>> close = list(range(1, 41))
    >>> volume = [100.0 + 5.0 * i for i in range(40)]
    >>> list(zeonta.vwmacd(close, volume, fast=3, slow=6, signal=2).columns)
    ['VWMACD_3_6_2', 'VWMACDs_3_6_2', 'VWMACDh_3_6_2']

    References
    ----------
    https://vectoralpha.dev/projects/ta/indicators/vwmacd/
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    signal = validate_length(signal, "signal")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")

    fast_vwma = vwma(close, volume, length=fast).to_numpy()
    slow_vwma = vwma(close, volume, length=slow).to_numpy()
    macd_line = fast_vwma - slow_vwma
    signal_line = ema_values(macd_line, signal)
    histogram = macd_line - signal_line

    suffix = f"{fast}_{slow}_{signal}"
    order = [f"VWMACD_{suffix}", f"VWMACDs_{suffix}", f"VWMACDh_{suffix}"]
    return wrap_frame(
        dict(zip(order, (macd_line, signal_line, histogram), strict=True)),
        common_index(close, volume),
        order=order,
    )
