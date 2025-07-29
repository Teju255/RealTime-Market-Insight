

from fyers_apiv3.FyersWebsocket import data_ws
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
import csv
import os
import threading

# === CSV Setup ===
csv_file = 'fyers_data.csv'
csv_header = ['Time', 'Symbol', 'LTP']
if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

# === Data Store ===
max_len = 100
timestamps = deque(maxlen=max_len)
ltps = deque(maxlen=max_len)

symbol_name = 'MCX:CRUDEOILM25MAYFUT'
latest_ltp = [0]

def onmessage(message):
    if isinstance(message, dict) and 'ltp' in message:
        current_time = time.strftime('%H:%M:%S')
        ltp = message['ltp']
        latest_ltp[0] = ltp
        timestamps.append(current_time)
        ltps.append(ltp)

        print(f"[{current_time}] {symbol_name} LTP: {ltp}")
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([current_time, symbol_name, ltp])

def onerror(message):
    print("Error:", message)

def onclose(message):
    print("Connection closed:", message)

def onopen():
    data_type = "SymbolUpdate"
    symbols = [symbol_name]
    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()

# === Read Token ===
with open('access.txt') as f:
    access_token = f.read()

# === WebSocket Setup ===
fyers = data_ws.FyersDataSocket(
    access_token=access_token,
    log_path="",
    litemode=False,
    write_to_file=False,
    reconnect=True,
    on_connect=onopen,
    on_close=onclose,
    on_error=onerror,
    on_message=onmessage
)

# === Chart Setup ===
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], '-o', color='cyan', markersize=4, label='LTP')

# Floating price label above the last point
price_text = ax.text(0, 0, '', fontsize=10, color='yellow', ha='center', va='bottom', fontweight='bold',
                     bbox=dict(facecolor='black', edgecolor='yellow'))

# Title and labels
ax.set_title(f'Live Price - {symbol_name}', fontsize=14, color='white')
ax.set_xlabel('Time', color='white')
ax.set_ylabel('Price', color='white')

# === Move Y-Axis to Right ===
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")

# Styling
ax.tick_params(colors='white')
ax.legend()
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)

# === Enable Grid Lines ===
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout()

def update_plot(frame):
    if timestamps and ltps:
        line.set_data(range(len(ltps)), ltps)
        ax.set_xlim(0, len(ltps))
        ax.set_xticks(range(len(timestamps)))
        ax.set_xticklabels(timestamps, rotation=45, ha='right', fontsize=8)
        ax.set_ylim(min(ltps) - 5, max(ltps) + 5)

        # Update floating price label
        x = len(ltps) - 1
        y = ltps[-1]
        price_text.set_position((x, y + 2))
        price_text.set_text(f'₹ {y:.2f}')

    return line, price_text

ani = animation.FuncAnimation(fig, update_plot, interval=1000)

# === Start WebSocket Thread ===
threading.Thread(target=fyers.connect).start()

# === Show Chart ===
plt.show()









