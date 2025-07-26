# Hướng Dẫn Implement AI Price Prediction System

## 1. Tổng Quan Kiến Trúc Hệ Thống

```
┌─────────────────┐    ┌─────────────────┐
│   Price Service │    │ Sentiment Service│
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
     ┌─────────────────────────────────┐
     │         Kafka Cluster           │
     │  Topics: price-data, sentiment  │
     └──────────────┬──────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────┐
     │      Feature Engineering        │
     │   (Real-time + Batch)           │
     └──────────────┬──────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────┐
     │       ML Inference              │
     │   (Model Serving + Registry)    │
     └──────────────┬──────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────┐
     │    Prediction Output            │
     │  (WebSocket + REST API)         │
     └─────────────────────────────────┘
```

## 2. Model Registry Implementation

### 2.1 MLflow Model Registry Setup

```python
# model_registry.py
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np

class ModelRegistry:
    def __init__(self, tracking_uri="http://localhost:5000"):
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        
    def register_model(self, model, model_name, metrics, metadata=None):
        """Đăng ký model mới vào registry"""
        with mlflow.start_run():
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log metrics
            for metric_name, value in metrics.items():
                mlflow.log_metric(metric_name, value)
            
            # Log metadata
            if metadata:
                for key, value in metadata.items():
                    mlflow.log_param(key, value)
            
            # Register model
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            mlflow.register_model(model_uri, model_name)
    
    def promote_model(self, model_name, version, stage="Production"):
        """Promote model lên production"""
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
    
    def load_production_model(self, model_name):
        """Load model production hiện tại"""
        model_version = self.client.get_latest_versions(
            model_name, stages=["Production"]
        )[0]
        model_uri = f"models:/{model_name}/{model_version.version}"
        return mlflow.sklearn.load_model(model_uri)
```

### 2.2 Model Management Service

```python
# model_manager.py
import asyncio
import threading
from datetime import datetime, timedelta
import pandas as pd

class ModelManager:
    def __init__(self, registry, refresh_interval=3600):
        self.registry = registry
        self.refresh_interval = refresh_interval
        self.current_models = {}
        self.model_performance = {}
        self.start_refresh_thread()
    
    def start_refresh_thread(self):
        """Tự động refresh models"""
        def refresh_loop():
            while True:
                try:
                    self.refresh_models()
                    time.sleep(self.refresh_interval)
                except Exception as e:
                    print(f"Error refreshing models: {e}")
        
        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
    
    def refresh_models(self):
        """Refresh tất cả models từ registry"""
        model_names = ["price_trend_lstm", "sentiment_classifier", "ensemble_model"]
        
        for model_name in model_names:
            try:
                model = self.registry.load_production_model(model_name)
                self.current_models[model_name] = model
                print(f"Refreshed model: {model_name}")
            except Exception as e:
                print(f"Failed to refresh {model_name}: {e}")
    
    def get_model(self, model_name):
        """Lấy model hiện tại"""
        return self.current_models.get(model_name)
    
    def evaluate_model_performance(self, model_name, predictions, actual):
        """Đánh giá performance model real-time"""
        accuracy = np.mean(predictions == actual)
        timestamp = datetime.now()
        
        if model_name not in self.model_performance:
            self.model_performance[model_name] = []
        
        self.model_performance[model_name].append({
            'timestamp': timestamp,
            'accuracy': accuracy
        })
        
        # Giữ lại chỉ 24h gần nhất
        cutoff_time = timestamp - timedelta(hours=24)
        self.model_performance[model_name] = [
            p for p in self.model_performance[model_name] 
            if p['timestamp'] > cutoff_time
        ]
```

## 3. Feature Engineering Pipeline

### 3.1 Technical Indicators

```python
# technical_indicators.py
import pandas as pd
import numpy as np
import talib

class TechnicalIndicators:
    @staticmethod
    def add_technical_features(df):
        """Thêm các technical indicators"""
        df = df.copy()
        
        # Price-based indicators
        df['sma_5'] = talib.SMA(df['close'], timeperiod=5)
        df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
        df['ema_12'] = talib.EMA(df['close'], timeperiod=12)
        df['ema_26'] = talib.EMA(df['close'], timeperiod=26)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])
        
        # RSI
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['close'])
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume indicators
        df['volume_sma'] = talib.SMA(df['volume'], timeperiod=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price change features
        df['price_change'] = df['close'].pct_change()
        df['price_change_5'] = df['close'].pct_change(5)
        df['volatility_5'] = df['price_change'].rolling(5).std()
        df['volatility_20'] = df['price_change'].rolling(20).std()
        
        return df
    
    @staticmethod
    def add_pattern_features(df):
        """Thêm candlestick patterns"""
        df = df.copy()
        
        # Candlestick patterns
        df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
        df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
        df['engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
        
        return df
```

