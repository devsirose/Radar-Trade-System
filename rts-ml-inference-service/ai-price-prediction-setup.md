# Hướng dẫn cài đặt hệ thống dự đoán giá với AI

## Phần 1: Cài đặt môi trường cơ bản

### 1.1. Yêu cầu hệ thống
```bash
# Minimum requirements
- CPU: 4 cores
- RAM: 16GB
- Storage: 100GB SSD
- OS: Ubuntu 20.04+ hoặc CentOS 8+
- Docker & Docker Compose
- Python 3.8+
```

### 1.2. Cài đặt Docker và Docker Compose
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 1.3. Clone project và cấu trúc thư mục
```bash
# Create project directory
mkdir -p ~/crypto-prediction-system
cd ~/crypto-prediction-system

# Create directory structure
mkdir -p {services,config,data,logs,models,scripts}
mkdir -p services/{price-service,sentiment-service,ml-inference,feature-engineering}
mkdir -p data/{kafka,zookeeper,postgres,redis}
mkdir -p models/{registry,artifacts}
```

## Phần 2: Cài đặt Kafka Cluster

### 2.1. Docker Compose cho Kafka
```yaml
# docker-compose-kafka.yml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - ./data/zookeeper/data:/var/lib/zookeeper/data
      - ./data/zookeeper/logs:/var/lib/zookeeper/log
    networks:
      - prediction-network

  kafka1:
    image: confluentinc/cp-kafka:7.4.0
    container_name: kafka1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
    volumes:
      - ./data/kafka/kafka1:/var/lib/kafka/data
    networks:
      - prediction-network

  kafka2:
    image: confluentinc/cp-kafka:7.4.0
    container_name: kafka2
    depends_on:
      - zookeeper
    ports:
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:29093,PLAINTEXT_HOST://localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9102
      KAFKA_JMX_HOSTNAME: localhost
    volumes:
      - ./data/kafka/kafka2:/var/lib/kafka/data
    networks:
      - prediction-network

  kafka3:
    image: confluentinc/cp-kafka:7.4.0
    container_name: kafka3
    depends_on:
      - zookeeper
    ports:
      - "9094:9094"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:29094,PLAINTEXT_HOST://localhost:9094
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9103
      KAFKA_JMX_HOSTNAME: localhost
    volumes:
      - ./data/kafka/kafka3:/var/lib/kafka/data
    networks:
      - prediction-network

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      - kafka1
      - kafka2
      - kafka3
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka1:29092,kafka2:29093,kafka3:29094
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    networks:
      - prediction-network

networks:
  prediction-network:
    driver: bridge
```

### 2.2. Khởi động Kafka và tạo topics
```bash
# Start Kafka cluster
docker-compose -f docker-compose-kafka.yml up -d

# Wait for Kafka to be ready
sleep 30

# Create topics
docker exec kafka1 kafka-topics --create \
  --bootstrap-server kafka1:29092 \
  --replication-factor 3 \
  --partitions 6 \
  --topic price.stream

docker exec kafka1 kafka-topics --create \
  --bootstrap-server kafka1:29092 \
  --replication-factor 3 \
  --partitions 6 \
  --topic sentiment.data

docker exec kafka1 kafka-topics --create \
  --bootstrap-server kafka1:29092 \
  --replication-factor 3 \
  --partitions 6 \
  --topic market.events

docker exec kafka1 kafka-topics --create \
  --bootstrap-server kafka1:29092 \
  --replication-factor 3 \
  --partitions 3 \
  --topic predictions.stream

# Verify topics
docker exec kafka1 kafka-topics --list --bootstrap-server kafka1:29092
```

## Phần 3: Cài đặt Database và Cache

