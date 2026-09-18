DROP VIEW IF EXISTS v_matches_clean;

CREATE VIEW v_matches_clean AS
SELECT
    *,
    TRIM(
        REPLACE(
            SUBSTR(
                venue,
                1,
                CASE
                    WHEN INSTR(venue, ',') > 0
                    THEN INSTR(venue, ',') - 1
                    ELSE LENGTH(venue)
                END
            ),
            'M.Chinnaswamy',
            'M Chinnaswamy'
        )
    ) AS venue_clean
FROM matches;