with 
 'BTC_XMR' as p_pair,
 60 as p_period,
 1636296780 as ts_min,
 1636297194 as ts_max

select 
   ts_main as ts,
   lowest_ask, 
   highest_bid

FROM 
	(SELECT 
		arrayJoin(range(1636296720, 1636297194, 60)) AS ts_main ORDER BY ts_main DESC ) AS tb1
	LEFT JOIN  
	(SELECT ts_group, ROUND(AVG(lowest_ask),8) AS lowest_ask, ROUND(AVG(highest_bid),8) AS highest_bid
	FROM 
		(SELECT 
		 	ROUND(ts/p_period)*p_period AS ts_group, 
			lowest_ask,
			highest_bid 
		FROM rt_dev.orderbook
		WHERE pair=p_pair AND ts between ts_min AND ts_max+p_period) AS TB
	GROUP BY ts_group) AS tb2
 ON tb1.ts_main=tb2.ts_group
