-- Season
-- 01: Summer
-- 02: Autumn
-- 03: Winter
-- 04: Spring

-- 2017
-- Summer: 2016-12-21 - 2017-03-19
SELECT
	code_wmo,
	'2017_01' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2016-12-21') AND julianday( v_date ) <= julianday('2017-03-19')
GROUP  BY code_wmo, season
HAVING
	julianday('2017-03-19') - julianday('2016-12-21') = COUNT(1) + 1
---
UNION
--- Autumn: 2017-03-20 - 2017-06-20
SELECT
	code_wmo,
	'2017_02' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2017-03-20') AND julianday( v_date ) <= julianday('2017-06-20')
GROUP  BY code_wmo, season
HAVING
	julianday('2017-06-20') - julianday('2017-03-20') = COUNT(1) + 1
---
UNION
--- Winter: 2017-06-21 - 2017-09-21
SELECT
	code_wmo,
	'2017_03' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2017-06-21') AND julianday( v_date ) <= julianday('2017-09-21')
GROUP  BY code_wmo, season
HAVING
	julianday('2017-09-21') - julianday('2017-06-21') = COUNT(1) + 1
---
UNION
--- Spring: 2017-09-22 - 2017-12-20
SELECT
	code_wmo,
	'2017_04' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2017-09-22') AND julianday( v_date ) <= julianday('2017-12-20')
GROUP  BY code_wmo, season
HAVING
	julianday('2017-12-20') - julianday('2017-09-22') = COUNT(1) + 1
-- 2018
UNION
-- Summer: 2017-12-21 - 2018-03-19
SELECT
	code_wmo,
	'2018_01' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2017-12-21') AND julianday( v_date ) <= julianday('2018-03-19')
GROUP  BY code_wmo, season
HAVING
	julianday('2018-03-19') - julianday('2017-12-21') = COUNT(1) + 1
---
UNION
--- Autumn: 2018-03-20 - 2018-06-20
SELECT
	code_wmo,
	'2018_02' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2018-03-20') AND julianday( v_date ) <= julianday('2018-06-20')
GROUP  BY code_wmo, season
HAVING
	julianday('2018-06-20') - julianday('2018-03-20') = COUNT(1) + 1
---
UNION
--- Winter: 2018-06-21 - 2018-09-21
SELECT
	code_wmo,
	'2018_03' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2018-06-21') AND julianday( v_date ) <= julianday('2018-09-21')
GROUP  BY code_wmo, season
HAVING
	julianday('2018-09-21') - julianday('2018-06-21') = COUNT(1) + 1
---
UNION
--- Spring: 2018-09-22 - 2018-12-20
SELECT
	code_wmo,
	'2018_04' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2018-09-22') AND julianday( v_date ) <= julianday('2018-12-20')
GROUP  BY code_wmo, season
HAVING
	julianday('2018-12-20') - julianday('2018-09-22') = COUNT(1) + 1
-- 2019
UNION
-- Summer: 2018-12-21 - 2019-03-19
SELECT
	code_wmo,
	'2019_01' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2018-12-21') AND julianday( v_date ) <= julianday('2019-03-19')
GROUP  BY code_wmo, season
HAVING
	julianday('2019-03-19') - julianday('2018-12-21') = COUNT(1) + 1
---
UNION
--- Autumn: 2019-03-20 - 2019-06-20
SELECT
	code_wmo,
	'2019_02' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2019-03-20') AND julianday( v_date ) <= julianday('2019-06-20')
GROUP  BY code_wmo, season
HAVING
	julianday('2019-06-20') - julianday('2019-03-20') = COUNT(1) + 1
---
UNION
--- Winter: 2019-06-21 - 2019-09-22
SELECT
	code_wmo,
	'2019_03' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2019-06-21') AND julianday( v_date ) <= julianday('2019-09-22')
GROUP  BY code_wmo, season
HAVING
	julianday('2019-09-22') - julianday('2019-06-21') = COUNT(1) + 1
---
UNION
--- Spring: 2019-09-23 - 2019-12-21
SELECT
	code_wmo,
	'2019_04' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2019-09-23') AND julianday( v_date ) <= julianday('2019-12-21')
GROUP  BY code_wmo, season
HAVING
	julianday('2019-12-21') - julianday('2019-09-23') = COUNT(1) + 1
-- 2020
UNION
-- Summer: 2019-12-22 - 2020-03-19
SELECT
	code_wmo,
	'2020_01' AS season,
	SUM(inmet_prep) AS inmet_prep, SUM(gpm_prep) AS gpm_prep
FROM stations_cerrado_prep_inmet_gpm
WHERE
	julianday( v_date ) >= julianday('2019-12-22') AND julianday( v_date ) <= julianday('2020-03-19')
GROUP  BY code_wmo, season
HAVING
	julianday('2020-03-19') - julianday('2019-12-22') = COUNT(1) + 1
---
ORDER BY code_wmo, season
