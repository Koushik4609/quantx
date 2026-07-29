import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice
import json

class Backtester:
    def __init__(self, symbol: str, timeframe: str = "1d", period: str = "1y"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.period = period
        self.data = pd.DataFrame()

    def fetch_data(self):
        ticker = yf.Ticker(self.symbol)
        # timeframe format in yf is '1d', '1wk', '1mo'
        interval = self.timeframe if self.timeframe in ['1d', '1wk', '1mo'] else '1d'
        self.data = ticker.history(period=self.period, interval=interval)
        if self.data.empty:
            raise ValueError(f"No data found for symbol {self.symbol}")
        
    def add_indicator(self, ind_name: str, timeperiod: int = 14):
        df = self.data
        if ind_name == "RSI":
            indicator = RSIIndicator(close=df['Close'], window=timeperiod)
            df[f'RSI_{timeperiod}'] = indicator.rsi()
        elif ind_name == "MACD":
            indicator = MACD(close=df['Close'])
            df['MACD'] = indicator.macd_diff() # Histogram
        elif ind_name == "EMA":
            indicator = EMAIndicator(close=df['Close'], window=timeperiod)
            df[f'EMA_{timeperiod}'] = indicator.ema_indicator()
        elif ind_name == "SMA":
            indicator = SMAIndicator(close=df['Close'], window=timeperiod)
            df[f'SMA_{timeperiod}'] = indicator.sma_indicator()
        elif ind_name == "VWAP":
            indicator = VolumeWeightedAveragePrice(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
            df['VWAP'] = indicator.volume_weighted_average_price()
        elif ind_name == "Bollinger Bands":
            indicator = BollingerBands(close=df['Close'], window=timeperiod)
            df[f'BB_High_{timeperiod}'] = indicator.bollinger_hband()
            df[f'BB_Low_{timeperiod}'] = indicator.bollinger_lband()

    def evaluate_condition(self, row, cond):
        ind = cond['indicator']
        val = cond['value']
        op = cond['operator']
        tp = cond.get('timeperiod', 14)
        
        col_name = ind
        if ind in ["RSI", "EMA", "SMA", "Bollinger Bands"]:
            if ind == "Bollinger Bands":
                # Simplified check for bb, assumes checking close vs bands
                pass
            else:
                col_name = f"{ind}_{tp}"
        
        if col_name not in self.data.columns:
            self.add_indicator(ind, tp)
            
        row_val = row.get(col_name, None)
        if row_val is None or pd.isna(row_val):
            return False
            
        if op == ">": return row_val > val
        if op == "<": return row_val < val
        if op == "==": return row_val == val
        if op == ">=": return row_val >= val
        if op == "<=": return row_val <= val
        
        return False

    def run(self, conditions_dict: dict):
        if self.data.empty:
            self.fetch_data()
            
        entry_conds = conditions_dict.get("entry", [])
        exit_conds = conditions_dict.get("exit", [])
        
        # Pre-calculate required indicators
        for cond in entry_conds + exit_conds:
            self.add_indicator(cond['indicator'], cond.get('timeperiod', 14))
            
        cash = 10000.0
        initial_cash = cash
        position = 0
        trades = []
        peak = initial_cash
        max_dd = 0.0
        win_trades = 0
        total_trades = 0
        entry_price = 0
        
        for date, row in self.data.iterrows():
            date_str = str(date).split(" ")[0]
            price = row['Close']
            
            # Check entry
            if position == 0 and entry_conds:
                enter = all(self.evaluate_condition(row, c) for c in entry_conds)
                if enter:
                    shares = int(cash // price)
                    if shares > 0:
                        cost = shares * price
                        cash -= cost
                        position = shares
                        entry_price = price
                        trades.append({"type": "Buy", "date": date_str, "price": float(price), "shares": shares})
                        
            # Check exit
            elif position > 0 and exit_conds:
                exit_pos = all(self.evaluate_condition(row, c) for c in exit_conds)
                if exit_pos:
                    revenue = position * price
                    cash += revenue
                    if price > entry_price:
                        win_trades += 1
                    total_trades += 1
                    trades.append({"type": "Sell", "date": date_str, "price": float(price), "shares": position})
                    position = 0
                    
            # Track max drawdown
            current_value = cash + (position * price)
            if current_value > peak:
                peak = current_value
            dd = (peak - current_value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
                
        # Close position at end of period
        if position > 0:
            price = self.data.iloc[-1]['Close']
            date_str = str(self.data.index[-1]).split(" ")[0]
            cash += position * price
            if price > entry_price:
                win_trades += 1
            total_trades += 1
            trades.append({"type": "Sell", "date": date_str, "price": float(price), "shares": position})
            position = 0
            
        total_return = ((cash - initial_cash) / initial_cash) * 100
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        return {
            "total_return": float(total_return),
            "win_rate": float(win_rate),
            "max_drawdown": float(max_dd * 100),
            "trades": trades
        }
