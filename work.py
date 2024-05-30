import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime


# Fetch historical data
ticker = 'AAPL'
data = yf.download(ticker, period='2y', interval='1d')

# Parameters
range_candle = 15
showPD = True
showBearishBOS = False
showBullishBOS = False

# Colors
bearishOBColour = 'rgba(255,0,0,0.35)'
bullishOBColour = 'rgba(0,255,0,0.35)'
BOSCandleColour = 'yellow'
bullishTrendColor = 'lime'
bearishTrendColour = 'red'

# Calculate PDH and PDL
data['PDH'] = data['High'].shift(1)
data['PDL'] = data['Low'].shift(1)
candle_width=0.5

yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterday_data = data.loc[data.index.date == yesterday]

# Plot PDH and PDL if showPD is True
fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        increasing_line_width=candle_width, decreasing_line_width=candle_width,
        increasing_line_color='green', decreasing_line_color='red'
    )])

if showPD:
    #fig.add_trace(go.Scatter(x=data.index, y=data['PDH'], mode='lines', name='PDH', line=dict(color='blue')))
    #fig.add_trace(go.Scatter(x=data.index, y=data['PDL'], mode='lines', name='PDL', line=dict(color='blue')))
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
    
# Calculate structure low
data['StructureLow'] = data['Low'].rolling(window=range_candle).min().shift(1)

# Initialize variables for tracking order blocks
lastDownIndex = lastDown = lastLow = 0
lastUpIndex = lastLongIndex = lastUp = lastUpLow = lastUpOpen = lastHigh = 0
longBoxes = []
shortBoxes = []
bosLines = []
CandleColourMode = 0
BosCandle = False

# Loop through the data to detect order blocks and BOS
for i in range(range_candle, len(data)):
    row = data.iloc[i]

    if row['Low'] < data['StructureLow'].iloc[i]:
        if i - lastUpIndex < 1000:
            shortBoxes.append((lastUpIndex, lastHigh, lastUpLow))
            if showBearishBOS:
                bosLines.append((data.index[lastUpIndex], lastUpLow, row.name, lastUpLow))
            BosCandle = True
            CandleColourMode = 0
    
    if len(shortBoxes) > 0:
        for box in shortBoxes[:]:
            if row['Close'] > box[1]:
                shortBoxes.remove(box)
                if i - lastDownIndex < 1000 and i > lastLongIndex:
                    longBoxes.append((lastDownIndex, lastDown, lastLow))
                    if showBullishBOS:
                        bosLines.append((data.index[lastDownIndex], lastDown, row.name, lastDown))
                    BosCandle = True
                    CandleColourMode = 1
                    lastLongIndex = i
                    lastBullBreakLow = row['Low']

    if len(longBoxes) > 0:
        for box in longBoxes[:]:
            if row['Close'] < box[2]:
                longBoxes.remove(box)

    CandleColour = bullishTrendColor if CandleColourMode == 1 else bearishTrendColour
    CandleColour = BOSCandleColour if BosCandle else CandleColour

    # Update last up and down candles
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

    # Update last high/low
    lastHigh = max(row['High'], lastHigh)
    lastLow = min(row['Low'], lastLow)

# Plot candlesticks
#fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlesticks'))

# Plot order blocks
for box in longBoxes:
    fig.add_shape(type='rect', x0=data.index[box[0]], x1=data.index[-1], y0=box[2], y1=box[1], line=dict(color=bullishOBColour), fillcolor=bullishOBColour)

for box in shortBoxes:
    fig.add_shape(type='rect', x0=data.index[box[0]], x1=data.index[-1], y0=box[2], y1=box[1], line=dict(color=bearishOBColour), fillcolor=bearishOBColour)

# Plot BOS lines
for line in bosLines:
    fig.add_shape(type='line', x0=line[0], x1=line[2], y0=line[1], y1=line[3], line=dict(color='red' if CandleColourMode == 0 else 'green'))

fig.update_layout(
            title='AAPL Stock Price 2 Years',
        yaxis_title='AAPL Stock',
        xaxis_rangeslider_visible=False
)
candle_width = 0.8
fig.show()
