# Just see what the columns are
select * from dfs.`/home/matt/workspace/analytics/rushing4insights/plays.json` limit 1;

# see how many passes and runs we have
select is_pass, count(*) from dfs.`/home/matt/workspace/analytics/rushing4insights/plays.json` group by is_pass;

# pass ratio by down
select 1.0 * sum(case when is_pass = 1 then 1 else 0 end) / count(*), down
from dfs.`/home/matt/workspace/analytics/rushing4insights/plays.json` 
group by down order by down;

# pass ratio by quarter
select 1.0 * sum(case when is_pass = 1 then 1 else 0 end) / count(*), quarter
from dfs.`/home/matt/workspace/analytics/rushing4insights/plays.json` 
group by quarter order by quarter;

# pass ratio by score difference
select 1.0 * sum(case when is_pass = 1 then 1 else 0 end) / count(*), score_diff
from dfs.`/home/matt/workspace/analytics/rushing4insights/plays.json` 
group by score_diff order by score_diff;

# pass ratio by down, dist_to_first
select 1.0 * sum(case when is_pass = 1 then 1 else 0 end) / count(*), 
down, dist_to_first
from dfs.`/home/matt/workspace/analytics/rushing4insights/plays.json` 
group by down, dist_to_first order by down, dist_to_first;
