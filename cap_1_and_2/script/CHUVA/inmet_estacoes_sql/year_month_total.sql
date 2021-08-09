SELECT v_year
     , COUNT(code_wmo) FILTER (WHERE v_month =  '01') AS Jan
     , COUNT(code_wmo) FILTER (WHERE v_month =  '02') AS Fev
     , COUNT(code_wmo) FILTER (WHERE v_month =  '03') AS Mar
     , COUNT(code_wmo) FILTER (WHERE v_month =  '04') AS Abr
     , COUNT(code_wmo) FILTER (WHERE v_month =  '05') AS Mai
     , COUNT(code_wmo) FILTER (WHERE v_month =  '06') AS Jun
     , COUNT(code_wmo) FILTER (WHERE v_month =  '07') AS Jul
     , COUNT(code_wmo) FILTER (WHERE v_month =  '08') AS Ago
     , COUNT(code_wmo) FILTER (WHERE v_month =  '09') AS 'Set'
     , COUNT(code_wmo) FILTER (WHERE v_month =  '10') AS Out
     , COUNT(code_wmo) FILTER (WHERE v_month =  '11') AS Nov
     , COUNT(code_wmo) FILTER (WHERE v_month =  '12') AS Dez
FROM stations_year_month_ok
GROUP BY v_year
