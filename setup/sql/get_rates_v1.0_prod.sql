with 
 'BTC_XMR' as p_pair,
 1636349220 as ts_min,
 1636379700 as ts_max

select 
   ts_main as ts,
   toDateTime(ts_main) as dt,
   lowest_ask, 
   highest_bid

from 

(select ts_r, AVG(lowest_ask) as lowest_ask, AVG(highest_bid) as highest_bid
FROM 
(select 
  ROUND(ts/60)*60 AS ts_r, 
  lowest_ask,
  highest_bid 
from rt.orderbook
WHERE pair=p_pair and ts between ts_min and ts_max
ORDER BY ts desc) AS TB
GROUP BY ts_r) as tb1
right join (select arrayJoin(range(ts_min, ts_max, 60)) as ts_main) as tb2 on tb1.ts_r=tb2.ts_main
order by ts desc