### 3.1. Docker Compose cho PostgreSQL và Redis
```yaml
# docker-compose-storage.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres-predictions
    environment:
      POSTGRES_DB: crypto_predictions
      POSTGRES_USER: prediction_user
      POSTGRES_PASSWORD: prediction_pass
    ports:
      - "5432:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - prediction-network

  redis:
    image: redis:7-alpine
    container_name: redis-predictions
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    networks:
      - prediction-network

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: redis-commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    networks:
      - prediction-network

networks:
  prediction-network:
    external: true
```

### 3.2. Initialize Database Script
```sql
-- scripts/init-db.sql
-- Create database and schemas
CREATE DATABASE crypto_predictions;
\c crypto_predictions;

-- Create ml_predictions schema
CREATE SCHEMA IF NOT EXISTS ml_predictions;

-- Create tables (copy from previous schema)
-- ... (insert all CREATE TABLE statements from previous response)

-- Create initial indexes
CREATE INDEX idx_predictions_created_at ON ml_predictions.predictions(created_at DESC);
CREATE INDEX idx_model_performance_version ON ml_predictions.model_performance(model_version, timestamp DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA ml_predictions TO prediction_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ml_predictions TO prediction_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ml_predictions TO prediction_user;
```

### 3.3. Start Storage Services
```bash
# Start storage services
docker-compose -f docker-compose-storage.yml up -d

# Verify PostgreSQL
docker exec -it postgres-predictions psql -U prediction_user -d crypto_predictions -c "\dt ml_predictions.*"

# Verify Redis
docker exec -it redis-predictions redis-cli ping
```

## Phần 4: Cài đặt ML Services

### 4.1. ML Inference Service Setup
```bash
cd services/ml-inference

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << EOF
aiokafka==0.8.1
asyncpg==0.28.0
aioredis==2.0.1
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
tensorflow==2.13.0
mlflow==2.7.1
prometheus-client==0.17.1
pydantic==2.4.2
python-json-logger==2.0.7
EOF

# Install dependencies
pip install -r requirements.txt
```

### 4.2. Dockerfile cho ML Inference Service
```dockerfile
# services/ml-inference/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV KAFKA_BOOTSTRAP_SERVERS=kafka1:29092,kafka2:29093,kafka3:29094
ENV POSTGRES_URL=postgresql://prediction_user:prediction_pass@postgres-predictions:5432/crypto_predictions
ENV REDIS_URL=redis://redis-predictions:6379

# Run the service
CMD ["python", "-m", "services.ml_inference_service"]
```

### 4.3. Docker Compose cho ML Services
```yaml
# docker-compose-ml.yml
version: '3.8'

services:
  ml-inference-1:
    build: ./services/ml-inference
    container_name: ml-inference-1
    environment:
      CONSUMER_ID: 1
      KAFKA_GROUP_ID: ml-inference-group
      MODEL_REGISTRY_URL: http://mlflow-server:5000
    depends_on:
      - mlflow-server
    networks:
      - prediction-network
    restart: unless-stopped

  ml-inference-2:
    build: ./services/ml-inference
    container_name: ml-inference-2
    environment:
      CONSUMER_ID: 2
      KAFKA_GROUP_ID: ml-inference-group
      MODEL_REGISTRY_URL: http://mlflow-server:5000
    depends_on:
      - mlflow-server
    networks:
      - prediction-network
    restart: unless-stopped

  ml-inference-3:
    build: ./services/ml-inference
    container_name: ml-inference-3
    environment:
      CONSUMER_ID: 3
      KAFKA_GROUP_ID: ml-inference-group
      MODEL_REGISTRY_URL: http://mlflow-server:5000
    depends_on:
      - mlflow-server
    networks:
      - prediction-network
    restart: unless-stopped

  mlflow-server:
    image: python:3.9-slim
    container_name: mlflow-server
    command: >
      bash -c "pip install mlflow boto3 psycopg2-binary &&
               mlflow server --host 0.0.0.0 --port 5000
               --backend-store-uri postgresql://prediction_user:prediction_pass@postgres-predictions:5432/crypto_predictions
               --default-artifact-root /mlflow/artifacts"
    ports:
      - "5000:5000"
    volumes:
      - ./models/artifacts:/mlflow/artifacts
    networks:
      - prediction-network
    restart: unless-stopped

networks:
  prediction-network:
    external: true
```

