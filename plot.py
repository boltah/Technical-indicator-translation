import utils
import plotly.graph_objects as go
import datetime


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
                increasing=dict(
                    line=dict(width=utils.CANDLE_WIDTH, color="green")),
                decreasing=dict(
                    line=dict(width=utils.CANDLE_WIDTH, color="red"))
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
    if utils.SHOW_PD:
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


def add_order_blocks_to_plot(fig, data, long_boxes, short_boxes):
    """Render representations of long and short order blocks to Plotly figure.

    This function iterates over lists of long and short order blocks
    and adds corresponding rectangle shapes to a Plotly figure to visually
    represent these blocks on the chart.

    Args:
        fig (plotly.graph_obs.Figure): The Plotly figure object to which
            the order block shapes will be added.
        data (pandas.DataFrame): The DataFrame containing the financial data,
            which must have an index that Plotly can use to
            place the rectangles on the x-axis.
        long_boxes (list of tuples): Each tuple contains indices and prices
            defining a long order block. Specifically, tuples are expected
            in the format (start_index, high_price, low_price)
        short_boxes (list of tuples): Each tuple contains indices and prices
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
            line=dict(color=utils.BULLISH_OB_COLOUR),
            fillcolor=utils.BULLISH_OB_COLOUR,
        )
    for box in short_boxes:
        fig.add_shape(
            type="rect",
            x0=data.index[box[0]],
            x1=data.index[-1],
            y0=box[2],
            y1=box[1],
            line=dict(color=utils.BEARISH_OB_COLOUR),
            fillcolor=utils.BEARISH_OB_COLOUR,
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
        period (str): The time period over which the data is being displayed
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
