CREATE TABLE rt_dev.orderbook (
        ts UInt32 NOT NULL,
	pair String NOT NULL,
	lowest_ask Decimal64(8) NOT NULL,
	highest_bid Decimal64(8) NOT NULL,
	asks_vol Tuple(ask_vol_1 Decimal128(8), ask_vol_2 Decimal128(8), ask_vol_3 Decimal128(8), ask_vol_4 Decimal128(8), ask_vol_5 Decimal128(8), ask_vol_6 Decimal128(8)) NOT NULL,
        bids_vol Tuple(bid_vol_1 Decimal128(8), bid_vol_2 Decimal128(8), bid_vol_3 Decimal128(8), bid_vol_4 Decimal128(8), bid_vol_5 Decimal128(8), bid_vol_6 Decimal128(8)) NOT NULL

) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(FROM_UNIXTIME(ts))
ORDER BY (ts, pair)
TTL FROM_UNIXTIME(ts) + INTERVAL 365 DAY