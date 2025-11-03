"""openbb-akshare router command example."""

import requests
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (ExtraParams, ProviderChoices,
                                                StandardParams)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.app.service.user_service import UserService
from pydantic import BaseModel
from mysharelib.registry import register_widget

router = Router(prefix="")

@register_widget({
    "name": "Company Facts",
    "description": "Get key company information including name, CIK, market cap, total employees, website URL, and more.",
    "category": "Equity",
    "subcategory": "Company Info",
    "type": "table",
    "widgetId": "company_facts",
    "endpoint": "company_facts",
    "gridData": {
        "w": 10,
        "h": 12
    },
    "params": [
        {
            "type": "endpoint",
            "paramName": "ticker",
            "label": "Symbol",
            "value": "600325",
            "description": "Ticker to get company facts for (Free tier: AAPL, MSFT, TSLA)",
            "optionsEndpoint": "/stock_tickers"
        }
    ]
})
@router.command(methods=["GET"])
async def company_facts(symbol: str = "600325") -> OBBject[dict]:
    """Get options data."""
    import numpy as np
    import pandas as pd

    from openbb_akshare.utils.fetch_equity_info import fetch_equity_info
    from mysharelib.tools import normalize_symbol

    user_setting = UserService.read_from_file()
    credentials = user_setting.credentials
    api_key = credentials.akshare_api_key.get_secret_value()
    df = fetch_equity_info(symbol, api_key=api_key, use_cache=True)
    df.set_index('symbol', inplace=True)
    
    _, symbol_f, _ = normalize_symbol(symbol)
    data = df.T.to_dict(orient="dict")[symbol_f]
    
    return OBBject(results=data)


@router.command(methods=["POST"])
async def post_example(
    data: dict,
    bid_col: str = "bid",
    ask_col: str = "ask",
) -> OBBject[dict]:
    """Calculate mid and spread."""
    bid = data[bid_col]
    ask = data[ask_col]
    mid = (bid + ask) / 2
    spread = ask - bid

    return OBBject(results={"mid": mid, "spread": spread})


# pylint: disable=unused-argument
@router.command(model="Example")
async def model_example(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Example Data."""
    return await OBBject.from_query(Query(**locals()))


# pylint: disable=unused-argument
@router.command(model="BusinessAnalysis")
async def business_analysis(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get business analysis data."""
    return await OBBject.from_query(Query(**locals()))


# pylint: disable=unused-argument
@router.command(model="EtfHoldings")
async def etf_holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get ETF holdings data."""
    return await OBBject.from_query(Query(**locals()))


# pylint: disable=unused-argument
@router.command(model="FundHoldings")
async def fund_holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get fund holdings data."""
    return await OBBject.from_query(Query(**locals()))