# Statistical Validation Report

## Step 4 — Statistical Testing

This report tests the findings identified during the IPL Cricket Analytics analysis.

The purpose of statistical testing is to determine whether the observed patterns provide enough evidence to reject the null hypothesis. Each test reports the sample size, p-value, effect size, and a plain-English verdict.

---

## T1 — Does winning the toss help you win the match?

**Finding:** Toss winners won 51.64% of decisive matches.

**Statistical question:** Is the toss winner's match-win rate significantly different from 50%?

**Null hypothesis:** H₀: Toss winners win 50% of decisive matches.

**Test:** Binomial test.

**Sample size:** n = 1,187

**Observed rate:** 51.64%

**p-value:** 0.2700

**Effect size:** 1.64 percentage points above 50%.

**95% confidence interval:** 48.80% to 54.48%.

**Verdict:** The test did not provide enough evidence to conclude that winning the toss changes the probability of winning the match.

---

## T2 — Does the decision taken after the toss matter?

**Finding:** Toss winners who chose to field had a higher match-win rate than those who chose to bat.

**Statistical question:** Is toss decision associated with whether the toss winner wins the match?

**Null hypothesis:** H₀: Toss decision and toss-winner match outcome are independent.

**Test:** Chi-square test of independence.

**Sample size:** n = 1,187

**Observed results:**

- Chose to bat: 184 wins, 218 losses — 45.77%
- Chose to field: 429 wins, 356 losses — 54.65%

**Chi-square:** 8.04

**Degrees of freedom:** 1

**p-value:** 0.0046

**Effect size:** Cramér's V ≈ 0.082.

**Verdict:** The test provides evidence of an association between toss decision and toss-winner match outcome, although the association effect is small.

---

## T3 — Does the chasing team really have an advantage?

**Finding:** Chasing teams won 54.51% of decisive matches.

**Statistical question:** Is the chasing team's win rate significantly different from 50%?

**Null hypothesis:** H₀: Chasing teams win 50% of decisive matches.

**Test:** Binomial test.

**Sample size:** n = 1,187

**Chases won:** 647

**Observed rate:** 54.51%

**p-value:** 0.0021

**Effect size:** 4.51 percentage points above 50%.

**95% confidence interval:** 51.66% to 57.32%.

**Verdict:** The test provides evidence that the chasing team's win rate differs from 50%, with the observed rate 4.51 percentage points higher.

---

## T4 — Does the chase win rate fall as the target rises?

**Finding:** Chase success decreases as the first-innings target increases.

**Statistical question:** Is chase outcome associated with the target band?

**Null hypothesis:** H₀: Chase outcome is independent of target band.

**Test:** Chi-square test of independence.

**Sample size:** n = 1,187

**Target-band results:**

| Target band | Won | Lost | Chase win rate |
|---|---:|---:|---:|
| Under 140 | 181 | 38 | 82.6% |
| 140–159 | 171 | 70 | 71.0% |
| 160–179 | 166 | 146 | 53.2% |
| 180–199 | 83 | 134 | 38.2% |
| 200+ | 46 | 152 | 23.2% |

**Chi-square:** 197.68

**Degrees of freedom:** 4

**p-value:** approximately 1 × 10⁻⁴¹

**Effect size:** Cramér's V ≈ 0.408.

**Verdict:** The test provides very strong evidence that chase success differs across target bands.

---

## T5 — Are defended totals actually bigger than chased totals?

**Finding:** Matches in which the first-innings total was successfully defended had higher first-innings totals than matches where the target was successfully chased.

**Statistical question:** Do defended and successfully chased matches have different mean first-innings totals?

**Null hypothesis:** H₀: The two groups have the same mean first-innings total.

**Test:** Welch independent t-test.

**Sample size:** n = 1,187

**Successfully defended:** n = 540, mean = 183.3 runs

**Successfully chased:** n = 647, mean = 155.5 runs

**Mean difference:** 27.8 runs

**t-statistic:** 15.73

**p-value:** approximately 1 × 10⁻⁵⁰

**Effect size:** Cohen's d = 0.92.

**Verdict:** The test provides strong evidence that defended matches had higher first-innings totals, with a large effect size of 0.92.

---

## T6 — Is the Powerplay really faster than the Middle overs?

**Finding:** Powerplay run rate appeared slightly higher than Middle-over run rate.

**Statistical question:** Is Powerplay run rate significantly different from Middle-over run rate within the same innings?

**Null hypothesis:** H₀: The mean Powerplay and Middle-over run rates are equal.

**Test:** Paired t-test.

**Sample size:** n = 2,406 innings

**Powerplay average run rate:** 8.02

**Middle-over average run rate:** 7.95

**Mean difference:** 0.08 runs per over

**t-statistic:** 1.53

**p-value:** 0.1259

**Effect size:** Paired Cohen's d ≈ 0.031.

**Verdict:** The test did not provide enough evidence to conclude that Powerplay run rate differs from Middle-over run rate.

