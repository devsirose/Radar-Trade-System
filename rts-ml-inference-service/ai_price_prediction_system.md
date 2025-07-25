# Hệ thống Dự đoán Xu hướng Giá bằng AI

## 1. Kiến trúc Tổng quan

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Price Service │    │Sentiment Service│    │  News Service   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ price-updates        │ sentiment-updates    │ news-updates
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Apache Kafka Cluster                        │
│  Topics: price-updates, sentiment-updates, news-updates        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
          ┌───────────▼────────────┐
          │   Feature Engineering  │
          │    Consumer Group      │
          └───────────┬────────────┘
                      │ enriched-features
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                ML Inference Service                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Consumer Group  │  │ Model Registry  │  │ Prediction API  │ │
│  │    (Scalable)   │  │   Integration   │  │   (REST/gRPC)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │ predictions
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Storage Layer                                 │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │     Redis       │              │   PostgreSQL    │           │
│  │  (Short-term)   │              │  (Long-term)    │           │
│  │ • Real-time     │              │ • Historical    │           │
│  │ • Cache         │              │ • Analytics     │           │
│  │ • TTL: 1-7 days │              │ • Reporting     │           │
│  └─────────────────┘              └─────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Kafka Topics Definition

### 2.1 Input Topics

#### `price-updates`
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-07-25T10:30:00Z",
  "price": 185.50,
  "volume": 1500000,
  "change": 2.30,
  "change_percent": 1.26,
  "market": "NASDAQ",
  "metadata": {
    "source": "market_data_feed",
    "quality_score": 0.98
  }
}
```

#### `sentiment-updates`
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-07-25T10:30:00Z",
  "sentiment_score": 0.75,
  "confidence": 0.89,
  "source_count": 150,
  "sentiment_breakdown": {
    "positive": 0.60,
    "neutral": 0.25,
    "negative": 0.15
  },
  "trending_keywords": ["earnings", "growth", "innovation"],
  "metadata": {
    "sources": ["twitter", "news", "reddit"],
    "analysis_model": "sentiment_v2.1"
  }
}
```

#### `news-updates`
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-07-25T10:30:00Z",
  "news_impact_score": 0.82,
  "article_count": 25,
  "categories": ["earnings", "product_launch", "analyst_rating"],
  "sentiment_weighted": 0.68,
  "urgency_score": 0.75,
  "metadata": {
    "sources": ["reuters", "bloomberg", "cnbc"],
    "analysis_window": "1h"
  }
}
```

### 2.2 Feature Engineering Topic

#### `enriched-features`
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-07-25T10:30:00Z",
  "features": {
    "price_features": {
      "current_price": 185.50,
      "sma_20": 182.30,
      "ema_12": 184.20,
      "rsi": 68.5,
      "bollinger_upper": 190.20,
      "bollinger_lower": 178.40,
      "volume_ratio": 1.15,
      "price_momentum": 0.024
    },
    "sentiment_features": {
      "sentiment_score": 0.75,
      "sentiment_momentum": 0.12,
      "sentiment_volatility": 0.08,
      "news_impact": 0.82,
      "social_buzz": 0.65
    },
    "technical_features": {
      "volatility_5d": 0.18,
      "correlation_spy": 0.82,
      "sector_performance": 0.035,
      "market_cap_tier": "large_cap"
    }
  },
  "metadata": {
    "feature_version": "v3.2",
    "completeness_score": 0.95
  }
}
```

### 2.3 Output Topic

