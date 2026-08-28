# Manual validation fixture

Rendered native-PDF pages were visually compared with the cleaned CSV rows. The machine-readable expectations are in `tests/fixtures/manual_verified_records.csv` and are enforced by a regression test.

Verified cases:

- First project in both months: `612786` (June p.59, July p.55).
- Page boundary: June serial 19 `701128` on p.59 and serial 20 `612793` on p.60; the corresponding July boundary is p.55/p.56.
- Very long project name and decreased revised cost: `618215` (July p.104).
- Changed revised cost, changed revised completion date, and decimal progress: `701107` (July p.55).
- Large cost: `705728`, original/revised cost 108000 crore (June p.91, July p.85).
- Missing approval and revised completion dates: `701530` (July p.152).
- Final project and missing revised completion date: `613787` (June p.159, July p.152).

The inspected values, including apparent source anomalies, were transcribed without imputation or correction.

## January-March 2026 layouts

Thirty additional rows were compared visually against rendered source pages after adding semantic table selection: ten rows per month, spanning the first page, the first two page boundaries, a middle long-name row, and the final page. Project name, agency, project and legacy codes where present, state, both date pairs, both cost values, expenditure, and physical progress were checked.

- January: serials `1`, `2`, `25`, `26`, `54`, `55`, `852`, `1700`, `1701`, `1702` on PDF pages 62, 63, 64, 93, and 133.
- February: serials `1`, `2`, `20`, `21`, `41`, `42`, `975`, `1946`, `1947`, `1948` on PDF pages 65, 66, 67, 112, and 167.
- March: serials `1`, `2`, `20`, `21`, `41`, `42`, `971`, `1939`, `1940`, `1941` on PDF pages 55, 56, 57, 102, and 156.

All 30 comparisons matched the cleaned CSV values. The checks include multiline project names, separate legacy-code lines in February and March, missing legacy identifiers, paired original/revised costs, missing revised completion dates, decimal physical progress, and the first and last projects in each report.
