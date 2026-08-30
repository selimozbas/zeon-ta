"""The indicators that set zeon-ta apart from a typical TA library.

Alongside the standard indicator set (see basic_usage.py), zeon-ta implements
tools most TA libraries don't carry at all: OHLC volatility estimators
standard in quantitative finance, and John Ehlers' cycle-analysis filters.
Every one of them is traced to a specific paper - see each function's own
docstring for the reference.

Run from the repository root:

    python examples/next_gen_indicators.py
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


def volatility_estimators(df: pd.DataFrame) -> None:
    """Four extreme-value OHLC volatility estimators, vs. plain ATR.

    None of them are in the typical TA library toolbox, and all four are
    more statistically efficient than a plain close-to-close standard
    deviation at the same window length.
    """
    print("\n--- OHLC volatility estimators (vs. plain ATR) ---")

    atr = zeonta.atr(df["high"], df["low"], df["close"], length=20)
    parkinson = zeonta.parkinson_volatility(df["high"], df["low"], length=20)
    garman_klass = zeonta.garman_klass_volatility(
        df["open"], df["high"], df["low"], df["close"], length=20
    )
    yang_zhang = zeonta.yang_zhang_volatility(
        df["open"], df["high"], df["low"], df["close"], length=20
    )

    comparison = pd.DataFrame(
        {
            "ATR_20": atr,
            "Parkinson_20": parkinson,
            "GarmanKlass_20": garman_klass,
            "YangZhang_20": yang_zhang,
        }
    )
    print(comparison.tail())


def ehlers_cycle_filters(df: pd.DataFrame) -> None:
    """Ehlers' cycle-analysis family.

    Strips trend and noise to isolate the cycle a plain oscillator would
    otherwise react to indiscriminately.
    """
    print("\n--- Ehlers cycle-analysis filters ---")

    roofed = zeonta.roofing_filter(df["close"], hp_length=48, lp_length=10)
    print("\nRoofing Filter, last 5 bars (feed this into an oscillator instead of raw price):")
    print(roofed.tail())

    sinewave = zeonta.even_better_sinewave(df["close"])
    print("\nEven Better Sinewave, last 5 bars (self-normalized, ranges roughly -1 to 1):")
    print(sinewave.tail())

    cycle = zeonta.cyber_cycle(df["high"], df["low"])
    print("\nCyber Cycle + trigger line, last 5 bars:")
    print(cycle.tail())

    voss = zeonta.voss_predictive_filter(df["close"], period=20, predict=3)
    print("\nVoss Predictive Filter (VOSS leads VOSSFILT), last 5 bars:")
    print(voss.tail())

    reflex = zeonta.reflex_trendflex(df["close"], length=20)
    print("\nReflex (cycle) vs. Trendflex (trend), last 5 bars:")
    print(reflex.tail())


def main() -> None:
    """Run both sections in turn against the same loaded fixture."""
    df = load_ohlcv()
    volatility_estimators(df)
    ehlers_cycle_filters(df)


if __name__ == "__main__":
    main()
