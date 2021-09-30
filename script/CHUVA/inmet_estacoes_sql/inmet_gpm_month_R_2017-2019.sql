SELECT gpm_prep AS Estimados, inmet_prep AS Observados
FROM vw_inmet_gpm_month 
WHERE NOT v_year = '2020'
