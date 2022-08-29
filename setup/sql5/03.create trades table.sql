CREATE TABLE trades (
    symbol String,
    ts UInt32,
    takerSide String,
    price Decimal128(12),
    quantity Decimal128(12),
    amount Decimal128(12),
    id String

) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMMDD(FROM_UNIXTIME(ts))
ORDER BY (symbol, ts, id)
TTL FROM_UNIXTIME(ts) + INTERVAL 90 DAY