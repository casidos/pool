-- SQLite
--DROP VIEW IF EXISTS Standings;

CREATE VIEW STANDINGS 
AS
SELECT 
row_number() OVER () as id
, cust.id AS user_id
, cust.username
, CASE WHEN (w.week_type_id = 1 and w.name = 'Hall of Fame') THEN p.score END AS PRE_HOF
, SUM(CASE WHEN w.week_type_id = 1 and w.name = 'Week 1' THEN p.score END) AS PRE_WEEK_1
, SUM(CASE WHEN w.week_type_id = 1 and w.name = 'Week 2' THEN p.score END) AS PRE_WEEK_2
, SUM(CASE WHEN w.week_type_id = 1 and w.name = 'Week 3' THEN p.score END) AS PRE_WEEK_3
, SUM(CASE WHEN w.week_type_id = 1 and w.name = 'Week 4' THEN p.score END) AS PRE_WEEK_4
, SUM(CASE WHEN w.week_type_id = 1 THEN p.score END) AS PRE_TOTAL
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 1' THEN p.score END) AS REG_WEEK_1
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 2' THEN p.score END) AS REG_WEEK_2
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 3' THEN p.score END) AS REG_WEEK_3
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 4' THEN p.score END) AS REG_WEEK_4
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 5' THEN p.score END) AS REG_WEEK_5
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 6' THEN p.score END) AS REG_WEEK_6
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 7' THEN p.score END) AS REG_WEEK_7
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 8' THEN p.score END) AS REG_WEEK_8
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 9' THEN p.score END) AS REG_WEEK_9
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 10' THEN p.score END) AS REG_WEEK_10
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 11' THEN p.score END) AS REG_WEEK_11
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 12' THEN p.score END) AS REG_WEEK_12
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 13' THEN p.score END) AS REG_WEEK_13
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 14' THEN p.score END) AS REG_WEEK_14
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 15' THEN p.score END) AS REG_WEEK_15
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 16' THEN p.score END) AS REG_WEEK_16
, SUM(CASE WHEN w.week_type_id = 2 and w.name = 'Week 17' THEN p.score END) AS REG_WEEK_17
, SUM(CASE WHEN w.week_type_id = 2 THEN p.score END) AS REG_TOTAL
, SUM(CASE WHEN w.week_type_id = 3 and w.name = 'Wild Card Weekend' THEN p.score END) AS POST_WEEK_1
, SUM(CASE WHEN w.week_type_id = 3 and w.name = 'Divisional Playoffs' THEN p.score END) AS POST_WEEK_2
, SUM(CASE WHEN w.week_type_id = 3 and w.name = 'Conference Championships' THEN p.score END) AS POST_WEEK_3
, SUM(CASE WHEN w.week_type_id = 3 and w.name = 'Super Bowl' THEN p.score END) AS POST_WEEK_4
, SUM(CASE WHEN w.week_type_id = 3 THEN p.score END) AS POST_TOTAL
, SUM(p.score) AS OVERALL_TOTAL
FROM pool_customuser cust
JOIN pool_pick p on p.user_id = cust.id
JOIN pool_game g on g.id = p.game_id
JOIN pool_week w on w.id = g.week_id
GROUP BY cust.id;