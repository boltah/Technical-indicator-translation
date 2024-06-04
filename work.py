"""This file is calculating and rendering Order Block indicator."""
import datetime

import yfinance as yf
import plotly.graph_objects as go

CANDLE_WIDTH = 0.5
RANGE_CANDLE = 15

SHOW_PD = True
SHOW_BEARISH_BOS = True
SHOW_BULLISH_BOS = True

BULLISH_OB_COLOUR = "rgba(0,255,0,0.35)"
BEARISH_OB_COLOUR = "rgba(255,0,0,0.35)"

TICKER = "AAPL"
PERIOD = "2y"


def fetch_historical_data(ticker, period, interval="1d"):
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


def calculate_pdh_pdl(data):
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


def initialize_plot(data):
    """Initialize a candlestick chart for data using Plotly.

    This function takes a DataFrame that contains financial market data and
    creates a candlestick chart representing the price movements.

    Args:
        data (pandas.DataFrame): A DataFrame with a DateTimeIndex and
                                columns labeled 'Open', 'High',
                                'Low', and 'Close' that contain the price data.

    Returns:
        plotly.graph_objs.Figure: A Plotly Figure object that contains
                                  the candlestick chart, ready to be displayed
                                  or further customized.
    """
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                increasing_line_width=CANDLE_WIDTH,
                decreasing_line_width=CANDLE_WIDTH,
                increasing_line_color="green",
                decreasing_line_color="red",
            )
        ]
    )
    return fig


def add_pdh_pdl_to_plot(fig, data):
    """Add horizontal lines for (PDH) and (PDL) to a Plotly candlestick chart.

    This function calculates the PDH and PDL for the previous day from the
    provided data and adds horizontal lines at these levels on the plot.
    The lines help to visually assess current day's movements to the previous.

    Args:
        fig (plotly.graph_objs.Figure): The existing Plotly Figure object
                                        that contains the candlestick chart.
        data (pandas.DataFrame): A DataFrame that includes a DateTimeIndex
                                 and columns 'PDH' and 'PDL' among others.
                                 The DataFrame should cover at least the
                                 previous day's data.

    Returns:
        fig (plotly.graph_objs.Figure): Modified Plotly Figure object
                                        that contains the candlestick chart
                                        and PDH and PDL lines.
    """
    if SHOW_PD:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_data = data.loc[data.index.date == yesterday]
        if not yesterday_data.empty:
            pdh = yesterday_data["PDH"].values[0]
            pdl = yesterday_data["PDL"].values[0]
            fig.add_shape(
                type="line",
                x0=0,
                x1=1,
                xref="paper",
                y0=pdh,
                y1=pdh,
                yref="y",
                line=dict(color="Blue", width=1),
            )
            fig.add_annotation(
                x=1,
                xref="paper",
                y=pdh,
                text="PDH",
                showarrow=False,
                bgcolor="Blue",
                font=dict(color="white"),
                xanchor="left",
            )
            fig.add_shape(
                type="line",
                x0=0,
                x1=1,
                xref="paper",
                y0=pdl,
                y1=pdl,
                yref="y",
                line=dict(color="Red", width=1),
            )
            fig.add_annotation(
                x=1,
                xref="paper",
                y=pdl,
                text="PDL",
                showarrow=False,
                bgcolor="Red",
                font=dict(color="white"),
                xanchor="left",
            )
    return fig


def calculate_structure_low(data):
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


def detect_order_blocks_bos(data):
    """Analyze data to detect order blocks and break of structure (BOS) points.

    This function traverses through the provided financial data and identifies
    'short' and 'long' order blocks, as well as lines indicating breaks of
    structure based on the closing prices. The detection logic includes
    conditions for how recent and how far apart these events must be relative
    to previous points of interest.

    Parameters:
    data (pandas.DataFrame): A DataFrame with columns 'Open', 'Close',
                             'High', 'Low', and 'StructureLow'.

    Returns:
    tuple: Returns a tuple containing three lists:
           - long_boxes (list): List of tuples representing long order blocks.
           - short_boxes (list): List of tuples representing short order blocks
           - bos_lines (list): List of tuples representing BOS lines.
    """
    last_down_index = last_down = last_low = 0
    last_up_index = last_long_index = last_up_low = last_high = 0
    long_boxes = []
    shor_boxes = []
    bos_lines = []
    candle_colour_mode = 0

    for i in range(RANGE_CANDLE, len(data)):
        row = data.iloc[i]
        if row["Low"] < row["StructureLow"]:
            if i - last_up_index < 1000:
                shor_boxes.append((last_up_index, last_high, last_up_low))
                if SHOW_BEARISH_BOS:
                    candle_colour_mode = 0
                    bos_lines.append(
                        (
                            data.index[last_up_index],
                            last_up_low,
                            data.index[i],
                            last_up_low,
                            candle_colour_mode,
                        )
                    )

        if len(shor_boxes) > 0:
            for box in shor_boxes[:]:
                if row["Close"] > box[1]:
                    shor_boxes.remove(box)
                    if i - last_down_index < 1000 and i > last_long_index:
                        long_boxes.append(
                            (last_down_index, last_down, last_low))
                        if SHOW_BULLISH_BOS:
                            candle_colour_mode = 1
                            bos_lines.append(
                                (
                                    data.index[last_down_index],
                                    last_down,
                                    row.name,
                                    last_down,
                                    candle_colour_mode,
                                )
                            )
                        last_long_index = i

        if len(long_boxes) > 0:
            for box in long_boxes[:]:
                if row["Close"] < box[2]:
                    long_boxes.remove(box)

        if row["Close"] < row["Open"]:
            last_down = row["High"]
            last_down_index = i
            last_low = row["Low"]

        if row["Close"] > row["Open"]:
            last_up_index = i
            last_up_low = row["Low"]
            last_high = row["High"]

        last_high = max(row["High"], last_high)
        last_low = min(row["Low"], last_low)

    return long_boxes, shor_boxes, bos_lines


