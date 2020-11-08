CREATE TABLE stations_cerrado_prep_ajust
AS
SELECT 
    code_wmo,
    REPLACE("data", '/', '-') || ' ' || 
    SUBSTR( REPLACE( hora, ':', '' ), 1, 2) || ':' || SUBSTR( REPLACE( hora, ':', '' ), 3,2) AS v_datetime,
    CAST ( prep_mm AS REAL ) AS  prep_mm
FROM  stations_cerrado_prep scp
WHERE NOT prep_mm IN ('-9999', '')
