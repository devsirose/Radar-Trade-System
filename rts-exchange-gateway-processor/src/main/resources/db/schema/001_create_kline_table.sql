CREATE TABLE klines (
    symbol       TEXT,
    interval     TEXT,
    open_time    BIGINT,
    close_time   BIGINT,
    open         NUMERIC,
    high         NUMERIC,
    low          NUMERIC,
    close        NUMERIC,
    volume       NUMERIC,
    trades_count INTEGER,
    closed       BOOLEAN,

    PRIMARY KEY (symbol, interval, open_time)
);