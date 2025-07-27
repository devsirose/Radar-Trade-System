import os
import pandas as pd
import numpy as np
import psycopg2
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from models.save_model import save_model, save_scaler
import argparse

DB_CONFIG = {
    'host': 'localhost',
    'port': 5431,
    'dbname': 'market-price',
    'user': 'root',
    'password': 'mysecretpassword'
}

SEQ_LEN = 500


def load_data(symbol, interval):
    conn = psycopg2.connect(**DB_CONFIG)
    query = f"""
        SELECT * FROM kline 
        WHERE symbol = %s
        AND interval = %s 
        ORDER BY open_time DESC
        LIMIT {SEQ_LEN * 2}
    """
    df = pd.read_sql(query, conn, params=(symbol, interval,))
    conn.close()

    if len(df) < SEQ_LEN + 1:
        raise ValueError(f"Not enough data for symbol {symbol}. Required at least {SEQ_LEN + 1} rows.")

    df = df.sort_values('open_time', ascending=True)
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
    df = load_data(symbol, interval)
    X, y, scaler = preprocess(df)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(SEQ_LEN, 1)),
        LSTM(50),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=32, verbose=1)

    model_dir = ensure_model_dirs(symbol)
    save_model(model, os.path.join(model_dir, 'model.pkl'))
    save_scaler(scaler, os.path.join(model_dir, 'scaler.pkl'))

    print(f"✅ Model trained and saved for symbol: {symbol}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Symbol in uppercase (e.g., BTCUSDT)')
    parser.add_argument('--interval', required=False, help='Symbol in uppercase (e.g., BTCUSDT)')
    args = parser.parse_args()

    train(args.symbol, args.interval)
