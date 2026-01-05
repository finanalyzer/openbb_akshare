
import os
from dotenv import load_dotenv
from openbb import obb
from openbb_akshare.utils.ak_key_metrics import fetch_key_metrics

def debug_fundamental_metrics(symbol: str):
    return obb.equity.fundamental.metrics(symbol=symbol, provider="akshare", use_cache=True).to_dataframe()

def debug_fetch_key_metrics_cache(symbol: str, api_key: str, use_cache: bool = True):
    print(f"Fetching key metrics for symbol: {symbol} with use_cache={use_cache}")
    return fetch_key_metrics(symbol=symbol, use_cache=use_cache, api_key=api_key)

if __name__ == "__main__":
    load_dotenv() 
    akshare_api_key = os.environ.get("AKSHARE_API_KEY")
    if akshare_api_key is None:
        raise ValueError("AKSHARE_API_KEY environment variable not set.")

    # Debug fundamental metrics fetch
    # Bank of China Hong Kong
    debug_fetch_key_metrics_cache("03988", akshare_api_key, use_cache=True)
    # Shanghai
    debug_fetch_key_metrics_cache("600177", akshare_api_key, use_cache=True)
    # Shenzhen
    debug_fetch_key_metrics_cache("001979", akshare_api_key, use_cache=True)
    