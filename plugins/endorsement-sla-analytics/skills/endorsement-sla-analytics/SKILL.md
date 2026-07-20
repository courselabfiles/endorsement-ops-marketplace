---
name: endorsement-sla-analytics
description: Measure endorsement cycle-time and SLA attainment, and quantify the financial impact of open defects. Computes days-to-close by line of business and source against SLA targets (with % within SLA), and ranks open defects by blocked cases and blocked written premium ($ at risk). Use when asked for "SLA analytics", "cycle-time", "days to close", "SLA attainment", "$ at risk", "blocked premium", or "which defects to fix first".
---

# Endorsement Cycle-Time & SLA Analytics

Turn endorsement data into two leadership answers: **are we hitting SLA?** and
**which open defects are costing us the most?**

## Data sources
- **Closed cases** (cycle-time extract): case_id, lob, source, created_date, closed_date,
  days_to_close, written_premium.
- **SLA targets**: lob, sla_target_days.
- **Open defects** — from `defects.csv`: incident_number,
  lob, pinc_ticket, pinc_status, pinc_summary, first_reported_date.
- **Open blocked cases**: case_id, incident_number, lob, source, written_premium, effective_date.

## A. Cycle-time vs SLA
1. days_to_close = closed_date − created_date (already provided).
2. A case is **within SLA** if days_to_close ≤ the SLA target for its LOB.
3. Report, by **LOB** and by **source** (and the LOB×source matrix): case count,
   average and median days-to-close, and **% within SLA** (attainment).
4. Call out overall attainment and the **worst LOB**.

## B. Bottleneck / $ at risk
1. Join open blocked cases to their defect on `incident_number`.
2. Per defect: **blocked_cases** = count, **blocked_premium** = sum of written_premium,
   **days_open** = as-of date − first_reported_date.
3. **Rank by blocked_premium** (then show blocked_cases too) — the highest-premium
   defects clear the most at-risk revenue when fixed.
4. Report **total written premium at risk** and the concentration **by LOB**.

## Rules
- Anchor all aging / windows to the extract's **as-of date**, never today — reproducible.
- Rank the fix list by **dollars at risk**, not just case volume (they differ).
- Never fabricate cases, defects, or figures; report only what the data/connectors return.
- This is analysis for humans to act on — present the numbers and the ranked list, don't
  take any irreversible action.

## How to run
`scripts/analyze.py` computes everything from the four extracts:
```
python scripts/analyze.py --data <extracts-dir> --asof 2026-06-09        # printed report
python scripts/analyze.py --data <extracts-dir> --asof 2026-06-09 --json # machine-readable
```
The script is stdlib-only, so it runs as-is in the Claude Desktop Code tab.

## Output
- An SLA scorecard (by LOB and source, with % within SLA)
- A defect ranking by blocked written premium ($ at risk) with defect aging
- Headline numbers: overall attainment, worst LOB, total $ at risk
