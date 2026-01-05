import os
from re import T
from dotenv import load_dotenv
from openbb import obb
def debug_equity_profile(symbol: str):
    return obb.equity.profile(symbol=symbol, provider="akshare").to_dataframe()

if __name__ == "__main__":
    load_dotenv() 
    akshare_api_key = os.environ.get("AKSHARE_API_KEY")
    if akshare_api_key is None:
        raise ValueError("AKSHARE_API_KEY environment variable not set.")

    symbol_hk = "02800"
    symbol_sh = "600177"
    symbol_sz = "000001"
    print(debug_equity_profile(symbol_hk))
    print(debug_equity_profile(symbol_sh))
    print(debug_equity_profile(symbol_sz))
    #from openbb_akshare.utils.fetch_equity_info import fetch_equity_info
    #print(fetch_equity_info(symbol_hk, api_key=akshare_api_key, use_cache=True))
    #print(fetch_equity_info(symbol_sh, api_key=akshare_api_key, use_cache=True))
    #print(fetch_equity_info(symbol_sz, api_key=akshare_api_key, use_cache=True))