#### `predictions`
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-07-25T10:30:00Z",
  "prediction_id": "pred_20250725_AAPL_103000",
  "predictions": {
    "price_1h": {
      "predicted_price": 186.20,
      "confidence": 0.78,
      "direction": "up",
      "probability_up": 0.72
    },
    "price_1d": {
      "predicted_price": 188.50,
      "confidence": 0.65,
      "direction": "up",
      "probability_up": 0.68
    },
    "price_1w": {
      "predicted_price": 192.00,
      "confidence": 0.52,
      "direction": "up",
      "probability_up": 0.58
    }
  },
  "model_info": {
    "model_name": "price_predictor_v4.1",
    "model_version": "20250720",
    "features_used": 45,
    "training_date": "2025-07-20",
    "backtesting_accuracy": 0.73
  },
  "risk_metrics": {
    "volatility_forecast": 0.22,
    "max_drawdown_probability": 0.15,
    "tail_risk_5p": -8.2
  }
}
```

## 3. ML Inference Service Architecture

### 3.1 Service Components

```python
# ml_inference_service/main.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import asyncio
import json
from kafka import KafkaConsumer, KafkaProducer
from redis import Redis
import psycopg2
from sqlalchemy import create_engine
import numpy as np
import pandas as pd

@dataclass
class PredictionConfig:
    model_registry_url: str
    kafka_bootstrap_servers: List[str]
    redis_host: str
    postgres_url: str
    consumer_group_id: str
    batch_size: int = 100
    prediction_intervals: List[str] = None

class ModelRegistry:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.models_cache = {}
    
    async def get_model(self, model_name: str, version: str = "latest"):
        """Load model from registry with caching"""
        cache_key = f"{model_name}:{version}"
        if cache_key not in self.models_cache:
            # Load from registry
            model = await self._fetch_model(model_name, version)
            self.models_cache[cache_key] = model
        return self.models_cache[cache_key]
    
    async def _fetch_model(self, model_name: str, version: str):
        # Implementation for fetching model from registry
        pass

class FeatureProcessor:
    def __init__(self):
        self.feature_extractors = {
            'technical': self._extract_technical_features,
            'sentiment': self._extract_sentiment_features,
            'market': self._extract_market_features
        }
    
    def process_features(self, raw_data: Dict) -> np.ndarray:
        """Convert raw data to model-ready features"""
        features = []
        for extractor in self.feature_extractors.values():
            features.extend(extractor(raw_data))
        return np.array(features)
    
    def _extract_technical_features(self, data: Dict) -> List[float]:
        # Extract technical indicators
        pass
    
    def _extract_sentiment_features(self, data: Dict) -> List[float]:
        # Extract sentiment features
        pass
    
    def _extract_market_features(self, data: Dict) -> List[float]:
        # Extract market context features
        pass

class PredictionStorage:
    def __init__(self, redis_client: Redis, postgres_engine):
        self.redis = redis_client
        self.postgres = postgres_engine
    
    async def store_prediction(self, prediction: Dict):
        """Store prediction in both Redis and PostgreSQL"""
        # Redis for real-time access
        await self._store_redis(prediction)
        # PostgreSQL for long-term storage
        await self._store_postgres(prediction)
    
    async def _store_redis(self, prediction: Dict):
        key = f"pred:{prediction['symbol']}:{prediction['timestamp']}"
        self.redis.setex(
            key, 
            86400 * 7,  # 7 days TTL
            json.dumps(prediction)
        )
    
    async def _store_postgres(self, prediction: Dict):
        # Store in PostgreSQL for historical analysis
        pass

