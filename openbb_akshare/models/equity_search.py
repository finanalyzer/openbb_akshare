"""AKShare Equity Search Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field

import logging
from openbb_akshare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)


class AKShareEquitySearchQueryParams(EquitySearchQueryParams):
    """AKShare Equity Search Query.
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )
    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class AKShareEquitySearchData(EquitySearchData):
    """AKShare Equity Search Data."""


class AKShareEquitySearchFetcher(
    Fetcher[
        AKShareEquitySearchQueryParams,
        List[AKShareEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquitySearchQueryParams:
        """Transform the query."""
        return AKShareEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareEquitySearchQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""

        from openbb_akshare.utils.ak_equity_search import get_symbols
        api_key = credentials.get("akshare_api_key") if credentials else ""
        data = get_symbols(query.use_cache, api_key=api_key)
        if query.limit is not None and query.limit > 0: data = data.head(query.limit)

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareEquitySearchQueryParams, data: Dict, **kwargs: Any
    ) -> List[AKShareEquitySearchData]:
        """Transform the data to the standard format."""

        if query.query:
            filtered = [
                d for d in data
                if query.query in d.get('name', '') or query.query in d.get('symbol', '')
            ]
            logger.info(f"Searching for {query.query} and found {len(filtered)} results.")
            return [AKShareEquitySearchData.model_validate(d) for d in filtered]

        return [AKShareEquitySearchData.model_validate(d) for d in data]
