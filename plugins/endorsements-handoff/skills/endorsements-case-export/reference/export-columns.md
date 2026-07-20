# Excel export — exact column spec

Worksheet name: **SI Queue**. One row per case (the currently filtered rows), in the
sorted order. Freeze the header row.

## Columns (in order)
1. Case #
2. Source
3. Quote #
4. Effective Date
5. Incident
6. PINC Ticket
7. PINC Status
8. PINC Summary
9. … **Linked Ticket 1 … Linked Ticket N** — N = the maximum number of linked
   BH/ACC tickets across the exported rows (detect dynamically; here N = 2). Each cell:
   `TICKET-KEY (Status)`, e.g. `BH-28243 (CANCELLED)`.
10. Sub-Category  (multiple joined with ", ")
11. Case Summary
12. Created Date
13. Aging (Days)
14. Aging Bucket

## Header formatting
- Fill: solid dark blue `#002060`
- Font: white, bold
- Freeze panes below the header row

## Filename
`Endorsements_Case_View_<as-of>.xlsx` (the extract's as-of date, 2026-06-09).
