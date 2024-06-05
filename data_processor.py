from utils import *


def calculate_pdh_pdl(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the Previous Day High (PDH) and Previous Day Low (PDL).

    This function adds two new columns to the DataFrame 'data': 'PDH' and 'PDL'
    'PDH' is derived from shifting the 'High' column down by one position,
    representing the high of the previous day. Similarly, 'PDL' is from
    shifting the 'Low' column down by one position, representing the low of
    the previous day.

    Args:
       data (pandas.DataFrame): A DataFrame containing at least two columns
                                'High' and 'Low' that represent the daily high
                                and low prices respectively.

    Returns:
        pandas.DataFrame: The modified DataFrame
                          with two new columns 'PDH' and 'PDL'.
    """
    data["PDH"] = data["High"].shift(1)
    data["PDL"] = data["Low"].shift(1)
    return data


def calculate_structure_low(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the structure lows in data based on rolling minimum values.

    This function computes the rolling minimum of the 'Low' price over a
    specified window (RANGE_CANDLE) and assigns this rolling minimum to a
    new column 'StructureLow' in the input DataFrame. It also calculates
    the index of the minimum value within each window and stores
    this index in 'StructureLowIndex'. The rolling
    minimum is shifted by one to prevent lookahead bias.

    Args:
        data (pandas.DataFrame): A DataFrame containing a 'Low' column

    Returns:
        pandas.DataFrame: The original DataFrame modified to include
                          two new columns: 'StructureLow' - the rolled and
                          shifted minimum values of the 'Low' price,
                          'StructureLowIndex' - the index of the minimum
                          value within each window.
    """
    low_rolling_min = data["Low"].rolling(window=RANGE_CANDLE).min()
    data["StructureLow"] = low_rolling_min.shift(1)
    data["StructureLowIndex"] = low_rolling_min.idxmin()
    return data
