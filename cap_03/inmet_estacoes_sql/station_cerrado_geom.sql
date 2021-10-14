-- Load extension
SELECT load_extension('mod_spatialite.so');
--
CREATE TABLE stations_cerrado_g (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_wmo TEXT, estacao TEXT,
    long TEXT, lat TEXT, alt TEXT 
);
-- Add Geometry column
SELECT gpkgAddGeometryColumn( 'stations_cerrado_g', 'geom', 'POINT', 0, 0, 4326 );
-- Added triggers geometry
SELECT gpkgAddGeometryTriggers( 'stations_cerrado_g', 'geom' );
-- Insert gpkg_contents
INSERT INTO gpkg_contents ( table_name, identifier, data_type, srs_id)
VALUES ( 'stations_cerrado_g', 'stations_cerrado_g', 'features', 4326);
-- Insert stations_cerrado_g
INSERT INTO stations_cerrado_g
SELECT 
    NULL, -- AUTOINCREMENT
    s.code_wmo, s.estacao,
    s.long, s.lat, s.alt,
    gpkgMakePoint( CAST( s.long AS REAL ), CAST( s.lat AS REAL ), 4326 ) AS geom
FROM stations s
INNER JOIN 
(
SELECT  s.code_wmo, MAX(source_ano) AS source_ano
FROM stations s 
INNER JOIN stations_cerrado sc  ON s.code_wmo = sc.code_wmo 
GROUP BY s.code_wmo
)t
ON s.code_wmo  = t.code_wmo AND s.source_ano = t.source_ano;
