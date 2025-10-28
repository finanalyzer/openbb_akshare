"""Akshare Fund Holdings Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from openbb_akshare.standard_models.fund_holdings import (
    FundHoldingsData,
    FundHoldingsQueryParams,
)
from openbb_akshare.utils.helpers import ak_fund_portfolio_hold_em
from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class AkshareFundHoldingsQueryParams(FundHoldingsQueryParams):
    """FMP Fund Holdings Query.

    Source: https://fundf10.eastmoney.com/ccmx_000001.html
    """

    date: Optional[Union[str, dateType]] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " Entering a date will attempt to return the NPORT-P filing for the entered date."
        + " For Provider Akshare, only the year of date functions."
        + " Use the holdings_date command/endpoint to find available filing dates for the Fund.",
        default="2024-01-01",
    )
    use_cache: Optional[bool] = Field(
        default=True,
        description="Whether or not to use cache. If True, cache will store for two days.",
    )


class AkshareFundHoldingsData(FundHoldingsData):
    """FMP Fund Holdings Data."""

    __alias_dict__ = {
        "name": "股票名称",
        "balance": "持股数",
        "value": "持仓市值",
        "weight": "占净值比例",
        "acceptance_datetime": "季度",
    }

    balance: Optional[ForceInt] = Field(
        description="The balance of the holding, in shares or units.", default=None
    )
    value: Optional[float] = Field(
        description="The value of the holding, in dollars.",
        default=None,
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    weight: Optional[float] = Field(
        description="The weight of the holding, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    acceptance_datetime: Optional[str] = Field(
        description="The acceptance datetime of the filing.",
        default=None,
    )

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        return float(v) if v else None

    @field_validator("balance", "name", "symbol", "value")
    @classmethod
    def replace_empty(cls, v):
        """Replace empty strings and 0s with None."""
        if isinstance(v, str):
            return v if v not in ("", "0", "-") else None
        if isinstance(v, (float, int)):
            return v if v and v not in (0.0, 0) else None
        return v if v else None


class AkshareFundHoldingsFetcher(
    Fetcher[
        AkshareFundHoldingsQueryParams,
        List[AkshareFundHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AkshareFundHoldingsQueryParams:
        """Transform the query."""
        try:
            params["symbol"] = params["symbol"].split(",")[0].split(".")[0]
        except Exception:
            raise Exception("Please enter a valid symbol")
        return AkshareFundHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AkshareFundHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from Akshare."""
        try:
            if isinstance(query.date, str):
                query.date = datetime.strptime(query.date, "%Y-%m-%d")
            fund_portfolio_hold_em_df = ak_fund_portfolio_hold_em(
                symbol=query.symbol,
                year=str(query.date.year),
                db_path="etf_fund_holdings",
                use_cache=query.use_cache,
            )
        except Exception:
            raise Exception(
                f"Error occurred while fetching data for symbol: {query.symbol},Akshare don't support this symbol"
            )
        fund_portfolio_hold_em_df.drop(["股票代码", "序号", "code"], axis=1, inplace=True)

        return fund_portfolio_hold_em_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AkshareFundHoldingsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AkshareFundHoldingsData]:
        """Return the transformed data."""
        # Limited to one alias per field, so we need to do these here.
        for i in data:
            if "SH" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("SH", "") + ".SS"
            elif "SZ" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("SZ", "") + ".SZ"
            elif "OF" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("OF", "") + ".OF"
            elif "BJ" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("BJ", "") + ".BJ"
        return [AkshareFundHoldingsData.model_validate(d) for d in data]