### 3.2 Feature Engineering Service

```python
# feature_engineering.py
from kafka import KafkaConsumer, KafkaProducer
import json
import pandas as pd
from collections import deque
import numpy as np

class FeatureEngineer:
    def __init__(self, lookback_window=100):
        self.lookback_window = lookback_window
        self.price_buffer = deque(maxlen=lookback_window)
        self.sentiment_buffer = deque(maxlen=50)
        self.technical_indicators = TechnicalIndicators()
        
        # Kafka setup
        self.consumer = KafkaConsumer(
            'price-data', 'sentiment-data',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    
    def process_price_data(self, price_data):
        """Xử lý dữ liệu giá"""
        self.price_buffer.append(price_data)
        
        if len(self.price_buffer) >= 30:  # Minimum for technical indicators
            df = pd.DataFrame(list(self.price_buffer))
            df = self.technical_indicators.add_technical_features(df)
            df = self.technical_indicators.add_pattern_features(df)
            
            return df.iloc[-1].to_dict()  # Return latest row
        return None
    
    def process_sentiment_data(self, sentiment_data):
        """Xử lý dữ liệu sentiment"""
        self.sentiment_buffer.append(sentiment_data)
        
        # Aggregate sentiment over different time windows
        recent_sentiments = list(self.sentiment_buffer)[-10:]  # Last 10 minutes
        
        sentiment_features = {
            'sentiment_avg_10min': np.mean([s['sentiment_score'] for s in recent_sentiments]),
            'sentiment_std_10min': np.std([s['sentiment_score'] for s in recent_sentiments]),
            'sentiment_trend': self.calculate_sentiment_trend(recent_sentiments),
            'news_volume_10min': len(recent_sentiments)
        }
        
        return sentiment_features
    
    def calculate_sentiment_trend(self, sentiments):
        """Tính trend của sentiment"""
        if len(sentiments) < 3:
            return 0
        
        scores = [s['sentiment_score'] for s in sentiments]
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        return slope
    
    def combine_features(self, price_features, sentiment_features):
        """Kết hợp features từ price và sentiment"""
        if price_features and sentiment_features:
            combined = {**price_features, **sentiment_features}
            
            # Thêm interaction features
            combined['price_sentiment_interaction'] = (
                combined.get('price_change', 0) * combined.get('sentiment_avg_10min', 0)
            )
            
            return combined
        return None
    
    def run(self):
        """Chạy feature engineering pipeline"""
        latest_price_features = None
        latest_sentiment_features = None
        
        for message in self.consumer:
            topic = message.topic
            data = message.value
            
            if topic == 'price-data':
                latest_price_features = self.process_price_data(data)
            elif topic == 'sentiment-data':
                latest_sentiment_features = self.process_sentiment_data(data)
            
            # Combine và publish features
            if latest_price_features and latest_sentiment_features:
                combined_features = self.combine_features(
                    latest_price_features, latest_sentiment_features
                )
                
                if combined_features:
                    self.producer.send('ml-features', combined_features)
                    print(f"Published features: {len(combined_features)} features")
```

## 4. Model Training Pipeline

### 4.1 LSTM Model cho Price Prediction

