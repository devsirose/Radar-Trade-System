CREATE TABLE kline (
    symbol       TEXT,
    interval     TEXT,
    open_time    TIMESTAMPTZ,
    close_time   TIMESTAMPTZ,
    open         NUMERIC(30,8),
    high         NUMERIC(30,8),
    low          NUMERIC(30,8),
    close        NUMERIC(30,8),
    volume       NUMERIC(30,8),
    trades_count INTEGER,
    closed       BOOLEAN,

    PRIMARY KEY (symbol, interval, open_time)
);