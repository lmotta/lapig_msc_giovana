CREATE TABLE stations_cerrado_prep_inmet_gpm AS
SELECT i.code_wmo, i.v_date, i.prep_mm AS inmet_prep, g.prep_mm AS gpm_prep  
FROM stations_cerrado_prep_daily i
INNER JOIN stations_cerrado_gpm g ON i.code_wmo = g.code_wmo AND i.v_date = g."date"
