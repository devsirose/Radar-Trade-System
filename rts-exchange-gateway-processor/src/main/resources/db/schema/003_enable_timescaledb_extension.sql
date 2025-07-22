CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('price', 'event_time');
SELECT create_hypertable('kline', 'open_time');