```python
# lstm_model.py
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import StandardScaler

class PriceTrendLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=128, num_layers=2, output_size=3):
        super(PriceTrendLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2)
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
        self.fc1 = nn.Linear(hidden_size, 64)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, output_size)  # 3 classes: down, stable, up
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # LSTM
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Attention mechanism
        lstm_out = lstm_out.transpose(0, 1)  # seq_len, batch, hidden_size
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        attn_out = attn_out.transpose(0, 1)  # batch, seq_len, hidden_size
        
        # Take last output
        last_output = attn_out[:, -1, :]
        
        # Classification layers
        out = self.fc1(last_output)
        out = torch.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return self.softmax(out)

class ModelTrainer:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        
    def prepare_sequences(self, features_df, target_df):
        """Chuẩn bị sequences cho LSTM"""
        # Normalize features
        features_scaled = self.scaler.fit_transform(features_df)
        
        X, y = [], []
        for i in range(self.sequence_length, len(features_scaled)):
            X.append(features_scaled[i-self.sequence_length:i])
            y.append(target_df.iloc[i])
        
        return np.array(X), np.array(y)
    
    def create_target(self, price_df, threshold=0.01):
        """Tạo target labels từ price changes"""
        price_changes = price_df['close'].pct_change().shift(-1)  # Next period change
        
        # 3 classes: 0=down, 1=stable, 2=up
        targets = []
        for change in price_changes:
            if change < -threshold:
                targets.append(0)  # Down
            elif change > threshold:
                targets.append(2)  # Up
            else:
                targets.append(1)  # Stable
        
        return np.array(targets)
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """Training LSTM model"""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Convert to tensors
        X_train = torch.FloatTensor(X_train).to(device)
        y_train = torch.LongTensor(y_train).to(device)
        X_val = torch.FloatTensor(X_val).to(device)
        y_val = torch.LongTensor(y_val).to(device)
        
        # Model
        input_size = X_train.shape[2]
        model = PriceTrendLSTM(input_size).to(device)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10)
        
        # Training loop
        best_val_loss = float('inf')
        patience = 20
        patience_counter = 0
        
        for epoch in range(200):
            model.train()
            optimizer.zero_grad()
            
            outputs = model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            # Validation
            model.eval()
            with torch.no_grad():
                val_outputs = model(X_val)
                val_loss = criterion(val_outputs, y_val)
                val_accuracy = (val_outputs.argmax(1) == y_val).float().mean()
            
            scheduler.step(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), 'best_model.pth')
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    break
            
            if epoch % 10 == 0:
                print(f'Epoch {epoch}, Loss: {loss:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.4f}')
        
        return model
```

## 5. Real-time Inference Service

### 5.1 ML Inference Engine

```python
# inference_engine.py
from kafka import KafkaConsumer, KafkaProducer
import torch
import numpy as np
import json
from collections import deque
import asyncio
import websockets

class MLInferenceEngine:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.feature_buffer = deque(maxlen=60)  # Sequence length
        
        # Kafka setup
        self.consumer = KafkaConsumer(
            'ml-features',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # WebSocket clients
        self.websocket_clients = set()
        
    def preprocess_features(self, features):
        """Chuẩn bị features cho prediction"""
        # Remove non-numeric fields
        numeric_features = {k: v for k, v in features.items() 
                          if isinstance(v, (int, float)) and not np.isnan(v)}
        
        return list(numeric_features.values())
    
    def make_prediction(self, features_sequence):
        """Thực hiện prediction"""
        try:
            # Load models
            lstm_model = self.model_manager.get_model('price_trend_lstm')
            ensemble_model = self.model_manager.get_model('ensemble_model')
            
            if not lstm_model:
                return None
            
            # Prepare input for LSTM
            features_array = np.array(features_sequence)
            features_tensor = torch.FloatTensor(features_array).unsqueeze(0)
            
            # LSTM prediction
            with torch.no_grad():
                lstm_probs = lstm_model(features_tensor)
                lstm_pred = lstm_probs.argmax(1).item()
                lstm_confidence = lstm_probs.max().item()
            
            # Ensemble với other models (nếu có)
            ensemble_features = features_array[-1]  # Latest features
            
            prediction_result = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'lstm_prediction': lstm_pred,
                'lstm_confidence': float(lstm_confidence),
                'prediction_probabilities': lstm_probs.squeeze().tolist(),
                'trend': ['DOWN', 'STABLE', 'UP'][lstm_pred]
            }
            
            return prediction_result
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return None
    
    async def broadcast_prediction(self, prediction):
        """Broadcast prediction qua WebSocket"""
        if self.websocket_clients and prediction:
            message = json.dumps(prediction)
            
            # Remove disconnected clients
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            self.websocket_clients -= disconnected
    
    async def websocket_handler(self, websocket, path):
        """WebSocket connection handler"""
        self.websocket_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.websocket_clients.discard(websocket)
    
    def run_inference_loop(self):
        """Main inference loop"""
        for message in self.consumer:
            features = message.value
            processed_features = self.preprocess_features(features)
            
            if processed_features:
                self.feature_buffer.append(processed_features)
                
                # Make prediction khi đủ sequence length
                if len(self.feature_buffer) == self.feature_buffer.maxlen:
                    features_sequence = list(self.feature_buffer)
                    prediction = self.make_prediction(features_sequence)
                    
                    if prediction:
                        # Publish to Kafka
                        self.producer.send('predictions', prediction)
                        
                        # Broadcast via WebSocket
                        asyncio.create_task(self.broadcast_prediction(prediction))
                        
                        print(f"Prediction: {prediction['trend']} "
                              f"(confidence: {prediction['lstm_confidence']:.3f})")
    
    def start_websocket_server(self):
        """Start WebSocket server"""
        return websockets.serve(self.websocket_handler, "localhost", 8765)
```

