"""Two-asset comparisons: correlation, beta, and a causal lead-lag transform.

zeonta.cross_asset holds the only functions in this library that take *two
independent* price series instead of one asset's own OHLCV — which is exactly
why they live outside the indicator registry and the `.zta` accessor: every
registered indicator assumes a single asset's own columns, and a second,
independent series doesn't fit that contract.

The repository ships only one symbol's OHLCV fixture, so this script builds a
second, clearly synthetic series from it (not a real second asset) purely to
have two inputs to compare. Swap in your own two real series to use this for
real work.

Run from the repository root:

    python examples/cross_asset.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from zeonta.cross_asset import beta, correlation, wavelet_lead_lag

DATA = Path(__file__).resolve().parent.parent / "tests" / "data" / "ohlcv.csv"


def load_close() -> pd.Series:
    """300 daily closes with a DatetimeIndex — the same fixture the tests use."""
    frame = pd.read_csv(DATA, parse_dates=["date"]).set_index("date")
    return frame["close"].astype("float64")


def main() -> None:
    """Build a synthetic second asset and compare it against the first."""
    asset_a = load_close()

    # A synthetic "second asset": asset_a's own returns, damped and lagged by
    # 3 bars, plus independent noise - just enough structure for correlation,
    # beta and lead-lag to have something real to find, without pretending
    # this is genuine market data for a second symbol.
    rng = np.random.default_rng(0)
    noise = rng.normal(scale=0.3, size=len(asset_a))
    asset_b = asset_a.shift(3).bfill() * 0.6 + 40.0 + noise

    print("--- Rolling correlation ---")
    corr = correlation(asset_a, asset_b, length=30)
    print(corr.tail())

    print("\n--- Rolling beta (asset_a's sensitivity to asset_b's returns) ---")
    b = beta(asset_a, asset_b, length=30)
    print(b.tail())

    print("\n--- Causal cross-wavelet lead-lag (period=20 bars) ---")
    lead_lag = wavelet_lead_lag(asset_a, asset_b, period=20)
    print(lead_lag.tail())
    phase = lead_lag["XWT_PHASE"].dropna().iloc[-1]
    leader = "asset_a leads" if phase > 0 else "asset_b leads"
    print(f"\nLatest phase: {phase:.4f} rad -> {leader}")


if __name__ == "__main__":
    main()
