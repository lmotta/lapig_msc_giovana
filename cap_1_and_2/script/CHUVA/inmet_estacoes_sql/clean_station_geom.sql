DROP TABLE stations_cerrado_g;

DELETE FROM gpkg_contents
WHERE table_name = 'stations_cerrado_g';

DELETE FROM gpkg_extensions
WHERE table_name = 'stations_cerrado_g';

DELETE FROM gpkg_geometry_columns
WHERE table_name = 'stations_cerrado_g';
