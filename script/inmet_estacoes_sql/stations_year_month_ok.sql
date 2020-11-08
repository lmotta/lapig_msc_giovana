CREATE TABLE stations_year_month_ok
AS
SELECT
    code_wmo, strftime('%Y', v_date) AS v_year, strftime('%m', v_date) AS v_month
FROM stations_month_24prep
GROUP BY code_wmo, v_year, v_month
HAVING COUNT(1) = (
    JULIANDAY( v_date,'start of month','+1 month','-1 day') -
    JULIANDAY( v_date,'start of month') + 1
)
