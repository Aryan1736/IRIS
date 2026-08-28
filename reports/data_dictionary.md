# PAIMANA Table 6 data dictionary

The canonical key is `project_code + report_month`. Duplicates are reported and retained until investigated.

| Field | Type | Source/meaning |
|---|---|---|
| project_code | string | PAIMANA Project Code; canonical cross-month identifier |
| legacy_ocms_code | string/nullable | Legacy OCMS identifier shown after Project Code |
| pmgid | string/nullable | PMG identifier shown after Legacy OCMS Code |
| project_name | string | Project name, with wrapped visual lines joined |
| agency | string/nullable | Implementing agency |
| ministry | string/nullable | Most recent ministry/department band in Table 6 |
| sector | string/nullable | Most recent sector band under the ministry/department |
| state | string/nullable | State or multi-state source label |
| approval_date | `YYYY-MM`/nullable | Source Date of Approval (`MM/YYYY`) |
| start_date | `YYYY-MM`/nullable | Parenthesized Start Date |
| original_completion_date | `YYYY-MM`/nullable | Original/Target DoC |
| revised_completion_date | `YYYY-MM`/nullable | Parenthesized Revised DoC |
| original_cost | number/nullable | First cost value, Rs crore |
| revised_cost | number/nullable | Parenthesized cost value, Rs crore |
| cumulative_expenditure | number/nullable | Cumulative expenditure, Rs crore |
| physical_progress | number/nullable | Physical progress percentage, not clamped |
| report_month | `YYYY-MM` | Month printed in the Table 6 banner |
| *_raw | string/nullable | Source representations for paired/date/numeric audit |
| source_file | string | Source PDF filename |
| source_page/source_pages | integer/string | Physical PDF page lineage |
| source_row_number | integer | Table row number within the source page |
| source_serial_number | integer | Printed Table 6 Sl.No |
| extraction_method | string | Versioned extraction method |

