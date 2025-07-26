                # Higher confidence for fresher data
                price_freshness = max(0, 1 - (now - price_time).seconds / 3600)  # 1 hour decay
                sentiment_freshness = max(0, 1 - (now - sentiment_time).seconds / 7200)  # 2 hour decay
                
                data_quality = (price_freshness + sentiment_freshness) / 2
                base_confidence = min(0.9, base_confidence + data_quality * 0.3)
            
            return base_confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence for {symbol}: {e}")
            return 0.5
    
    async def _get_feature_summary(self, symbol: str) -> Dict[str, Any]:
        """Get summary of features used in prediction"""
        price_data = await self.redis_client.get_json(f"price:{symbol}")
        sentiment_data = await self.redis_client.get_json(f"sentiment:{symbol}")
        
        return {
            'price_data_available': price_data is not None,
            'sentiment_data_available': sentiment_data is not None,
            'price_timestamp': price_data.get('collected_at') if price_data else None,
            'sentiment_timestamp': sentiment_data.get('analyzed_at') if sentiment_data else None
        }
    
    async def _send_prediction(self, symbol: str, prediction: Dict[str, Any]):
        """Send prediction to Kafka and store in Redis"""
        try:
            # Store in Redis for API access
            redis_key = f"prediction:{symbol}"
            await self.redis_client.set_json(redis_key, prediction, ttl=settings.REDIS_TTL)
            
            # Send to Kafka
            await self.kafka_producer.send_prediction(
                topic=settings.KAFKA_PREDICTION_TOPIC,
                symbol=symbol,
                data=prediction
            )
            
            logger.info(f"Sent prediction for {symbol}: {prediction.get('predictions', {})}")
            
        except Exception as e:
            logger.error(f"Error sending prediction for {symbol}: {e}")
    
    async def get_prediction(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest prediction for a symbol"""
        try:
            redis_key = f"prediction:{symbol}"
            return await self.redis_client.get_json(redis_key)
        except Exception as e:
            logger.error(f"Error getting prediction for {symbol}: {e}")
            return None

## Kafka Producer (streaming/kafka_producer.py)
```python
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from config.settings import settings

logger = logging.getLogger(__name__)

class KafkaProducerService:
    """Async Kafka producer service"""
    
    def __init__(self):
        self.producer = None
        self._lock = asyncio.Lock()
    
    async def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if self.producer is None:
            async with self._lock:
                if self.producer is None:
                    self.producer = KafkaProducer(
                        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                        key_serializer=lambda k: k.encode('utf-8') if k else None,
                        acks='all',
                        retries=settings.MAX_RETRIES,
                        max_in_flight_requests_per_connection=1,
                        compression_type='gzip',
                        batch_size=16384,
                        linger_ms=10
                    )
                    logger.info("Kafka producer initialized")
        
        return self.producer
    
    async def send_price_data(self, topic: str, symbol: str, data: Dict[str, Any]) -> bool:
        """Send price data to Kafka topic"""
        try:
            producer = await self._get_producer()
            
            message = {
                'type': 'price_update',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            future = producer.send(topic, key=symbol, value=message)
            producer.flush(timeout=5)
            
            # Wait for send confirmation
            record_metadata = future.get(timeout=10)
            logger.debug(f"Sent price data for {symbol} to {record_metadata.topic}:{record_metadata.partition}")
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending price data for {symbol}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending price data for {symbol}: {e}")
            return False
    
    async def send_sentiment_data(self, topic: str, symbol: str, data: Dict[str, Any]) -> bool:
        """Send sentiment data to Kafka topic"""
        try:
            producer = await self._get_producer()
            
            message = {
                'type': 'sentiment_update',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            future = producer.send(topic, key=symbol, value=message)
            producer.flush(timeout=5)
            
            record_metadata = future.get(timeout=10)
            logger.debug(f"Sent sentiment data for {symbol} to {record_metadata.topic}:{record_metadata.partition}")
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending sentiment data for {symbol}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending sentiment data for {symbol}: {e}")
            return False
    
    async def send_prediction(self, topic: str, symbol: str, data: Dict[str, Any]) -> bool:
        """Send prediction data to Kafka topic"""
        try:
            producer = await self._get_producer()
            
            message = {
                'type': 'prediction_update',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            future = producer.send(topic, key=symbol, value=message)
            producer.flush(timeout=5)
            
            record_metadata = future.get(timeout=10)
            logger.debug(f"Sent prediction for {symbol} to {record_metadata.topic}:{record_metadata.partition}")
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending prediction for {symbol}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending prediction for {symbol}: {e}")
            return False
    
    async def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close(timeout=10)
            self.producer = None
            logger.info("Kafka producer closed")

## Redis Client (utils/redis_client.py)
```python
import json
import logging
from typing import Any, Optional, Dict
import redis.asyncio as redis
from config.settings import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.redis = None
    
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self.redis is None:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        return self.redis
    
    async def set_json(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set JSON value in Redis"""
        try:
            client = await self._get_client()
            json_str = json.dumps(value, default=str)
            
            if ttl:
                await client.setex(key, ttl, json_str)
            else:
                await client.set(key, json_str)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting JSON in Redis for key {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from Redis"""
        try:
            client = await self._get_client()
            value = await client.get(key)
            
            if value is None:
                return None
            
            return json.loads(value)
            
        except Exception as e:
            logger.error(f"Error getting JSON from Redis for key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            client = await self._get_client()
            return await client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Error checking existence of key {key} in Redis: {e}")
            return False
    
    async def keys(self, pattern: str) -> list:
        """Get keys matching pattern"""
        try:
            client = await self._get_client()
            return await client.keys(pattern)
            
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

## FastAPI Main Application (api/main.py)
```python
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from services.price_service import PriceService
from services.sentiment_service import SentimentService
from services.ml_inference_service import MLInferenceService
from api.routes.predictions import router as predictions_router
from api.routes.market_data import router as market_data_router
from api.routes.websocket import WebSocketManager
from monitoring.health_check import HealthChecker
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
price_service = None
sentiment_service = None
inference_service = None
websocket_manager = None
health_checker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global price_service, sentiment_service, inference_service, websocket_manager, health_checker
    
    # Startup
    logger.info("Starting Stock Prediction Streaming Service...")
    
    try:
        # Initialize services
        price_service = PriceService()
        sentiment_service = SentimentService()
        inference_service = MLInferenceService()
        websocket_manager = WebSocketManager()
        health_checker = HealthChecker()
        
        # Start services
        await price_service.start()
        await sentiment_service.start()
        await inference_service.start()
        await health_checker.start()
        
        # Store services in app state
        app.state.price_service = price_service
        app.state.sentiment_service = sentiment_service
        app.state.inference_service = inference_service
        app.state.websocket_manager = websocket_manager
        app.state.health_checker = health_checker
        
        logger.info("All services started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down services...")
        
        if price_service:
            await price_service.stop()
        if sentiment_service:
            await sentiment_service.stop()
        if inference_service:
            await inference_service.stop()
        if health_checker:
            await health_checker.stop()
        
        logger.info("All services stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time stock prediction streaming service with ML inference",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions_router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(market_data_router, prefix="/api/v1/market", tags=["market"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predictions": "/api/v1/predictions",
            "market_data": "/api/v1/market",
            "websocket": "/ws/{symbol}"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = await app.state.health_checker.get_health_status()
        
        if health_status["status"] == "healthy":
            return health_status
        else:
            return JSONResponse(
                status_code=503,
                content=health_status
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

# WebSocket endpoint
@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time updates"""
    await app.state.websocket_manager.connect(websocket, symbol.upper())
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Handle client messages (e.g., subscribe to additional symbols)
            try:
                import json
                message = json.loads(data)
                await app.state.websocket_manager.handle_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            
    except WebSocketDisconnect:
        app.state.websocket_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
        app.state.websocket_manager.disconnect(websocket)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )

## Docker Compose (docker-compose.yml)
```yaml
version: '3.8'

services:
  # Kafka & Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost

  # Redis
  redis:
    image: redis:7-alpine
    hostname: redis
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # MongoDB
  mongodb:
    image: mongo:6.0
    hostname: mongodb
    container_name: mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
      MONGO_INITDB_DATABASE: stock_prediction
    volumes:
      - mongodb_data:/data/db

  # MLflow
  mlflow:
    image: python:3.9-slim
    hostname: mlflow
    container_name: mlflow
    ports:
      - "5000:5000"
    command: >
      bash -c "
        pip install mlflow psycopg2-binary &&
        mlflow server 
        --backend-store-uri sqlite:///mlflow.db 
        --default-artifact-root ./artifacts 
        --host 0.0.0.0 
        --port 5000
      "
    volumes:
      - mlflow_data:/mlflow

  # Stock Prediction Streaming Service
  streaming-service:
    build: .
    hostname: streaming-service
    container_name: streaming-service
    ports:
      - "8000:8000"
      - "9090:9090"  # Prometheus metrics
    depends_on:
      - kafka
      - redis
      - mongodb
      - mlflow
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - REDIS_URL=redis://redis:6379
      - MONGODB_URL=mongodb://admin:password@mongodb:27017
      - MODEL_REGISTRY_URL=http://mlflow:5000
      - LOG_LEVEL=INFO
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Prometheus (optional - for monitoring)
  prometheus:
    image: prom/prometheus:latest
    hostname: prometheus
    container_name: prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  # Grafana (optional - for dashboards)
  grafana:
    image: grafana/grafana:latest
    hostname: grafana
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  redis_data:
  mongodb_data:
  mlflow_data:
  grafana_data:

## Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

## Environment Configuration (.env.example)
```env
# Application
APP_NAME=Stock Prediction Streaming
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=stock-prices
KAFKA_SENTIMENT_TOPIC=market-sentiment
KAFKA_PREDICTION_TOPIC=price-predictions
KAFKA_CONSUMER_GROUP=streaming-service

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_TTL=3600

# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=stock_prediction

# External APIs (get your own API keys)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
FINNHUB_API_KEY=your_finnhub_key

# Model Configuration
MODEL_REGISTRY_URL=http://localhost:5000
MODEL_UPDATE_INTERVAL=3600
PRICE_MODEL_NAME=hybrid_price_predictor
SENTIMENT_MODEL_NAME=sentiment_analyzer

# Streaming Configuration
BATCH_SIZE=100
PROCESSING_INTERVAL=60
MAX_RETRIES=3

# Monitoring
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# Security
API_KEY_HEADER=X-API-Key
ALLOWED_ORIGINS=["*"]

# Data Collection
DEFAULT_SYMBOLS=["AAPL","GOOGL","MSFT","TSLA","AMZN","META","NVDA"]
DATA_COLLECTION_INTERVAL=300
```

## Setup Scripts (scripts/start_services.py)
```python
#!/usr/bin/env python3
"""
Script to start all services
"""
import asyncio
import logging
import signal
import sys
from services.price_service import PriceService
from services.sentiment_service import SentimentService
from services.ml_inference_service import MLInferenceService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.services = []
        self.running = False
    
    async def start_all_services(self):
        """Start all services"""
        try:
            # Initialize services
            price_service = PriceService()
            sentiment_service = SentimentService()
            inference_service = MLInferenceService()
            
            self.services = [price_service, sentiment_service, inference_service]
            
            # Start services
            for service in self.services:
                await service.start()
                logger.info(f"Started {service.__class__.__name__}")
            
            self.running = True
            logger.info("All services started successfully")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error starting services: {e}")
            await self.stop_all_services()
            raise
    
    async def stop_all_services(self):
        """Stop all services"""
        self.running = False
        
        for service in self.services:
            try:
                await service.stop()
                logger.info(f"Stopped {service.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error stopping {service.__class__.__name__}: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop_all_services())

async def main():
    manager = ServiceManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        await manager.start_all_services()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
        await manager.stop_all_services()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```1, env="API_WORKERS")
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_PRICE_TOPIC: str = Field(default="stock-prices", env="KAFKA_PRICE_TOPIC")
    KAFKA_SENTIMENT_TOPIC: str = Field(default="market-sentiment", env="KAFKA_SENTIMENT_TOPIC")
    KAFKA_PREDICTION_TOPIC: str = Field(default="price-predictions", env="KAFKA_PREDICTION_TOPIC")
    KAFKA_CONSUMER_GROUP: str = Field(default="streaming-service", env="KAFKA_CONSUMER_GROUP")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_TTL: int = Field(default=3600, env="REDIS_TTL")  # 1 hour
    
    # Database Configuration
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    DATABASE_NAME: str = Field(default="stock_prediction", env="DATABASE_NAME")
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    NEWS_API_KEY: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    FINNHUB_API_KEY: Optional[str] = Field(default=None, env="FINNHUB_API_KEY")
    
    # Model Configuration
    MODEL_REGISTRY_URL: str = Field(default="http://localhost:5000", env="MODEL_REGISTRY_URL")
    MODEL_UPDATE_INTERVAL: int = Field(default=3600, env="MODEL_UPDATE_INTERVAL")  # 1 hour
    PRICE_MODEL_NAME: str = Field(default="hybrid_price_predictor", env="PRICE_MODEL_NAME")
    SENTIMENT_MODEL_NAME: str = Field(default="sentiment_analyzer", env="SENTIMENT_MODEL_NAME")
    
    # Streaming Configuration
    BATCH_SIZE: int = Field(default=100, env="BATCH_SIZE")
    PROCESSING_INTERVAL: int = Field(default=60, env="PROCESSING_INTERVAL")  # seconds
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Security
    API_KEY_HEADER: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Data Collection
    DEFAULT_SYMBOLS: List[str] = Field(
        default=["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"],
        env="DEFAULT_SYMBOLS"
    )
    DATA_COLLECTION_INTERVAL: int = Field(default=300, env="DATA_COLLECTION_INTERVAL")  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Price Service (services/price_service.py)
```python
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
import pandas as pd
from streaming.kafka_producer import KafkaProducerService
from utils.redis_client import RedisClient
from config.settings import settings

logger = logging.getLogger(__name__)

class PriceService:
    """Service for collecting and streaming real-time price data"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducerService()
        self.redis_client = RedisClient()
        self.symbols = settings.DEFAULT_SYMBOLS
        self.running = False
        self.last_prices = {}
        
    async def start(self):
        """Start the price service"""
        self.running = True
        logger.info("Starting Price Service...")
        
        # Start data collection task
        asyncio.create_task(self._collect_price_data())
        
    async def stop(self):
        """Stop the price service"""
        self.running = False
        await self.kafka_producer.close()
        logger.info("Price Service stopped")
    
    async def _collect_price_data(self):
        """Main data collection loop"""
        while self.running:
            try:
                # Collect data for all symbols
                tasks = [self._fetch_symbol_data(symbol) for symbol in self.symbols]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for symbol, result in zip(self.symbols, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching data for {symbol}: {result}")
                        continue
                    
                    if result:
                        await self._process_price_data(symbol, result)
                
                # Wait before next collection
                await asyncio.sleep(settings.DATA_COLLECTION_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in price data collection: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _fetch_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a single symbol"""
        try:
            # Use yfinance to get real-time data
            ticker = yf.Ticker(symbol)
            
            # Get latest price data
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                logger.warning(f"No recent data for {symbol}")
                return None
            
            latest = hist.iloc[-1]
            
            # Get additional info
            info = ticker.info
            
            price_data = {
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "close": float(latest['Close']),
                "volume": int(latest['Volume']),
                "timestamp": latest.name.isoformat(),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "avg_volume": info.get('averageVolume'),
                "dividend_yield": info.get('dividendYield')
            }
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def _process_price_data(self, symbol: str, price_data: Dict[str, Any]):
        """Process and stream price data"""
        try:
            # Add metadata
            processed_data = {
                **price_data,
                "symbol": symbol,
                "collected_at": datetime.now().isoformat(),
                "source": "yfinance"
            }
            
            # Calculate additional metrics
            if symbol in self.last_prices:
                last_price = self.last_prices[symbol].get('close', 0)
                current_price = price_data['close']
                
                processed_data.update({
                    "price_change": current_price - last_price,
                    "price_change_percent": ((current_price - last_price) / last_price * 100) if last_price > 0 else 0
                })
            
            # Store in Redis for quick access
            redis_key = f"price:{symbol}"
            await self.redis_client.set_json(redis_key, processed_data, ttl=settings.REDIS_TTL)
            
            # Send to Kafka
            await self.kafka_producer.send_price_data(
                topic=settings.KAFKA_PRICE_TOPIC,
                symbol=symbol,
                data=processed_data
            )
            
            # Update last prices
            self.last_prices[symbol] = processed_data
            
            logger.debug(f"Processed price data for {symbol}: ${price_data['close']}")
            
        except Exception as e:
            logger.error(f"Error processing price data for {symbol}: {e}")
    
    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for a symbol"""
        try:
            redis_key = f"price:{symbol}"
            return await self.redis_client.get_json(redis_key)
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, 
                                symbol: str, 
                                period: str = "1mo",
                                interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return None
            
            # Reset index to make timestamp a column
            hist.reset_index(inplace=True)
            hist['symbol'] = symbol
            
            return hist
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def add_symbol(self, symbol: str):
        """Add a new symbol to track"""
        if symbol not in self.symbols:
            self.symbols.append(symbol.upper())
            logger.info(f"Added {symbol} to tracking list")
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from tracking"""
        if symbol in self.symbols:
            self.symbols.remove(symbol.upper())
            logger.info(f"Removed {symbol} from tracking list")

## Sentiment Service (services/sentiment_service.py)
```python
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from streaming.kafka_producer import KafkaProducerService
from utils.redis_client import RedisClient
from config.settings import settings

logger = logging.getLogger(__name__)

class SentimentService:
    """Service for collecting and analyzing market sentiment"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducerService()
        self.redis_client = RedisClient()
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.symbols = settings.DEFAULT_SYMBOLS
        self.running = False
        
        # Financial keywords for enhanced sentiment analysis
        self.financial_keywords = {
            'positive': ['bullish', 'bull', 'buy', 'strong', 'growth', 'profit', 'earnings', 'upgrade', 'outperform'],
            'negative': ['bearish', 'bear', 'sell', 'weak', 'decline', 'loss', 'downgrade', 'underperform', 'crash']
        }
        
    async def start(self):
        """Start the sentiment service"""
        self.running = True
        logger.info("Starting Sentiment Service...")
        
        # Start sentiment collection task
        asyncio.create_task(self._collect_sentiment_data())
        
    async def stop(self):
        """Stop the sentiment service"""
        self.running = False
        await self.kafka_producer.close()
        logger.info("Sentiment Service stopped")
    
    async def _collect_sentiment_data(self):
        """Main sentiment collection loop"""
        while self.running:
            try:
                # Collect sentiment for all symbols
                tasks = [self._analyze_symbol_sentiment(symbol) for symbol in self.symbols]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for symbol, result in zip(self.symbols, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error analyzing sentiment for {symbol}: {result}")
                        continue
                    
                    if result:
                        await self._process_sentiment_data(symbol, result)
                
                # Wait before next collection (sentiment updates less frequently)
                await asyncio.sleep(settings.DATA_COLLECTION_INTERVAL * 4)  # 20 minutes
                
            except Exception as e:
                logger.error(f"Error in sentiment collection: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _analyze_symbol_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment for a single symbol"""
        try:
            # Collect news data
            news_data = await self._fetch_news_data(symbol)
            
            if not news_data:
                logger.warning(f"No news data found for {symbol}")
                return None
            
            # Analyze sentiment from news
            sentiment_scores = []
            article_count = 0
            
            for article in news_data:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                if text.strip():
                    sentiment = self._analyze_text_sentiment(text)
                    sentiment_scores.append(sentiment)
                    article_count += 1
            
            if not sentiment_scores:
                return None
            
            # Aggregate sentiment scores
            overall_sentiment = self._aggregate_sentiment(sentiment_scores)
            
            # Add metadata
            sentiment_data = {
                **overall_sentiment,
                "article_count": article_count,
                "source": "news_api",
                "analyzed_at": datetime.now().isoformat(),
                "symbol": symbol
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return None
    
    async def _fetch_news_data(self, symbol: str, days: int = 1) -> List[Dict[str, Any]]:
        """Fetch news data for a symbol"""
        if not settings.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not configured")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'{symbol} stock OR {symbol} shares',
                'from': from_date,
                'sortBy': 'publishedAt',
                'apiKey': settings.NEWS_API_KEY,
                'language': 'en',
                'pageSize': 50
            }
            
            async with asyncio.timeout(30):  # 30 second timeout
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get('articles', [])
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def _analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text"""
        if not text:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        # Clean text
        text = text.lower().strip()
        
        # VADER sentiment analysis
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # Financial keyword analysis
        financial_score = self._analyze_financial_keywords(text)
        
        # Combine scores with weights
        combined_sentiment = (
            vader_scores['compound'] * 0.4 +
            textblob_sentiment * 0.3 +
            financial_score * 0.3
        )
        
        return {
            'compound': combined_sentiment,
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'textblob_sentiment': textblob_sentiment,
            'financial_sentiment': financial_score
        }
    
    def _analyze_financial_keywords(self, text: str) -> float:
        """Analyze financial keywords in text"""
        words = text.split()
        positive_count = 0
        negative_count = 0
        
        for word in words:
            if word in self.financial_keywords['positive']:
                positive_count += 1
            elif word in self.financial_keywords['negative']:
                negative_count += 1
        
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return 0.0
        
        # Return sentiment score between -1 and 1
        return (positive_count - negative_count) / total_keywords
    
    def _aggregate_sentiment(self, sentiment_scores: List[Dict[str, float]]) -> Dict[str, Any]:
        """Aggregate multiple sentiment scores"""
        if not sentiment_scores:
            return {
                'overall_sentiment': 0.0,
                'sentiment_magnitude': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 1.0
            }
        
        # Calculate overall sentiment (weighted average)
        compounds = [score['compound'] for score in sentiment_scores]
        overall_sentiment = sum(compounds) / len(compounds)
        
        # Calculate sentiment magnitude (standard deviation)
        if len(compounds) > 1:
            mean_sentiment = overall_sentiment
            variance = sum((x - mean_sentiment) ** 2 for x in compounds) / len(compounds)
            sentiment_magnitude = variance ** 0.5
        else:
            sentiment_magnitude = 0.0
        
        # Calculate ratios
        positive_count = sum(1 for score in sentiment_scores if score['compound'] > 0.1)
        negative_count = sum(1 for score in sentiment_scores if score['compound'] < -0.1)
        neutral_count = len(sentiment_scores) - positive_count - negative_count
        
        total_count = len(sentiment_scores)
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_magnitude': sentiment_magnitude,
            'positive_ratio': positive_count / total_count,
            'negative_ratio': negative_count / total_count,
            'neutral_ratio': neutral_count / total_count,
            'sentiment_trend': self._calculate_sentiment_trend(sentiment_scores)
        }
    
    def _calculate_sentiment_trend(self, sentiment_scores: List[Dict[str, float]]) -> float:
        """Calculate sentiment trend (recent vs older sentiment)"""
        if len(sentiment_scores) < 4:
            return 0.0
        
        # Split into recent and older sentiment
        mid_point = len(sentiment_scores) // 2
        older_sentiment = [score['compound'] for score in sentiment_scores[:mid_point]]
        recent_sentiment = [score['compound'] for score in sentiment_scores[mid_point:]]
        
        older_avg = sum(older_sentiment) / len(older_sentiment)
        recent_avg = sum(recent_sentiment) / len(recent_sentiment)
        
        return recent_avg - older_avg
    
    async def _process_sentiment_data(self, symbol: str, sentiment_data: Dict[str, Any]):
        """Process and stream sentiment data"""
        try:
            # Store in Redis
            redis_key = f"sentiment:{symbol}"
            await self.redis_client.set_json(redis_key, sentiment_data, ttl=settings.REDIS_TTL)
            
            # Send to Kafka
            await self.kafka_producer.send_sentiment_data(
                topic=settings.KAFKA_SENTIMENT_TOPIC,
                symbol=symbol,
                data=sentiment_data
            )
            
            logger.debug(f"Processed sentiment for {symbol}: {sentiment_data['overall_sentiment']:.3f}")
            
        except Exception as e:
            logger.error(f"Error processing sentiment data for {symbol}: {e}")
    
    async def get_latest_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest sentiment for a symbol"""
        try:
            redis_key = f"sentiment:{symbol}"
            return await self.redis_client.get_json(redis_key)
        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {e}")
            return None

## ML Inference Service (services/ml_inference_service.py)
```python
import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from kafka import KafkaConsumer
from streaming.kafka_producer import KafkaProducerService
from utils.redis_client import RedisClient
from services.model_loader import ModelLoader
from config.settings import settings

logger = logging.getLogger(__name__)

class MLInferenceService:
    """ML inference service for real-time predictions"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducerService()
        self.redis_client = RedisClient()
        self.model_loader = ModelLoader()
        
        # Data buffers for inference
        self.price_buffer = {}
        self.sentiment_buffer = {}
        
        # Models
        self.price_model = None
        self.sentiment_model = None
        
        self.running = False
        
    async def start(self):
        """Start the ML inference service"""
        self.running = True
        logger.info("Starting ML Inference Service...")
        
        # Load models
        await self._load_models()
        
        # Start inference task
        asyncio.create_task(self._inference_loop())
        
        # Start model update task
        asyncio.create_task(self._model_update_loop())
        
    async def stop(self):
        """Stop the ML inference service"""
        self.running = False
        await self.kafka_producer.close()
        logger.info("ML Inference Service stopped")
    
    async def _load_models(self):
        """Load ML models"""
        try:
            # Load price prediction model
            self.price_model = await self.model_loader.load_model(
                settings.PRICE_MODEL_NAME, "latest"
            )
            
            if self.price_model:
                logger.info("Price prediction model loaded successfully")
            else:
                logger.warning("Failed to load price prediction model")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    async def _model_update_loop(self):
        """Periodically update models"""
        while self.running:
            try:
                await asyncio.sleep(settings.MODEL_UPDATE_INTERVAL)
                
                # Check for model updates
                new_model = await self.model_loader.load_model(
                    settings.PRICE_MODEL_NAME, "latest"
                )
                
                if new_model and new_model != self.price_model:
                    self.price_model = new_model
                    logger.info("Updated price prediction model")
                    
            except Exception as e:
                logger.error(f"Error updating models: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _inference_loop(self):
        """Main inference loop"""
        while self.running:
            try:
                # Get symbols with sufficient data
                symbols_ready = await self._get_symbols_ready_for_prediction()
                
                # Generate predictions for each symbol
                tasks = [self._generate_prediction(symbol) for symbol in symbols_ready]
                predictions = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process predictions
                for symbol, prediction in zip(symbols_ready, predictions):
                    if isinstance(prediction, Exception):
                        logger.error(f"Error generating prediction for {symbol}: {prediction}")
                        continue
                    
                    if prediction:
                        await self._send_prediction(symbol, prediction)
                
                # Wait before next inference cycle
                await asyncio.sleep(settings.PROCESSING_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in inference loop: {e}")
                await asyncio.sleep(60)
    
    async def _get_symbols_ready_for_prediction(self) -> List[str]:
        """Get symbols with sufficient data for prediction"""
        ready_symbols = []
        
        for symbol in settings.DEFAULT_SYMBOLS:
            try:
                # Check if we have recent price data
                price_key = f"price:{symbol}"
                price_data = await self.redis_client.get_json(price_key)
                
                # Check if we have recent sentiment data
                sentiment_key = f"sentiment:{symbol}"
                sentiment_data = await self.redis_client.get_json(sentiment_key)
                
                if price_data and sentiment_data:
                    # Check data freshness
                    price_time = datetime.fromisoformat(price_data.get('collected_at', ''))
                    sentiment_time = datetime.fromisoformat(sentiment_data.get('analyzed_at', ''))
                    
                    now = datetime.now()
                    
                    # Data should be less than 30 minutes old
                    if (now - price_time).seconds < 1800 and (now - sentiment_time).seconds < 3600:
                        ready_symbols.append(symbol)
                
            except Exception as e:
                logger.debug(f"Symbol {symbol} not ready for prediction: {e}")
                continue
        
        return ready_symbols
    
    async def _generate_prediction(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate prediction for a symbol"""
        try:
            if not self.price_model:
                logger.warning("No price model available for prediction")
                return None
            
            # Prepare features
            features = await self._prepare_features(symbol)
            if features is None:
                return None
            
            # Make prediction
            if hasattr(self.price_model, 'predict'):
                predictions = self.price_model.predict(features)
            else:
                # Fallback prediction
                predictions = await self._simple_prediction(symbol)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(symbol, predictions)
            
            # Get current price for reference
            price_data = await self.redis_client.get_json(f"price:{symbol}")
            current_price = price_data.get('close', 0) if price_data else 0
            
            prediction_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'current_price': current_price,
                'predictions': predictions,
                'confidence': confidence,
                'model_version': getattr(self.price_model, 'version', 'unknown'),
                'features_used': await self._get_feature_summary(symbol)
            }
            
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error generating prediction for {symbol}: {e}")
            return None
    
    async def _prepare_features(self, symbol: str) -> Optional[np.ndarray]:
        """Prepare features for prediction"""
        try:
            # Get historical price data (simplified - in production, you'd have more sophisticated feature preparation)
            price_data = await self.redis_client.get_json(f"price:{symbol}")
            sentiment_data = await self.redis_client.get_json(f"sentiment:{symbol}")
            
            if not price_data or not sentiment_data:
                return None
            
            # Create feature vector (simplified)
            features = np.array([
                price_data.get('close', 0),
                price_data.get('volume', 0),
                price_data.get('price_change_percent', 0),
                sentiment_data.get('overall_sentiment', 0),
                sentiment_data.get('sentiment_magnitude', 0),
                sentiment_data.get('positive_ratio', 0),
                sentiment_data.get('negative_ratio', 0)
            ]).reshape(1, 1, -1)  # Reshape for LSTM input
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features for {symbol}: {e}")
            return None
    
    async def _simple_prediction(self, symbol: str) -> Dict[str, float]:
        """Simple fallback prediction"""
        try:
            price_data = await self.redis_client.get_json(f"price:{symbol}")
            sentiment_data = await self.redis_client.get_json(f"sentiment:{symbol}")
            
            if not price_data:
                return {'simple': 0.0}
            
            current_price = price_data.get('close', 0)
            price_change = price_data.get('price_change_percent', 0)
            sentiment = sentiment_data.get('overall_sentiment', 0) if sentiment_data else 0
            
            # Simple prediction based on momentum and sentiment
            momentum_factor = 1 + (price_change / 100) * 0.5
            sentiment_factor = 1 + sentiment * 0.1
            
            predicted_price = current_price * momentum_factor * sentiment_factor
            
            return {
                'simple': predicted_price,
                'current_price': current_price,
                'momentum_factor': momentum_factor,
                'sentiment_factor': sentiment_factor
            }
            
        except Exception as e:
            logger.error(f"Error in simple prediction for {symbol}: {e}")
            return {'simple': 0.0}
    
    async def _calculate_confidence(self, symbol: str, predictions: Dict[str, float]) -> float:
        """Calculate prediction confidence"""
        try:
            # Base confidence on data quality and model agreement
            base_confidence = 0.5
            
            # Check data freshness
            price_data = await self.redis_client.get_json(f"price:{symbol}")
            sentiment_data = await self.redis_client.get_json(f"sentiment:{symbol}")
            
            if price_data and sentiment_data:
                price_time = datetime.fromisoformat(price_data.get('collected_at', ''))
                sentiment_time = datetime.fromisoformat(sentiment_data.get('analyzed_at', ''))
                now = datetime.now()
                
                # Higher confidence for fresher data
                price_freshness = max(0, 1 - (now - price_time).seconds / 3600)  # 1 hour decay
                sentiment_freshness = max(0, 1 - (now - sentiment_time).seconds / 7200)  # 2 hour decay
                # Repository 2: Streaming & Inference Service
# stock-prediction-streaming/

## Project Structure
```
stock-prediction-streaming/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── kafka_config.py
├── services/
│   ├── __init__.py
│   ├── price_service.py
│   ├── sentiment_service.py
│   ├── ml_inference_service.py
│   └── model_loader.py
├── streaming/
│   ├── __init__.py
│   ├── kafka_producer.py
│   ├── kafka_consumer.py
│   ├── stream_processor.py
│   └── data_pipeline.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── predictions.py
│   │   ├── market_data.py
│   │   └── websocket.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── rate_limit.py
│   └── schemas/
│       ├── __init__.py
│       ├── prediction.py
│       └── market_data.py
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py
│   ├── health_check.py
│   └── alerts.py
├── utils/
│   ├── __init__.py
│   ├── redis_client.py
│   ├── logger.py
│   └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_services.py
│   ├── test_streaming.py
│   └── test_api.py
└── scripts/
    ├── start_services.py
    ├── setup_kafka.py
    └── deploy.sh
```

## Requirements (requirements.txt)
```
# Core Framework
fastapi>=0.85.0
uvicorn[standard]>=0.18.0
websockets>=10.3

# Streaming & Messaging
kafka-python>=2.0.2
confluent-kafka>=1.9.0
redis>=4.3.0

# Data & ML
pandas>=1.4.0
numpy>=1.21.0
scikit-learn>=1.1.0
torch>=1.12.0
mlflow>=1.28.0

# HTTP & API
httpx>=0.23.0
requests>=2.28.0
pydantic>=1.10.0

# Database
pymongo>=4.2.0
motor>=3.0.0

# Monitoring & Logging
prometheus-client>=0.14.0
structlog>=22.1.0

# Financial Data
yfinance>=0.1.74
alpha-vantage>=2.3.0

# Sentiment Analysis
textblob>=0.17.0
vaderSentiment>=3.3.0
transformers>=4.21.0

# Utilities
python-dotenv>=0.20.0
click>=8.1.0
schedule>=1.1.0
aiofiles>=0.8.0

# Development
pytest>=7.1.0
pytest-asyncio>=0.19.0
black>=22.6.0
flake8>=5.0.0
```

## Configuration (config/settings.py)
```python
import os
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Application
    APP_NAME: str = Field(default="Stock Prediction Streaming", env="APP_NAME")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=