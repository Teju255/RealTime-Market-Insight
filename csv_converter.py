import pandas as pd
import plotly.graph_objects as go

# ==================== Read Data From CSV ====================
# Replace API fetch with CSV import
data = pd.read_csv("AXISBANK.csv")

# Convert 'date' column to datetime and set as index
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace=True)

# ==================== Plot Line Chart ====================
fig = go.Figure()

# Add line for close price
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

# ==================== Show Chart ====================
fig.show()


