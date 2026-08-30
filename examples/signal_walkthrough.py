"""How a signal built from more than one indicator typically gets assembled.

This combines a trend read (SuperTrend's own direction flip) with a momentum
confirmation (RSI back above its own midline) into one boolean column — the
shape most simple rule-based signals take, regardless of which two indicators
go into it. This is illustrative of *how to wire indicators together*, not a
trading strategy: it has no position sizing, no risk management, and has not
been backtested for profitability. Do not trade on it as-is.

Run from the repository root:

    python examples/signal_walkthrough.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import zeonta

DATA = Path(__file__).resolve().parent.parent / "tests" / "data" / "ohlcv.csv"


def load_ohlcv() -> pd.DataFrame:
    """300 daily OHLCV bars with a DatetimeIndex — the same fixture the tests use."""
    frame = pd.read_csv(DATA, parse_dates=["date"]).set_index("date")
    return frame.astype("float64")


def build_signal(df: pd.DataFrame) -> pd.DataFrame:
    """Combine a SuperTrend direction flip with an RSI momentum confirmation."""
    supertrend = zeonta.supertrend(df["high"], df["low"], df["close"], length=10, multiplier=3.0)
    rsi = zeonta.rsi(df["close"], length=14)

    direction = supertrend["SUPERTd_10_3.0"]
    flipped_bullish = (direction == 1.0) & (direction.shift(1) == -1.0)
    rsi_confirms = rsi > 50.0

    signal = pd.DataFrame(index=df.index)
    signal["close"] = df["close"]
    signal["supertrend_direction"] = direction
    signal["rsi_14"] = rsi
    signal["entry_signal"] = flipped_bullish & rsi_confirms
    return signal


def main() -> None:
    """Build the signal and print where it fired."""
    df = load_ohlcv()
    signal = build_signal(df)

    triggered = signal[signal["entry_signal"]]
    print(f"Entry signal fired on {len(triggered)} of {len(signal)} bars.\n")
    print("Bars where it fired:")
    print(triggered)

    print("\nLast 10 bars of context:")
    print(signal.tail(10))


if __name__ == "__main__":
    main()
