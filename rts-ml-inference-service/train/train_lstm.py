import argparse
import os
import pickle
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler


env_profile = os.getenv("APP_PROFILE", "local")
load_dotenv(f".env.{env_profile}")

def save_model(model, symbol):

    dir_path = os.path.join(os.path.dirname(__file__), f"../models/{symbol}")
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, "model.pkl")
    with open(path, 'wb') as f:
        pickle.dump(model, f)

def save_scaler(scaler, symbol):
    dir_path = os.path.join(os.path.dirname(__file__), f"../models/{symbol}")
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, "scaler.pkl")
    with open(path, 'wb') as f:
        pickle.dump(scaler, f)


SEQ_LEN=500

BINANCE_BASE_URL = "https://api.binance.com/api/v3/klines"


def fetch_latest(symbol, interval, limit=500):
    params = {
        'symbol': symbol.upper(),
        'interval': interval,
        'limit': limit,
    }

    response = requests.get(BINANCE_BASE_URL, params=params)
    response.raise_for_status()
    raw_klines = response.json()

    df = pd.DataFrame(raw_klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])

    # Convert timestamp to datetime and cast types
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df = df.sort_values("open_time")
    return df

def preprocess(df):
    df = df[['close']]
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)

    X, y = [], []
    for i in range(SEQ_LEN, len(scaled)):
        X.append(scaled[i - SEQ_LEN:i])
        y.append(scaled[i])

    X = np.array(X).reshape(-1, SEQ_LEN, 1)
    y = np.array(y)
    return X, y, scaler


def ensure_model_dirs(symbol):
    model_dir = f'./models/{symbol}'
    os.makedirs(model_dir, exist_ok=True)
    return model_dir


def train(symbol, interval='1m'):
    df = fetch_latest(symbol, interval, SEQ_LEN + 1)
    X, y, scaler = preprocess(df)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(SEQ_LEN, 1)),
        LSTM(50),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=32, verbose=1)

    model_dir = ensure_model_dirs(symbol)
    save_model(model, os.path.join(model_dir))
    save_scaler(scaler, os.path.join(model_dir))

    print(f"✅ Model trained and saved for symbol: {symbol}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Symbol in uppercase (e.g., BTCUSDT)')
    parser.add_argument('--interval', required=False, help='Symbol in uppercase (e.g., BTCUSDT)')
    args = parser.parse_args()

    train(args.symbol, args.interval)
