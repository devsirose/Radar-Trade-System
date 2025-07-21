CREATE TABLE kline (
    symbol       TEXT,
    interval     TEXT,
    open_time    BIGINT,
    close_time   BIGINT,
    open         NUMERIC(18,8),
    high         NUMERIC(18,8),
    low          NUMERIC(18,8),
    close        NUMERIC(18,8),
    volume       NUMERIC(18,8),
    trades_count INTEGER,
    closed       BOOLEAN,

    PRIMARY KEY (symbol, interval, open_time)
);