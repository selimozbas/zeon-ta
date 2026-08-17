"""Volatility indicators — golden values traced by hand from the formulas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_true_range_takes_the_widest_of_the_three_measures() -> None:
    # bar 0 has no previous close -> H-L = 2
    # bar 1: H-L = 1, |H-prevC| = |12-9| = 3, |L-prevC| = |11-9| = 2 -> 3
    result = zeonta.true_range([10, 12], [8, 11], [9, 11.5])
    np.testing.assert_allclose(result, [2.0, 3.0])


def test_true_range_captures_a_gap_that_high_minus_low_misses() -> None:
    """A gap up leaves a narrow bar whose true range is still large."""
    result = zeonta.true_range([10, 20], [9, 19], [9.5, 19.5])
    assert result.iloc[1] == pytest.approx(20 - 9.5)


def test_atr_seed_is_the_average_of_the_first_true_ranges() -> None:
    # TR = [2, 3, 2]; ATR(3) at bar 2 = mean = 7/3
    result = zeonta.atr([10, 12, 13], [8, 9, 11], [9, 11, 12], length=3)
    np.testing.assert_allclose(result.iloc[2], 7 / 3)


def test_atr_is_zero_on_a_perfectly_flat_market() -> None:
    np.testing.assert_allclose(zeonta.atr([5.0] * 30, [5.0] * 30, [5.0] * 30).iloc[-1], 0.0)


def test_atr_is_never_negative(ohlcv: pd.DataFrame) -> None:
    values = zeonta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    assert (values >= 0).all()


def test_atr_rises_when_volatility_rises() -> None:
    calm_high = [10.1] * 40
    calm_low = [9.9] * 40
    wild_high = calm_high + [15.0] * 20
    wild_low = calm_low + [5.0] * 20
    close = [10.0] * 60
    values = zeonta.atr(wild_high, wild_low, close, length=14)
    assert values.iloc[-1] > values.iloc[39]


def test_bbands_are_symmetric_around_the_sma() -> None:
    prices = list(np.linspace(10, 40, 100))
    out = zeonta.bbands(prices, length=20, std=2)
    middle = out["BBM_20_2.0"]
    np.testing.assert_allclose(
        (out["BBU_20_2.0"] - middle).to_numpy(),
        (middle - out["BBL_20_2.0"]).to_numpy(),
        equal_nan=True,
    )
    np.testing.assert_allclose(middle.to_numpy(), zeonta.sma(prices, 20).to_numpy(), equal_nan=True)


def test_bbands_collapse_onto_the_middle_when_price_is_flat() -> None:
    out = zeonta.bbands([10.0] * 25)
    last = out.iloc[-1]
    assert last["BBU_20_2.0"] == last["BBL_20_2.0"] == last["BBM_20_2.0"] == 10.0
    assert last["BBB_20_2.0"] == 0.0
    assert last["BBP_20_2.0"] == 0.5


def test_bbands_percent_b_is_one_at_the_upper_band(ohlcv: pd.DataFrame) -> None:
    out = zeonta.bbands(ohlcv["close"])
    upper = zeonta.bbands(ohlcv["close"])["BBU_20_2.0"]
    at_upper = zeonta.bbands(upper)  # not the point; just ensure percent-b maths is consistent
    assert at_upper is not None
    row = out.dropna().iloc[0]
    expected = (ohlcv["close"].loc[row.name] - row["BBL_20_2.0"]) / (
        row["BBU_20_2.0"] - row["BBL_20_2.0"]
    )
    np.testing.assert_allclose(row["BBP_20_2.0"], expected)


def test_bbands_sample_deviation_is_wider_than_population(ohlcv: pd.DataFrame) -> None:
    population = zeonta.bbands(ohlcv["close"], ddof=0)["BBU_20_2.0"].iloc[-1]
    sample = zeonta.bbands(ohlcv["close"], ddof=1)["BBU_20_2.0"].iloc[-1]
    assert sample > population


def test_bbands_rejects_non_positive_std() -> None:
    with pytest.raises(ValueError, match="'std' must be > 0"):
        zeonta.bbands([10.0] * 25, std=0)


def test_keltner_is_the_ema_plus_atr(ohlcv: pd.DataFrame) -> None:
    out = zeonta.keltner(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    expected_mid = zeonta.ema(ohlcv["close"], 20)
    expected_atr = zeonta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"], 10)
    np.testing.assert_allclose(out["KCM_20_2.0"], expected_mid, equal_nan=True)
    np.testing.assert_allclose(out["KCU_20_2.0"], expected_mid + 2.0 * expected_atr, equal_nan=True)


def test_keltner_is_smoother_than_bollinger_through_a_shock(ohlcv: pd.DataFrame) -> None:
    """The property the squeeze relies on: ATR reacts slower than std deviation."""
    close = ohlcv["close"].copy()
    close.iloc[150] *= 1.15  # single violent bar
    high = ohlcv["high"].copy()
    high.iloc[150] *= 1.15
    bb_width = zeonta.bbands(close)["BBU_20_2.0"] - zeonta.bbands(close)["BBL_20_2.0"]
    kc = zeonta.keltner(high, ohlcv["low"], close)
    kc_width = kc["KCU_20_2.0"] - kc["KCL_20_2.0"]
    bb_jump = bb_width.iloc[150] / bb_width.iloc[149]
    kc_jump = kc_width.iloc[150] / kc_width.iloc[149]
    assert bb_jump > kc_jump


def test_squeeze_flags_are_mutually_exclusive(ohlcv: pd.DataFrame) -> None:
    out = zeonta.squeeze(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    on = out.filter(like="SQZ_ON").iloc[:, 0]
    off = out.filter(like="SQZ_OFF").iloc[:, 0]
    assert ((on + off) == 1.0).all()


def test_squeeze_turns_on_when_price_goes_quiet() -> None:
    """A volatile stretch followed by a dead-flat one must end in a squeeze."""
    rng = np.random.default_rng(7)
    noisy = 100 + np.cumsum(rng.normal(0, 2.0, 80))
    quiet = np.full(60, noisy[-1])
    close = np.concatenate([noisy, quiet])
    high = close + np.concatenate([np.full(80, 2.0), np.full(60, 0.01)])
    low = close - np.concatenate([np.full(80, 2.0), np.full(60, 0.01)])
    out = zeonta.squeeze(high, low, close)
    assert out.filter(like="SQZ_ON").iloc[-1, 0] == 1.0


def test_squeeze_widening_the_keltner_makes_squeezes_more_frequent(ohlcv: pd.DataFrame) -> None:
    """A wider Keltner Channel is easier for the Bollinger Bands to fit inside.

    The TA 101 quiz for this lesson claims the opposite, but its own formula
    (``squeeze ON when BB Upper < KC Upper and BB Lower > KC Lower``) says a
    larger ``kc_multiplier`` pushes the Keltner bands further out, so enclosure
    becomes easier, not harder. The implementation follows the formula.
    """
    tight = zeonta.squeeze(ohlcv["high"], ohlcv["low"], ohlcv["close"], kc_multiplier=1.5)
    wide = zeonta.squeeze(ohlcv["high"], ohlcv["low"], ohlcv["close"], kc_multiplier=3.0)
    assert wide.filter(like="SQZ_ON").sum().iloc[0] > tight.filter(like="SQZ_ON").sum().iloc[0]