## Phần 5: Monitoring và Logging

### 5.1. Prometheus và Grafana Setup
```yaml
# docker-compose-monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - prediction-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - prediction-network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    networks:
      - prediction-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  prediction-network:
    external: true
```

### 5.2. Prometheus Configuration
```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ml-inference'
    static_configs:
      - targets: ['ml-inference-1:8000', 'ml-inference-2:8000', 'ml-inference-3:8000']

  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka1:9101', 'kafka2:9102', 'kafka3:9103']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

## Phần 6: Khởi động toàn bộ hệ thống

### 6.1. Script khởi động
```bash
#!/bin/bash
# scripts/start-system.sh

echo "Starting Crypto Prediction System..."

# Create network
docker network create prediction-network 2>/dev/null

# Start Kafka
echo "Starting Kafka cluster..."
docker-compose -f docker-compose-kafka.yml up -d

# Wait for Kafka
echo "Waiting for Kafka to be ready..."
sleep 30

# Create topics
echo "Creating Kafka topics..."
./scripts/create-topics.sh

# Start Storage
echo "Starting storage services..."
docker-compose -f docker-compose-storage.yml up -d

# Wait for storage
sleep 20

# Start ML Services
echo "Building and starting ML services..."
docker-compose -f docker-compose-ml.yml up -d --build

# Start Monitoring
echo "Starting monitoring services..."
docker-compose -f docker-compose-monitoring.yml up -d

echo "System started successfully!"
echo "Access points:"
echo "- Kafka UI: http://localhost:8080"
echo "- MLflow: http://localhost:5000"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- Prometheus: http://localhost:9090"
echo "- Redis Commander: http://localhost:8081"
```

### 6.2. Verification Script
```bash
#!/bin/bash
# scripts/verify-system.sh

echo "Verifying system components..."

# Check Kafka
echo -n "Kafka: "
docker exec kafka1 kafka-broker-api-versions --bootstrap-server kafka1:29092 &>/dev/null && echo "OK" || echo "FAILED"

# Check PostgreSQL
echo -n "PostgreSQL: "
docker exec postgres-predictions pg_isready &>/dev/null && echo "OK" || echo "FAILED"

# Check Redis
echo -n "Redis: "
docker exec redis-predictions redis-cli ping &>/dev/null && echo "OK" || echo "FAILED"

# Check ML Services
echo -n "ML Inference Services: "
docker ps | grep -c "ml-inference" | xargs -I {} echo "{}/3 running"

# Check MLflow
echo -n "MLflow: "
curl -s http://localhost:5000/health &>/dev/null && echo "OK" || echo "FAILED"
```

## Phần 7: Training và Deploy Model

### 7.1. Train Model Script
```python
# scripts/train_model.py
import mlflow
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

def train_price_prediction_model():
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    # Start MLflow run
    with mlflow.start_run():
        # Generate sample data (replace with real data)
        X = np.random.rand(10000, 15)  # 15 features
        y = np.random.rand(10000, 3)   # 3 targets (1h, 4h, 24h)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        score = model.score(X_test, y_test)
        
        # Log metrics
        mlflow.log_metric("r2_score", score)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)
        
        # Save model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="price_prediction"
        )
        
        print(f"Model trained with R2 score: {score}")

if __name__ == "__main__":
    train_price_prediction_model()
