"""Akshare ETF Holdings Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_akshare.utils.helpers import ak_fund_portfolio_hold_em
from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class AkshareEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """FMP ETF Holdings Query.

    Source: https://fundf10.eastmoney.com/ccmx_000001.html
    """

    year: Optional[str] = Field(
        description=QUERY_DESCRIPTIONS.get("year", "")
        + " Entering a year will attempt to return the NPORT-P filing for the entered year."
        + " For Provider Akshare, only the year of date functions."
        + " Use the holdings_date command/endpoint to find available filing year for the ETF.",
        default="2024",
    )
    quarter: Optional[str] = Field(
        description="Enter the quarter for which you want to retrieve the ETF holdings data.",
        default="4",
    )
    use_cache: Optional[bool] = Field(
        default=True,
        description="Whether or not to use cache. If True, cache will store for two days.",
    )


class AkshareEtfHoldingsData(EtfHoldingsData):
    """FMP ETF Holdings Data."""

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


class AkshareEtfHoldingsFetcher(
    Fetcher[
        AkshareEtfHoldingsQueryParams,
        List[AkshareEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AkshareEtfHoldingsQueryParams:
        """Transform the query."""
        try:
            params["symbol"] = params["symbol"].split(",")[0].split(".")[0]
        except:
            raise Exception("Please enter a valid symbol")
        return AkshareEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AkshareEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from Akshare."""
        try:
            fund_portfolio_hold_em_df = ak_fund_portfolio_hold_em(
                symbol=query.symbol,
                year=query.year,
                db_path="etf_fund_holdings",
                use_cache=query.use_cache,
            )
        except:
            raise Exception(
                f"Error occurred while fetching data for symbol: {query.symbol},Akshare don't support this symbol"
            )
        fund_portfolio_hold_em_df.drop(["股票代码", "序号", "code"], axis=1, inplace=True)
        fund_portfolio_hold_em_df = fund_portfolio_hold_em_df[fund_portfolio_hold_em_df["季度"].str.contains(str(query.quarter) + "季度")]
        return fund_portfolio_hold_em_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AkshareEtfHoldingsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AkshareEtfHoldingsData]:
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
        return [AkshareEtfHoldingsData.model_validate(d) for d in data]
