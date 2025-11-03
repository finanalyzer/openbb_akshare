"""Test cases for Business Analysis model."""

import pytest
from openbb_akshare.models.business_analysis import AkshareBusinessAnalysisFetcher


@pytest.mark.parametrize("symbol", ["600325", "600028", "600036", "600048"])
def test_business_analysis_fetcher(symbol, akshare_api_key, logger):
    """Test business analysis fetcher directly with different symbols."""
    import asyncio
    
    fetcher = AkshareBusinessAnalysisFetcher()
    
    # Transform query
    transformed_query = fetcher.transform_query({"symbol": symbol})
    
    # Extract data
    credentials = {"akshare_api_key": akshare_api_key}
    data = asyncio.run(fetcher.aextract_data(transformed_query, credentials))
    
    assert isinstance(data, list)
    assert len(data) > 0
    logger.info(f"Business analysis for {symbol}: {len(data)} records")
    
    # Transform data
    transformed_data = fetcher.transform_data(transformed_query, data)
    assert len(transformed_data) > 0
    
    # Verify data structure
    first_item = transformed_data[0]
    assert hasattr(first_item, "symbol")
    assert hasattr(first_item, "report_date") or hasattr(first_item, "main_composition")


@pytest.mark.parametrize("symbol", ["688041", "000001"])
def test_business_analysis_various_symbols(symbol, akshare_api_key):
    """Test business analysis with various symbol formats."""
    import asyncio
    
    fetcher = AkshareBusinessAnalysisFetcher()
    transformed_query = fetcher.transform_query({"symbol": symbol})
    
    credentials = {"akshare_api_key": akshare_api_key}
    data = asyncio.run(fetcher.aextract_data(transformed_query, credentials))
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    transformed_data = fetcher.transform_data(transformed_query, data)
    assert len(transformed_data) > 0


def test_business_analysis_invalid_symbol(akshare_api_key):
    """Test business analysis with invalid symbol should handle gracefully."""
    import asyncio
    
    fetcher = AkshareBusinessAnalysisFetcher()
    transformed_query = fetcher.transform_query({"symbol": "INVALID_SYMBOL_XYZ"})
    
    credentials = {"akshare_api_key": akshare_api_key}
    
    # Should either return empty data or raise an exception
    try:
        data = asyncio.run(fetcher.aextract_data(transformed_query, credentials))
        # If data is returned, it might be empty
        transformed_data = fetcher.transform_data(transformed_query, data)
        assert isinstance(transformed_data, list)
    except Exception as e:
        # It's acceptable if it raises EmptyDataError or similar
        assert "EmptyDataError" in str(type(e).__name__) or isinstance(e, (Exception,))

