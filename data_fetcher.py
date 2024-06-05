from utils import *


def fetch_historical_data(ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
    """Fetch historical market data for ticker using the Yahoo Finance API.

    This function retrieves historical data for the given 'TICKER' over the
    specified 'PERIOD' and at the provided 'interval'. By default, the data is
    fetched at daily intervals unless specified otherwise.

    Args:
        ticker (str): The stock ticker symbol for which to fetch the data.
        period (str): The time period over which to fetch the data.
                      Examples include "1mo", "1y", "5y".
        interval (str, optional): The frequency at which to fetch the data.
                                  Default is "1d". Other possible values
                                  include "1wk" (weekly) and "1mo" (monthly).

    Returns:
        pandas.DataFrame: A DataFrame containing the historical market data
                          for the specified ticker,including columns for open,
                          high, low, close prices, and volume.
    """
    return yf.download(ticker, period=period, interval=interval)