```

### 7.2. Deploy Model
```bash
# Deploy model to production
python scripts/promote_model.py --model-name price_prediction --version 1 --stage Production
```

## Phần 8: Khóa học và tài liệu học tập

### 8.1. Khóa học Online được đề xuất

#### **1. Coursera**
- **"Machine Learning Engineering for Production (MLOps)"** - Andrew Ng
  - Link: https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops
  - Nội dung: MLOps, Model deployment, Monitoring
  - Phù hợp cho: Production ML systems

- **"Apache Kafka Series"** - Stephane Maarek
  - Covers: Kafka fundamentals, Kafka Streams, Kafka Connect
  - Platform: Udemy

#### **2. Udemy**
- **"Event-Driven Microservices: Spring Boot, Kafka and Elastic"**
  - Tập trung vào Kafka và microservices
  - Hands-on projects

- **"Complete Guide to Building ML Systems with Feature Stores"**
  - Feature engineering at scale
  - Real-time ML pipelines

#### **3. Fast.ai**
- **"Practical Deep Learning for Coders"**
  - Link: https://course.fast.ai/
  - Free, practical approach
  - Focus on deployment

### 8.2. Sách tham khảo

1. **"Designing Machine Learning Systems"** - Chip Huyen
   - Kiến trúc ML systems
   - Real-time ML
   - Monitoring và debugging

2. **"Building Machine Learning Powered Applications"** - Emmanuel Ameisen
   - End-to-end ML projects
   - Production considerations

3. **"Kafka: The Definitive Guide"** - Neha Narkhede
   - Kafka architecture
   - Best practices
   - Performance tuning

### 8.3. Resources và Documentation

#### **Official Documentation**
- Kafka: https://kafka.apache.org/documentation/
- MLflow: https://mlflow.org/docs/latest/index.html
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/documentation

#### **GitHub Repositories**
```bash
# Awesome MLOps
https://github.com/visenger/awesome-mlops

# ML System Design
https://github.com/chiphuyen/machine-learning-systems-design

# Real-time ML
https://github.com/online-ml/river
```

### 8.4. Hands-on Projects

#### **Project 1: Basic Price Prediction**
```python
# Bắt đầu với project đơn giản
# 1. Thu thập dữ liệu từ 1 exchange
# 2. Train model đơn giản (Linear Regression)
# 3. Deploy với Flask API
# 4. Monitor với Prometheus
```

#### **Project 2: Stream Processing**
```python
# Xử lý real-time data
# 1. Setup Kafka với 1 broker
# 2. Stream price data
# 3. Calculate moving averages
# 4. Store in Redis
```

#### **Project 3: Full System**
```python
# Combine tất cả components
# 1. Multi-source data collection
# 2. Feature engineering pipeline
# 3. Model training và deployment
# 4. Real-time predictions
# 5. Monitoring và alerting
```

### 8.5. Learning Path được đề xuất

```mermaid
graph TD
    A[Python Basics] --> B[ML Fundamentals]
    B --> C[Kafka & Streaming]
    C --> D[Docker & Containers]
    D --> E[MLOps Basics]
    E --> F[System Design]
    F --> G[Production Deployment]
    
    B --> H[Time Series Analysis]
    H --> I[Financial ML]
    
    C --> J[Real-time Processing]
    J --> K[Feature Engineering]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#9f9,stroke:#333,stroke-width:2px
```

### 8.6. Thời gian học tập ước tính

| Phase | Nội dung | Thời gian |
|-------|----------|-----------|
| 1 | Python & ML Basics | 2-3 months |
| 2 | Kafka & Streaming | 1-2 months |
| 3 | Docker & DevOps | 1 month |
| 4 | MLOps & Production | 2-3 months |
| 5 | Build Full System | 2-3 months |

**Tổng thời gian**: 8-12 tháng để master được toàn bộ system

### 8.7. Tips để học hiệu quả

1. **Start Small**: Bắt đầu với components đơn giản
2. **Hands-on First**: Code trước, theory sau
3. **Build Projects**: Áp dụng ngay những gì học được
4. **Join Communities**: 
   - MLOps Community Slack
   - Kafka Users Group
   - Reddit: r/MachineLearning

5. **Practice Daily**: Dành 1-2 giờ mỗi ngày
6. **Document Everything**: Viết blog về journey của bạn

Bạn có muốn tôi giải thích chi tiết hơn về phần nào không?