def add_order_blocks_to_plot(fig, data, long_boxes, shor_boxes):
    """Render representations of long and short order blocks to Plotly figure.

    This function iterates over lists of long and short order blocks
    and adds corresponding rectangle shapes to a Plotly figure to visually
    represent these blocks on the chart.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure object to which
            the order block shapes will be added.
        data (pandas.DataFrame): The DataFrame containing the financial data,
            which must have an index that Plotly can use to
            place the rectangles on the x-axis.
        long_boxes (list of tuples): Each tuple contains indices and prices
            defining a long order block. Specifically, tuples are expected
            in the format (start_index, high_price, low_price)
        shor_boxes (list of tuples): Each tuple contains indices and prices
            defining a short order block. The format is similar to long_boxes.

    Returns:
        plotly.graph_objs.Figure: The modified figure object with
            added shapes for order blocks.
    """
    for box in long_boxes:
        fig.add_shape(
            type="rect",
            x0=data.index[box[0]],
            x1=data.index[-1],
            y0=box[2],
            y1=box[1],
            line=dict(color=BULLISH_OB_COLOUR),
            fillcolor=BULLISH_OB_COLOUR,
        )
    for box in shor_boxes:
        fig.add_shape(
            type="rect",
            x0=data.index[box[0]],
            x1=data.index[-1],
            y0=box[2],
            y1=box[1],
            line=dict(color=BEARISH_OB_COLOUR),
            fillcolor=BEARISH_OB_COLOUR,
        )
    return fig


def add_bos_lines_to_plot(fig, bos_lines):
    """Add BOS (Break of Structure) lines to a Plotly figure.

    This function iterates over a list of BOS lines and adds corresponding
    lines to a Plotly figure. The color of each line is determined by a
    specific value in the line tuple, allowing visualization
    of different types of BOS events: bearish (red), bullish (green).

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure object
            to which the BOS lines will be added.
        bos_lines (list of tuples): Each tuple contains the data needed
            to plot a line. Expected tuple format is
            (start_x, start_y, end_x, end_y, color_code),
            where 'color_code' is 0 for red, 1 for green.

    Returns:
        plotly.graph_objs.Figure: The modified figure with added BOS lines.
    """
    for line in bos_lines:
        fig.add_shape(
            type="line",
            x0=line[0],
            x1=line[2],
            y0=line[1],
            y1=line[3],
            line=dict(color='red' if line[4] == 0 else 'green'),
        )
    return fig


# finalizes the chart
def finalize_plot(fig, ticker, period):
    """Finalize the appearance of a Plotly figure.

    This function updates the layout of a given Plotly figure to include a
    title that reflects the stock ticker and the time period over which the
    data is displayed. It also sets up the y-axis title to indicate
    it's displaying stock information, and hides the x-axis range slider
    typically used for dynamic temporal scaling, for a cleaner and more
    focused presentation.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure that is finalized.
        ticker (str): The ticker symbol of the stock, which will be used
            to generate the titles for the chart.
        PERIOD (str): The time period over which the data is being displayed
            (e.g., "1m", "6m", "1y"), which will also be included in the chart
            title to indicate the duration of the data shown.

    Returns:
        plotly.graph_objs.Figure: The modified figure with updated
        layout settings, ready for presentation.
    """
    fig.update_layout(
        title=ticker + " Stock Price for " + period,
        yaxis_title=ticker + "Stock",
        xaxis_rangeslider_visible=False
    )
    return fig


data = fetch_historical_data(TICKER, PERIOD)
data = calculate_pdh_pdl(data)
fig = initialize_plot(data)
fig = add_pdh_pdl_to_plot(fig, data)
data = calculate_structure_low(data)
long_boxes, shor_boxes, bos_lines = detect_order_blocks_bos(data)
fig = add_order_blocks_to_plot(fig, data, long_boxes, shor_boxes)
fig = add_bos_lines_to_plot(fig, bos_lines)
fig = finalize_plot(fig, TICKER, PERIOD)
fig.show()
