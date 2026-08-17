"""Volume-based indicators: On-Balance Volume, Chaikin Money Flow, Money Flow Index.

None of these are part of the TA 101 curriculum; see each function's own
``References`` section for its source. They sit apart from
:func:`zeonta.relative_volume` (which normalises raw volume against its own
recent average) and :func:`zeonta.vwap` (which weights *price* by volume) —
this module instead combines volume with price *direction* to build a
running measure of buying versus selling pressure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    as_array,
    common_index,
    indicator,
    require_aligned_index,
    require_same_length,
    rolling_sum,
    validate_length,
    wrap_series,
)

__all__ = ["cmf", "mfi", "obv"]


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

    # diff against the bar's own close makes bar 0's contribution exactly 0,
    # matching "OBV starts at 0" without a special-cased first element.
    direction = np.sign(np.diff(close_values, prepend=close_values[0]))
    result = np.cumsum(direction * volume_values)

    return wrap_series(result, common_index(close, volume), "OBV")


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

    span = high_values - low_values
    with np.errstate(divide="ignore", invalid="ignore"):
        multiplier = ((close_values - low_values) - (high_values - close_values)) / span
    # A zero-range bar carries no information about buying/selling pressure.
    multiplier = np.where(span == 0.0, 0.0, multiplier)

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
