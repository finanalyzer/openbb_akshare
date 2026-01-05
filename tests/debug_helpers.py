
def get_data(code: str) -> dict:
    import pandas as pd
    from mysharelib.tools import calculate_price_performance, last_closing_day
    from openbb_akshare.utils.helpers import get_list_date, ak_download

    df = ak_download(symbol=code, start_date=get_list_date(code), end_date=last_closing_day())
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return calculate_price_performance(code, df)

if __name__ == "__main__":
    print(get_data("601919"))