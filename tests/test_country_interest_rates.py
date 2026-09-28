"""Test cases for the Country Interest Rates model."""

from datetime import date

import pytest
from openbb import obb


@pytest.mark.parametrize("country", ["china", "united_states"])
@pytest.mark.parametrize("maturity", ["2y", "10y", "30y"])
def test_country_interest_rates(country, maturity):
    """Daily yields arrive as decimals, in date order, inside the window."""
    df = obb.economy.interest_rates(
        provider="akshare",
        country=country,
        maturity=maturity,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    ).to_dataframe()
    assert len(df) > 200, f"expected a year of daily yields, got {len(df)} rows"
    assert df.index.is_monotonic_increasing
    assert df.index.min().year == 2024 and df.index.max().year == 2024
    assert df["value"].between(0, 0.1).all(), df["value"].describe()
    assert (df["country"] == country).all()
