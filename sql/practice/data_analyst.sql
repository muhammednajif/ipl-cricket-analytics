 1--Find the top 10 grounds by number of matches
SELECT
    venue_clean,
    COUNT(DISTINCT match_id) AS matches
FROM v_matches_clean
GROUP BY venue_clean
ORDER BY matches DESC
LIMIT 10;

--Explanation
--SELECT venue_clean → shows the cleaned ground/venue name.
--COUNT(DISTINCT match_id) → counts how many different matches were played there.
--GROUP BY venue_clean → groups all matches according to the ground.
--ORDER BY matches DESC → puts the highest number of matches first.
--LIMIT 10 → shows only the top 10 grounds.

2--Find grounds with an average innings score above 165, using a minimum of 25 matches
SELECT
    m.venue_clean,
    COUNT(DISTINCT m.match_id) AS matches,
    ROUND(AVG(i.runs), 1) AS avg_innings_score
FROM v_matches_clean m
JOIN v_innings i
    ON i.match_id = m.match_id
GROUP BY m.venue_clean
HAVING matches >= 25
   AND avg_innings_score > 165
ORDER BY avg_innings_score DESC;

--Explanation
--SELECT m.venue_clean → shows the cleaned ground/venue name.
--COUNT(DISTINCT m.match_id) → counts the number of different matches played at each ground.
--AVG(i.runs) → calculates the average innings score.
--ROUND(AVG(i.runs), 1) → rounds the average score to 1 decimal place.
--FROM v_matches_clean m → takes the cleaned match information.
--JOIN v_innings i → connects the match data with innings score data.
--ON i.match_id = m.match_id → joins both tables using the match ID.
--GROUP BY m.venue_clean → groups the innings according to the ground.
--HAVING matches >= 25 → keeps only grounds where at least 25 matches were played.
--AND avg_innings_score > 165 → keeps only grounds where the average innings score is above 165.
--ORDER BY avg_innings_score DESC → puts the highest average score first.

3--Calculate the chase win percentage for grounds with at least 50 matches
SELECT
    venue_clean,
    COUNT(*) AS matches,
    ROUND(100.0 * AVG(chase_won), 1) AS chase_win_pct
FROM v_match_totals
GROUP BY venue_clean
HAVING matches >= 50
ORDER BY chase_win_pct DESC;

--Explanation
--SELECT venue_clean → shows the cleaned ground/venue name.
--COUNT(*) → counts the total number of matches.
--AVG(chase_won) → calculates the average of the chase-won values.
--100.0 * AVG(chase_won) → converts the average into a percentage.
--ROUND(..., 1) → rounds the percentage to 1 decimal place.
--FROM v_match_totals → uses the match-level data where each row represents a match.
--GROUP BY venue_clean → groups the matches according to the ground.
--HAVING matches >= 50 → considers only grounds with at least 50 matches.
--ORDER BY chase_win_pct DESC → puts the highest chase win percentage first.

4--Count the number of unique cleaned venues
SELECT
    COUNT(DISTINCT venue_clean) AS unique_venues
FROM v_matches_clean;

--Explanation
--SELECT → tells SQL what information we want.
--COUNT(DISTINCT venue_clean) → counts each different venue only once.
--venue_clean → contains the cleaned venue names.
--DISTINCT → removes duplicate venue names.
--AS unique_venues → gives the result a clear column name.
--FROM v_matches_clean → takes the venue information from the cleaned match data.

5--Find the five grounds with the lowest powerplay run rate
SELECT
    m.venue_clean,
    ROUND(
        6.0 * SUM(
            CASE
                WHEN b.phase = 'Powerplay'
                THEN b.total_runs
                ELSE 0
            END
        ) / NULLIF(
            SUM(
                CASE
                    WHEN b.phase = 'Powerplay'
                    THEN b.is_legal
                    ELSE 0
                END
            ), 0
        ),
        2
    ) AS powerplay_run_rate
FROM v_matches_clean m
JOIN v_ball b
    ON b.match_id = m.match_id
GROUP BY m.venue_clean
ORDER BY powerplay_run_rate ASC
LIMIT 5;

--explanation
--SELECT m.venue_clean → shows the cleaned ground/venue name.
--b.phase = 'Powerplay' → selects only the balls bowled during the Powerplay.
--SUM(b.total_runs) → calculates the total runs scored during the Powerplay.
--SUM(b.is_legal) → counts the legal balls bowled during the Powerplay.
--CASE WHEN ... THEN ... ELSE ... END → selects Powerplay data and ignores other phases.
--6.0 * runs / legal_balls → calculates the run rate per over.
--NULLIF(..., 0) → prevents a division-by-zero error.
--ROUND(..., 2) → rounds the Powerplay run rate to 2 decimal places.
--JOIN v_ball b → connects match information with ball-by-ball information.
--ON b.match_id = m.match_id → joins the tables using the match ID.
--GROUP BY m.venue_clean → calculates the run rate separately for each ground.
--ORDER BY powerplay_run_rate ASC → puts the lowest run rate first.
--LIMIT 5 → shows only the five grounds with the lowest Powerplay run rate.

6--Why can COUNT(DISTINCT match_id) be safer than COUNT(*) after a JOIN?
SELECT
    venue_clean,
    COUNT(DISTINCT match_id) AS matches
FROM v_matches_clean
GROUP BY venue_clean;

--explanation
--COUNT(*) → counts every row in the result.
--JOIN → can create multiple rows for the same match.
--COUNT(DISTINCT match_id) → counts each match only once.
--DISTINCT match_id → removes duplicate match IDs before counting.
--This is safer when joining a match table with a delivery/ball table.
--One match can have many delivery rows.
--Therefore, COUNT(*) might count deliveries instead of matches.
--COUNT(DISTINCT match_id) → gives the actual number of unique matches.

7--Why can't the day/night question be answered from match_date alone?
SELECT
    match_date
FROM matches_clean
LIMIT 10;

--explanation
--SELECT match_date → shows the match date.
--FROM matches_clean → gets the date from the cleaned matches table.
--LIMIT 10 → shows only 10 rows.
--match_date → tells us which day the match was played.
--match_date → does not tell us the starting time.
--Without a time column such as start_time or match_time, we cannot determine whether the match was a day or night match.