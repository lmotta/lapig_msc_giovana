SELECT 
	code_wmo,
	strftime('%Y', v_date) AS v_year, strftime('%m', v_date) AS v_month,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE NOT v_year IN ('2016', '2020')
GROUP BY code_wmo, v_year, v_month
-- Check all days of month
HAVING 
  julianday(v_date, 'start of month', '+1 month' ) - julianday(v_date, 'start of month')
  - COUNT(1) = 0
--
ORDER BY code_wmo, v_year, v_month
