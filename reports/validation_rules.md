# PAIMANA source-data plausibility rules

These rules emit quality records only. They never alter source values or reject a structurally parsed project. Each output includes `severity`, `priority`, and `category`:

- `ERROR / HIGH / STRUCTURAL_OR_IMPOSSIBLE`: structurally unparseable or impossible numeric/timeline values.
- `WARNING / MEDIUM / STRONG_PLAUSIBILITY_ANOMALY`: strong inconsistencies that still require source review rather than correction.
- `INFO / LOW / UNUSUAL_BUSINESS_STATE`: unusual but potentially legitimate reporting or business states.

| Rule | Condition |
|---|---|
| `ZERO_EXPENDITURE_POSITIVE_PROGRESS` | Cumulative expenditure equals 0, physical progress is above 0, and start month is not after report month (or start is unavailable) |
| `PROGRESS_REPORTED_BEFORE_START` | Physical progress is above 0 while start month is after report month |
| `EXPENDITURE_WITH_ZERO_PROGRESS` | Cumulative expenditure is above 0 while physical progress equals 0 |
| `FULL_PROGRESS_STILL_ONGOING` | Physical progress equals 100 in Table 6, which is explicitly the ongoing-project table |
| `PHYSICAL_PROGRESS_ABOVE_100` | Physical progress is above 100 |
| `NEGATIVE_EXPENDITURE` | Cumulative expenditure is below 0 |
| `EXTREME_EXPENDITURE_COST_MISMATCH` | Cumulative expenditure exceeds three times revised cost |
| `REVISED_COST_BELOW_ORIGINAL` | Revised cost is below original cost |
| `COMPLETION_DATE_BEFORE_START_DATE` | Original and/or revised completion month precedes start month |

The validation-only `qc_metrics_YYYY_MM.csv` files also contain:

- `financial_progress = cumulative_expenditure / revised_cost * 100`, calculated only when revised cost is positive.
- `physical_financial_gap = physical_progress - financial_progress`, calculated only when both inputs are available.

Derived values are rounded to six decimal places and are not added to clean monthly or combined datasets.
