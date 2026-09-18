-- Fix 2: Merge category variants

-- Gujarat Lions and Gujarat Titans are DIFFERENT franchises.
-- They are deliberately not merged. Do not 'fix' this.

DROP VIEW IF EXISTS v_deliveries_clean;

CREATE VIEW v_deliveries_clean AS
SELECT
    *,
    CASE
        WHEN bowler_type = 'Fast medium'
        THEN 'Fast Medium'
        ELSE bowler_type
    END AS bowler_type_clean
FROM deliveries;


DROP VIEW IF EXISTS v_teams_clean;

CREATE VIEW v_teams_clean AS
SELECT
    *,
    CASE
        WHEN team_name = 'Rising Pune Supergiants'
        THEN 'Rising Pune Supergiant'
        ELSE team_name
    END AS team_name_clean
FROM teams;