## 6. Model Monitoring và A/B Testing

### 6.1 Model Performance Monitor

```python
# model_monitor.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

class ModelMonitor:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.prediction_history = []
        self.actual_results = []
        self.performance_metrics = {}
        
    def log_prediction(self, prediction, features):
        """Log prediction để theo dõi"""
        log_entry = {
            'timestamp': datetime.now(),
            'prediction': prediction,
            'features': features,
            'actual_result': None  # Sẽ được update sau
        }
        self.prediction_history.append(log_entry)
    
    def update_actual_result(self, timestamp, actual_trend):
        """Update kết quả thực tế"""
        # Tìm prediction gần nhất với timestamp
        for entry in self.prediction_history:
            if abs((entry['timestamp'] - timestamp).total_seconds()) < 300:  # 5 minutes
                entry['actual_result'] = actual_trend
                break
    
    def calculate_metrics(self, window_hours=24):
        """Tính toán metrics trong time window"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        recent_predictions = [
            p for p in self.prediction_history 
            if p['timestamp'] > cutoff_time and p['actual_result'] is not None
        ]
        
        if not recent_predictions:
            return {}
        
        predictions = [p['prediction']['lstm_prediction'] for p in recent_predictions]
        actuals = [p['actual_result'] for p in recent_predictions]
        
        accuracy = np.mean([p == a for p, a in zip(predictions, actuals)])
        
        # Precision, Recall cho từng class
        classes = [0, 1, 2]  # Down, Stable, Up
        precision_per_class = {}
        recall_per_class = {}
        
        for cls in classes:
            tp = sum([1 for p, a in zip(predictions, actuals) if p == cls and a == cls])
            fp = sum([1 for p, a in zip(predictions, actuals) if p == cls and a != cls])
            fn = sum([1 for p, a in zip(predictions, actuals) if p != cls and a == cls])
            
            precision_per_class[cls] = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall_per_class[cls] = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision_per_class': precision_per_class,
            'recall_per_class': recall_per_class,
            'total_predictions': len(recent_predictions),
            'window_hours': window_hours
        }
    
    def detect_model_drift(self):
        """Phát hiện model drift"""
        current_metrics = self.calculate_metrics(window_hours=24)
        baseline_metrics = self.calculate_metrics(window_hours=168)  # 1 week
        
        if not current_metrics or not baseline_metrics:
            return False
        
        # Threshold cho drift detection
        accuracy_threshold = 0.05  # 5% drop in accuracy
        
        accuracy_drop = baseline_metrics['accuracy'] - current_metrics['accuracy']
        
        if accuracy_drop > accuracy_threshold:
            print(f"Model drift detected! Accuracy dropped by {accuracy_drop:.3f}")
            return True
        
        return False
    
    async def monitoring_loop(self):
        """Loop monitoring model performance"""
        while True:
            try:
                metrics = self.calculate_metrics()
                if metrics:
                    print(f"Model Performance (24h): Accuracy = {metrics['accuracy']:.3f}")
                    
                    # Check for drift
                    if self.detect_model_drift():
                        # Trigger retraining alert
                        await self.trigger_retraining_alert()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def trigger_retraining_alert(self):
        """Gửi alert khi cần retrain model"""
        alert = {
            'type': 'model_drift',
            'timestamp': datetime.now().isoformat(),
            'message': 'Model performance degraded, retraining recommended',
            'metrics': self.calculate_metrics()
        }
        
        # Send to monitoring system (Slack, email, etc.)
        print(f"ALERT: {alert}")
```

## 7. Deployment và Configuration

### 7.1 Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  mlflow:
    image: python:3.9
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow:/mlflow
    command: >
      bash -c "pip install mlflow boto3 && 
               mlflow server --host 0.0.0.0 --port 5000 --default-artifact-root /mlflow/artifacts"

  feature-engineering:
    build: .
    depends_on:
      - kafka
    command: python feature_engineering.py
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092

  ml-inference:
    build: .
    depends_on:
      - kafka
      - mlflow
    ports:
      - "8765:8765"
    command: python inference_engine.py
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - MLFLOW_TRACKING_URI=http://mlflow:5000

  model-training:
    build: .
    depends_on:
      - mlflow
    command: python model_trainer.py
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
```

### 7.2 Main Application

```python
# main.py
import asyncio
import threading
from model_registry import ModelRegistry
from model_manager import ModelManager
from inference_engine import MLInferenceEngine
from model_monitor import ModelMonitor

