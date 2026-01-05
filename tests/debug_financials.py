from openbb import obb

if __name__ == "__main__":
    symbol_hk = "01088"
    symbol_sh = "600325"
    symbol_sz = "000001"
    period_t = "annual"
    limit = 3
    default_provider = "akshare"

    print(obb.equity.fundamental.balance(symbol=symbol_hk, period=period_t, limit=limit, provider=default_provider).to_dataframe())