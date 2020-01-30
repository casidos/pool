-- SQLite
CREATE VIEW STANDINGS 
AS
SELECT 
row_number() OVER () as id,
cu.id AS user_id
FROM pool_customuser cu