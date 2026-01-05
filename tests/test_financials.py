import pytest
import pandas as pd
from openbb import obb

symbols = ["600325", "600028","600036","600048","01088"]

@pytest.mark.parametrize("symbol", symbols)
@pytest.mark.parametrize("period_t", ["annual", "quarter"])
@pytest.mark.parametrize("limit", [3,5,7,10])
def test_balance_sheet(symbol, period_t, limit, default_provider):
    balance_df = obb.equity.fundamental.balance(symbol=symbol, period=period_t, limit=limit, provider=default_provider).to_dataframe()
    assert not balance_df.empty
    # Check that we get at most the requested limit (some symbols may have less data available)
    assert len(balance_df) <= limit
    assert len(balance_df) > 0

@pytest.mark.parametrize("symbol", symbols)
@pytest.mark.parametrize("period_t", ["annual", "quarter"])
@pytest.mark.parametrize("limit", [3,5,7,10])
def test_income(symbol, period_t, limit, default_provider):
    income_df = obb.equity.fundamental.income(symbol=symbol, period=period_t, limit=limit, provider=default_provider).to_dataframe()
    assert not income_df.empty
    # Check that we get at most the requested limit (some symbols may have less data available)
    assert len(income_df) <= limit
    assert len(income_df) > 0

@pytest.mark.parametrize("symbol", symbols)
@pytest.mark.parametrize("period_t", ["annual", "quarter"])
@pytest.mark.parametrize("limit", [3,5,7,10])
def test_cash_flow(symbol, period_t, limit, default_provider):
    cash_flow_df = obb.equity.fundamental.cash(symbol=symbol, period=period_t, limit=limit, provider=default_provider).to_dataframe()
    assert not cash_flow_df.empty
    # Check that we get at most the requested limit (some symbols may have less data available)
    assert len(cash_flow_df) <= limit
    assert len(cash_flow_df) > 0
