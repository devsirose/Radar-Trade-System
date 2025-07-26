# Stock Price Prediction System with AI & Sentiment Analysis

## Project Structure
```
stock-prediction-system/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── kafka_config.py
├── models/
│   ├── __init__.py
│   ├── price_predictor.py
│   ├── sentiment_analyzer.py
│   └── ensemble_model.py
├── services/
│   ├── __init__.py
│   ├── price_service.py
│   ├── sentiment_service.py
│   ├── ml_inference_service.py
│   └── model_registry.py
├── data/
│   ├── __init__.py
│   ├── data_collector.py
│   ├── data_processor.py
│   └── feature_engineering.py
├── streaming/
│   ├── __init__.py
│   ├── kafka_producer.py
│   ├── kafka_consumer.py
│   └── stream_processor.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   └── websocket_handler.py
├── training/
│   ├── __init__.py
│   ├── train_price_model.py
│   ├── train_sentiment_model.py
│   └── model_evaluation.py
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py
│   └── alerts.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_streaming.py
└── scripts/
    ├── setup.sh
    ├── deploy.sh
    └── run_training.py
```

## Core Components

### 1. Configuration (config/settings.py)
```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_PRICE_TOPIC: str = "stock-prices"
    KAFKA_SENTIMENT_TOPIC: str = "market-sentiment"
    KAFKA_PREDICTION_TOPIC: str = "price-predictions"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Model Registry
    MODEL_REGISTRY_PATH: str = "./model_registry"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Model Registry (services/model_registry.py)
```python
import mlflow
import mlflow.sklearn
import mlflow.pytorch
import joblib
import torch
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    def __init__(self, registry_path: str, mlflow_uri: str):
        self.registry_path = registry_path
        mlflow.set_tracking_uri(mlflow_uri)
        os.makedirs(registry_path, exist_ok=True)
    
    def register_model(self, 
                      model: Any, 
                      model_name: str, 
                      model_type: str,
                      metrics: Dict[str, float],
                      metadata: Dict[str, Any] = None) -> str:
        """Register a new model version"""
        
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log metrics
            for metric_name, value in metrics.items():
                mlflow.log_metric(metric_name, value)
            
            # Log metadata
            if metadata:
                for key, value in metadata.items():
                    mlflow.log_param(key, value)
            
            # Save model based on type
            if model_type == "sklearn":
                mlflow.sklearn.log_model(model, model_name)
                model_path = os.path.join(self.registry_path, f"{model_name}_sklearn.pkl")
                joblib.dump(model, model_path)
            
            elif model_type == "pytorch":
                mlflow.pytorch.log_model(model, model_name)
                model_path = os.path.join(self.registry_path, f"{model_name}_pytorch.pth")
                torch.save(model.state_dict(), model_path)
            
            run_id = mlflow.active_run().info.run_id
            
            # Register model in MLflow Model Registry
            mlflow.register_model(f"runs:/{run_id}/{model_name}", model_name)
            
            logger.info(f"Model {model_name} registered with run_id: {run_id}")
            return run_id
    
    def load_model(self, model_name: str, version: str = "latest") -> Any:
        """Load a model from registry"""
        try:
            if version == "latest":
                model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
            else:
                model = mlflow.pyfunc.load_model(f"models:/{model_name}/{version}")
            
            return model
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return None
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model information and metrics"""
        client = mlflow.tracking.MlflowClient()
        try:
            latest_version = client.get_latest_versions(model_name, stages=["Production"])
            if not latest_version:
                latest_version = client.get_latest_versions(model_name, stages=["None"])
            
            if latest_version:
                version_info = latest_version[0]
                run_info = client.get_run(version_info.run_id)
                
                return {
                    "name": model_name,
                    "version": version_info.version,
                    "stage": version_info.current_stage,
                    "run_id": version_info.run_id,
                    "metrics": run_info.data.metrics,
                    "params": run_info.data.params,
                    "created_at": version_info.creation_timestamp
                }
        except Exception as e:
            logger.error(f"Error getting model info for {model_name}: {e}")
            return {}
```

### 3. Price Prediction Model (models/price_predictor.py)
```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LSTMPricePredictor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, dropout: float = 0.2):
        super(LSTMPricePredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        batch_size = x.size(0)
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size)
        
        lstm_out, _ = self.lstm(x, (h0, c0))
        lstm_out = self.dropout(lstm_out[:, -1, :])  # Take last output
        output = self.fc(lstm_out)
        return output

class HybridPricePredictor:
    def __init__(self):
        self.lstm_model = None
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.price_scaler = MinMaxScaler()
        self.is_trained = False
    
    def prepare_features(self, df: pd.DataFrame, lookback: int = 30) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for training"""
        # Technical indicators
        df['sma_5'] = df['close'].rolling(5).mean()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price features
        df['price_change'] = df['close'].pct_change()
        df['high_low_ratio'] = df['high'] / df['low']
        df['open_close_ratio'] = df['open'] / df['close']
        
        # Volatility
        df['volatility'] = df['price_change'].rolling(20).std()
        
        feature_columns = [
            'sma_5', 'sma_20', 'ema_12', 'ema_26', 'rsi', 'macd', 'macd_signal',
            'bb_position', 'volume_ratio', 'high_low_ratio', 'open_close_ratio', 'volatility'
        ]
        
        # Add sentiment features if available
        if 'sentiment_score' in df.columns:
            feature_columns.extend(['sentiment_score', 'sentiment_magnitude'])
        
        df = df.dropna()
        
        # Prepare sequences for LSTM
        features = df[feature_columns].values
        targets = df['close'].values
        
        X, y = [], []
        for i in range(lookback, len(features)):
            X.append(features[i-lookback:i])
            y.append(targets[i])
        
        return np.array(X), np.array(y)
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict[str, float]:
        """Train the hybrid model"""
        logger.info("Preparing features for training...")
        X, y = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
        X_test_scaled = self.scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)
        
        # Scale targets
        y_train_scaled = self.price_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
        y_test_scaled = self.price_scaler.transform(y_test.reshape(-1, 1)).flatten()
        
        # Train LSTM
        logger.info("Training LSTM model...")
        self.lstm_model = LSTMPricePredictor(input_size=X_train.shape[-1])
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.lstm_model.parameters(), lr=0.001)
        
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train_scaled)
        y_train_tensor = torch.FloatTensor(y_train_scaled)
        X_test_tensor = torch.FloatTensor(X_test_scaled)
        y_test_tensor = torch.FloatTensor(y_test_scaled)
        
        # Training loop
        for epoch in range(100):
            self.lstm_model.train()
            optimizer.zero_grad()
            outputs = self.lstm_model(X_train_tensor)
            loss = criterion(outputs.squeeze(), y_train_tensor)
            loss.backward()
            optimizer.step()
            
            if epoch % 20 == 0:
                logger.info(f"LSTM Epoch {epoch}, Loss: {loss.item():.6f}")
        
        # Train traditional models with flattened features
        logger.info("Training traditional models...")
        X_train_flat = X_train_scaled.reshape(X_train_scaled.shape[0], -1)
        X_test_flat = X_test_scaled.reshape(X_test_scaled.shape[0], -1)
        
        self.rf_model.fit(X_train_flat, y_train_scaled)
        self.gb_model.fit(X_train_flat, y_train_scaled)
        
        # Evaluate models
        self.lstm_model.eval()
        with torch.no_grad():
            lstm_pred = self.lstm_model(X_test_tensor).squeeze().numpy()
        
        rf_pred = self.rf_model.predict(X_test_flat)
        gb_pred = self.gb_model.predict(X_test_flat)
        
        # Ensemble prediction (weighted average)
        ensemble_pred = 0.5 * lstm_pred + 0.25 * rf_pred + 0.25 * gb_pred
        
        # Inverse scale predictions
        lstm_pred_unscaled = self.price_scaler.inverse_transform(lstm_pred.reshape(-1, 1)).flatten()
        rf_pred_unscaled = self.price_scaler.inverse_transform(rf_pred.reshape(-1, 1)).flatten()
        gb_pred_unscaled = self.price_scaler.inverse_transform(gb_pred.reshape(-1, 1)).flatten()
        ensemble_pred_unscaled = self.price_scaler.inverse_transform(ensemble_pred.reshape(-1, 1)).flatten()
        y_test_unscaled = self.price_scaler.inverse_transform(y_test_scaled.reshape(-1, 1)).flatten()
        
        # Calculate metrics
        metrics = {
            "lstm_mse": mean_squared_error(y_test_unscaled, lstm_pred_unscaled),
            "lstm_r2": r2_score(y_test_unscaled, lstm_pred_unscaled),
            "rf_mse": mean_squared_error(y_test_unscaled, rf_pred_unscaled),
            "rf_r2": r2_score(y_test_unscaled, rf_pred_unscaled),
            "gb_mse": mean_squared_error(y_test_unscaled, gb_pred_unscaled),
            "gb_r2": r2_score(y_test_unscaled, gb_pred_unscaled),
            "ensemble_mse": mean_squared_error(y_test_unscaled, ensemble_pred_unscaled),
            "ensemble_r2": r2_score(y_test_unscaled, ensemble_pred_unscaled)
        }
        
        self.is_trained = True
        logger.info(f"Training completed. Ensemble R2: {metrics['ensemble_r2']:.4f}")
        
        return metrics
    
    def predict(self, features: np.ndarray) -> Dict[str, float]:
        """Make prediction using ensemble model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(-1, features.shape[-1])).reshape(features.shape)
        
        # LSTM prediction
        self.lstm_model.eval()
        with torch.no_grad():
            features_tensor = torch.FloatTensor(features_scaled)
            lstm_pred = self.lstm_model(features_tensor).squeeze().numpy()
        
        # Traditional model predictions
        features_flat = features_scaled.reshape(features_scaled.shape[0], -1)
        rf_pred = self.rf_model.predict(features_flat)
        gb_pred = self.gb_model.predict(features_flat)
        
        # Ensemble prediction
        ensemble_pred = 0.5 * lstm_pred + 0.25 * rf_pred + 0.25 * gb_pred
        
        # Inverse scale predictions
        predictions = {
            "lstm": self.price_scaler.inverse_transform(lstm_pred.reshape(-1, 1)).flatten()[0],
            "random_forest": self.price_scaler.inverse_transform(rf_pred.reshape(-1, 1)).flatten()[0],
            "gradient_boosting": self.price_scaler.inverse_transform(gb_pred.reshape(-1, 1)).flatten()[0],
            "ensemble": self.price_scaler.inverse_transform(ensemble_pred.reshape(-1, 1)).flatten()[0]
        }
        
        return predictions
```

### 4. Sentiment Analysis Model (models/sentiment_analyzer.py)
```python
import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
import requests
from typing import Dict, List, Any
import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, news_api_key: str):
        self.news_api_key = news_api_key
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Financial keyword weights
        self.financial_keywords = {
            'bullish': 0.8, 'bull': 0.6, 'buy': 0.7, 'strong': 0.5, 'growth': 0.6,
            'profit': 0.7, 'revenue': 0.5, 'earnings': 0.6, 'upgrade': 0.8,
            'bearish': -0.8, 'bear': -0.6, 'sell': -0.7, 'weak': -0.5, 'decline': -0.6,
            'loss': -0.7, 'downgrade': -0.8, 'crash': -0.9, 'recession': -0.8
        }
    
    def get_news_data(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """Fetch news data for a given symbol"""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': f'{symbol} stock OR {symbol} shares',
                'from': from_date,
                'sortBy': 'publishedAt',
                'apiKey': self.news_api_key,
                'language': 'en',
                'pageSize': 100
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            
            news_data = []
            for article in articles:
                news_data.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', '')
                })
            
            logger.info(f"Fetched {len(news_data)} news articles for {symbol}")
            return news_data
            
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text"""
        if not text:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        # Clean text
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
        
        # VADER sentiment
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # Financial keyword analysis
        financial_score = 0
        word_count = 0
        words = text.lower().split()
        
        for word in words:
            if word in self.financial_keywords:
                financial_score += self.financial_keywords[word]
                word_count += 1
        
        if word_count > 0:
            financial_score /= word_count
        
        # Combine scores
        combined_score = (vader_scores['compound'] + textblob_sentiment + financial_score) / 3
        
        return {
            'compound': combined_score,
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'financial_sentiment': financial_score,
            'textblob_sentiment': textblob_sentiment
        }
    
    def analyze_news_sentiment(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """Analyze sentiment from news articles"""
        news_data = self.get_news_data(symbol, days)
        
        if not news_data:
            return {
                'overall_sentiment': 0.0,
                'sentiment_magnitude': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in news_data:
            # Combine title and description for analysis
            text = f"{article['title']} {article['description']}"
            sentiment = self.analyze_text_sentiment(text)
            sentiments.append(sentiment['compound'])
            
            if sentiment['compound'] > 0.1:
                positive_count += 1
            elif sentiment['compound'] < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        overall_sentiment = np.mean(sentiments) if sentiments else 0.0
        sentiment_magnitude = np.std(sentiments) if sentiments else 0.0
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_magnitude': sentiment_magnitude,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_articles': len(news_data),
            'sentiment_trend': self._calculate_sentiment_trend(news_data)
        }
    
    def _calculate_sentiment_trend(self, news_data: List[Dict[str, Any]]) -> float:
        """Calculate sentiment trend over time"""
        if len(news_data) < 2:
            return 0.0
        
        # Sort by published date
        sorted_news = sorted(news_data, key=lambda x: x['published_at'])
        
        # Calculate sentiment for first and second half
        mid_point = len(sorted_news) // 2
        first_half = sorted_news[:mid_point]
        second_half = sorted_news[mid_point:]
        
        first_half_sentiment = np.mean([
            self.analyze_text_sentiment(f"{article['title']} {article['description']}")['compound']
            for article in first_half
        ])
        
        second_half_sentiment = np.mean([
            self.analyze_text_sentiment(f"{article['title']} {article['description']}")['compound']
            for article in second_half
        ])
        
        return second_half_sentiment - first_half_sentiment
    
    def get_social_sentiment(self, symbol: str) -> Dict[str, float]:
        """Get social media sentiment (placeholder for Twitter API, Reddit API, etc.)"""
        # This would integrate with Twitter API, Reddit API, etc.
        # For now, return neutral sentiment
        return {
            'twitter_sentiment': 0.0,
            'reddit_sentiment': 0.0,
            'social_volume': 0.0
        }
    
    def get_comprehensive_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive sentiment analysis"""
        news_sentiment = self.analyze_news_sentiment(symbol)
        social_sentiment = self.get_social_sentiment(symbol)
        
        # Combine news and social sentiment
        combined_sentiment = (news_sentiment['overall_sentiment'] * 0.7 + 
                            (social_sentiment['twitter_sentiment'] + social_sentiment['reddit_sentiment']) / 2 * 0.3)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'combined_sentiment': combined_sentiment,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'sentiment_category': self._categorize_sentiment(combined_sentiment)
        }
    
    def _categorize_sentiment(self, sentiment_score: float) -> str:
        """Categorize sentiment score"""
        if sentiment_score > 0.3:
            return "Very Positive"
        elif sentiment_score > 0.1:
            return "Positive"
        elif sentiment_score > -0.1:
            return "Neutral"
        elif sentiment_score > -0.3:
            return "Negative"
        else:
            return "Very Negative"
```

### 5. Kafka Streaming Components (streaming/kafka_producer.py)
```python
from kafka import KafkaProducer
import json
import logging
from typing import Dict, Any
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class StockDataProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1,
            compression_type='gzip'
        )
        
    def send_price_data(self, topic: str, symbol: str, price_data: Dict[str, Any]):
        """Send price data to Kafka topic"""
        try:
            message = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data': price_data
            }
            
            future = self.producer.send(topic, key=symbol, value=message)
            self.producer.flush()
            
            logger.debug(f"Sent price data for {symbol} to topic {topic}")
            return future
            
        except Exception as e:
            logger.error(f"Error sending price data: {e}")
            raise
    
    def send_sentiment_data(self, topic: str, symbol: str, sentiment_data: Dict[str, Any]):
        """Send sentiment data to Kafka topic"""
        try:
            message = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data': sentiment_data
            }
            
            future = self.producer.send(topic, key=symbol, value=message)
            self.producer.flush()
            
            logger.debug(f"Sent sentiment data for {symbol} to topic {topic}")
            return future
            
        except Exception as e:
            logger.error(f"Error sending sentiment data: {e}")
            raise
    
    def send_prediction(self, topic: str, symbol: str, prediction_data: Dict[str, Any]):
        """Send prediction data to Kafka topic"""
        try:
            message = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'prediction': prediction_data
            }
            
            future = self.producer.send(topic, key=symbol, value=message)
            self.producer.flush()
            
            logger.debug(f"Sent prediction for {symbol} to topic {topic}")
            return future
            
        except Exception as e:
            logger.error(f"Error sending prediction: {e}")
            raise
    
    def close(self):
        """Close the producer"""
        self.producer.close()
```

### 6. ML Inference Service (services/ml_inference_service.py)
```python
from kafka import KafkaConsumer, KafkaProducer
import json
import logging
import threading
import time
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import redis
from models.price_predictor import HybridPricePredictor
from models.sentiment_analyzer import SentimentAnalyzer
from services.model_registry import ModelRegistry
from config.settings import settings

logger = logging.getLogger(__name__)

class MLInferenceService:
    def __init__(self):
        self.consumer = KafkaConsumer(
            settings.KAFKA_PRICE_TOPIC,
            settings.KAFKA_SENTIMENT_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='ml-inference-group'
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.model_registry = ModelRegistry(settings.MODEL_REGISTRY_PATH, settings.MLFLOW_TRACKING_URI)
        
        # Load models
        self.price_predictor = self.load_price_model()
        self.sentiment_analyzer = SentimentAnalyzer(settings.NEWS_API_KEY)
        
        # Data buffers
        self.price_buffer = {}
        self.sentiment_buffer = {}
        
        self.running = False
        
    def load_price_model(self):
        """Load the latest price prediction model"""
        try:
            model = self.model_registry.load_model("hybrid_price_predictor")
            if model:
                logger.info("Loaded price prediction model from registry")
                return model
            else:
                logger.warning("No price model found in registry, using default")
                return HybridPricePredictor()
        except Exception as e:
            logger.error(f"Error loading price model: {e}")
            return HybridPricePredictor()
    
    def start(self):
        """Start the ML inference service"""
        self.running = True
        
        # Start consumer thread
        consumer_thread = threading.Thread(target=self._consume_messages)
        consumer_thread.daemon = True
        consumer_thread.start()
        
        # Start prediction thread
        prediction_thread = threading.Thread(target=self._generate_predictions)
        prediction_thread.daemon = True
        prediction_thread.start()
        
        logger.info("ML Inference Service started")
    
    def stop(self):
        """Stop the ML inference service"""
        self.running = False
        self.consumer.close()
        self.producer.close()
        logger.info("ML Inference Service stopped")
    
    def _consume_messages(self):
        """Consume messages from Kafka topics"""
        while self.running:
            try:
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    topic = topic_partition.topic
                    
                    for message in messages:
                        data = message.value
                        symbol = data.get('symbol')
                        timestamp = data.get('timestamp')
                        
                        if topic == settings.KAFKA_PRICE_TOPIC:
                            self._process_price_data(symbol, timestamp, data.get('data'))
                        elif topic == settings.KAFKA_SENTIMENT_TOPIC:
                            self._process_sentiment_data(symbol, timestamp, data.get('data'))
                            
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
                time.sleep(1)
    
    def _process_price_data(self, symbol: str, timestamp: str, price_data: Dict[str, Any]):
        """Process incoming price data"""
        try:
            # Store in Redis for quick access
            redis_key = f"price:{symbol}"
            self.redis_client.hset(redis_key, timestamp, json.dumps(price_data))
            self.redis_client.expire(redis_key, 86400)  # 24 hours
            
            # Update buffer
            if symbol not in self.price_buffer:
                self.price_buffer[symbol] = []
            
            self.price_buffer[symbol].append({
                'timestamp': timestamp,
                'data': price_data
            })
            
            # Keep only recent data (last 100 points)
            if len(self.price_buffer[symbol]) > 100:
                self.price_buffer[symbol] = self.price_buffer[symbol][-100:]
                
            logger.debug(f"Processed price data for {symbol}")
            
        except Exception as e:
            logger.error(f"Error processing price data: {e}")
    
    def _process_sentiment_data(self, symbol: str, timestamp: str, sentiment_data: Dict[str, Any]):
        """Process incoming sentiment data"""
        try:
            # Store in Redis
            redis_key = f"sentiment:{symbol}"
            self.redis_client.hset(redis_key, timestamp, json.dumps(sentiment_data))
            self.redis_client.expire(redis_key, 86400)  # 24 hours
            
            # Update buffer
            if symbol not in self.sentiment_buffer:
                self.sentiment_buffer[symbol] = []
            
            self.sentiment_buffer[symbol].append({
                'timestamp': timestamp,
                'data': sentiment_data
            })
            
            # Keep only recent data
            if len(self.sentiment_buffer[symbol]) > 50:
                self.sentiment_buffer[symbol] = self.sentiment_buffer[symbol][-50:]
                
            logger.debug(f"Processed sentiment data for {symbol}")
            
        except Exception as e:
            logger.error(f"Error processing sentiment data: {e}")
    
    def _generate_predictions(self):
        """Generate predictions periodically"""
        while self.running:
            try:
                # Get all symbols with sufficient data
                symbols_to_predict = self._get_symbols_ready_for_prediction()
                
                for symbol in symbols_to_predict:
                    prediction = self._make_prediction(symbol)
                    if prediction:
                        self._send_prediction(symbol, prediction)
                
                time.sleep(60)  # Generate predictions every minute
                
            except Exception as e:
                logger.error(f"Error generating predictions: {e}")
                time.sleep(60)
    
    def _get_symbols_ready_for_prediction(self) -> List[str]:
        """Get symbols that have sufficient data for prediction"""
        ready_symbols = []
        
        for symbol in self.price_buffer.keys():
            if (len(self.price_buffer.get(symbol, [])) >= 30 and  # At least 30 price points
                len(self.sentiment_buffer.get(symbol, [])) >= 1):    # At least 1 sentiment point
                ready_symbols.append(symbol)
        
        return ready_symbols
    
    def _make_prediction(self, symbol: str) -> Dict[str, Any]:
        """Make prediction for a given symbol"""
        try:
            # Prepare features
            features = self._prepare_features(symbol)
            if features is None:
                return None
            
            # Make prediction using ensemble model
            if hasattr(self.price_predictor, 'predict') and self.price_predictor.is_trained:
                predictions = self.price_predictor.predict(features)
            else:
                # Fallback to simple prediction
                predictions = self._simple_prediction(symbol)
            
            # Add confidence score
            confidence = self._calculate_confidence(symbol, predictions)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'predictions': predictions,
                'confidence': confidence,
                'features_used': self._get_feature_summary(symbol)
            }
            
        except Exception as e:
            logger.error(f"Error making prediction for {symbol}: {e}")
            return None
    
    def _prepare_features(self, symbol: str) -> np.ndarray:
        """Prepare features for prediction"""
        try:
            # Get price data
            price_data = self.price_buffer.get(symbol, [])
            if len(price_data) < 30:
                return None
            
            # Convert to DataFrame
            price_df = pd.DataFrame([
                {
                    'timestamp': pd.to_datetime(item['timestamp']),
                    'open': item['data'].get('open', 0),
                    'high': item['data'].get('high', 0),
                    'low': item['data'].get('low', 0),
                    'close': item['data'].get('close', 0),
                    'volume': item['data'].get('volume', 0)
                }
                for item in price_data[-30:]  # Last 30 points
            ]).sort_values('timestamp')
            
            # Get latest sentiment data
            sentiment_data = self.sentiment_buffer.get(symbol, [])
            latest_sentiment = sentiment_data[-1]['data'] if sentiment_data else {}
            
            # Add sentiment features to price data
            price_df['sentiment_score'] = latest_sentiment.get('combined_sentiment', 0)
            price_df['sentiment_magnitude'] = latest_sentiment.get('news_sentiment', {}).get('sentiment_magnitude', 0)
            
            # Prepare features using the model's method
            if hasattr(self.price_predictor, 'prepare_features'):
                X, _ = self.price_predictor.prepare_features(price_df, lookback=30)
                return X[-1:] if len(X) > 0 else None  # Return last sequence
            else:
                return self._simple_feature_preparation(price_df)
                
        except Exception as e:
            logger.error(f"Error preparing features for {symbol}: {e}")
            return None
    
    def _simple_feature_preparation(self, df: pd.DataFrame) -> np.ndarray:
        """Simple feature preparation fallback"""
        # Basic technical indicators
        df['sma_5'] = df['close'].rolling(5).mean()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['rsi'] = self._calculate_rsi(df['close'])
        df['price_change'] = df['close'].pct_change()
        
        features = df[['sma_5', 'sma_20', 'rsi', 'price_change', 'sentiment_score']].iloc[-1:].values
        return features.reshape(1, 1, -1)  # Reshape for LSTM input
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _simple_prediction(self, symbol: str) -> Dict[str, float]:
        """Simple prediction fallback"""
        price_data = self.price_buffer.get(symbol, [])
        if not price_data:
            return {'simple': 0.0}
        
        recent_prices = [item['data'].get('close', 0) for item in price_data[-5:]]
        trend = np.mean(np.diff(recent_prices)) if len(recent_prices) > 1 else 0
        
        current_price = recent_prices[-1] if recent_prices else 0
        predicted_price = current_price + trend
        
        return {
            'simple': predicted_price,
            'trend': trend,
            'current_price': current_price
        }
    
    def _calculate_confidence(self, symbol: str, predictions: Dict[str, float]) -> float:
        """Calculate prediction confidence"""
        try:
            # Factors affecting confidence
            price_data_count = len(self.price_buffer.get(symbol, []))
            sentiment_data_count = len(self.sentiment_buffer.get(symbol, []))
            
            # Base confidence on data availability
            data_confidence = min(1.0, (price_data_count / 50) * 0.7 + (sentiment_data_count / 10) * 0.3)
            
            # Model agreement (if multiple predictions available)
            if len(predictions) > 1:
                pred_values = list(predictions.values())
                if isinstance(pred_values[0], (int, float)):
                    std_dev = np.std(pred_values)
                    mean_pred = np.mean(pred_values)
                    agreement_confidence = 1.0 - min(1.0, std_dev / abs(mean_pred) if mean_pred != 0 else 1.0)
                else:
                    agreement_confidence = 0.5
            else:
                agreement_confidence = 0.5
            
            return (data_confidence + agreement_confidence) / 2
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_feature_summary(self, symbol: str) -> Dict[str, Any]:
        """Get summary of features used"""
        price_count = len(self.price_buffer.get(symbol, []))
        sentiment_count = len(self.sentiment_buffer.get(symbol, []))
        
        return {
            'price_data_points': price_count,
            'sentiment_data_points': sentiment_count,
            'lookback_period': min(30, price_count)
        }
    
    def _send_prediction(self, symbol: str, prediction: Dict[str, Any]):
        """Send prediction to Kafka topic"""
        try:
            self.producer.send(
                settings.KAFKA_PREDICTION_TOPIC,
                key=symbol,
                value=prediction
            )
            self.producer.flush()
            
            # Also store in Redis for API access
            redis_key = f"prediction:{symbol}"
            self.redis_client.set(redis_key, json.dumps(prediction), ex=3600)  # 1 hour
            
            logger.info(f"Sent prediction for {symbol}: {prediction.get('predictions', {})}")
            
        except Exception as e:
            logger.error(f"Error sending prediction: {e}")

# Service runner
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = MLInferenceService()
    try:
        service.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
```

### 7. Real-time API with WebSocket (api/main.py)
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import asyncio
from typing import Dict, List, Any
import redis
from datetime import datetime
import uvicorn
from pydantic import BaseModel
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Prediction API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscribers: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from symbol subscriptions
        for symbol, connections in self.symbol_subscribers.items():
            if websocket in connections:
                connections.remove(websocket)
    
    def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        if symbol not in self.symbol_subscribers:
            self.symbol_subscribers[symbol] = []
        if websocket not in self.symbol_subscribers[symbol]:
            self.symbol_subscribers[symbol].append(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
    
    async def broadcast_to_symbol(self, symbol: str, message: str):
        if symbol in self.symbol_subscribers:
            disconnected = []
            for connection in self.symbol_subscribers[symbol]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

# Pydantic models
class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"

class SymbolSubscription(BaseModel):
    symbols: List[str]

# API Routes
@app.get("/")
async def root():
    return {"message": "Stock Prediction API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/prediction/{symbol}")
async def get_prediction(symbol: str):
    """Get latest prediction for a symbol"""
    try:
        redis_key = f"prediction:{symbol.upper()}"
        prediction_data = redis_client.get(redis_key)
        
        if not prediction_data:
            raise HTTPException(status_code=404, detail=f"No prediction found for {symbol}")
        
        return json.loads(prediction_data)
    
    except Exception as e:
        logger.error(f"Error getting prediction for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """Get latest sentiment data for a symbol"""
    try:
        redis_key = f"sentiment:{symbol.upper()}"
        # Get latest sentiment data
        sentiment_data = redis_client.hgetall(redis_key)
        
        if not sentiment_data:
            raise HTTPException(status_code=404, detail=f"No sentiment data found for {symbol}")
        
        # Get the most recent entry
        latest_timestamp = max(sentiment_data.keys(), key=lambda x: x.decode())
        latest_data = json.loads(sentiment_data[latest_timestamp])
        
        return {
            "symbol": symbol.upper(),
            "timestamp": latest_timestamp.decode(),
            "sentiment": latest_data
        }
    
    except Exception as e:
        logger.error(f"Error getting sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get latest price data for a symbol"""
    try:
        redis_key = f"price:{symbol.upper()}"
        price_data = redis_client.hgetall(redis_key)
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No price data found for {symbol}")
        
        # Get the most recent entry
        latest_timestamp = max(price_data.keys(), key=lambda x: x.decode())
        latest_data = json.loads(price_data[latest_timestamp])
        
        return {
            "symbol": symbol.upper(),
            "timestamp": latest_timestamp.decode(),
            "price": latest_data
        }
    
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/symbols")
async def get_available_symbols():
    """Get list of available symbols with data"""
    try:
        # Get all prediction keys
        prediction_keys = redis_client.keys("prediction:*")
        symbols = [key.decode().split(":")[1] for key in prediction_keys]
        
        return {"symbols": symbols, "count": len(symbols)}
    
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time data"""
    await manager.connect(websocket)
    manager.subscribe_to_symbol(websocket, symbol.upper())
    
    try:
        # Send initial data
        try:
            prediction = await get_prediction(symbol)
            await manager.send_personal_message(
                json.dumps({"type": "prediction", "data": prediction}),
                websocket
            )
        except:
            pass
        
        try:
            price = await get_price(symbol)
            await manager.send_personal_message(
                json.dumps({"type": "price", "data": price}),
                websocket
            )
        except:
            pass
        
        try:
            sentiment = await get_sentiment(symbol)
            await manager.send_personal_message(
                json.dumps({"type": "sentiment", "data": sentiment}),
                websocket
            )
        except:
            pass
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                new_symbols = message.get("symbols", [])
                for new_symbol in new_symbols:
                    manager.subscribe_to_symbol(websocket, new_symbol.upper())
            
            await manager.send_personal_message(
                json.dumps({"type": "ack", "message": "Message received"}),
                websocket
            )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
        manager.disconnect(websocket)

# Background task to push real-time updates
async def push_updates():
    """Background task to push updates to WebSocket clients"""
    import asyncio
    
    while True:
        try:
            # Get all active symbols
            prediction_keys = redis_client.keys("prediction:*")
            
            for key in prediction_keys:
                symbol = key.decode().split(":")[1]
                
                # Get latest prediction
                prediction_data = redis_client.get(key)
                if prediction_data:
                    message = json.dumps({
                        "type": "prediction_update",
                        "symbol": symbol,
                        "data": json.loads(prediction_data)
                    })
                    await manager.broadcast_to_symbol(symbol, message)
            
            await asyncio.sleep(30)  # Push updates every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in push_updates: {e}")
            await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(push_updates())
    logger.info("API server started")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )
```

### 8. Training Scripts (training/train_price_model.py)
```python
import pandas as pd
import numpy as np
import yfinance as yf
from models.price_predictor import HybridPricePredictor
from models.sentiment_analyzer import SentimentAnalyzer
from services.model_registry import ModelRegistry
from config.settings import settings
import logging
from datetime import datetime, timedelta
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.model_registry = ModelRegistry(settings.MODEL_REGISTRY_PATH, settings.MLFLOW_TRACKING_URI)
        self.sentiment_analyzer = SentimentAnalyzer(settings.NEWS_API_KEY)
    
    def collect_training_data(self, symbols: list, period: str = "2y") -> pd.DataFrame:
        """Collect training data for multiple symbols"""
        all_data = []
        
        for symbol in symbols:
            try:
                logger.info(f"Collecting data for {symbol}")
                
                # Get price data
                ticker = yf.Ticker(symbol)
                price_data = ticker.history(period=period)
                
                if price_data.empty:
                    logger.warning(f"No price data found for {symbol}")
                    continue
                
                price_data['symbol'] = symbol
                price_data.reset_index(inplace=True)
                
                # Get sentiment data (for recent periods)
                if period in ["1y", "6mo", "3mo"]:
                    try:
                        sentiment_data = self.sentiment_analyzer.analyze_news_sentiment(symbol, days=30)
                        price_data['sentiment_score'] = sentiment_data['overall_sentiment']
                        price_data['sentiment_magnitude'] = sentiment_data['sentiment_magnitude']
                    except Exception as e:
                        logger.warning(f"Could not get sentiment data for {symbol}: {e}")
                        price_data['sentiment_score'] = 0.0
                        price_data['sentiment_magnitude'] = 0.0
                else:
                    # For longer periods, use neutral sentiment
                    price_data['sentiment_score'] = 0.0
                    price_data['sentiment_magnitude'] = 0.0
                
                # Rename columns to match expected format
                price_data.columns = [col.lower() for col in price_data.columns]
                
                all_data.append(price_data)
                
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {e}")
                continue
        
        if not all_data:
            raise ValueError("No training data collected")
        
        combined_data = pd.concat(all_data, ignore_index=True)
        logger.info(f"Collected {len(combined_data)} data points for {len(symbols)} symbols")
        
        return combined_data
    
    def train_price_model(self, symbols: list, test_size: float = 0.2) -> dict:
        """Train the price prediction model"""
        logger.info("Starting price model training...")
        
        # Collect training data
        training_data = self.collect_training_data(symbols)
        
        # Initialize and train model
        model = HybridPricePredictor()
        metrics = model.train(training_data, test_size=test_size)
        
        # Register model
        metadata = {
            "symbols": symbols,
            "training_samples": len(training_data),
            "test_size": test_size,
            "training_date": datetime.now().isoformat()
        }
        
        run_id = self.model_registry.register_model(
            model=model,
            model_name="hybrid_price_predictor",
            model_type="pytorch",  # Mixed model, but using pytorch for main component
            metrics=metrics,
            metadata=metadata
        )
        
        logger.info(f"Price model training completed. Run ID: {run_id}")
        logger.info(f"Metrics: {metrics}")
        
        return {
            "run_id": run_id,
            "metrics": metrics,
            "metadata": metadata
        }
    
    def evaluate_model(self, symbols: list, model_name: str = "hybrid_price_predictor"):
        """Evaluate model performance on recent data"""
        logger.info("Evaluating model performance...")
        
        # Load model
        model = self.model_registry.load_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        # Get recent data for evaluation
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        evaluation_results = {}
        
        for symbol in symbols:
            try:
                # Get recent data
                ticker = yf.Ticker(symbol)
                recent_data = ticker.history(start=start_date, end=end_date)
                
                if len(recent_data) < 10:
                    continue
                
                # Add sentiment data
                sentiment_data = self.sentiment_analyzer.analyze_news_sentiment(symbol, days=7)
                recent_data['sentiment_score'] = sentiment_data['overall_sentiment']
                recent_data['sentiment_magnitude'] = sentiment_data['sentiment_magnitude']
                
                # Prepare features
                recent_data.columns = [col.lower() for col in recent_data.columns]
                recent_data.reset_index(inplace=True)
                
                # Make predictions (simplified evaluation)
                actual_prices = recent_data['close'].values[-5:]  # Last 5 days
                
                # Calculate simple metrics (placeholder for more sophisticated evaluation)
                price_std = np.std(actual_prices)
                price_mean = np.mean(actual_prices)
                
                evaluation_results[symbol] = {
                    "price_volatility": price_std,
                    "average_price": price_mean,
                    "data_points": len(recent_data)
                }
                
            except Exception as e:
                logger.error(f"Error evaluating {symbol}: {e}")
                continue
        
        logger.info(f"Evaluation completed for {len(evaluation_results)} symbols")
        return evaluation_results

def main():
    parser = argparse.ArgumentParser(description='Train stock prediction models')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'],
                       help='Stock symbols to train on')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test size for train/test split')
    parser.add_argument('--evaluate', action='store_true',
                       help='Run evaluation after training')
    
    args = parser.parse_args()
    
    trainer = ModelTrainer()
    
    try:
        # Train model
        results = trainer.train_price_model(args.symbols, args.test_size)
        print(f"Training completed successfully!")
        print(f"Run ID: {results['run_id']}")
        print(f"Metrics: {results['metrics']}")
        
        # Evaluate if requested
        if args.evaluate:
            evaluation = trainer.evaluate_model(args.symbols)
            print(f"Evaluation results: {evaluation}")
            
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
```