DROP VIEW IF EXISTS v_deliveries_clean; 
  -- Step 2: create the view that holds the rule 
CREATE VIEW v_deliveries_clean AS 
SELECT *, 
       NULLIF(TRIM(bowler_type), '') AS bowler_type_clean 
FROM   deliveries;

DROP VIEW IF EXISTS v_example;    -- so the file can be run twice 
CREATE VIEW v_example AS 
SELECT match_id, venue FROM matches; 
  
SELECT * FROM v_example LIMIT 5;  -- query it like a table