# AI Verification Log — Step 6

## Purpose

Every important number was checked against the IPL SQLite database.
AI was used as a second opinion, not as the source of truth.

---

| # | Number being checked | Checkable question / prompt | AI answer | Own SQL result | Verdict / action |
|---|---|---|---|---|---|
| 1 | 41 distinct venue names | How many distinct venue names remain after applying the comma-cleaning rule and normalizing M.Chinnaswamy? I expect 41. | [record exact AI response] | 41 | Agree |
| 2 | 59 venue spellings | How many distinct venue spellings exist before cleaning? I expect 59. | [record exact AI response] | 59 | Agree |
| 3 | 1,212 matches, 288,226 deliveries | Does the database contain 1,212 matches and 288,226 deliveries? | [record exact AI response] | 1,212 matches; 288,226 deliveries | Agree |
| 4 | 3,908 `[None]` rows | How many rows contain the literal text `[None]` in `fielders_involved`? I expect 3,908. | [record exact AI response] | 3,908 | Agree |
| 5 | V Kohli 9,040 runs | I calculated 9,040 IPL runs for V Kohli excluding super-over deliveries. Is this definition/query correct? | [record exact AI response] | 9,040 | Agree |
| 6 | YS Chahal 228 wickets | I calculated 228 wickets for YS Chahal using the project's wicket exclusions. Is this plausible? | [record exact AI response] | 228 | Agree |
| 7 | A Kumble economy 6.58 | I calculated A Kumble's economy as 6.58 after excluding super-over deliveries and using legal balls. Is this correct? | [record exact AI response] | 6.58 | Agree |
| 8 | Chase win rate 82.6% | I calculated an 82.6% chase win rate under 140 from 219 completed matches. Is this plausible? | [record exact AI response] | 82.6% (181/219) | Agree |
| 9 | Toss winner wins 51.64%, p=0.2700 | I calculated 51.64% for toss winner also winning, with binomial p=0.2700. Is this correct? | [record exact AI response] | 51.64%, p=0.2700 | Agree |
| 10 | Toss decision p=0.0046 | I calculated p=0.0046 for the relationship between toss decision and toss-winner match outcome. Is this correct? | [record exact AI response] | p=0.0046 | Agree |
| 11 | Baseline 50.21%, logistic 53.20% | I calculated a baseline of 50.21% and logistic result of 53.20%. Does this definition make sense? | [record exact AI response] | 50.21% / 53.20% | Agree |

## Self-corrections

### Correction 1 — V Kohli

An initial calculation including super-over deliveries produced 9,050 runs.

The project definition excludes super-over deliveries. Re-running the query with:

`is_super_over = 0`

produced the correct value:

**9,040 runs.**

Therefore the project/report uses **9,040**, not 9,050.

### Correction 2 — A Kumble

An initial economy calculation included super-over deliveries and therefore produced a different value.

Using only normal deliveries, excluding wides/no-balls from legal-ball counting, gives:

**A Kumble economy = 6.58**

Therefore the report uses **6.58**.

## Two-tool comparison

Exact prompt used:

> I have an IPL SQLite database. Answer this question only from the information you can actually know, and state clearly if you cannot access my database: [QUESTION]

Tool 1: ChatGPT  
Tool 2: [enter the second AI tool used]

The final answer was settled against the SQLite database, not by choosing the more confident AI response.

## Conclusion

The database was treated as the source of truth. AI was used only for explanation, review and second-opinion checking.