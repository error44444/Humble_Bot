
# Trading Bot and Backtesting Suite
#### Video Demo: https://youtu.be/aa9LAuaQNns
#### Description:

The project is structured around a trading bot (`humblebot3`) and a backtesting script (`humble2`).


---

**API Key Setup:**
To set up your API keys for the bot, visit [Phemex Exchange](https://phemex.com/account/referral/invite-friends-entry?referralCode=GW7R43).
---

**1. Trading Bot (`humblebot3`):**
- **Purpose:** 
  This bot interacts with a cryptocurrency exchange to fetch trading data, calculate simple moving averages (SMA), and make trading decisions based on those averages.
  
- **Key Components:**
  - **Initialization**: Initializes with exchange details, trading pair (e.g., 'uBTCUSD'), short and long SMA periods, and a trailing stop distance.
  - **Data Fetching**: Fetches Open-High-Low-Close-Volume (OHLCV) data for the given trading pair.
  - **SMA Calculation**: Calculates the short and long SMAs for the fetched data.
  - **Trading Signal Generation**: Generates a 'buy' signal if the short SMA crosses above the long SMA and a 'sell' signal if the short SMA crosses below the long SMA.
  - **Trade Execution**: Executes the trade based on the generated signal and manages the trade to check if the trailing stop is hit.
  - **Error Handling**: Equipped with error handling mechanisms to deal with network errors, exchange errors, and other unexpected errors.

- **Logic:** 
  Uses a crossover strategy where a 'buy' signal is generated when the short-term SMA (7 days by default) crosses above the long-term SMA (20 days by default), and a 'sell' signal when the reverse happens.

---

**2. Backtest (`humble2`):**
- **Purpose:** 
  Designed to test the trading strategy on historical data to understand its performance without actually executing trades in real-time.
  
- **Key Components:**
  - **Data Loading**: Loads CSV trading data into a DataFrame with the 'Date' column as the index.
  - **Strategy Class (SmaCross)**: Defines the trading strategy logic. Inherits from `SignalStrategy` and `TrailingStrategy` from the `backtesting` library.
  - **Signal Generation**: Calculates when the short SMA crosses the long SMA to generate buy/sell signals.
  - **Backtest Execution**: Uses the `Backtest` class from the `backtesting` library to simulate trades based on historical data and the defined strategy.
  
- **Logic:** 
  Uses the same SMA crossover strategy defined in the trading bot. Simulates trades on historical data to evaluate the strategy's performance.

- **Results:** 
  Upon completion, it provides performance metrics like net profit, number of trades, win rate, and more, offering insights into the strategy's effectiveness.

---

**Note:** The specifics of the results and exact metrics would depend on the historical data used and the exact configurations of the SMA periods.

This README offers an overview of the bot and backtest. For a detailed understanding and exact logic, refer to the code of `humblebot3` and `humble2`. Note: For backtesting, the historical data was downloaded from Yahoo Finance's crypto historical data.

