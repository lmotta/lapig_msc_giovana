SELECT code_wmo,
	ROUND( CAST(n11 AS REAL) / (n11+n10) * 100, 2 ) AS POD,
	ROUND( CAST(n01 AS REAL) / (n11+n01) * 100, 2 ) AS FAR,
	ROUND( CAST(n11 AS REAL) / (n11+n01+n10) * 100, 2 ) AS CSI,
	ROUND( CAST((n11+n00) AS REAL) / (n00+n11+n01+n10) * 100, 2 ) AS PC
FROM
(
SELECT code_wmo,
	COUNT(1) FILTER (WHERE prob = 'n01') 'n01',
	COUNT(1) FILTER (WHERE prob = 'n10') 'n10',
	COUNT(1) FILTER (WHERE prob = 'n11') 'n11',
	COUNT(1) FILTER (WHERE prob = 'n00') 'n00'
FROM 
(
SELECT code_wmo,
CASE
--    WHEN inmet_prep > 0 AND gpm_prep > 0 THEN 'n11'
--    WHEN inmet_prep = 0 AND gpm_prep > 0 THEN 'n01'
--    WHEN inmet_prep > 0 AND gpm_prep = 0 THEN 'n10'
--    WHEN inmet_prep = 0 AND gpm_prep = 0 THEN 'n00'
    WHEN inmet_prep > 0 AND gpm_prep > 0.2 THEN 'n11'
    WHEN inmet_prep = 0 AND gpm_prep > 0.2 THEN 'n01'
    WHEN inmet_prep > 0 AND gpm_prep < 0.2 THEN 'n10'
    WHEN inmet_prep = 0 AND gpm_prep < 0.2 THEN 'n00'
    ELSE 'others'
END AS prob
FROM stations_cerrado_prep_inmet_gpm
WHERE NOT strftime('%Y', v_date) IN ('2016', '2020')
)
GROUP BY code_wmo
)
