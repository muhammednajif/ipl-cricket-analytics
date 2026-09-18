DROP VIEW IF EXISTS 
v_matches_city_clean; 
CREATE VIEW v_matches_city_clean AS SELECT m.*, 
COALESCE( v.city, m.city, 'UNKNOWN' ) AS city_clean 
FROM matches m LEFT JOIN v_venues_clean v ON v.venue = m.venue;