# Initial extractor comparison

Representative pages inspected: first, continuation, middle, and final Table 6 pages in both June and July 2026.

| Approach | Evidence | Decision |
|---|---|---|
| pdfplumber, vector `lines` strategies | One table per representative page; exactly 8 columns; multiline names/agencies and paired values remained within a project row; serial/project codes stayed intact; totals/headings were distinct rows | Selected primary extractor |
| pypdf generic text extraction | Confirmed all pages contain selectable native text and enabled fast reconnaissance, but flattened cells into reading-order lines and did not provide defensible project row/column boundaries | Used only for investigation, not structured extraction |
| pdfplumber `text` table strategies | On July page 55 produced 136 rows and 20 inferred columns versus the visual 8-column table; excessive fragmentation | Rejected |
| OCR | Zero pages lacked native text; OCR would add avoidable risk to identifiers, dates, and decimals | Not used |
| Camelot/Tabula | Not needed after the ruled vector grid produced complete, consistent 8-column extraction; adding Java/Ghostscript dependencies would not improve the observed structure | Reserved as future page-level fallback only after a logged schema/extraction failure |

The production parser locates Table 6 semantically and does not hard-code June/July page numbers.

