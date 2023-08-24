import pandas as pd
from backtesting import Backtest
from backtesting.lib import SignalStrategy, TrailingStrategy
from backtesting.test import SMA

# Load CSV data into a DataFrame and parse dates
trade_data = pd.read_csv('modified_data.csv', parse_dates=['Date'])

## Drop rows with missing values
trade_data.dropna(inplace=True)
trade_data.fillna(0, inplace=True)
trade_data.index.is_unique
trade_data.index.has_duplicates
# Set the 'Date' column as the index
trade_data.set_index('Date', inplace=True)


class SmaCross(SignalStrategy, TrailingStrategy):
    short_sma_period = 7
    long_sma_period = 20
    
    
    
    def init(self):
        super().init()
        
        sma1 = self.I(SMA, self.data.Close, self.short_sma_period)
        sma2 = self.I(SMA, self.data.Close, self.long_sma_period)
        
        
        signal = (pd.Series(sma1) > sma2 ).astype(int).diff().fillna(0)
        signal = signal.replace(-1, 0)
        
        entry_size = signal * 0.95
                
        self.set_signal(entry_size=entry_size)
        self.set_trailing_sl(2)

# Convert 'Close' column to numeric
trade_data['Close'] = pd.to_numeric(trade_data['Close'], errors='coerce')

# Convert index to numeric
trade_data.index = pd.to_numeric(trade_data.index, errors='coerce')

bt = Backtest(trade_data, SmaCross,cash = 100_000, commission=0.002)
stats = bt.run()
print(stats)
# Step 7: Plot the backtest results
bt.plot()  # Resample to 1-hour intervals
