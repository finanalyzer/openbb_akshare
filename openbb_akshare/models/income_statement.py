"""AKShare Income Statement Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class AKShareIncomeStatementQueryParams(IncomeStatementQueryParams):
    """AKShare Income Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class AKShareIncomeStatementData(IncomeStatementData):
    """AKShare Income Statement Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "reported_currency": "CURRENCY",
        "总营收": "TOTAL_OPERATE_INCOME",
        "净利润": "PARENT_NETPROFIT"
    }

    reported_currency: Optional[str] = Field(
        default=None,
        description="The currency in which the balance sheet was reported.",
    )
    总营收: Optional[float] = Field(
        default=None,
        description="Total pre-tax income.",
    )
    净利润: Optional[float] = Field(
        default=None,
        description="Income tax expense.",
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class AKShareIncomeStatementFetcher(
    Fetcher[
        AKShareIncomeStatementQueryParams,
        List[AKShareIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareIncomeStatementQueryParams:
        """Transform the query params."""
        return AKShareIncomeStatementQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: AKShareIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        api_key = credentials.get("akshare_api_key") if credentials else ""

        em_df = get_data(query.symbol, query.period, query.use_cache, api_key=api_key, limit=query.limit)

        if query.limit is None:
            return em_df.to_dict(orient="records")
        else:
            return em_df.head(query.limit).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareIncomeStatementData]:
        """Return the transformed data."""
        for result in data:
            result.pop("symbol", None)
            result.pop("cik", None)
        return [AKShareIncomeStatementData.model_validate(d) for d in data]

def get_data(symbol: str, period: Literal["annual", "quarter"] = "annual", use_cache: bool = True, api_key:str="", limit:int = 5) -> pd.DataFrame:
    from openbb_akshare import project_name
    from mysharelib.blob_cache import BlobCache
    cache = BlobCache(table_name="income_statement", project=project_name)
    logger.info(f"Fetching income statement data for {symbol} with limit {limit} and use_cache={use_cache}")
    
    try:
        data = cache.load_cached_data(symbol, period, use_cache, get_income_statement, api_key, limit)
    except NotImplementedError:
        logger.warning("Cached data contained pandas extension dtypes that could not be unpickled; refreshing cache.")
        # Try again without using cache so we regenerate a fresh, safe cache entry
        data = cache.load_cached_data(symbol, period, False, get_income_statement, api_key, limit)

    if data is None:
        return pd.DataFrame()

    # Ensure loaded DataFrame has no pandas extension dtypes (e.g., StringDtype)
    if isinstance(data, pd.DataFrame):
        for col in data.columns:
            if pd.api.types.is_extension_array_dtype(data[col].dtype):
                data[col] = data[col].astype(object)
        data.index = data.index.astype(object)

    return data

def get_income_statement(symbol: str, period: Literal["annual", "quarter"] = "annual", api_key : Optional[str] = "", limit:int = 5) -> pd.DataFrame:
    from openbb_akshare.utils.ak_income_statement import ak_stock_income_statement

    logger.info(f"Getting income statement data for {symbol} with limit {limit}")
    return ak_stock_income_statement(symbol, limit, period)