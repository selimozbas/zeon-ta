"""Basic usage examples for zeon-ta.

Runs a handful of indicators — one per category — against the same 300-bar
OHLCV fixture the test suite uses, and prints their tail. No plotting, no
extra dependencies beyond zeon-ta's own (NumPy and pandas); no trading
strategy or signal logic is implied by anything printed here, this is purely
about how to call the library.

Run from the repository root:

    python examples/basic_usage.py
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


def functional_api(df: pd.DataFrame) -> None:
    """Every indicator is a plain function: pass Series in, get Series/DataFrame out."""
    print("\n--- Functional API ---")

    rsi = zeonta.rsi(df["close"], length=14)
    print("\nRSI(14), last 5 bars:")
    print(rsi.tail())

    macd = zeonta.macd(df["close"])
    print("\nMACD (default 12/26/9), last 5 bars:")
    print(macd.tail())

    bands = zeonta.bbands(df["close"], length=20, std=2)
    print("\nBollinger Bands(20, 2), last 5 bars:")
    print(bands.tail())


def accessor_api(df: pd.DataFrame) -> None:
    """The .zta accessor routes to the exact same code — same numbers, less typing."""
    print("\n--- DataFrame accessor (.zta) ---")

    supertrend = df.zta.supertrend(length=10, multiplier=3)
    print("\nSuperTrend(10, 3.0), last 5 bars:")
    print(supertrend.tail())

    vortex = df.zta.vortex(length=14)
    print("\nVortex(14), last 5 bars:")
    print(vortex.tail())


def multi_line_output(df: pd.DataFrame) -> None:
    """Multi-line indicators return a DataFrame; pick columns like any other."""
    print("\n--- Multi-line output ---")

    aroon = zeonta.aroon(df["high"], df["low"], length=25)
    up_trending = aroon["AROONOSC_25"] > 50
    print(f"\nAroon Oscillator(25) > 50 on {int(up_trending.sum())} of {len(aroon)} bars")


def discovery() -> None:
    """list_indicators() enumerates every registered indicator with its inputs,
    parameters, output columns, and — for the minority that cite one — the
    external source its formula was verified against."""
    print("\n--- Discovery ---")

    table = zeonta.list_indicators()
    print(f"\n{len(table)} indicators registered, across categories:")
    print(table["category"].value_counts())

    print("\nA volume-category sample:")
    print(table[table["category"] == "volume"][["name", "summary"]].to_string(index=False))


def main() -> None:
    df = load_ohlcv()
    print(f"Loaded {len(df)} bars from {DATA.name}, {df.index[0].date()} to {df.index[-1].date()}")

    functional_api(df)
    accessor_api(df)
    multi_line_output(df)
    discovery()


if __name__ == "__main__":
    main()
