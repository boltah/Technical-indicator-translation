# Code explanation

## How the Script Works
The script is organized into several functions, each with a specific task, from fetching data to calculating certain financial metrics and plotting them. Here’s a breakdown of the main components:

## Dependencies
datetime: Provides classes for manipulating dates and times.
yfinance: A library for fetching historical market data from Yahoo Finance.
plotly.graph_objects: Used for creating interactive plots. The go module contains various graph objects like Candlestick for plotting candlestick charts.

## Constants
CANDLE_WIDTH, RANGE_CANDLE: Constants that define the style and analysis range of the candlesticks.
SHOW_PD, SHOW_BEARISH_BOS, SHOW_BULLISH_BOS: Boolean flags to control the display of certain plot elements.
BULLISH_OB_COLOUR, BEARISH_OB_COLOUR: Color settings for bullish and bearish order blocks.
TICKER, PERIOD: Variables to specify which stock ticker to analyze and the period over which to fetch data.

## Functions
fetch_historical_data(ticker, period, interval='1d'): Fetches historical stock data from Yahoo Finance for a given ticker and period.

calculate_pdh_pdl(data): Calculates the Previous Day High (PDH) and Previous Day Low (PDL) based on the fetched data and adds these as new columns to the DataFrame.

initialize_plot(data): Initializes a candlestick chart using Plotly with the provided data.

add_pdh_pdl_to_plot(fig, data): Adds horizontal lines to the plot representing the PDH and PDL values.

calculate_structure_low(data): Calculates rolling minimum values to find structure lows in the stock data.

detect_order_blocks_bos(data): Analyzes the data to detect order blocks and points of structure breaks.

add_order_blocks_to_plot(fig, data, long_boxes, shor_boxes): Visualizes the detected order blocks by adding colored rectangles to the chart.

add_bos_lines_to_plot(fig, bos_lines): Adds lines to the chart that indicate significant breaks in the stock’s structure.

finalize_plot(fig, ticker, period): Finalizes the plot by setting titles and adjusting layout settings.

## Main Execution Flow
Data is fetched for the specified ticker and period.
Various calculations are performed on this data, including PDH, PDL, and structure lows.
The final plot is displayed using Plotly’s interactive viewer.
