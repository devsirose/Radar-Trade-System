# 📄 Requirement: Exchange Gateway Processor Service

## 🎯 Mục tiêu

Xây dựng service `exchange-processor` có nhiệm vụ:

* Tiếp nhận và xử lý dữ liệu giá từ các nguồn như Binance, Coinbase...
* Thực hiện fan-out dữ liệu tới các consumer khác nhau (price-service, analytics, prediction...)
* Đảm bảo khả năng xử lý theo thời gian thực, mở rộng và dễ maintain.

---

## 📌 Functional Requirements

1. **Input nguồn dữ liệu**
   * Nhận real-time price từ WebSocket (Binance, etc.)
   * Có thể mở rộng thêm Kafka / Redis Stream nếu cần
2. **Xử lý dữ liệu**
   * Parse dữ liệu JSON thành domain object chuẩn
   * Chuẩn hóa giá (price, volume, symbol, timestamp)
   * Có thể thêm validate, enrich dữ liệu (nếu cần)
3. **Fan-out**
   * Gửi dữ liệu đã xử lý tới các channel:
     * ✅ Redis Pub/Sub
     * ✅ Kafka topic (nếu dùng event sourcing)
     * ✅ SSE Endpoint
4. **Monitoring & Logging**
   * Ghi log mỗi khi có lỗi parse hoặc push fail
   * Expose Prometheus metrics (số lượng msg/s, errors, latency...)
5. **Configurable**
   * Cho phép bật/tắt từng nguồn dữ liệu
   * Cho phép cấu hình các kênh output

---

## 🧩 Suggested Architecture / Flow

```
           +---------------------+
           | WebSocket Client(s) |
           +----------+----------+
                      |
                      v
           +----------+----------+
           |   Raw Message Input |
           +----------+----------+
                      |
                      v
           +----------+----------+
           |   ExchangeProcessor  | <-- service chính
           | (parse + transform) |
           +----------+----------+
                      |
     +----------------+----------------+
     |                |                |
     v                v                v
Redis Pub/Sub   Kafka Topic   SSE Endpoint (price-service)

```

---

## 🚀 Gợi ý triển khai bằng Spring Boot (Reactive)

### 📦 Module

* `exchange-processor`
* Dùng Spring Boot WebFlux + Reactor + WebSocket Client

### 🔧 Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
<dependency>
    <groupId>io.projectreactor.netty</groupId>
    <artifactId>reactor-netty</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis-reactive</artifactId>
</dependency>
```

### 🔁 WebSocket Client (Binance)

```java
WebSocketClient client = new ReactorNettyWebSocketClient();
URI uri = URI.create("wss://stream.binance.com/ws/btcusdt@trade");

client.execute(uri, session ->
    session.receive()
           .map(WebSocketMessage::getPayloadAsText)
           .map(this::processRawPriceMessage)
           .doOnNext(this::fanOut)
           .then()
).subscribe();
```

### 🔄 fanOut Method

```java
private void fanOut(PriceEvent event) {
    redisTemplate.convertAndSend("price-channel", event);
    kafkaTemplate.send("price-topic", event);
    // Optionally cache in Redis or expose over SSE
}
```

### 📈 Monitoring

* Micrometer + Prometheus:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
```

---

## ✅ Test Cases

* WebSocket nhận được dữ liệu trong 100ms
* Event được gửi tới Redis Pub/Sub thành công
* SSE client nhận được dữ liệu liên tục

---

## 🔮 Future Ideas

* Buffering, backpressure handling
* Health check đến WebSocket endpoints
* Multiple input sources (multi-symbol)
* Fallback từ Redis sang Kafka nếu kênh lỗi

---

> Bạn có thể dùng cấu trúc này để dựng PoC hoặc triển khai service thực tế.
>
