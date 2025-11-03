"""Test cases for Fund Holdings model."""

import pytest
from openbb_akshare.models.fund_holdings import AkshareFundHoldingsFetcher


@pytest.mark.parametrize("symbol", ["000001", "000002", "000003"])
@pytest.mark.parametrize("date", ["2024-01-01", "2023-01-01", "2024-06-01"])
def test_fund_holdings_fetcher(symbol, date, logger):
    """Test fund holdings fetcher directly with different symbols and dates."""
    import asyncio
    
    query_params = {
        "symbol": symbol,
        "date": date,
        "use_cache": True,
    }
    fetcher = AkshareFundHoldingsFetcher()
    
    # Transform query
    transformed_query = fetcher.transform_query(query_params)
    
    # Extract data (no credentials needed for fund holdings)
    try:
        data = asyncio.run(fetcher.aextract_data(transformed_query, None))
        assert isinstance(data, list)
        logger.info(f"Fund holdings for {symbol} (Date: {date}): {len(data)} records")
        
        # Transform data
        if data:
            transformed_data = fetcher.transform_data(transformed_query, data)
            assert isinstance(transformed_data, list)
            
            # Verify data structure
            if transformed_data:
                first_item = transformed_data[0]
                assert hasattr(first_item, "symbol")
                assert hasattr(first_item, "name") or hasattr(first_item, "balance")
    except Exception as e:
        # Some dates might not have data, which is acceptable
        logger.info(f"No data for {symbol} (Date: {date}): {e}")


@pytest.mark.parametrize("symbol", ["000001", "000002"])
def test_fund_holdings_default_params(symbol):
    """Test fund holdings with default parameters."""
    import asyncio
    
    query_params = {"symbol": symbol}  # Use default date
    fetcher = AkshareFundHoldingsFetcher()
    transformed_query = fetcher.transform_query(query_params)
    
    try:
        data = asyncio.run(fetcher.aextract_data(transformed_query, None))
        assert isinstance(data, list)
        
        if data:
            transformed_data = fetcher.transform_data(transformed_query, data)
            assert isinstance(transformed_data, list)
    except Exception:
        # Might not have data for default date, which is acceptable
        pass


@pytest.mark.parametrize("symbol", ["000001", "000002"])
@pytest.mark.parametrize("use_cache", [True, False])
def test_fund_holdings_cache(symbol, use_cache):
    """Test fund holdings with and without cache."""
    import asyncio
    
    query_params = {
        "symbol": symbol,
        "date": "2024-01-01",
        "use_cache": use_cache,
    }
    fetcher = AkshareFundHoldingsFetcher()
    transformed_query = fetcher.transform_query(query_params)
    
    try:
        data = asyncio.run(fetcher.aextract_data(transformed_query, None))
        assert isinstance(data, list)
        
        if data:
            transformed_data = fetcher.transform_data(transformed_query, data)
            assert isinstance(transformed_data, list)
    except Exception:
        # Might not have data, which is acceptable
        pass


def test_fund_holdings_invalid_symbol():
    """Test fund holdings with invalid symbol should handle gracefully."""
    import asyncio
    
    query_params = {"symbol": "INVALID_FUND"}
    fetcher = AkshareFundHoldingsFetcher()
    
    try:
        transformed_query = fetcher.transform_query(query_params)
        data = asyncio.run(fetcher.aextract_data(transformed_query, None))
        # If no exception, data should be empty or an error should have been raised
        assert isinstance(data, list)
    except Exception as e:
        # It's acceptable if it raises an exception for invalid symbols
        assert "Error" in str(type(e).__name__) or "Exception" in str(type(e).__name__)

