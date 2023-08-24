import ccxt
import pandas as pd
import Key_File as keys_module
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

traiding_pair= 'uBTCUSD'
short_sma_period = 7
long_sma_period = 20
trailing_stop_distance = 2

class TradingBot:
    def __init__(self, exchange, trading_pair, short_sma_period=7, long_sma_period=20, trailing_stop_distance=2):
        self.exchange = exchange
        self.trading_pair = trading_pair
        self.short_sma_period = short_sma_period
        self.long_sma_period = long_sma_period
        self.trailing_stop_distance = trailing_stop_distance
        self.current_order = None
        self.last_price = None
        
        
    def fetch_data(self, limit=100):
        ohlcv_data = self.exchange.fetch_ohlcv(self.trading_pair, limit=limit)
        trade_data = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        trade_data['timestamp'] = pd.to_datetime(trade_data['timestamp'], unit='ms')
        return trade_data

    def calculate_sma(self, trade_data):
        trade_data[f'sma{self.short_sma_period}'] = trade_data['close'].rolling(self.short_sma_period).mean()
        trade_data[f'sma{self.long_sma_period}'] = trade_data['close'].rolling(self.long_sma_period).mean()
        return trade_data

    def generate_signal(self, trade_data):
        if trade_data.iloc[-2][f'sma{self.short_sma_period}'] < trade_data.iloc[-2][f'sma{self.long_sma_period}'] and trade_data.iloc[-1][f'sma{self.short_sma_period}'] > trade_data.iloc[-1][f'sma{self.long_sma_period}']:
            return 'buy'
        elif trade_data.iloc[-2][f'sma{self.short_sma_period}'] > trade_data.iloc[-2][f'sma{self.long_sma_period}'] and trade_data.iloc[-1][f'sma{self.short_sma_period}'] < trade_data.iloc[-1][f'sma{self.long_sma_period}']:
            return 'sell'
        return None

    def execute_order(self, signal):
        if signal == 'buy':
            self.current_order = {'type': 'buy', 'price': self.last_price}
        elif signal == 'sell':
            self.current_order = None

    def manage_trade(self, trade_data):
        if self.current_order:
            if self.current_order['type'] == 'buy':
                if trade_data['close'].iloc[-1] > self.current_order['price'] + self.trailing_stop_distance:
                    self.current_order['price'] = trade_data['close'].iloc[-1]
                elif trade_data['close'].iloc[-1] < self.current_order['price'] - self.trailing_stop_distance:
                    self.execute_order('sell')
        
    def run(self):
        trade_data = self.fetch_data()
        trade_data = self.calculate_sma(trade_data)
        signal = self.generate_signal(trade_data)
        if signal:
            self.execute_order(signal)
        self.manage_trade(trade_data)
        return trade_data   

    

class PhemexTradingBot(TradingBot):
    def __init__(self, api_key, api_secret, trading_pair, short_sma_period=7, long_sma_period=20, trailing_stop_distance=2, order_size=1):
        exchange = ccxt.phemex({
            'apiKey': api_key,
            'secret': api_secret
        })
        super().__init__(exchange, trading_pair, short_sma_period, long_sma_period, trailing_stop_distance)
        self.order_size = order_size

    def execute_order(self, signal):
        if signal == 'buy':
            self.current_order = self.exchange.create_market_buy_order(self.trading_pair, self.order_size)
            logging.info(f"Entered BUY trade at {self.current_order['price']}")
        elif signal == 'sell' and self.current_order:
            self.current_order = self.exchange.create_market_sell_order(self.trading_pair, self.order_size)
            logging.info(f"Exited trade at {self.current_order['price']}")
            self.current_order = None



class OptimizedPhemexTradingBot(PhemexTradingBot):

    def fetch_data(self, limit=100, timeframe='5m'):
        ohlcv_data = self.exchange.fetch_ohlcv(self.trading_pair, timeframe=timeframe, limit=limit)
        trade_data = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        trade_data['timestamp'] = pd.to_datetime(trade_data['timestamp'], unit='ms')
        return trade_data

    def manage_trade(self, trade_data):
        if self.current_order:
            if self.current_order['type'] == 'buy':
                if trade_data['close'].iloc[-1] > self.current_order['price'] + self.trailing_stop_distance:
                    self.current_order['price'] = trade_data['close'].iloc[-1]
                elif trade_data['close'].iloc[-1] < self.current_order['price'] - self.trailing_stop_distance:
                    self.execute_order('sell')

    def execute_order(self, signal):
        if signal == 'buy' and not self.current_order:
            self.current_order = self.exchange.create_market_buy_order(self.trading_pair, 0.01)
            logging.info(f"Entered BUY trade at {self.current_order['price']}")
        elif signal == 'sell' and self.current_order:
            self.current_order = self.exchange.create_market_sell_order(self.trading_pair, 0.01)
            logging.info(f"Exited trade at {self.current_order['price']}")
            self.current_order = None

    def check_trade_status(self):
        if self.current_order:
            logging.info(f"In a trade. Order type: {self.current_order['type']}, Price: {self.current_order['price']}")
        else:
            logging.info("Not in a trade currently.")

    def run(self):
        while True:
            try:
                trade_data = self.fetch_data(limit=100, timeframe='5m')
                trade_data = self.calculate_sma(trade_data)
                signal = self.generate_signal(trade_data)
                if signal:
                    self.execute_order(signal)
                self.manage_trade(trade_data)
                self.check_trade_status()
                logging.info(f"Bot ran successfully. Last close price: {trade_data['close'].iloc[-1]}")
            except ccxt.NetworkError as e:
                logging.error(f"Network Error: {e}")
                time.sleep(10)
            except ccxt.ExchangeError as e:
                logging.error(f"Exchange Error: {e}")
                time.sleep(10)
            except Exception as e:
                logging.error(f"Unexpected Error: {e}")
                time.sleep(10)
            time.sleep(60)  # Run the bot every 15 minutes


# To run the bot:
bot = OptimizedPhemexTradingBot(keys_module.key, keys_module.secret, 'uBTCUSD', order_size=1)
bot.run()