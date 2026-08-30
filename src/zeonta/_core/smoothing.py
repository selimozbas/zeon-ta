"""Recursive smoothing primitives shared by EMA, RSI, ATR and ADX.

Both smoothers implemented here follow the same shape: seed the recursion with a
simple average of the first complete window, then apply

    out[i] = alpha * value[i] + (1 - alpha) * out[i - 1]

Only ``alpha`` differs — ``2 / (length + 1)`` for the exponential moving average
and ``1 / length`` for Wilder's smoothing. Sharing one seeded implementation is
what keeps RSI, ATR and ADX numerically consistent with each other.
"""

from __future__ import annotations

import numpy as np

__all__ = ["ema_values", "first_full_window", "super_smoother_values", "wilder_values"]


def first_full_window(values: np.ndarray, length: int) -> int:
    """Index of the last bar of the earliest all-finite window of *length* bars.

    Returns ``-1`` when no such window exists, which callers treat as "the result
    is entirely NaN".
    """
    finite = np.isfinite(values)
    run = 0
    for i in range(values.shape[0]):
        run = run + 1 if finite[i] else 0
        if run >= length:
            return i
    return -1


def _seeded_recursive(values: np.ndarray, length: int, alpha: float) -> np.ndarray:
    out = np.full(values.shape[0], np.nan, dtype="float64")
    seed_index = first_full_window(values, length)
    if seed_index < 0:
        return out

    out[seed_index] = values[seed_index - length + 1 : seed_index + 1].mean()
    one_minus = 1.0 - alpha
    previous = out[seed_index]
    for i in range(seed_index + 1, values.shape[0]):
        value = values[i]
        if not np.isfinite(value):
            # Keep the recursion alive across gaps rather than poisoning the tail.
            out[i] = previous
            continue
        previous = alpha * value + one_minus * previous
        out[i] = previous
    return out


def ema_values(values: np.ndarray, length: int) -> np.ndarray:
    """Exponential moving average, seeded with the SMA of the first *length* bars."""
    if length == 1:
        return values.astype("float64", copy=True)
    return _seeded_recursive(values, length, 2.0 / (length + 1.0))


def wilder_values(values: np.ndarray, length: int) -> np.ndarray:
    """Wilder's smoothing (a.k.a. RMA), seeded with the SMA of the first *length* bars.

    Equivalent to the textbook ``(prev * (n - 1) + value) / n`` recursion used by
    Wilder for ATR, RSI and ADX.
    """
    if length == 1:
        return values.astype("float64", copy=True)
    return _seeded_recursive(values, length, 1.0 / length)


def super_smoother_values(values: np.ndarray, length: float) -> np.ndarray:
    """Ehlers' Super Smoother Filter.

    A 2-pole low-pass with far less lag than an EMA of the same critical
    period. See :func:`zeonta.super_smoother` for the full formula and
    its own reference; this raw-array form is shared with the Ehlers
    cycle tools in :mod:`zeonta.oscillators` that apply it as a
    pre-processing low-pass stage rather than as their own final output —
    including at a non-integer ``length`` such as half a caller's own
    period, which the formula (an exponential/cosine of ``length``) has
    no trouble with even though the public :func:`zeonta.super_smoother`
    only ever passes it a whole number of bars.
    """
    size = values.shape[0]
    a1 = np.exp(-1.414 * np.pi / length)
    b1 = 2.0 * a1 * np.cos(1.414 * np.pi / length)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1.0 - c2 - c3

    result = np.full(size, np.nan, dtype="float64")
    prev_price = np.nan
    f1 = np.nan
    f2 = np.nan

    for i in range(size):
        price = values[i]
        if not np.isfinite(price):
            # Hold the last filtered value through a gap rather than
            # poisoning the recursion, the same convention ema_values() uses.
            result[i] = f1
            continue
        if not (np.isfinite(f1) and np.isfinite(f2) and np.isfinite(prev_price)):
            filtered = price
        else:
            filtered = c1 * (price + prev_price) / 2.0 + c2 * f1 + c3 * f2
        result[i] = filtered
        f2 = f1
        f1 = filtered
        prev_price = price

    return result
