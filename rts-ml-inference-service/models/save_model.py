import os
import pickle

def save_model(model, symbol):
    dir_path = f"../models/{symbol}"
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, "model.pkl")
    with open(path, 'wb') as f:
        pickle.dump(model, f)

def save_scaler(scaler, symbol):
    dir_path = f"../models/{symbol}"
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, "scaler.pkl")
    with open(path, 'wb') as f:
        pickle.dump(scaler, f)
