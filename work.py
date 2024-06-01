import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime

# Fetches data of specified company 
def fetch_historical_data(ticker, period='2y', interval='1d'):
    return yf.download(ticker, period=period, interval=interval)

#Calculates previous day high and low
def calculate_pdh_pdl(data):
    data['PDH'] = data['High'].shift(1)
    data['PDL'] = data['Low'].shift(1)
    return data

#initializes graph
def initialize_plot(data, candle_width=0.5):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        increasing_line_width=candle_width, decreasing_line_width=candle_width,
        increasing_line_color='green', decreasing_line_color='red'
    )])
    return fig

#adds labels ofprevious day high and low
def add_pdh_pdl_to_plot(fig, data, showPD=True):
    if showPD:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_data = data.loc[data.index.date == yesterday]
        if not yesterday_data.empty:
                pdh = yesterday_data['PDH'].values[0]
                pdl = yesterday_data['PDL'].values[0]
                fig.add_shape(type="line",
                  x0=0, x1=1, xref='paper',
                  y0=pdh, y1=pdh, yref='y',
                  line=dict(color="Blue", width=1))
                fig.add_annotation(x=1, xref='paper', y=pdh,
                       text="PDH",
                       showarrow=False,
                       bgcolor="Blue",
                       font=dict(color="white"),
                       xanchor='left')
                fig.add_shape(type="line",
                  x0=0, x1=1, xref='paper',
                  y0=pdl, y1=pdl, yref='y',
                  line=dict(color="Red", width=1))
                fig.add_annotation(x=1, xref='paper', y=pdl,
                       text="PDL",
                       showarrow=False,
                       bgcolor="Red",
                       font=dict(color="white"),
                       xanchor='left')
    return fig

#calculates structure low 
def calculate_structure_low(data, range_candle):
    data['StructureLow'] = data['Low'].rolling(window=range_candle).min().shift(1)
    data['StructureLowIndex'] = data['Low'].rolling(window=range_candle).min().idxmin()
    return data

# main code to detect blocks and breaks of structures 
def detect_order_blocks_bos(data, range_candle, showBearishBOS=True, showBullishBOS=True):
    lastDownIndex = lastDown = lastLow = 0
    lastUpIndex = lastLongIndex = lastUp = lastUpLow = lastUpOpen = lastHigh = 0
    longBoxes = []
    shortBoxes = []
    bosLines = []
    CandleColourMode = 0
    BosCandle = False

    for i in range(range_candle, len(data)):
        row = data.iloc[i]

        if row['Low'] < data['StructureLow'].iloc[i]:
            if i - lastUpIndex < 1000 and lastUpIndex is not None:
                shortBoxes.append((lastUpIndex, lastHigh, lastUpLow))
                if showBearishBOS:
                    CandleColourMode = 0
                    bosLines.append((data.index[lastUpIndex], lastUpLow, row.name, lastUpLow, CandleColourMode))
                BosCandle = True
                
        
        if len(shortBoxes) > 0:
            for box in shortBoxes[:]:
                if row['Close'] > box[1]:
                    shortBoxes.remove(box)
                    if i - lastDownIndex < 1000 and i > lastLongIndex:
                        longBoxes.append((lastDownIndex, lastDown, lastLow))
                        if showBullishBOS:
                            CandleColourMode = 1
                            bosLines.append((data.index[lastDownIndex], lastDown, row.name, lastDown,CandleColourMode))
                        BosCandle = True
                        lastLongIndex = i
                        lastBullBreakLow = row['Low']

        if len(longBoxes) > 0:
            for box in longBoxes[:]:
                if row['Close'] < box[2]:
                    longBoxes.remove(box)

        if row['Close'] < row['Open']:
            lastDown = row['High']
            lastDownIndex = i
            lastLow = row['Low']

        if row['Close'] > row['Open']:
            lastUp = row['Close']
            lastUpIndex = i
            lastUpOpen = row['Open']
            lastUpLow = row['Low']
            lastHigh = row['High']

        lastHigh = max(row['High'], lastHigh)
        lastLow = min(row['Low'], lastLow)

    return longBoxes, shortBoxes, bosLines

#renders order blocks to chart
def add_order_blocks_to_plot(fig, data, longBoxes, shortBoxes, bullishOBColour='rgba(0,255,0,0.35)', bearishOBColour='rgba(255,0,0,0.35)'):
    for box in longBoxes:
        fig.add_shape(type='rect', x0=data.index[box[0]], x1=data.index[-1], y0=box[2], y1=box[1], line=dict(color=bullishOBColour), fillcolor=bullishOBColour)
    for box in shortBoxes:
        fig.add_shape(type='rect', x0=data.index[box[0]], x1=data.index[-1], y0=box[2], y1=box[1], line=dict(color=bearishOBColour), fillcolor=bearishOBColour)
    return fig

#adds break of structure lines to chart 
def add_bos_lines_to_plot(fig, bosLines, BOSCandleColour='yellow'):
    for line in bosLines:
        fig.add_shape(type='line', x0=line[0], x1=line[2], y0=line[1], y1=line[3],  line=dict(color='red' if line[4] == 0 else 'green'))
    return fig

#finalizes the chart 
def finalize_plot(fig, title='AAPL Stock Price 2 Years'):
    fig.update_layout(
        title=title,
        yaxis_title='AAPL Stock',
        xaxis_rangeslider_visible=False
    )
    return fig

# main code
ticker = 'AAPL'
data = fetch_historical_data(ticker)
data = calculate_pdh_pdl(data)
fig = initialize_plot(data)
fig = add_pdh_pdl_to_plot(fig, data)
data = calculate_structure_low(data, range_candle=15)
longBoxes, shortBoxes, bosLines = detect_order_blocks_bos(data, range_candle=15)
fig = add_order_blocks_to_plot(fig, data, longBoxes, shortBoxes)
fig = add_bos_lines_to_plot(fig, bosLines)
fig = finalize_plot(fig)
fig.show()