class MLInferenceService:
    def __init__(self, config: PredictionConfig):
        self.config = config
        self.model_registry = ModelRegistry(config.model_registry_url)
        self.feature_processor = FeatureProcessor()
        self.storage = PredictionStorage(
            Redis(host=config.redis_host),
            create_engine(config.postgres_url)
        )
        
        # Kafka setup
        self.consumer = KafkaConsumer(
            'enriched-features',
            bootstrap_servers=config.kafka_bootstrap_servers,
            group_id=config.consumer_group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True,
            auto_offset_reset='latest'
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    async def start_inference_loop(self):
        """Main inference loop with batch processing"""
        batch = []
        
        for message in self.consumer:
            batch.append(message.value)
            
            if len(batch) >= self.config.batch_size:
                await self._process_batch(batch)
                batch = []
    
    async def _process_batch(self, batch: List[Dict]):
        """Process batch of features and generate predictions"""
        predictions = []
        
        for feature_data in batch:
            try:
                prediction = await self._generate_prediction(feature_data)
                predictions.append(prediction)
            except Exception as e:
                print(f"Error processing {feature_data.get('symbol')}: {e}")
        
        # Store predictions
        for prediction in predictions:
            await self.storage.store_prediction(prediction)
            
            # Send to predictions topic
            self.producer.send('predictions', prediction)
    
    async def _generate_prediction(self, feature_data: Dict) -> Dict:
        """Generate prediction for single symbol"""
        # Get model
        model = await self.model_registry.get_model('price_predictor')
        
        # Process features
        features = self.feature_processor.process_features(feature_data)
        
        # Generate predictions for multiple time horizons
        predictions = {}
        for interval in ['1h', '1d', '1w']:
            pred_result = model.predict(features, time_horizon=interval)
            predictions[f'price_{interval}'] = {
                'predicted_price': float(pred_result['price']),
                'confidence': float(pred_result['confidence']),
                'direction': 'up' if pred_result['price'] > feature_data['features']['price_features']['current_price'] else 'down',
                'probability_up': float(pred_result['probability_up'])
            }
        
        return {
            'symbol': feature_data['symbol'],
            'timestamp': feature_data['timestamp'],
            'prediction_id': f"pred_{feature_data['timestamp'].replace(':', '').replace('-', '')}_{feature_data['symbol']}",
            'predictions': predictions,
            'model_info': {
                'model_name': model.name,
                'model_version': model.version,
                'features_used': len(features),
                'training_date': model.training_date,
                'backtesting_accuracy': model.accuracy
            }
        }

# Usage
if __name__ == "__main__":
    config = PredictionConfig(
        model_registry_url="http://model-registry:8080",
        kafka_bootstrap_servers=["kafka1:9092", "kafka2:9092"],
        redis_host="redis:6379",
        postgres_url="postgresql://user:pass@postgres:5432/predictions",
        consumer_group_id="ml-inference-group",
        batch_size=50
    )
    
    service = MLInferenceService(config)
    asyncio.run(service.start_inference_loop())
```

### 3.2 Consumer Group Scaling

```yaml
# docker-compose.yml
version: '3.8'
services:
  ml-inference-1:
    image: ml-inference-service:latest
    environment:
      - CONSUMER_GROUP_ID=ml-inference-group
      - CONSUMER_INSTANCE_ID=inference-1
      - KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092
    depends_on:
      - kafka
      - redis
      - postgres

  ml-inference-2:
    image: ml-inference-service:latest
    environment:
      - CONSUMER_GROUP_ID=ml-inference-group
      - CONSUMER_INSTANCE_ID=inference-2
      - KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092
    depends_on:
      - kafka
      - redis
      - postgres

  ml-inference-3:
    image: ml-inference-service:latest
    environment:
      - CONSUMER_GROUP_ID=ml-inference-group
      - CONSUMER_INSTANCE_ID=inference-3
      - KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092
    depends_on:
      - kafka
      - redis
      - postgres
```

## 4. Storage Strategy

### 4.1 Redis Schema (Short-term)

```python
# Redis key patterns
PREDICTION_KEY = "pred:{symbol}:{timestamp}"
LATEST_PREDICTION = "latest_pred:{symbol}"
SYMBOL_METRICS = "metrics:{symbol}"
MODEL_PERFORMANCE = "model_perf:{model_name}:{date}"

# TTL Strategy
PREDICTION_TTL = 86400 * 7  # 7 days
METRICS_TTL = 86400 * 1     # 1 day
PERFORMANCE_TTL = 86400 * 30 # 30 days
```

### 4.2 PostgreSQL Schema (Long-term)

```sql
-- Predictions table
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    prediction_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Predictions for different time horizons
    price_1h DECIMAL(10,2),
    confidence_1h DECIMAL(5,4),
    probability_up_1h DECIMAL(5,4),
    
    price_1d DECIMAL(10,2),
    confidence_1d DECIMAL(5,4),
    probability_up_1d DECIMAL(5,4),
    
    price_1w DECIMAL(10,2),
    confidence_1w DECIMAL(5,4),
    probability_up_1w DECIMAL(5,4),
    
    -- Model info
    model_name VARCHAR(50),
    model_version VARCHAR(20),
    features_used INTEGER,
    backtesting_accuracy DECIMAL(5,4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_symbol_timestamp (symbol, timestamp),
    INDEX idx_prediction_id (prediction_id),
    INDEX idx_created_at (created_at)
);

-- Model performance tracking
CREATE TABLE model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    evaluation_date DATE NOT NULL,
    
    -- Performance metrics
    accuracy_1h DECIMAL(5,4),
    accuracy_1d DECIMAL(5,4),
    accuracy_1w DECIMAL(5,4),
    
    mse_1h DECIMAL(10,6),
    mse_1d DECIMAL(10,6), 
    mse_1w DECIMAL(10,6),
    
    directional_accuracy DECIMAL(5,4),
    sharpe_ratio DECIMAL(6,4),
    
    total_predictions INTEGER,
    
    UNIQUE(model_name, model_version, evaluation_date)
);

