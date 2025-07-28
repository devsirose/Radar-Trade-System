import os
import time
import json
import pickle
import numpy as np
import pandas as pd
import psycopg2
import requests

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'port': 5431,
    'dbname': 'market-price',
    'user': 'root',
    'password': 'mysecretpassword'
}

SEQ_LEN = 500

def load_model(symbol):
    path = f"../models/models/{symbol}/model.pkl/model.pkl"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found for symbol: {symbol}")
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_scaler(symbol):
    path = f"../models/models/{symbol}/scaler.pkl/scaler.pkl"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Scaler not found for symbol: {symbol}")
    with open(path, 'rb') as f:
        return pickle.load(f)

def fetch_latest(symbol, interval):
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT * FROM kline 
        WHERE symbol = %s AND interval = %s
        ORDER BY open_time DESC 
        LIMIT %s
    """
    df = pd.read_sql(query, conn, params=(symbol, interval, SEQ_LEN))
    conn.close()
    df = df.sort_values('open_time')
    return df

def get_realtime_price(symbol):

    url = f"https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch price from Binance: {response.text}")

    data = response.json()
    return float(data['price'])

@app.route('/predict/stream', methods=['GET'])
def predict_stream():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '1m')  # default to 1m

    if not symbol:
        return jsonify({'error': 'Missing symbol parameter'}), 400

    try:
        model = load_model(symbol)
        scaler = load_scaler(symbol)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    def generate():
        while True:
            try:
                df = fetch_latest(symbol, interval)
                if df.empty:
                    yield f"data: {json.dumps({'error': 'Empty dataframe'})}\n\n"
                    time.sleep(1)
                    continue

                data = scaler.transform(df[['close']])
                x_input = np.array(data).reshape(1, SEQ_LEN, 1)
                prediction = model.predict(x_input)
                predicted_price = (float(scaler.inverse_transform(prediction)[0][0]) + get_realtime_price(symbol)) / 2

                payload = {
                    'symbol': symbol,
                    'next_price': predicted_price
                }
                yield f"data: {json.dumps(payload)}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            time.sleep(interval)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084)
