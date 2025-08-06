import os
import json
import time
import pickle
import numpy as np
import redis
import pandas as pd
import requests

from flask import Flask, Response, request, jsonify
from keras.models import load_model as keras_load_model
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# --- Config ---
SEQ_LEN = 60  # số nến cho mỗi lần dự đoán
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

# --- Load model ---
def load_model(symbol):
    path = os.path.join(os.path.dirname(__file__), f"../models/models/{symbol}/model.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found for symbol: {symbol}")
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_scaler(symbol):
    path = os.path.join(os.path.dirname(__file__), f"../models/models/{symbol}/scaler.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Scaler not found for symbol: {symbol}")
    with open(path, 'rb') as f:
        return pickle.load(f)

# --- Fetch nến từ Binance ---
def fetch_latest(symbol, interval, limit=SEQ_LEN):
    url = f'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol.upper(),
        'interval': interval,
        'limit': limit
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close',
            'volume', 'close_time', 'quote_asset_volume',
            'number_of_trades', 'taker_buy_base_vol',
            'taker_buy_quote_vol', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"[ERROR] Failed to fetch candles: {e}")
        return pd.DataFrame()

def interval_to_ttl(interval: str) -> int:
    unit = interval[-1]
    value = int(interval[:-1])

    if unit == 'm':  # minutes
        return value * 60
    elif unit == 'h':  # hours
        return value * 60 * 60
    elif unit == 'd':  # days
        return value * 60 * 60 * 24
    else:
        raise ValueError(f"Unsupported interval unit: {unit}")


# --- API dự đoán giá với cache Redis ---
@app.route('/api/v1/ml-inference/predict/stream', methods=['GET'])
def predict_stream():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '1m')  # default to 1m

    if not symbol:
        return jsonify({'error': 'Missing symbol parameter'}), 400

    redis_key = f'kline.updates:predict:{symbol.lower()}:{interval}'

    try:
        model = load_model(symbol)
        scaler = load_scaler(symbol)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    def generate():
        while True:
            try:
                # 1. Check Redis cache
                cached_data = redis_client.get(redis_key)
                if cached_data:
                    print(f"[CACHE HIT] key={redis_key}")
                    yield f"data: {cached_data.decode()}\n\n"
                    time.sleep(30)
                    continue
                else:
                    print(f"[CACHE MISS] key={redis_key}")

                # 2. Nếu không có trong Redis → fetch + predict
                df = fetch_latest(symbol, interval, SEQ_LEN)
                if df.empty:
                    yield f"data: {json.dumps({'error': 'Empty dataframe'})}\n\n"
                    time.sleep(30)
                    continue

                data = scaler.transform(df[['close']])
                x_input = np.array(data).reshape(1, SEQ_LEN, 1)
                prediction = model.predict(x_input)
                predicted_price = float(scaler.inverse_transform(prediction)[0][0])

                payload = {
                    'symbol': symbol,
                    'interval': interval,
                    'next_price': predicted_price,
                    'timestamp': int(time.time() * 1000)
                }

                payload_json = json.dumps(payload)

                ttl = interval_to_ttl(interval)

                redis_client.setex(redis_key, ttl, payload_json)

                yield f"data: {payload_json}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            time.sleep(30)

    return Response(generate(), mimetype='text/event-stream')

from py_eureka_client import eureka_client

# --- Config Eureka ---
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://localhost:8761")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8081))
SERVICE_NAME = os.getenv("SERVICE_NAME", "ml-inference-service")
INSTANCE_IP = os.getenv("INSTANCE_IP", "127.0.0.1")

if __name__ == '__main__':
    # Đăng ký với Eureka
    eureka_client.init(
        eureka_server=EUREKA_SERVER,
        app_name=SERVICE_NAME,
        instance_port=SERVICE_PORT,
        instance_ip=INSTANCE_IP,
        health_check_url=f"http://{INSTANCE_IP}:{SERVICE_PORT}/health",
        home_page_url=f"http://{INSTANCE_IP}:{SERVICE_PORT}/",
        status_page_url=f"http://{INSTANCE_IP}:{SERVICE_PORT}/info",
        data_center_name="MyOwn",
        renewal_interval_in_secs=30,
        duration_in_secs=90,
    )

    # Flask run
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
