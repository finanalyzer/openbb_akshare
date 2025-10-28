"""Akshare Equity Business Analysis Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from openbb_akshare.standard_models.business_analysis import (
    BusinessAnalysisData,
    BusinessAnalysisQueryParams,
)
from openbb_akshare.utils.helpers import (
    convert_stock_code_format,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field


class AkshareBusinessAnalysisQueryParams(BusinessAnalysisQueryParams):
    """Akshare Business Analysis Query.

    Source: https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/Index?type=web&code=SH688041#

    """


class AkshareBusinessAnalysisData(BusinessAnalysisData):
    """Akshare Index Business Analysis Data."""

    __alias_dict__ = {
        "report_date": "报告日期",
        "category_type": "分类类型",
        "main_composition": "主营构成",
        "main_revenue": "主营收入",
        "revenue_ratio": "收入比例",
        "main_cost": "主营成本",
        "cost_ratio": "成本比例",
        "main_profit": "主营利润",
        "profit_ratio": "利润比例",
        "gross_margin": "毛利率",
        "code": "股票代码",
    }
    category_type: Optional[str] = Field(
        default=None,
        description="The category or classification type of the financial data, e.g., '按产品分类' (By product classification).",
    )

    main_revenue: Optional[float] = Field(
        default=None,
        description="The main revenue for the financial period, e.g., 101126021100.0.",
    )

    revenue_ratio: Optional[float] = Field(
        default=None,
        description="The ratio of main revenue to total revenue, e.g., 0.837301.",
    )

    main_cost: Optional[float] = Field(
        default=None,
        description="The main cost associated with the product or business, e.g., NaN (Not available).",
    )

    cost_ratio: Optional[float] = Field(
        default=None,
        description="The ratio of main cost to total cost, e.g., NaN (Not available).",
    )

    main_profit: Optional[float] = Field(
        default=None,
        description="The main profit for the financial period, e.g., NaN (Not available).",
    )

    profit_ratio: Optional[float] = Field(
        default=None,
        description="The ratio of main profit to total profit, e.g., NaN (Not available).",
    )

    gross_margin: Optional[float] = Field(
        default=None,
        description="The gross margin for the financial period, e.g., NaN (Not available).",
    )


class AkshareBusinessAnalysisFetcher(
    Fetcher[
        AkshareBusinessAnalysisQueryParams,
        List[AkshareBusinessAnalysisData],
    ]
):
    """Transform the query, extract and transform the data from the Akshare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AkshareBusinessAnalysisQueryParams:
        """Transform the query params."""
        params["symbol"] = convert_stock_code_format(params.get("symbol", ""))
        return AkshareBusinessAnalysisQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AkshareBusinessAnalysisQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Akshare endpoint."""
        # pylint: disable=import-outside-toplevel
        import akshare as ak

        stock_zygc_em_df = ak.stock_zygc_em(symbol=query.symbol)
        stock_zygc_em_df["symbol"] = query.symbol
        stock_zygc_em_df["分类类型"] = np.where(
            pd.isna(stock_zygc_em_df["分类类型"]),
            "按行业分类",
            stock_zygc_em_df["分类类型"],
        )
        stock_zygc_em_df = stock_zygc_em_df.where(~stock_zygc_em_df.isna(), None)
        return stock_zygc_em_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AkshareBusinessAnalysisQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AkshareBusinessAnalysisData]:
        """Return the transformed data."""
        for i in data:
            if "SH" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("SH", "") + ".SS"
            elif "SZ" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("SZ", "") + ".SZ"
            elif "OF" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("OF", "") + ".OF"
            elif "BJ" in i["symbol"]:
                i["symbol"] = i["symbol"].replace("BJ", "") + ".BJ"
        return [AkshareBusinessAnalysisData.model_validate(d) for d in data]
