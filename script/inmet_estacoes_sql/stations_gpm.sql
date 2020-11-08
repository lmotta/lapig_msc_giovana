-- Create
CREATE TABLE stations_cerrado_gpm (
    code_wmo TEXT, date TEXT, prep_mm REAL
);
-- Insert Values from sc_temp1, .., sc_temp4
INSERT INTO stations_cerrado_gpm
SELECT "id", "date", CAST( total_mm AS REAL )
FROM sc_temp1;
INSERT INTO stations_cerrado_gpm
SELECT "id", "date", CAST( total_mm AS REAL )
FROM sc_temp2;
INSERT INTO stations_cerrado_gpm
SELECT "id", "date", CAST( total_mm AS REAL )
FROM sc_temp3;
INSERT INTO stations_cerrado_gpm
SELECT "id", "date", CAST( total_mm AS REAL )
FROM sc_temp4;
INSERT INTO stations_cerrado_gpm
SELECT "id", "date", CAST( total_mm AS REAL )
FROM sc_temp5;
-- Drop tables sc_temp1, .., sc_temp
DROP TABLE sc_temp1;
DROP TABLE sc_temp2;
DROP TABLE sc_temp3;
DROP TABLE sc_temp4;
DROP TABLE sc_temp5;
