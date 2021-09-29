SELECT 
	code_wmo,
	strftime('%Y', v_date) AS v_year, strftime('%m', v_date) AS v_month, strftime('%d', v_date) AS v_day, 
	inmet_prep, gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE NOT v_year IN ('2016', '2020')
ORDER BY code_wmo, v_year, v_month, v_day
