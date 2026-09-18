DROP TABLE IF EXISTS matches_clean;

CREATE TABLE matches_clean AS
SELECT
    *
FROM v_matches_season_clean;