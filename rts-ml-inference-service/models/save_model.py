import os
import pickle

def save_model(model, symbol):
    print(symbol)
    dir_path = os.path.join(os.path.dirname(__file__), f"../models/models/{symbol}")
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, "model.pkl")

    with open(path, 'wb') as f:
        pickle.dump(model, f)

def save_scaler(scaler, symbol):
    dir_path = os.path.join(os.path.dirname(__file__), f"../models/models/{symbol}")
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, "scaler.pkl")
    with open(path, 'wb') as f:
        pickle.dump(scaler, f)