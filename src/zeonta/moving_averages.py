"""Moving averages: SMA, EMA, crossovers and the EMA ribbon.

Formulas follow the TA 101 *Moving Averages* module.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    as_array,
    common_index,
    ema_values,
    indicator,
    rolling_mean,
    validate_length,
    wrap_frame,
    wrap_series,
)

__all__ = ["ema", "ema_ribbon", "ma_cross", "sma"]


@indicator(
    category="moving_averages",
    summary="Equally weighted average of the last n closes.",
    lesson="sma",
    outputs=("SMA",),
)
def sma(close: ArrayLike, length: int = 20) -> pd.Series:
    """Simple Moving Average.

    ``SMA(n) = (1/n) * sum(Close[i])`` over the last ``n`` bars — an equally
    weighted average of the ``n`` most recent closes.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window in bars. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``SMA_{length}``. The first ``length - 1`` bars are ``NaN``.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.sma([1, 2, 3, 4, 5], length=3).tolist()
    [nan, nan, 2.0, 3.0, 4.0]

    References
    ----------
    https://ta.cognicode.org/learn/sma
    """
    length = validate_length(length)
    values = as_array(close, "close")
    return wrap_series(rolling_mean(values, length), common_index(close), f"SMA_{length}")


@indicator(
    category="moving_averages",
    summary="Exponentially weighted average that reacts faster to recent closes.",
    lesson="ema",
    outputs=("EMA",),
)
def ema(close: ArrayLike, length: int = 20) -> pd.Series:
    """Exponential Moving Average.

    ``EMA(n) today = Close * k + EMA(n) yesterday * (1 - k)`` with ``k = 2 / (n + 1)``.
    The recursion is seeded with the SMA of the first ``n`` closes, so the first
    non-``NaN`` value lands on bar ``n - 1``.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window in bars. Must be >= 1 (``length=1`` returns the input).

    Returns
    -------
    pandas.Series
        Named ``EMA_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.ema([1, 2, 3, 4, 5], length=3).iloc[-1])
    4.0

    References
    ----------
    https://ta.cognicode.org/learn/ema
    """
    length = validate_length(length)
    values = as_array(close, "close")
    return wrap_series(ema_values(values, length), common_index(close), f"EMA_{length}")


@indicator(
    category="moving_averages",
    summary="Fast/slow moving-average crossover signals (golden and death cross).",
    lesson="ma-crossovers",
    outputs=("MAfast", "MAslow", "cross"),
)
def ma_cross(
    close: ArrayLike,
    fast: int = 50,
    slow: int = 200,
    mode: str = "sma",
) -> pd.DataFrame:
    """Moving-average crossover signals.

    Bullish crossover (a *golden cross* at the 50/200 default):
    ``fast[i-1] <= slow[i-1] and fast[i] > slow[i]``.
    Bearish crossunder (*death cross*): ``fast[i-1] >= slow[i-1] and fast[i] < slow[i]``.

    Parameters
    ----------
    close:
        Closing prices.
    fast:
        Length of the fast average. Must be smaller than ``slow``.
    slow:
        Length of the slow average.
    mode:
        ``"sma"`` or ``"ema"`` — which average to cross.

    Returns
    -------
    pandas.DataFrame
        Columns ``MAfast_{fast}``, ``MAslow_{slow}`` and ``cross_{fast}_{slow}``,
        where ``cross`` is ``1.0`` on a bullish crossover, ``-1.0`` on a bearish
        crossunder and ``0.0`` otherwise (``NaN`` while either average is warming up).

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.ma_cross(list(range(1, 30)), fast=3, slow=5)
    >>> sorted(out.columns)
    ['MAfast_3', 'MAslow_5', 'cross_3_5']

    References
    ----------
    https://ta.cognicode.org/learn/ma-crossovers
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")
    if mode not in ("sma", "ema"):
        raise ValueError(f"'mode' must be 'sma' or 'ema', got {mode!r}")

    values = as_array(close, "close")
    smoother = rolling_mean if mode == "sma" else ema_values
    fast_line = smoother(values, fast)
    slow_line = smoother(values, slow)

    difference = fast_line - slow_line
    previous = np.concatenate(([np.nan], difference[:-1]))

    cross = np.full(values.shape[0], np.nan, dtype="float64")
    comparable = np.isfinite(difference) & np.isfinite(previous)
    cross[comparable] = 0.0
    cross[comparable & (previous <= 0) & (difference > 0)] = 1.0
    cross[comparable & (previous >= 0) & (difference < 0)] = -1.0

    return wrap_frame(
        {
            f"MAfast_{fast}": fast_line,
            f"MAslow_{slow}": slow_line,
            f"cross_{fast}_{slow}": cross,
        },
        common_index(close),
        order=[f"MAfast_{fast}", f"MAslow_{slow}", f"cross_{fast}_{slow}"],
    )


@indicator(
    category="moving_averages",
    summary="A fan of EMAs of increasing length; spacing shows trend strength.",
    lesson="ema-ribbon",
    outputs=("EMA",),
    returns_frame=True,
)
def ema_ribbon(
    close: ArrayLike,
    lengths: Sequence[int] = (20, 30, 40, 50, 60, 70),
) -> pd.DataFrame:
    """EMA Ribbon — several EMAs of increasing length plotted together.

    The default is the evenly spaced ``20, 30, 40, 50, 60, 70`` set; the
    Fibonacci-flavoured ``8, 13, 21, 34, 55, 89`` is an equally common choice.
    Each line is a plain :func:`ema`.

    Parameters
    ----------
    close:
        Closing prices.
    lengths:
        Strictly increasing EMA lengths.

    Returns
    -------
    pandas.DataFrame
        One ``EMA_{length}`` column per requested length, in the given order.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.ema_ribbon(list(range(50)), lengths=(5, 10)).columns)
    ['EMA_5', 'EMA_10']

    References
    ----------
    https://ta.cognicode.org/learn/ema-ribbon
    """
    if len(lengths) < 2:
        raise ValueError(f"'lengths' must contain at least two lengths, got {list(lengths)}")
    checked = [validate_length(length, "lengths") for length in lengths]
    if any(later <= earlier for earlier, later in itertools.pairwise(checked)):
        raise ValueError(f"'lengths' must be strictly increasing, got {checked}")

    values = as_array(close, "close")
    columns = {f"EMA_{length}": ema_values(values, length) for length in checked}
    return wrap_frame(columns, common_index(close), order=list(columns))