async def main():
    # Initialize components
    registry = ModelRegistry()
    model_manager = ModelManager(registry)
    inference_engine = MLInferenceEngine(model_manager)
    monitor = ModelMonitor(model_manager)
    
    # Start WebSocket server
    websocket_server = inference_engine.start_websocket_server()
    
    # Start inference loop in thread
    inference_thread = threading.Thread(
        target=inference_engine.run_inference_loop,
        daemon=True
    )
    inference_thread.start()
    
    # Start monitoring
    monitoring_task = asyncio.create_task(monitor.monitoring_loop())
    
    # Run WebSocket server
    await asyncio.gather(
        websocket_server,
        monitoring_task
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## 8. Testing và Optimization

### 8.1 Backtesting Framework

```python
# backtesting.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Backtester:
    def __init__(self, model, feature_engineer):
        self.model = model
        self.feature_engineer = feature_engineer
        
    def run_backtest(self, historical_data, start_date, end_date):
        """Chạy backtest trên historical data"""
        results = []
        
        for date in pd.date_range(start_date, end_date, freq='H'):
            # Simulate real-time prediction
            historical_window = historical_data[
                historical_data.index <= date
            ].tail(100)  # Last 100 records
            
            if len(historical_window) < 60:
                continue
                
            # Feature engineering
            features = self.feature_engineer.process_historical_data(historical_window)
            
            # Make prediction
            prediction = self.model.predict(features)
            
            # Get actual result (1 hour later)
            future_date = date + timedelta(hours=1)
            actual_data = historical_data[
                historical_data.index == future_date
            ]
            
            if not actual_data.empty:
                actual_trend = self.calculate_actual_trend(
                    historical_window.iloc[-1]['close'],
                    actual_data.iloc[0]['close']
                )
                
                results.append({
                    'timestamp': date,
                    'prediction': prediction,
                    'actual': actual_trend,
                    'correct': prediction == actual_trend
                })
        
        return pd.DataFrame(results)
    
    def calculate_metrics(self, backtest_results):
        """Tính toán backtest metrics"""
        accuracy = backtest_results['correct'].mean()
        
        # Confusion matrix
        from sklearn.metrics import classification_report, confusion_matrix
        
        report = classification_report(
            backtest_results['actual'],
            backtest_results['prediction'],
            target_names=['DOWN', 'STABLE', 'UP']
        )
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'total_predictions': len(backtest_results)
        }
```

## 9. Next Steps và Optimization

### 9.1 Advanced Features

1. **Multi-timeframe Analysis**: Tích hợp predictions từ nhiều timeframes (1min, 5min, 1h)
2. **Ensemble Methods**: Kết hợp multiple models (LSTM, XGBoost, Transformer)
3. **Online Learning**: Continuous learning từ new data
4. **Risk Management**: Thêm risk scores và confidence intervals
5. **Market Regime Detection**: Phát hiện bull/bear markets

### 9.2 Performance Optimization

1. **Caching**: Redis để cache features và predictions
2. **Parallel Processing**: Async processing multiple symbols
3. **GPU Acceleration**: CUDA cho model inference
4. **Database Optimization**: ClickHouse cho time-series data
5. **Load Balancing**: Multiple inference servers

### 9.3 Monitoring và Alerting

1. **Grafana Dashboards**: Visualize model performance
2. **Prometheus Metrics**: System và model metrics
3. **Slack Integration**: Alerts và notifications
4. **A/B Testing**: Compare model versions
5. **Feature Importance Tracking**: Monitor feature contributions

Hệ thống này cung cấp foundation solid cho AI-powered price prediction với real-time inference và proper model management. Bạn có thể bắt đầu implement từng component một cách tuần tự.




Repository 1: ML Models & Training 📊
Chức năng chính:

Phát triển và huấn luyện các mô hình ML (LSTM, Random Forest, Gradient Boosting)
Feature engineering và technical indicators
Model registry với MLflow
Backtesting và evaluation
Export models để sử dụng trong production

Tính năng nổi bật:

Hybrid Model: Kết hợp LSTM + ensemble methods
Advanced Feature Engineering: 50+ technical indicators
Model Versioning: MLflow integration cho model management
Comprehensive Training Pipeline: Automated training với validation
Jupyter Notebooks: Để research và experimentation

Repository 2: Streaming & Inference Service 🚀
Chức năng chính:

Real-time data streaming với Kafka
Sentiment analysis từ news
ML inference service
WebSocket API cho real-time updates
Monitoring và health checks

Tính năng nổi bật:

Real-time Processing: Kafka + Redis cho low-latency
Scalable Architecture: Docker compose với microservices
WebSocket Support: Real-time updates cho clients
Comprehensive API: RESTful + WebSocket endpoints
Production Ready: Health checks, monitoring, logging