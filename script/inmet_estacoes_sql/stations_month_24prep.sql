CREATE TABLE stations_month_24prep
AS
SELECT code_wmo, date(v_datetime) AS v_date
FROM  stations_cerrado_prep_ajust
GROUP BY code_wmo, v_date
HAVING  COUNT(1) = 24
