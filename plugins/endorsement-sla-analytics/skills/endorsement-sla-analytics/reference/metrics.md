# Metric definitions

| Metric | Definition |
|---|---|
| days_to_close | closed_date − created_date, in days (provided per closed case) |
| within SLA | days_to_close ≤ sla_target_days for the case's LOB |
| % within SLA (attainment) | within-SLA cases ÷ total cases, for a slice (LOB, source, or LOB×source) |
| avg / median days | mean / median of days_to_close across the slice |
| blocked_cases | count of open cases linked to a defect (on incident_number) |
| blocked_premium ($ at risk) | sum of written_premium across a defect's blocked open cases |
| days_open (defect aging) | as-of date − first_reported_date |
| total at risk | sum of blocked_premium across all open defects |

## Conventions
- As-of date anchors all aging and windows (default 2026-06-09). Never use "today".
- Rank the defect fix-list by **blocked_premium** (dollars), not by blocked_cases (volume).
- Currency formatted as whole dollars, e.g. $1,530,569.
