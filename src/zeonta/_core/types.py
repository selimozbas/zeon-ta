"""Shared type aliases used across the public API."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

#: Anything accepted as a price/volume input by every public indicator.
ArrayLike = pd.Series | np.ndarray | Sequence[float]

#: Numeric parameter that may be integer or fractional (multipliers, std devs).
Number = int | float

__all__ = ["ArrayLike", "Number"]
