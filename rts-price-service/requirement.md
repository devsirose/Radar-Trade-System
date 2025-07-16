# Price-Service - RadarTrade

## 🎯 Chức năng chính của price-service


| Vai trò                                          | Mô tả                                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Lấy dữ liệu giá từ sàn (Binance)            | Kết nối tới WebSocket của Binance để lấy dữ liệu nến (candlestick / ticker) theo thời gian thực   |
| Cập nhật realtime                               | Stream dữ liệu giá theo các cặp coin như BTC/USDT, ETH/USDT cho nhiều khung thời gian (1m, 5m, 1h...) |
| Phục vụ frontend biểu đồ                     | Cung cấp dữ liệu cho frontend hiển thị biểu đồ kỹ thuật (TradingView, ChartJS, v.v.)                |
| Đẩy dữ liệu đến client qua WebSocket riêng | Gửi dữ liệu realtime đến người dùng (qua RTWebsocketGateway)                                          |
| Cung cấp dữ liệu cho ML hoặc backtesting      | Dữ liệu lịch sử giá để mô hình dự đoán hoặc kiểm thử chiến lược đầu tư                   |
| Cache giá gần nhất                             | Lưu dữ liệu mới nhất vào Redis để truy vấn nhanh                                                     |
| Thống kê, logging, monitoring                   | Ghi log, push metrics để đo lường hiệu suất                                                            |

---

## Thành phần bên trong price-service


| Thành phần                | Vai trò                                              |
| --------------------------- | ----------------------------------------------------- |
| BinanceWebsocketClient      | Kết nối đến Binance để stream nến              |
| PriceCacheService           | Lưu dữ liệu giá mới nhất vào Redis             |
| PriceRestController         | Cung cấp API HTTP: lấy lịch sử, giá hiện tại   |
| PriceStreamingPublisher     | Gửi giá đến các client frontend                  |
| PriceAggregator (nâng cao) | Gộp nhiều nguồn giá, chuẩn hóa khung thời gian |

---

## 🔁 Flow dữ liệu

Binance WebSocket
│
▼
┌──────────────────────────────┐
│     Price-service (sharded) │ ◄─── Connects to Binance WS (multi-symbol)
└──────────────────────────────┘
│  (per-symbol message)
▼
┌──────────────────────────────┐
│     Kafka (price-stream)     │ ◄─── Partition theo symbol key (BTCUSDT, etc)
└──────────────────────────────┘
│
▼
┌───────────────────────────────────────┐
│ WebSocket-Gateway (Kafka Consumer)   │ ◄─── Subscribed to topic "price-stream"
│ - Push message vào Redis pub/sub     │
└───────────────────────────────────────┘
│
▼
┌───────────────────────────────────────┐
│ Redis Pub/Sub                         │ ◄─── Channel per symbol (ex: "price:BTCUSDT")
└───────────────────────────────────────┘
│
▼
┌───────────────────────────────────────┐
│ WebSocket Gateway instances (STOMP)  │ ◄─── Subscribe Redis channel per symbol
│ - Gửi message WebSocket cho clients  │
└───────────────────────────────────────┘
│
▼
┌──────────────────────────────┐
│      Frontend Client         │ ◄─── Subscribes to /topic/price/BTCUSDT
└──────────────────────────────┘---

## Ví dụ API


| Endpoint                                                 | Mô tả                                 |
| -------------------------------------------------------- | --------------------------------------- |
| GET`/price/history?symbol=BTCUSDT&interval=1m&limit=500` | Lấy 500 nến lịch sử BTCUSDT         |
| GET`/price/current?symbol=BTCUSDT`                       | Lấy giá hiện tại                    |
| WebSocket`/ws/price?symbol=BTCUSDT`                      | Gửi stream giá realtime qua WebSocket |

---

## Giao tiếp với hệ thống khác


| Đối tượng        | Mục đích                                     |
| -------------------- | ----------------------------------------------- |
| Frontend             | Hiển thị biểu đồ giá                      |
| ML-Inference-Service | Cần giá để dự đoán                       |
| Backtest-Engine      | Nạp dữ liệu nến quá khứ                   |
| RTWebsocketGateway   | Forward realtime đến người dùng            |
| Redis                | Cache giá gần nhất để API phản hồi nhanh |

---

## ✅ Kết luận

`price-service` là trung tâm dữ liệu giá trong hệ thống RadarTrade, phục vụ cho các chức năng:

- Biểu đồ kỹ thuật
- Phân tích kỹ thuật
- Dự đoán bằng AI
- Kiểm thử chiến lược đầu tư (Backtesting)

## **Note**

**refactoring Spring integration**

## **Kiến trúc tổng thể flow dữ liệu realtime**

<pre class="overflow-visible!" data-start="259" data-end="1435"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"></div></pre>
