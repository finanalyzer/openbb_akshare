"""AKShare Equity Quote Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field
import logging
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_akshare import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)

class AKShareEquityQuoteQueryParams(EquityQuoteQueryParams):
    """AKShare Equity Quote Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class AKShareEquityQuoteData(EquityQuoteData):
    """AKShare Equity Quote Data."""

    __alias_dict__ = {
        "symbol": "代码",
        "name": "名称",
        "last_price": "最新价",
        "open": "今开",
        "high": "最高",
        "low": "最低",
        "prev_close": "昨收",
        "volume": "成交量",
        "turnover": "成交额",
        "change": "涨跌额",
        "change_percent": "涨跌幅",
        "amplitude": "振幅",
        "turnover_rate": "换手率",
        "pe_ratio": "市盈率",
        "pb_ratio": "市净率",
    }


class AKShareEquityQuoteFetcher(
    Fetcher[AKShareEquityQuoteQueryParams, List[AKShareEquityQuoteData]]
):
    """AKShare Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquityQuoteQueryParams:
        """Transform the query."""
        return AKShareEquityQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from AKShare."""
        # pylint: disable=import-outside-toplevel
        import pandas as pd

        api_key = credentials.get("akshare_api_key", "") if credentials else ""

        symbols = query.symbol.split(",")
        all_data = []

        if not api_key:
            logger.error("AKShare requires an API key.")
            return all_data

        def get_one(symbol, api_key: str, use_cache) -> pd.DataFrame:
            """Get the data for one ticker symbol."""
            quote = pd.DataFrame()
            symbol_b, symbol_f, market = normalize_symbol(symbol)

            if market == "HK":
                symbol_xq = symbol_b
            else:
                symbol_xq = f"{market}{symbol_b}"

            logger.info(f"Fetching data for symbol: {symbol_xq}")

            import akshare as ak

            ak.stock.cons.xq_a_token = api_key
            stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol=symbol_xq)

            if stock_individual_spot_xq_df.empty:
                return pd.DataFrame([{"symbol": symbol, "error": "Symbol not found"}])
            else:
                data = stock_individual_spot_xq_df.set_index("item")
                #logger.info(f"Fetched data for symbol: {data}")
                return data.T

        for symbol in symbols:
            try:        
                data = get_one(symbol, api_key=api_key, use_cache=query.use_cache)
                all_data.append(data.to_dict(orient="records")[0])
                
            except Exception as e:
                print(f"Error fetching data for symbol {symbol}: {e}")
                continue

        return all_data

    @staticmethod
    def transform_data(
        query: AKShareEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareEquityQuoteData]:
        """Transform the data."""
        return [AKShareEquityQuoteData.model_validate(d) for d in data]
