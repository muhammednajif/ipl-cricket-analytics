DROP VIEW IF EXISTS v_venues_clean;

CREATE VIEW v_venues_clean AS
SELECT
	venue,
	MAX(city) AS city
FROM venues
GROUP BY venue;