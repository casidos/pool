-- SQLite
SELECT 
row_number() OVER () as id
, u.username
, wt.name
, w.name
, g.number
, p.score
--, CASE WHEN wt.id = 1 THEN COALESCE(SUM(p.score), 0) END AS PRE_TOTAL,
--, CASE WHEN wt.id = 2 THEN IfNull(SUM(p.score), 0) END AS REG_TOTAL
--, CASE WHEN wt.id = 3 THEN COALESCE(SUM(p.score), 0) END AS POST_TOTAL,
--, COALESCE(SUM(p.score), 0) AS OVERALL_TOTAL
FROM pool_pick p
JOIN pool_game g on g.id = p.game_id
JOIN pool_week w on w.id = g.week_id
JOIN pool_weektype wt on wt.id = w.week_type_id
JOIN pool_customuser u on u.id = p.user_id
WHERE user_id = 1 AND wt.id =2 
--GROUP BY user_id, w.week_type_id