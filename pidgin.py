import ccxt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import streamlit as st

# Initialize Binance API with your API keys
binance = ccxt.binance({
    'apiKey': 'jvkno680FsAjxFmjtbfFATjsE6ZX6b64XWDYAO83Qtujx8hpPz3y4Hn0HSOWN9zH',
    'secret': 'xtow50oJLhVwcpDoUUS0zf6hy4dy4bRfEkpBmHvYRrXOJNuUL5QqH3iiIz1mkrqs'
})

# Define trading pairs to be analyzed
pairs = [
    ('BTC/USDT', 'ETH/BTC', 'ETH/USDT'),
    ('BTC/USDT', 'BNB/BTC', 'BNB/USDT'),
    ('ETH/USDT', 'BNB/ETH', 'BNB/USDT'),
    # Add more trading pairs as needed
]

# Define the time window for historical data (in minutes)
time_window = 60

# Fetch historical data for a trading pair
def get_historical_data(symbol):
    ohlcvs = binance.fetch_ohlcv(symbol, '1m', limit=time_window)
    return np.array([item[4] for item in ohlcvs]).reshape(-1, 1)

# Normalize the data using MinMaxScaler
def normalize_data(data):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data)

# Split the data into training and testing sets
def split_data(data, train_ratio=0.8):
    train_size = int(len(data) * train_ratio)
    train_data = data[:train_size, :]
    test_data = data[train_size:, :]
    return train_data, test_data

# Create the RNN model
def create_model(n_steps):
    model = Sequential()
    model.add(LSTM(64, activation='relu', input_shape=(n_steps, 1)))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

# Train the model
def train_model(model, X_train, y_train, n_epochs=100, batch_size=32):
    return model.fit(X_train, y_train, epochs=n_epochs, batch_size=batch_size, verbose=0)

# Predict the future price based on historical data
def predict_future_price(model, data, n_steps):
    last_n_prices = data[-n_steps:]
    input_data = np.array(last_n_prices).reshape(1, n_steps, 1)
    return model.predict(input_data)[0][0]

# Define the trading fee (default Binance fee is 0.001)
fee = 0.001

st.title("Triangular Arbitrage Trading Bot")

# Loop through all available trading pairs and find the best triangular arbitrage opportunities
for symbols in pairs:
    st.header(f"Trading Pair: {symbols[0]}, {symbols[1]}, {symbols[2]}")
    tickers = {}
    for symbol in symbols:
        tickers[symbol] = binance.fetch_ticker(symbol)

    # Calculate potential profits for each triangular arbitrage opportunity
    prices = [float(tickers[symbol]['bid']) for symbol in symbols]
    normalized_prices = normalize_data(np.array(prices).reshape(-1, 1))
    train_data, test_data = split_data(normalized_prices)
    X_train, y_train = train_data[:-1], train_data[1:]
    n_steps = len(X_train)
    model = create_model(n_steps)
    train_model(model, X_train, y_train)
    future_price = predict_future_price(model, normalized_prices, n_steps)
    profit = 1.0
    for i in range(len(symbols)):
        j = (i + 1) % len(symbols)
        k = (j + 1) % len(symbols)

        # Calculate the potential profit for this triangular arbitrage opportunity
        buy_price = float(tickers[symbols[i]]['ask'])
        sell_price = float(tickers[symbols[j]]['bid'])
        exchange_rate = future_price / normalized_prices[j][0]
        potential_profit = (sell_price / buy_price) * exchange_rate * (1 - fee) ** 3 - 1

        # Update the best arbitrage opportunity if this one is more profitable
        if potential_profit > profit:
            profit = potential_profit
            buy_symbol = symbols[i]
            sell_symbol = symbols[j]
            exchange_symbol = symbols[k]
            buy_price = float(tickers[buy_symbol]['ask'])
            sell_price = float(tickers[sell_symbol]['bid'])
            exchange_rate = future_price / normalized_prices[j][0]
            buy_amount = 1.0
            sell_amount = buy_amount * buy_price
            exchange_amount = sell_amount * sell_price
            profit_amount = exchange_amount * exchange_rate - buy_amount
            st.write(f"Buy {buy_symbol} @ {buy_price:.8f}")
            st.write(f"Sell {sell_symbol} @ {sell_price:.8f}")
            st.write(f"Exchange {exchange_symbol} @ {exchange_rate:.8f}")
            st.write(f"Potential profit: {profit_amount:.8f} {buy_symbol}")