-- Feature importance tracking
CREATE TABLE feature_importance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    importance_score DECIMAL(8,6),
    feature_category VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_model_version (model_name, model_version)
);
```

## 5. Model Registry Integration

```python
class ModelRegistry:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.model_cache = {}
        self.model_metadata = {}
    
    async def register_model(self, model_path: str, metadata: Dict):
        """Register new model version"""
        response = await self._post(f"{self.registry_url}/models", {
            'model_path': model_path,
            'metadata': metadata
        })
        return response
    
    async def get_model_versions(self, model_name: str):
        """Get all versions of a model"""
        response = await self._get(f"{self.registry_url}/models/{model_name}/versions")
        return response
    
    async def promote_model(self, model_name: str, version: str, stage: str):
        """Promote model to production/staging"""
        response = await self._put(
            f"{self.registry_url}/models/{model_name}/versions/{version}/stage",
            {'stage': stage}
        )
        return response
    
    async def get_production_model(self, model_name: str):
        """Get current production model"""
        response = await self._get(f"{self.registry_url}/models/{model_name}/production")
        return response
```

## 6. Monitoring và Observability

### 6.1 Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Prediction metrics
prediction_counter = Counter('predictions_total', 'Total predictions made', ['symbol', 'model'])
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
model_accuracy = Gauge('model_accuracy', 'Model accuracy', ['model', 'time_horizon'])
kafka_lag = Gauge('kafka_consumer_lag', 'Kafka consumer lag', ['topic', 'partition'])

# Feature engineering metrics
feature_completeness = Gauge('feature_completeness', 'Feature completeness score', ['symbol'])
```

### 6.2 Alerting Rules

```yaml
# alerting_rules.yml
groups:
  - name: ml_inference
    rules:
      - alert: HighPredictionLatency
        expr: prediction_latency_seconds > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High prediction latency detected"
      
      - alert: LowModelAccuracy
        expr: model_accuracy < 0.6
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Model accuracy dropped below threshold"
      
      - alert: KafkaConsumerLag
        expr: kafka_consumer_lag > 1000
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High Kafka consumer lag"
```

## 7. Deployment và Scaling

### 7.1 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
    spec:
      containers:
      - name: ml-inference
        image: ml-inference:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-cluster:9092"
        - name: REDIS_HOST
          value: "redis-cluster"
        - name: POSTGRES_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url

---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  selector:
    app: ml-inference
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-inference-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 8. Performance Optimization

### 8.1 Batch Processing
- Process features in batches of 50-100 để giảm overhead
- Sử dụng async/await cho I/O operations
- Connection pooling cho database connections

### 8.2 Model Optimization
- Model quantization để giảm memory usage
- ONNX runtime để tăng inference speed
- Model caching để tránh reload liên tục

### 8.3 Feature Caching
- Cache computed features trong Redis
- Incremental feature computation
- Feature versioning để backward compatibility

Hệ thống này cung cấp một kiến trúc scalable và robust cho việc dự đoán xu hướng giá bằng AI, với khả năng xử lý real-time data và lưu trữ hiệu quả cho cả short-term và long-term analysis.