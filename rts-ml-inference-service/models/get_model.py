import os
import pickle
from keras.models import load_model as keras_load_model


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

