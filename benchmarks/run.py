"""Timing benchmark for every registered indicator, at increasing data sizes.

Purpose: find real bottlenecks before optimizing anything, rather than
guessing. Every indicator in the registry is timed against synthetic OHLCV
data at 10k, 100k and 1M bars.

Run from the repository root:

    python benchmarks/run.py                    # all sizes
    python benchmarks/run.py --sizes 10000       # just one size, for a quick pass
    python benchmarks/run.py --sort name         # sort by name instead of by time
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from zeonta._core import IndicatorSpec, iter_specs

DEFAULT_SIZES = [10_000, 100_000, 1_000_000]


def synthetic_ohlcv(size: int, seed: int = 0) -> pd.DataFrame:
    """A deterministic random walk with realistic OHLC ordering and no zero ranges."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(loc=0.0, scale=0.5, size=size)
    close = 100.0 + np.cumsum(steps)
    close = np.maximum(close, 1.0)  # keep strictly positive
    spread = np.abs(rng.normal(loc=0.3, scale=0.15, size=size)) + 0.05
    high = close + spread
    low = close - spread
    open_ = low + (high - low) * rng.random(size)
    volume = rng.integers(1_000, 1_000_000, size=size).astype("float64")
    index = pd.date_range("2000-01-01", periods=size, freq="min")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=index
    )


def time_indicator(spec: IndicatorSpec, frame: pd.DataFrame) -> float:
    series = [frame[field] for field in spec.inputs]
    start = time.perf_counter()
    spec.func(*series)
    return time.perf_counter() - start


def run(sizes: list[int]) -> pd.DataFrame:
    specs = list(iter_specs())
    rows: list[dict[str, object]] = []
    for size in sizes:
        frame = synthetic_ohlcv(size)
        print(f"\n--- {size:,} bars ---", file=sys.stderr)
        for spec in specs:
            elapsed = time_indicator(spec, frame)
            rows.append(
                {
                    "name": spec.name,
                    "category": spec.category,
                    "bars": size,
                    "seconds": elapsed,
                    "bars_per_sec": size / elapsed if elapsed > 0 else float("inf"),
                }
            )
            print(f"  {spec.name:<22} {elapsed:8.4f}s", file=sys.stderr)
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark every registered indicator.")
    parser.add_argument(
        "--sizes", type=int, nargs="+", default=DEFAULT_SIZES, help="Bar counts to test."
    )
    parser.add_argument(
        "--sort", choices=["time", "name"], default="time", help="How to order the summary table."
    )
    parser.add_argument("--csv", type=str, default=None, help="Optional path to write raw results.")
    args = parser.parse_args()

    results = run(args.sizes)
    if args.csv:
        results.to_csv(args.csv, index=False)
        print(f"\nWrote raw results to {args.csv}", file=sys.stderr)

    largest = results[results["bars"] == max(args.sizes)].copy()
    if args.sort == "time":
        largest = largest.sort_values("seconds", ascending=False)
    else:
        largest = largest.sort_values("name")

    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", 120)
    print(f"\n=== Summary at {max(args.sizes):,} bars, slowest first ===\n")
    print(
        largest[["name", "category", "seconds", "bars_per_sec"]].to_string(
            index=False, float_format=lambda v: f"{v:,.4f}"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
