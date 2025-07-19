🚀 1. Cài đặt TimescaleDB (cho PostgreSQL)
Trên Ubuntu:

# Cài TimescaleDB phù hợp với PostgreSQL version
sudo apt install postgresql-15-timescaledb-2-postgresql

Kích hoạt extension trong PostgreSQL:

CREATE EXTENSION IF NOT EXISTS timescaledb;

🧱 2. Tạo bảng dữ liệu time series

Giống PostgreSQL thông thường, nhưng cần 1 cột timestamp:

CREATE TABLE temperature (
  time        TIMESTAMPTZ       NOT NULL,
  location    TEXT              NOT NULL,
  value       DOUBLE PRECISION  NULL
);

🔁 3. Biến bảng thành hypertable

SELECT create_hypertable('temperature', 'time');

    ✅ Lúc này bảng temperature được chia nhỏ (partition) theo thời gian và được Timescale tối ưu insert/query.

📊 4. Sử dụng continuous aggregates (truy vấn tổng hợp liên tục)

CREATE MATERIALIZED VIEW avg_temp_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS bucket,
       location,
       AVG(value) AS avg_temp
FROM temperature
GROUP BY bucket, location;

    👉 Timescale sẽ tự động cập nhật dữ liệu mỗi lần bạn insert mới — truy vấn báo cáo siêu nhanh.

📦 5. Bật nén dữ liệu (compression)
Bật compression cho bảng:

ALTER TABLE temperature SET (timescaledb.compress, timescaledb.compress_segmentby = 'location');

Cấu hình policy tự nén dữ liệu sau 7 ngày:

SELECT add_compression_policy('temperature', INTERVAL '7 days');

🗑️ 6. Thêm retention policy (xóa dữ liệu cũ)

SELECT add_retention_policy('temperature', INTERVAL '30 days');

→ Tự động xóa bản ghi quá 30 ngày, giúp không đầy ổ.
✅ 7. Truy vấn dữ liệu time series

-- Lấy trung bình mỗi giờ trong 1 ngày gần nhất
SELECT time_bucket('1 hour', time) AS hour,
       AVG(value)
FROM temperature
WHERE time > now() - interval '1 day'
GROUP BY hour
ORDER BY hour;

📈 8. Kết nối TimescaleDB với các công cụ dashboard
Tool	Hỗ trợ
Grafana	✅ Có plugin Timescale/PostgreSQL
Metabase	✅ Kết nối như PostgreSQL
Apache Superset	✅
Power BI / Tableau	✅ dùng PostgreSQL connector
🧪 Tổng kết: Các tính năng chính bạn nên dùng
Tính năng	Cách dùng
Hypertable	create_hypertable()
Compression	ALTER TABLE ... SET (compress...)
Retention Policy	add_retention_policy()
Continuous Aggregates	CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous)
Time Bucket	time_bucket() trong SQL
Job Scheduler	timescaledb_information.jobs – chạy auto policy