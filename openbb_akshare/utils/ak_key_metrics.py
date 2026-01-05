import logging
import pandas as pd
import akshare as ak
from typing import Optional, Literal
from openbb_akshare import project_name
from mysharelib.tools import setup_logger, normalize_symbol

setup_logger(project_name)
logger = logging.getLogger(__name__)

def fetch_key_metrics(
        symbol: str, 
        period: Literal["annual", "quarter"] = "quarter",
        use_cache: bool = True,
        api_key: Optional[str] = None,
        ) -> pd.DataFrame:
    """
    Fetches key financial metrics for a specific equity symbol.

    Args:
        symbol (str): The stock symbol to fetch metrics for.
                      such as "601127.SH".

    Returns:
        pd.DataFrame: A DataFrame containing the key metrics.
    """
    from mysharelib.blob_cache import BlobCache

    logger.debug(f"Fetching key metrics for symbol: {symbol}, period: {period}, use_cache: {use_cache}")
    symbol_b, _, market = normalize_symbol(symbol)
    if market not in ["SH", "SZ", "BJ", "HK"]:
        logger.warning("AKShare key metrics only support A shares.")
        return pd.DataFrame()
    cache = BlobCache(table_name="key_metrics", project=project_name)
    try:
        data = cache.load_cached_data(symbol_b, period, use_cache, _get_key_metrics, api_key=api_key)
    except NotImplementedError:
        logger.warning("Cached data contained pandas extension dtypes that could not be unpickled; refreshing cache.")
        # Try again without using cache so we regenerate a fresh, safe cache entry
        data = cache.load_cached_data(symbol_b, period, False, _get_key_metrics, api_key=api_key)

    if data is None:
        return pd.DataFrame()

    # Ensure loaded DataFrame has no pandas extension dtypes (e.g., StringDtype)
    if isinstance(data, pd.DataFrame):
        for col in data.columns:
            if pd.api.types.is_extension_array_dtype(data[col].dtype):
                data[col] = data[col].astype(object)
        data.index = data.index.astype(object)

        # If cached data is missing required fields (e.g., '证券代码'), regenerate cache
        if "证券代码" not in data.index:
            logger.warning("Cached key metrics missing '证券代码'; refreshing cache.")
            data = cache.load_cached_data(symbol_b, period, False, _get_key_metrics, api_key=api_key)
            if isinstance(data, pd.DataFrame):
                for col in data.columns:
                    if pd.api.types.is_extension_array_dtype(data[col].dtype):
                        data[col] = data[col].astype(object)
                data.index = data.index.astype(object)

    return data

def _get_key_metrics(
    symbol: str,
    period: str = "quarter",
    api_key: Optional[str] = None
) -> pd.DataFrame:
    import akshare as ak
    from mysharelib.em.get_a_info_em import get_a_info_em
    from mysharelib.em.get_hk_info_em import get_hk_info_em

    symbol_b, symbol_f, market = normalize_symbol(symbol)
    df_base = pd.DataFrame()
    if market == "HK":
        df_base, _ = get_hk_info_em(symbol_f)
    else:
        df_base, _ = get_a_info_em(symbol_f)

    # Convert any existing StringDtype or extension array columns to object type immediately
    for col in df_base.columns:
        if pd.api.types.is_extension_array_dtype(df_base[col].dtype) or pd.api.types.is_string_dtype(df_base[col]):
            df_base[col] = df_base[col].astype(object)

    if api_key:
        try:
            ak.stock.cons.xq_a_token = api_key
            stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol=f"{market}{symbol_b}")

            def get_metric(df, metric_name):
                result = df.loc[df["item"] == metric_name, "value"]
                if not result.empty:
                    return result.iloc[0]
                return None

            # Add new metrics and ensure they're proper types
            metrics_to_add = {
                "市盈率(动)": get_metric(stock_individual_spot_xq_df, "市盈率(动)"),
                "市盈率(TTM)": get_metric(stock_individual_spot_xq_df, "市盈率(TTM)"),
                "市盈率(静)": get_metric(stock_individual_spot_xq_df, "市盈率(静)"),
                "市净率": get_metric(stock_individual_spot_xq_df, "市净率"),
                "流通值": get_metric(stock_individual_spot_xq_df, "流通值"),
                "52周最低": get_metric(stock_individual_spot_xq_df, "52周最低"),
                "52周最高": get_metric(stock_individual_spot_xq_df, "52周最高"),
                "股息(TTM)": get_metric(stock_individual_spot_xq_df, "股息(TTM)"),
                "股息率(TTM)": get_metric(stock_individual_spot_xq_df, "股息率(TTM)"),
                "发行日期": get_metric(stock_individual_spot_xq_df, "发行日期")
            }
            
            # Add metrics to df_base ensuring proper data types
            for metric_name, value in metrics_to_add.items():
                df_base.loc[metric_name] = str(value) if value is not None else None
        except NotImplementedError:
            logger.warning("akshare returned an unexpected format; skipping extra spot metrics.")
        except Exception:
            logger.warning("Failed to fetch additional spot metrics from akshare; proceeding without them.")

    # Ensure symbol field is present for downstream data model validation
    if "证券代码" not in df_base.index:
        df_base.loc["证券代码"] = symbol

    # Final comprehensive conversion to ensure no pandas extension dtypes (e.g., StringDtype) remain
    df_converted = df_base.copy()
    for col in df_converted.columns:
        if pd.api.types.is_extension_array_dtype(df_converted[col].dtype):
            df_converted[col] = df_converted[col].astype(object)
        else:
            df_converted[col] = df_converted[col].astype(object)
    # Ensure index values are plain Python objects (avoid extension dtypes)
    df_converted.index = df_converted.index.astype(object)
    
    return df_converted