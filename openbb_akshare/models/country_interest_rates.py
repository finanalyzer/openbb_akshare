"""AKShare Country Interest Rates Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.country_interest_rates import (
    CountryInterestRatesData,
    CountryInterestRatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

# The column prefix each country carries in ak.bond_zh_us_rate.
COUNTRY_COLUMN_PREFIX = {
    "china": "中国国债收益率",
    "united_states": "美国国债收益率",
}

# The column suffix each maturity carries in ak.bond_zh_us_rate.
MATURITY_COLUMN_SUFFIX = {
    "2y": "2年",
    "5y": "5年",
    "10y": "10年",
    "30y": "30年",
}


class AKShareCountryInterestRatesQueryParams(CountryInterestRatesQueryParams):
    """AKShare Country Interest Rates Query.

    Source: https://data.eastmoney.com/cjsj/zmgzsyl.html
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": False,
            "choices": list(COUNTRY_COLUMN_PREFIX),
        },
        "maturity": {
            "multiple_items_allowed": False,
            "choices": list(MATURITY_COLUMN_SUFFIX),
        },
    }

    country: Literal["china", "united_states"] = Field(
        default="united_states",
        description="Country whose government bond yield is returned.",
    )
    maturity: Literal["2y", "5y", "10y", "30y"] = Field(
        default="10y",
        description="Maturity of the government bond whose yield is returned.",
    )


class AKShareCountryInterestRatesData(CountryInterestRatesData):
    """AKShare Country Interest Rates Data."""


class AKShareCountryInterestRatesFetcher(
    Fetcher[
        AKShareCountryInterestRatesQueryParams,
        List[AKShareCountryInterestRatesData],
    ]
):
    """Daily government bond yields from the East Money China-US yield table."""

    # The provider's api_key is the Xueqiu token used only by the equity
    # profile fetcher; this endpoint is public.
    require_credentials = False

    @staticmethod
    def transform_query(
        params: Dict[str, Any],
    ) -> AKShareCountryInterestRatesQueryParams:
        """Transform the query params."""
        return AKShareCountryInterestRatesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareCountryInterestRatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        # pylint: disable=import-outside-toplevel
        import akshare as ak
        import pandas as pd

        start = query.start_date.strftime("%Y%m%d") if query.start_date else "19901219"
        raw = ak.bond_zh_us_rate(start_date=start)
        column = (
            COUNTRY_COLUMN_PREFIX[query.country]
            + MATURITY_COLUMN_SUFFIX[query.maturity]
        )
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(raw["日期"]).dt.date,
                "value": raw[column] / 100,
                "country": query.country,
            }
        ).dropna(subset=["value"])
        if query.start_date:
            df = df[df["date"] >= query.start_date]
        if query.end_date:
            df = df[df["date"] <= query.end_date]
        if df.empty:
            raise EmptyDataError()
        return df.sort_values("date").to_dict("records")

    @staticmethod
    def transform_data(
        query: AKShareCountryInterestRatesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareCountryInterestRatesData]:
        """Return the transformed data."""
        return [AKShareCountryInterestRatesData.model_validate(d) for d in data]
