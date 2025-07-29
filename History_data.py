# import credentials as crs
# from fyers_apiv3 import fyersModel
# import pandas as pd
# import datetime as dt
# import plotly.graph_objects as go
# import plotly.express as px

# # ----------------------------------------
# # 1. Load Credentials and Access Token
# # ----------------------------------------
# client_id = crs.client_id
# secret_key = crs.secret_key
# redirect_uri = crs.redirect_uri

# with open('access.txt') as f:
#     access_token = f.read()

# # ----------------------------------------
# # 2. Define Symbol
# # ----------------------------------------
# exchange = 'NSE'
# sec_type = 'INDEX'
# symbol = 'NIFTY50'
# ticker = f"{exchange}:{symbol}-{sec_type}"
# print(f"Fetching data for: {ticker}")

# # ----------------------------------------
# # 3. Fetch Historical Data from Fyers
# # ----------------------------------------
# fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

# current_date = dt.date.today()
# data = {
#     "symbol": ticker,
#     "resolution": "1",
#     "date_format": '1',
#     "range_from": (current_date - dt.timedelta(days=20)),
#     "range_to": current_date,
#     "cont_flag": 1,
# }

# response = fyers.history(data=data)

# if response.get('code') != 200:
#     print("Error fetching data:", response)
#     exit()

# # ----------------------------------------
# # 4. Format Data into DataFrame
# # ----------------------------------------
# history_df = pd.DataFrame(response['candles'])
# history_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
# history_df['date'] = pd.to_datetime(history_df['date'], unit='s')
# history_df['date'] = history_df['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
# history_df = history_df.set_index('date')
# print("Data Preview:\n", history_df.tail())

# # ----------------------------------------
# # 5. Plotting Functions
# # ----------------------------------------
# def plot_line_chart(df):
#     fig = px.line(
#         df,
#         x=df.index,
#         y="close",
#         title="📈 NIFTY50 - 15m Closing Price Trend",
#         labels={"close": "Close Price", "date": "Date/Time"},
#     )
#     fig.update_traces(line_color='royalblue', line_width=2)
#     fig.update_layout(
#         template="plotly_dark",
#         xaxis_title="Time",
#         yaxis_title="Price (INR)",
#         title_font_size=20,
#         title_x=0.5,
#         height=600
#     )
#     fig.show()

# def plot_candlestick_chart(df):
#     fig = go.Figure(data=[go.Candlestick(
#         x=df.index,
#         open=df['open'],
#         high=df['high'],
#         low=df['low'],
#         close=df['close'],
#         increasing_line_color='limegreen',
#         decreasing_line_color='red',
#         showlegend=False
#     )])
#     fig.update_layout(
#         title="🕯️ NIFTY50 - Candlestick Chart (15 Min)",
#         xaxis_title="Date/Time",
#         yaxis_title="Price (INR)",
#         template="plotly_dark",
#         height=700,
#         title_font_size=20,
#         title_x=0.5
#     )
#     fig.show()

# def plot_volume_barchart(df):
#     fig = px.bar(
#         df,
#         x=df.index,
#         y='volume',
#         title='📊 NIFTY50 - Volume Traded (15 Min)',
#         labels={'volume': 'Volume', 'date': 'Date/Time'},
#     )
#     fig.update_traces(marker_color='orange')
#     fig.update_layout(
#         template='plotly_dark',
#         xaxis_title='Time',
#         yaxis_title='Volume',
#         title_font_size=20,
#         title_x=0.5,
#         height=500
#     )
#     fig.show()

# # ----------------------------------------
# # 6. Display Charts
# # ----------------------------------------
# plot_line_chart(history_df)
# plot_candlestick_chart(history_df)
# plot_volume_barchart(history_df)


















import credentials as crs
from fyers_apiv3 import fyersModel
import pandas as pd
import datetime as dt
import plotly.graph_objects as go

# ==================== Credentials ====================
# #  Load Credentials and Access Token
# # ----------------------------------------
client_id = crs.client_id
secret_key = crs.secret_key
redirect_uri = crs.redirect_uri

# ==================== Access Token ====================
with open('access.txt') as f:
    access_token = f.read().strip()

# ==================== Initialize FyersModel ====================
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

# ==================== Define gethistory Function ====================
# # ----------------------------------------
# # . Fetch Historical Data from Fyers
# # ----------------------------------------
def gethistory(symbol1, type, duration):
    symbol = f"NSE:{symbol1}-{type}"
    start = dt.date.today() - dt.timedelta(duration)
    end = dt.date.today()
    sdata = pd.DataFrame()
    while start <= end:
        end2 = start + dt.timedelta(60)
        data = {
            "symbol": symbol,
            "resolution": "1",  # 1-minute candles
            "date_format": "1",
            "range_from": start.strftime('%Y-%m-%d'),
            "range_to": end2.strftime('%Y-%m-%d'),
            "cont_flag": "1"
        }
        response = fyers.history(data)
        temp = pd.DataFrame(response['candles'])
        sdata = pd.concat([sdata, temp], ignore_index=True)
        start = end2 + dt.timedelta(1)

    sdata.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    sdata['date'] = pd.to_datetime(sdata['date'], unit='s')
    sdata['date'] = sdata['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
    sdata['date'] = sdata['date'].dt.tz_localize(None)
    sdata.set_index('date', inplace=True)
    return sdata

# ==================== Fetch Data ====================
# # ----------------------------------------
# # . Define Symbol
# # ----------------------------------------
data = gethistory('NIFTYBANK', 'INDEX', 7)  # Use 30 days instead of 3000 for faster testing
print(data)

# ==================== Plot Line Chart ====================
fig = go.Figure()

# Add line for close price

# # ----------------------------------------
# # . Plotting Functions
# # ----------------------------------------

fig.add_trace(go.Scatter(
    x=data.index,
    y=data['close'],
    mode='lines',
    name='Close Price',
    line=dict(color='blue')
))

# ==================== Layout Settings ====================
fig.update_layout(
    title='NIFTYBANK Close Price Over Time (1-min)',
    xaxis_title='Time',
    yaxis_title='Price (INR)',
    template='plotly_white',
    height=600
)
# plotly_dark
# # ----------------------------------------
# # . Display Charts
# # ----------------------------------------

fig.show()



