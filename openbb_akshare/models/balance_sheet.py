"""AKShare Balance Sheet Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)


class AKShareBalanceSheetQueryParams(BalanceSheetQueryParams):
    """AKShare Balance Sheet Query.

    Source: https://akshare.akfamily.xyz/data/stock/stock.html#id180
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


class AKShareBalanceSheetData(BalanceSheetData):
    """AKShare Balance Sheet Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "股东权益": "TOTAL_EQUITY",
        "总负债": "TOTAL_LIABILITIES",
        "总资产": "TOTAL_ASSETS"
    }

    总权益: Optional[float] = Field(
        default=None,
        description="总权益.",
    )
    负债总额: Optional[float] = Field(
        default=None,
        description="负债总额.",
    )
    总资产: Optional[float] = Field(
        default=None,
        description="总资产.",
    )

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class AKShareBalanceSheetFetcher(
    Fetcher[
        AKShareBalanceSheetQueryParams,
        list[AKShareBalanceSheetData],
    ]
):
    """AKShare Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AKShareBalanceSheetQueryParams:
        """Transform the query parameters."""
        return AKShareBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareBalanceSheetQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the AKShare endpoints."""
        api_key = credentials.get("akshare_api_key") if credentials else ""
        # pylint: disable=import-outside-toplevel
        limit = query.limit if query.limit is not None else 5
        em_df = get_data(query.symbol, query.period, query.use_cache, api_key=api_key, limit=limit)
        return em_df.head(limit).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareBalanceSheetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AKShareBalanceSheetData]:
        """Transform the data."""
        return [AKShareBalanceSheetData.model_validate(d) for d in data]

def get_data(symbol: str, period: Literal["annual", "quarter"] = "annual", use_cache: bool = True, api_key:str="", limit:int = 5) -> pd.DataFrame:
    from openbb_akshare import project_name
    from mysharelib.blob_cache import BlobCache
    cache = BlobCache(table_name="balance_sheet", project=project_name)
    logger.info(f"Fetching balance sheet data for {symbol} with limit {limit} and use_cache={use_cache}")
    return cache.load_cached_data(symbol, period, use_cache, get_ak_data, api_key, limit)

def get_ak_data(symbol: str, period: Literal["annual", "quarter"] = "annual", api_key : Optional[str] = "", limit:int = 5) -> pd.DataFrame:
    from openbb_akshare.utils.ak_balance_sheet import ak_stock_balance_sheet

    logger.info(f"Getting balance sheet data for {symbol} with limit {limit}")
    return ak_stock_balance_sheet(symbol, limit, period)
