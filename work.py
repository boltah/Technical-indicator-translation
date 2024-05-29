import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# Fetch Apple stock data using yfinance
ticker = 'AAPL'
df = yf.download(ticker, start='2015-01-01', end='2024-01-01')

# Function to create a candlestick chart with adjustable candle width
def create_candlestick_chart(df, candle_width=0.5):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_width=candle_width, decreasing_line_width=candle_width,
        increasing_line_color='green', decreasing_line_color='red'
    )])

    fig.update_layout(
        title='AAPL Stock Price (2015-2024)',
        yaxis_title='AAPL Stock',
        xaxis_rangeslider_visible=False
    )

    return fig

# Create and show the candlestick chart with adjustable candle width
candle_width = 0.8  # Adjust this value to change the width of the candlesticks
fig = create_candlestick_chart(df, candle_width=candle_width)
fig.show()