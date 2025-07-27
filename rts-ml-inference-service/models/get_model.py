import os
import pickle
from keras.models import load_model as keras_load_model


def load_model(symbol):
    dir_path = f"../models/{symbol}"
    model_path = os.path.join(dir_path, "model.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found for symbol: {symbol}")

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model


def load_scaler(symbol):
    dir_path = f"../models/{symbol}"
    scaler_path = os.path.join(dir_path, "scaler.pkl")

    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler not found for symbol: {symbol}")

    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    return scaler

