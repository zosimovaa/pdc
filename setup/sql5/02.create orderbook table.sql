CREATE TABLE orderbook (
    symbol String NOT NULL,
    ts UInt64 NOT NULL,
	lowest_ask Decimal128(12) NOT NULL,
	highest_bid Decimal128(12) NOT NULL,
	asks Map(String, Float64) NOT NULL,
	bids Map(String, Float64) NOT NULL

) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(FROM_UNIXTIME(ts))
ORDER BY (symbol, ts)
TTL FROM_UNIXTIME(ts) + INTERVAL 90 DAY