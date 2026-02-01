"""AKShare Cash Flow Statement Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class AKShareCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """AKShare Cash Flow Statement Query.

    Source: https://finance.yahoo.com/
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


class AKShareCashFlowStatementData(CashFlowStatementData):
    """AKShare Cash Flow Statement Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "reported_currency": "CURRENCY",
        "营业性现金流": "NETCASH_OPERATE",
        "投资性现金流": "NETCASH_INVEST",
        "融资性现金流": "NETCASH_FINANCE",
    }
    营业性现金流: Optional[float] = Field(
        default=None,
        description="营业性现金流.",
    )
    投资性现金流: Optional[float] = Field(
        default=None,
        description="投资性现金流.",
    )
    融资性现金流: Optional[float] = Field(
        default=None,
        description="融资性现金流.",
    )

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class AKShareCashFlowStatementFetcher(
    Fetcher[
        AKShareCashFlowStatementQueryParams,
        list[AKShareCashFlowStatementData],
    ]
):
    """AKShare Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AKShareCashFlowStatementQueryParams:
        """Transform the query parameters."""
        return AKShareCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareCashFlowStatementQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the AKShare endpoints."""
        # pylint: disable=import-outside-toplevel
        api_key = credentials.get("akshare_api_key") if credentials else ""
        limit = query.limit if query.limit is not None else 5
        em_df = get_data(query.symbol, query.period, query.use_cache, api_key=api_key, limit=limit)

        if limit is None:
            return em_df.to_dict(orient="records")
        else:
            return em_df.head(limit).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareCashFlowStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AKShareCashFlowStatementData]:
        """Transform the data."""
        return [AKShareCashFlowStatementData.model_validate(d) for d in data]

def get_data(symbol: str, period: Literal["annual", "quarter"] = "annual", use_cache: bool = True, api_key:str="", limit:int = 5) -> pd.DataFrame:
    from openbb_akshare import project_name
    from mysharelib.blob_cache import BlobCache
    cache = BlobCache(table_name="cash_flow", project=project_name)
    logger.info(f"Fetching cash flow data for {symbol} with limit {limit} and use_cache={use_cache}")
    return cache.load_cached_data(symbol, period, use_cache, get_ak_data, api_key, limit)

def get_ak_data(symbol: str, period: Literal["annual", "quarter"] = "annual", api_key : Optional[str] = "", limit:int = 5) -> pd.DataFrame:
    from openbb_akshare.utils.ak_cash_flow import ak_stock_cash_flow

    logger.info(f"Getting cash flow data for {symbol} with limit {limit}")
    return ak_stock_cash_flow(symbol, limit, period)