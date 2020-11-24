--- Create table stations_cerrado_prep_daily (2016-12-21 - 2020-03-20)
---- 1) stations_cerrado_prep_ajust (2016-12-20 - 2020-03-20)
CREATE TABLE temp_1 AS
SELECT code_wmo, DATE(v_datetime) AS v_date, v_datetime, prep_mm
FROM stations_cerrado_prep_ajust
WHERE v_date >= '2016-12-20' AND DATE(v_datetime) <= '2020-03-20';
--- 2) stations_cerrado_prep_ajust (2016-12-20 - 2020-03-20) only stations_month_24prep(code_wmo, v_date)
CREATE TABLE temp_2 AS
SELECT t1.code_wmo, t1.v_date, v_datetime, prep_mm
FROM temp_1 t1
INNER JOIN stations_month_24prep t24 ON t1.code_wmo = t24.code_wmo AND t1.v_date = t24.v_date;
-- 3) stations_cerrado_prep_total_half (2016-12-20 - 2020-03-20)
CREATE TABLE stations_cerrado_prep_total_half AS
SELECT
    code_wmo, v_date
    , SUM(prep_mm) FILTER(WHERE CAST( TIME(v_datetime) AS INTEGER ) <= 12) AS total_prep_mm_12
    , SUM(prep_mm) FILTER(WHERE CAST( TIME(v_datetime) AS INTEGER ) >= 13) AS total_prep_mm_13
FROM temp_2
GROUP BY code_wmo, v_date;
-- Drop temp_1, temp_2
DROP TABLE temp_1;
DROP TABLE temp_2;
-- 4) stations_cerrado_prep_daily (2016-12-21 - 2020-03-20)
CREATE TABLE stations_cerrado_prep_daily AS
SELECT 
	c.code_wmo, c.v_date,
	c.total_prep_mm_12 + p.total_prep_mm_13 AS prep_mm
FROM stations_cerrado_prep_total_half c
INNER JOIN stations_cerrado_prep_total_half p 
ON c.v_date >= '2016-12-21' AND c.code_wmo  = p.code_wmo AND p.v_date = DATE(c.v_date, '-1 day');
-- Drop stations_cerrado_prep_total_half
DROP TABLE stations_cerrado_prep_total_half;

