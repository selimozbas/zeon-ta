"""Chaining the .zta accessor to build a feature table for further analysis.

Each `.zta` call routes to the exact same functional code — the point here is
showing how naturally that reads when you're assembling several indicators
into one DataFrame at once, the way a feature-engineering step for a model or
a screener typically looks. No trading strategy or signal logic is implied by
anything computed here.

Run from the repository root:

    python examples/accessor_pipeline.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import zeonta  # noqa: F401  (registers the .zta accessor)

DATA = Path(__file__).resolve().parent.parent / "tests" / "data" / "ohlcv.csv"


def load_ohlcv() -> pd.DataFrame:
    """300 daily OHLCV bars with a DatetimeIndex — the same fixture the tests use."""
    frame = pd.read_csv(DATA, parse_dates=["date"]).set_index("date")
    return frame.astype("float64")


def build_feature_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per bar, one column per feature.

    Each computed through the accessor and assembled with plain pandas
    assignment.
    """
    features = pd.DataFrame(index=df.index)

    features["close"] = df["close"]
    features["rsi_14"] = df.zta.rsi(length=14)
    features["natr_14"] = df.zta.natr(length=14)

    macd = df.zta.macd()
    features["macd_hist"] = macd["MACDh_12_26_9"]

    supertrend = df.zta.supertrend(length=10, multiplier=3.0)
    features["supertrend_direction"] = supertrend["SUPERTd_10_3.0"]

    bbands = df.zta.bbands(length=20, std=2.0)
    features["bb_percent"] = bbands["BBP_20_2.0"]

    features["efficiency_ratio_10"] = df.zta.efficiency_ratio(length=10)

    return features


def main() -> None:
    """Build the feature table and print a summary."""
    df = load_ohlcv()
    features = build_feature_table(df)

    print("Feature table, last 10 bars:")
    print(features.tail(10))

    print("\nFeature table shape:", features.shape)
    print("\nRows with every feature warmed up:", features.dropna().shape[0])


if __name__ == "__main__":
    main()
