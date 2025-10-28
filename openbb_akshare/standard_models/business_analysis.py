"""Equity Business Analysis Standard Model."""

from datetime import datetime
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class BusinessAnalysisQueryParams(QueryParams):
    """Business Analysis Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class BusinessAnalysisData(Data):
    """Business Analysis Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    report_date: Optional[datetime] = Field(
        default=None,
        description="The report date for the financial data, e.g., '2024-09-30'.",
    )
    main_composition: Optional[str] = Field(
        default=None,
        description="The main composition or product of the financial data, e.g., '茅台酒' (Moutai liquor).",
    )
