"""openbb_akshare OpenBB Platform Provider."""

from openbb_core.provider.abstract.provider import Provider
from openbb_akshare.models.available_indices import AKShareAvailableIndicesFetcher
from openbb_akshare.models.balance_sheet import AKShareBalanceSheetFetcher
from openbb_akshare.models.cash_flow import AKShareCashFlowStatementFetcher
from openbb_akshare.models.company_news import AKShareCompanyNewsFetcher
from openbb_akshare.models.currency_historical import AKShareCurrencyHistoricalFetcher
from openbb_akshare.models.currency_snapshots import AKShareCurrencySnapshotsFetcher
from openbb_akshare.models.equity_quote import AKShareEquityQuoteFetcher
from openbb_akshare.models.equity_historical import AKShareEquityHistoricalFetcher
from openbb_akshare.models.equity_profile import AKShareEquityProfileFetcher
from openbb_akshare.models.historical_dividends import AKShareHistoricalDividendsFetcher
from openbb_akshare.models.income_statement import AKShareIncomeStatementFetcher

# mypy: disable-error-code="list-item"

provider = Provider(
    name="akshare",
    description="Data provider for openbb-akshare.",
    # Only add 'credentials' if they are needed.
    # For multiple login details, list them all here.
    # credentials=["api_key"],
    website="https://akshare.akfamily.xyz/",
    # Here, we list out the fetchers showing what our provider can get.
    # The dictionary key is the fetcher's name, used in the `router.py`.
    fetcher_dict={
        "AvailableIndices": AKShareAvailableIndicesFetcher,
        "BalanceSheet": AKShareBalanceSheetFetcher,
        "CashFlowStatement": AKShareCashFlowStatementFetcher,
        "CompanyNews": AKShareCompanyNewsFetcher,
        "CurrencyHistorical": AKShareCurrencyHistoricalFetcher,
        "CurrencySnapshots": AKShareCurrencySnapshotsFetcher,
        "EquityQuote": AKShareEquityQuoteFetcher,
        "EquityHistorical": AKShareEquityHistoricalFetcher,
        "EquityInfo": AKShareEquityProfileFetcher,
        "HistoricalDividends": AKShareHistoricalDividendsFetcher,
        "IncomeStatement": AKShareIncomeStatementFetcher,
    }
)
