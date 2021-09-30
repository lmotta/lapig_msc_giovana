SELECT gpm_prep AS Estimados, inmet_prep AS Observados
FROM stations_cerrado_prep_inmet_gpm
WHERE NOT strftime('%Y', v_date) IN ('2016', '2020')
