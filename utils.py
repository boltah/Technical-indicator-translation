import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

import datetime


TICKER = "AAPL"
PERIOD = "2y"

CANDLE_WIDTH: float = 0.5
RANGE_CANDLE: int = 15

SHOW_PD: bool = True
SHOW_BEARISH_BOS: bool = True
SHOW_BULLISH_BOS: bool = True

BULLISH_OB_COLOUR: str = "rgba(0,255,0,0.35)"
BEARISH_OB_COLOUR: str = "rgba(255,0,0,0.35)"
