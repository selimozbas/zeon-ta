"""Shared fixtures.

``ohlcv`` is a committed 300-bar synthetic series with volatility clustering, so
trend, volatility and squeeze indicators all have real structure to react to.
Being committed (rather than generated per run) means a numeric regression shows
up as a failing assertion instead of flaky noise.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import zeonta
from zeonta._core import IndicatorSpec, iter_specs

DATA = Path(__file__).parent / "data" / "ohlcv.csv"


@pytest.fixture(scope="session")
def ohlcv() -> pd.DataFrame:
    """300 daily OHLCV bars with a ``DatetimeIndex``."""
    frame = pd.read_csv(DATA, parse_dates=["date"]).set_index("date")
    return frame.astype("float64")


@pytest.fixture(params=[item.name for item in iter_specs()])
def spec(request: pytest.FixtureRequest) -> IndicatorSpec:
    """Each registered indicator in turn."""
    return zeonta.get_spec(request.param)
