"""AKShare Equity Profile Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from datetime import (date as dateType, datetime)

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field, field_validator
import pandas as pd
from mysharelib.tools import get_timestamp


class AKShareEquityProfileQueryParams(EquityInfoQueryParams):
    """AKShare Equity Profile Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )

class AKShareEquityProfileData(EquityInfoData):
    """AKShare Equity Profile Data."""

    __alias_dict__ = {
        "公司名称": "org_name_cn",
        "公司简介": "org_cn_introduction",
        "主要范围": "main_operation_business",
        "成立日期": "established_date",
        "上市日期": "listed_date",
        "name": "org_name_en",
        "ceo": "chairman",
        "company_url": "org_website",
        "business_address": "reg_address_cn",
        "mailing_address": "office_address_cn",
        "business_phone_no": "telephone",
        "hq_address_postal_code": "postcode",
        "hq_state": "provincial_name",
        "employees": "staff_num",
        "sector": "affiliate_industry",
        "industry_category": "operating_scope",
    }

    公司名称: Optional[str] = Field(
        description="Alias of org_name_cn.",
        default=None,
    )
    公司简介: Optional[str] = Field(
        description="Alias of org_name_cn.",
        default=None,
    )
    主要范围: Optional[str] = Field(
        description="Alias of org_name_cn.",
        default=None,
    )
    上市日期: Optional[dateType|None] = Field(
        default=None, description="Date of the establishment."
    )
    org_name_cn: Optional[str] = Field(
        description="Chinese name of the asset.",
        default=None,
    )
    org_short_name_cn: Optional[str] = Field(
        description="Short Chinese name of the asset.",
        default=None,
    )
    org_short_name_en: Optional[str] = Field(
        description="Short English name of the asset.",
        default=None,
    )
    org_id: Optional[str] = Field(
        description="The number of listed shares outstanding.",
        default=None,
    )
    established_date: Optional[dateType|None] = Field(
        default=None, description="Date of the establishment."
    )
    actual_issue_vol: Optional[int] = Field(
        description="The number of shares in the public float.",
        default=None,
    )
    reg_asset: Optional[float] = Field(
        description=(
            "总股本（股）"),
        default=None,
    )
    issue_price: Optional[float] = Field(
        description="发行价格.",
        default=None,
    )
    currency: Optional[str] = Field(
        description="The currency in which the asset is traded.", default=None
    )

    @field_validator("actual_issue_vol", mode="before", check_fields=False)
    @classmethod
    def validate_actual_issue_vol(cls, v: Optional[int]) -> Optional[int]:
        """Return 0 if it is nan."""
        if v is None or v == "" or pd.isna(v):
            return 0
        else:
            return int(v)

    @field_validator("employees", mode="before", check_fields=False)
    @classmethod
    def validate_employees(cls, v: Optional[int]) -> Optional[int]:
        """Return 0 if it is nan."""
        if v is None or v == "" or pd.isna(v):
            return 0
        else:
            return int(v)

    @field_validator("established_date", mode="before", check_fields=False)
    @classmethod
    def validate_established_date(cls, v):
        """Validate first stock price date."""
        # pylint: disable=import-outside-toplevel
        from datetime import timezone  # noqa
        from openbb_core.provider.utils.helpers import safe_fromtimestamp  # noqa
        if pd.isna(v):
            return None

        return safe_fromtimestamp(get_timestamp(v), tz=timezone.utc).date() if v else None

    @field_validator("上市日期", mode="before", check_fields=False)
    @classmethod
    def validate_first_trade_date(cls, v):
        """Validate first stock price date."""
        # pylint: disable=import-outside-toplevel
        from datetime import timezone  # noqa
        from openbb_core.provider.utils.helpers import safe_fromtimestamp  # noqa
        if pd.isna(v):
            return None

        return safe_fromtimestamp(get_timestamp(v), tz=timezone.utc).date() if v else None


class AKShareEquityProfileFetcher(
    Fetcher[AKShareEquityProfileQueryParams, List[AKShareEquityProfileData]]
):
    """AKShare Equity Profile fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquityProfileQueryParams:
        """Transform the query."""
        return AKShareEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareEquityProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from AKShare."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from warnings import warn

        api_key = credentials.get("akshare_api_key", "") if credentials else ""

        symbols = query.symbol.split(",")
        results = []
        messages: list = []

        async def get_one(symbol, api_key: str | None, use_cache: bool = True):
            from openbb_akshare.utils.fetch_equity_info import fetch_equity_info
            """Get the data for one ticker symbol."""
            try:
                result: dict = {}
                result = fetch_equity_info(symbol, api_key=api_key, use_cache=use_cache).to_dict(orient="records")[0]
                if result:
                    results.append(result)
            except Exception as e:
                messages.append(
                    f"Error getting data for {symbol} -> {e.__class__.__name__}: {e}"
                )

        tasks = [get_one(symbol, api_key=api_key, use_cache=query.use_cache) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if not results and not messages:
            raise EmptyDataError("No data was returned for any symbol")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: AKShareEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareEquityProfileData]:
        """Transform the data."""
        return [AKShareEquityProfileData.model_validate(d) for d in data]
