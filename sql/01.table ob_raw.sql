CREATE TABLE rt_dev.ob_raw (
    ts UInt32 NOT NULL,
	pair String NOT NULL,
	lowest_ask Decimal64(8) NOT NULL,
	highest_bid Decimal64(8) NOT NULL,
	asks Map(String, Float32) NOT NULL,
	bids Map(String, Float32) NOT NULL,
	isFrozen Boolean,
	postOnly Boolean

) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(FROM_UNIXTIME(ts))
ORDER BY (ts, pair)
TTL FROM_UNIXTIME(ts) + INTERVAL 900 DAY