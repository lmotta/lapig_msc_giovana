CREATE VIEW vw_inmet_gpm_seasons AS
SELECT
	code_wmo, v_year,
	CASE
	    WHEN v_month IN('01', '02', '03') THEN '01_summer'
	    WHEN v_month IN('04', '05', '06') THEN '02_autumn'
	    WHEN v_month IN('07', '08', '09') THEN '03_winter'
	    WHEN v_month IN('10', '11', '12') THEN '04_spring'
	    ELSE 'others'
	END AS 'seasons',
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM vw_inmet_gpm_month
WHERE NOT v_year = '2020'
GROUP BY code_wmo, v_year, seasons
ORDER BY code_wmo, v_year, seasons;
