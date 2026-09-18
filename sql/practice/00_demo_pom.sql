DROP VIEW IF EXISTS v_demo_pom;

CREATE VIEW v_demo_pom AS
SELECT match_id,
player_of_match,
NULLIF(TRIM(player_of_match), '') AS pom_clean
matches;

FROM matches;