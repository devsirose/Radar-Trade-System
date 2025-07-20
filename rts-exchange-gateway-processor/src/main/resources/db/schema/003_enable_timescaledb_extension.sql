CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('price', 'event_time');