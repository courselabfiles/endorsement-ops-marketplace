---
name: endorsements-case-export
description: Build the weekly Endorsements System Issues Queue (SI Queue) handoff — pull open cases and their incidents/dev tickets from the Salesforce and Jira demo connectors, assemble the case view, export a formatted Excel workbook, and draft the handoff email to the development and underwriting teams. Use when asked for the "endorsements handoff", the "what's blocked package", an "SI queue export", or the weekly blocked-cases email.
---

# Endorsements Case Export & Handoff

Produce the recurring "here's what's blocked" package for the endorsement operations
System Issues Queue, the same way every week, so any analyst gets an identical result.

## When to use
Use this when someone asks for the endorsements handoff, the weekly blocked-cases
package, the SI-Queue export, or the email to the dev / underwriting teams.

## Data sources (connectors)
- **Salesforce Demo** — `list_open_cases`, `get_case`
- **Jira Demo** — `search_issues`, `get_linked_tickets`

## Steps
1. **Pull.** Get the open SI-Queue cases from the Salesforce Demo connector, and the
   incidents + linked dev tickets from the Jira Demo connector. Anchor aging to the extract's
   as-of date of 2026-06-09, not today.
2. **Join.** Join on `incident_number`. For each incident, `earliestCreatedDate` =
   the earliest `created_date` across its linked cases. Split the pipe-delimited
   `sub_categories` into a list.
3. **Age.** Aging = days from `earliestCreatedDate` to the **as-of date** (never today),
   bucketed: 1–5, 6–10, 11–15, 16–30, 31–60, 61–90, 90+ Days.
4. **Sort.** Sub-category A→Z (rows with none last), then `earliestCreatedDate` ascending.
5. **Export Excel.** Follow `reference/export-columns.md` exactly — column order,
   the dynamic `Linked Ticket N` columns, and the dark-blue (ExcelJS ARGB FF002060) white-bold header.
   Save as `Endorsements_Case_View_<as-of>.xlsx`.
6. **Draft email.** Subject `Endorsements Case View - MM/DD/YYYY`. Body summarizes open
   cases, unique incidents, lines of business, and the single oldest blocker (incident,
   days, PINC ticket + status). Attach the workbook.

## Rules
- Anchor aging to the extract's as-of date of 2026-06-09, not today; results must be reproducible.
- Never invent cases, tickets, or numbers; report only what the connectors return.
- The email is a **draft for a human to review and send**; remind them to attach the workbook.

## Output
- `Endorsements_Case_View_<as-of>.xlsx` (formatted)
- A drafted handoff email (subject + body) to the development and underwriting teams
