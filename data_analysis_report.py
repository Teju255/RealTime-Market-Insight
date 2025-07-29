import credentials as crs
from fyers_apiv3 import fyersModel
import pandas as pd
import datetime as dt
import logging
import os
import csv
import matplotlib.pyplot as plt

# Logging setup
logging.basicConfig(filename='fyers_backtest.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class FyersDataFetcher:
    def __init__(self, client_id, access_token):
        self.fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

    def get_historical_data(self, symbol, resolution, days_back):
        from_date = (dt.datetime.now() - dt.timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = dt.datetime.now().strftime('%Y-%m-%d')

        data = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": '1',
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": 1,
        }

        response = self.fyers.history(data=data)
        if 'candles' not in response:
            raise Exception(f"'candles' not found in response: {response}")

        df = pd.DataFrame(response['candles'], columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        df.set_index('date', inplace=True)
        return df

def log_trade_to_csv(trades):
    file = 'logbook.csv'
    with open(file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Action", "Entry Price", "Exit Price", "Profit/Loss", "Exit Reason"])
        for trade in trades:
            if trade["exit_price"] is not None:
                profit = trade["exit_price"] - trade["entry_price"] if trade["action"] == "BUY" else trade["entry_price"] - trade["exit_price"]
                writer.writerow([trade["date"].strftime('%Y-%m-%d'), trade["action"], trade["entry_price"], trade["exit_price"], round(profit, 2), trade["exit_reason"]])

def backtest_strategy(ticker, target_percentage, stop_loss_percentage, total_days):
    historical_data = fyers_data.get_historical_data(ticker, '15', total_days)

    trades = []
    trade_active = False
    entry_price = 0.0
    direction = None
    target_hits = 0
    stop_loss_hits = 0

    grouped = historical_data.groupby(historical_data.index.date)

    for day, group in grouped:
        if len(group) < 2:
            continue

        first_candle = group.iloc[0]
        day_data = group.iloc[1:]

        first_high = first_candle['high']
        first_low = first_candle['low']

        for _, row in day_data.iterrows():
            if not trade_active:
                if row['high'] > first_high:
                    direction = "BUY"
                    entry_price = first_high
                    trade_active = True
                    trades.append({"date": row.name, "action": "BUY", "entry_price": entry_price, "exit_price": None, "exit_reason": None})
                elif row['low'] < first_low:
                    direction = "SELL"
                    entry_price = first_low
                    trade_active = True
                    trades.append({"date": row.name, "action": "SELL", "entry_price": entry_price, "exit_price": None, "exit_reason": None})
            else:
                target_price = entry_price * (1 + target_percentage / 100) if direction == "BUY" else entry_price * (1 - target_percentage / 100)
                stop_loss_price = entry_price * (1 - stop_loss_percentage / 100) if direction == "BUY" else entry_price * (1 + stop_loss_percentage / 100)

                if (direction == "BUY" and row['close'] >= target_price) or (direction == "SELL" and row['close'] <= target_price):
                    trades[-1].update({"exit_price": row['close'], "exit_reason": "Target Hit"})
                    trade_active = False
                    target_hits += 1
                elif (direction == "BUY" and row['close'] <= stop_loss_price) or (direction == "SELL" and row['close'] >= stop_loss_price):
                    trades[-1].update({"exit_price": row['close'], "exit_reason": "Stop Loss Hit"})
                    trade_active = False
                    stop_loss_hits += 1

    return trades, target_hits, stop_loss_hits

def analyze_results(trades, target_hits, stop_loss_hits, chart_type):
    total_profit = 0
    grouped_data = {}

    for trade in trades:
        if trade["exit_price"] is not None:
            if chart_type == 'M':
                key = trade["date"].strftime('%Y-%m')
            else:
                key = trade["date"].strftime('%Y-%m-%d')

            profit = trade["exit_price"] - trade["entry_price"] if trade["action"] == "BUY" else trade["entry_price"] - trade["exit_price"]
            total_profit += profit
            if key not in grouped_data:
                grouped_data[key] = {"profit": 0, "target": 0, "stoploss": 0}
            grouped_data[key]["profit"] += profit
            if trade["exit_reason"] == "Target Hit":
                grouped_data[key]["target"] += 1
            elif trade["exit_reason"] == "Stop Loss Hit":
                grouped_data[key]["stoploss"] += 1

    print("\n----- Backtest Results -----")
    print(f"Total Trades: {len(trades)}")
    print(f"Target Hits: {target_hits}")
    print(f"Stop Loss Hits: {stop_loss_hits}")
    print(f"Net Profit: ₹{total_profit:.2f}")
    print("-----------------------------")

    # Chart
    keys = list(grouped_data.keys())
    profits = [grouped_data[k]['profit'] for k in keys]
    targets = [grouped_data[k]['target'] for k in keys]
    stoplosses = [grouped_data[k]['stoploss'] for k in keys]

    fig, ax1 = plt.subplots(figsize=(12, 7))
    ax1.grid(True, linestyle='--', alpha=0.5)

    bars = ax1.bar(keys, profits, color='skyblue', edgecolor='black', label='Profit/Loss')
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 5, f'₹{height:.0f}', ha='center', va='bottom')

    ax1.set_ylabel('Profit/Loss (₹)')
    ax1.set_title('Profit/Loss Chart with Target and Stoploss Hits')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(keys, targets, color='green', marker='o', label='Target Hits')
    ax2.plot(keys, stoplosses, color='red', marker='x', label='Stoploss Hits')
    ax2.set_ylabel('Hits Count')
    ax2.legend(loc='upper right')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    client_id = crs.client_id
    access_token = open('access.txt').read().strip()
    global fyers_data
    fyers_data = FyersDataFetcher(client_id, access_token)

    ticker = input("Enter the symbol (e.g., NSE:NIFTYBANK-INDEX): ").strip()
    target_percentage = float(input("Enter target percentage (e.g., 1 for 1%): "))
    stop_loss_percentage = float(input("Enter stop-loss percentage (e.g., 1 for 1%): "))
    total_days = int(input("How many days back do you want to backtest?: "))
    chart_type = input("Do you want a Monthly or Daily chart? (M/D): ").strip().upper()

    try:
        trades, target_hits, stop_loss_hits = backtest_strategy(ticker, target_percentage, stop_loss_percentage, total_days)
        log_trade_to_csv(trades)
        analyze_results(trades, target_hits, stop_loss_hits, chart_type)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()





# 1:1 R:R 100 days  Monthly
# Enter the symbol (e.g., NSE:NIFTYBANK-INDEX): NSE:NIFTYBANK-INDEX
# Enter target percentage (e.g., 1 for 1%): 1
# Enter stop-loss percentage (e.g., 1 for 1%): 1
# How many days back do you want to backtest?: 100
# Do you want a Monthly or Daily chart? (M/D): D