---

## T7 — Do left-handers really hit harder than right-handers?

**Finding:** Left-handed batters appeared to have a similar strike rate to right-handed batters.

**Statistical question:** Do left-handed and right-handed batters have different average strike rates?

**Null hypothesis:** H₀: Left-handed and right-handed batters have the same mean strike rate.

**Test:** Welch independent t-test.

**Sample size:** n = 137 batters.

**Left-handed batters:** n = 50, mean strike rate = 136.60

**Right-handed batters:** n = 87, mean strike rate = 136.62

**Mean difference:** 0.02

**p-value:** 0.9942

**Effect size:** Cohen's d = 0.001.

**Verdict:** The test did not provide enough evidence to conclude that left-handed and right-handed batters differ in average strike rate.

---

## T8 — Are spinners genuinely cheaper than fast bowlers?

**Finding:** Spin bowlers had a lower average economy rate than pace bowlers.

**Statistical question:** Do spin and pace bowlers have different average economy rates?

**Null hypothesis:** H₀: Spin and pace bowlers have the same mean economy rate.

**Test:** Welch independent t-test.

**Sample size:** n = 149 bowlers.

**Spin bowlers:** n = 49, average economy = 7.68

**Pace bowlers:** n = 100, average economy = 8.49

**Mean difference:** 0.80 runs per over.

**p-value:** approximately 9 × 10⁻¹¹

**Effect size:** Cohen's d = 1.18.

**Verdict:** The test provides strong evidence that spin and pace bowlers have different average economy rates, with a large effect size.

---

## T9 — Does Sawai Mansingh really favour the chasing team?

**Finding:** Sawai Mansingh Stadium had a 65.15% chase win rate compared with the league-wide rate of 54.51%.

**Statistical question:** Is the venue's chase win rate significantly different from the league-wide chase win rate?

**Null hypothesis:** H₀: The venue's chase win rate is equal to the league-wide rate of 54.51%.

**Test:** Binomial test.

**Sample size:** n = 66

**Chases won:** 43

**Venue chase rate:** 65.15%

**League chase rate:** 54.51%

**p-value:** 0.0849

**Effect size:** 10.64 percentage points above the league rate.

**95% confidence interval:** 53.11% to 75.52%.

**Verdict:** The test did not provide enough evidence to conclude that Sawai Mansingh Stadium's chase win rate differs from the league-wide rate.

---

## T10 — Has scoring genuinely risen across the seasons?

**Finding:** Average innings score increased across the seasons.

**Statistical question:** Is there a significant positive linear relationship between season year and average innings score?

**Null hypothesis:** H₀: There is no linear relationship between season year and average innings score.

**Test:** Pearson correlation.

**Sample size:** n = 19 seasons.

**First-season average:** 154.6 runs

**Last-season average:** 184.0 runs

**Pearson correlation:** r = 0.862

**R²:** 0.743

**p-value:** 0.0000021

**Effect size:** Pearson r = 0.862.

**Verdict:** The test provides strong evidence of a positive linear association between season year and average innings score.

**Alternative explanation:** The increase could also be associated with changes in bat technology, boundary sizes, playing rules, pitch/venue conditions, or changes in team composition. Correlation alone does not establish that time itself caused the increase.

---

# Step 4.15 — My Three Findings

The three findings below are the findings I selected from my Step 3 Analysis Report because I had the least confidence in them.

## Finding 1

**Finding:** [Paste your first Step 3 finding here]

**Statistical question:** [Write the precise question]

**Null hypothesis:** H₀: [Write the null hypothesis]

**Test:** [Test name]

**Sample size:** n = [value]

**p-value:** [value]

**Effect size:** [value]

**Verdict:** [Plain-English verdict]

---

## Finding 2

**Finding:** [Paste your second Step 3 finding here]

**Statistical question:** [Write the precise question]

**Null hypothesis:** H₀: [Write the null hypothesis]

**Test:** [Test name]

**Sample size:** n = [value]

**p-value:** [value]

**Effect size:** [value]

**Verdict:** [Plain-English verdict]

---

## Finding 3

**Finding:** [Paste your third Step 3 finding here]

**Statistical question:** [Write the precise question]

**Null hypothesis:** H₀: [Write the null hypothesis]

**Test:** [Test name]

**Sample size:** n = [value]

**p-value:** [value]

**Effect size:** [value]

**Verdict:** [Plain-English verdict]

---

# Overall Statistical Summary

The statistical tests show that some Step 3 findings are supported by statistical evidence while others are not.

The toss-winner finding did not survive statistical testing. The chasing advantage, target-band relationship, defended-versus-chased total difference, and bowling-style economy difference were supported by the corresponding tests. The Powerplay versus Middle-over difference, left-versus-right batting strike-rate difference, and Sawai Mansingh venue difference did not have enough statistical evidence at the 0.05 level.

The season analysis showed a strong positive correlation between season year and average innings score, although this correlation does not establish causation.
