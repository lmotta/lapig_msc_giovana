CREATE TABLE stations_cerrado_prep
AS
SELECT t.code_wmo, t.data, t.hora, t.prep_mm
FROM  stations_table t
INNER JOIN stations_cerrado sc 
ON t.code_wmo  = sc.code_wmo;
