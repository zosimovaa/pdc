CREATE TABLE trades (
    `ts` UInt32 NOT NULL,
    `pair` String NOT NULL,
    `type` String NOT NULL,
    `rate` Decimal64(8) NOT NULL,
 	`amount` Decimal64(8) NOT NULL,
 	`total` Decimal64(8) NOT NULL,
 	`orderNumber` Int64,
    `globalTradeID` Int64,
    `tradeID` Int64


) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(FROM_UNIXTIME(ts))
ORDER BY (ts, pair, tradeID)
TTL FROM_UNIXTIME(ts) + INTERVAL 90 DAY