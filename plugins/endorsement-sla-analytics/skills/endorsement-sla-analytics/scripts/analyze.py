#!/usr/bin/env python3
"""
Endorsement Cycle-Time & SLA Analytics
======================================
Reads four extracts (the same masked data the Salesforce + Jira demo connectors
serve) and computes:

  A. Cycle-time vs SLA  — days-to-close by LOB and source against the SLA target,
                          plus % within SLA (attainment).
  B. Bottleneck / $ at risk — open defects ranked by blocked cases and by blocked
                          written premium, with defect aging.

Usage:
    python analyze.py --data ./input-files --asof 2026-06-09 [--json]

No third-party dependencies (stdlib only) so it runs anywhere, including the
Claude Desktop Code tab.
"""
import argparse, csv, json, os, statistics
from datetime import date


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _money(n):
    return "${:,.0f}".format(n)


def analyze(data_dir, asof):
    closed   = _read(os.path.join(data_dir, "closed_cases.csv"))
    targets  = {r["lob"]: int(r["sla_target_days"]) for r in _read(os.path.join(data_dir, "sla_targets.csv"))}
    defects  = _read(os.path.join(data_dir, "defects.csv"))
    blocked  = _read(os.path.join(data_dir, "open_blocked_cases.csv"))

    for r in closed:
        r["days_to_close"] = int(r["days_to_close"])
        r["written_premium"] = int(r["written_premium"])
        r["within_sla"] = r["days_to_close"] <= targets[r["lob"]]
    for r in blocked:
        r["written_premium"] = int(r["written_premium"])

    lobs = sorted(targets, key=lambda l: targets[l])

    # ---- A. cycle-time vs SLA ----
    def attain(rows):
        return round(100 * sum(r["within_sla"] for r in rows) / len(rows), 1) if rows else 0.0

    by_lob = {}
    for lob in lobs:
        rows = [r for r in closed if r["lob"] == lob]
        by_lob[lob] = dict(
            cases=len(rows),
            sla_target=targets[lob],
            avg_days=round(statistics.mean(r["days_to_close"] for r in rows), 1),
            median_days=statistics.median(r["days_to_close"] for r in rows),
            pct_within_sla=attain(rows),
        )

    by_source = {}
    for src in ("onshore", "offshore"):
        rows = [r for r in closed if r["source"] == src]
        by_source[src] = dict(cases=len(rows),
                              avg_days=round(statistics.mean(r["days_to_close"] for r in rows), 1),
                              pct_within_sla=attain(rows))

    # LOB x source attainment matrix
    matrix = {lob: {src: attain([r for r in closed if r["lob"] == lob and r["source"] == src])
                    for src in ("onshore", "offshore")} for lob in lobs}

    overall_attain = attain(closed)
    worst_lob = min(by_lob, key=lambda l: by_lob[l]["pct_within_sla"])

    # ---- B. bottleneck / $ at risk ----
    info = {d["incident_number"]: d for d in defects}
    agg = {}
    for r in blocked:
        a = agg.setdefault(r["incident_number"], dict(cases=0, premium=0))
        a["cases"] += 1
        a["premium"] += r["written_premium"]

    ranked = []
    for inc, a in agg.items():
        d = info.get(inc, {})
        days_open = (asof - date.fromisoformat(d["first_reported_date"])).days if d.get("first_reported_date") else None
        ranked.append(dict(incident=inc, lob=d.get("lob", ""), pinc=d.get("pinc_ticket", ""),
                           status=d.get("pinc_status", ""), summary=d.get("pinc_summary", ""),
                           blocked_cases=a["cases"], blocked_premium=a["premium"], days_open=days_open))
    ranked.sort(key=lambda x: x["blocked_premium"], reverse=True)

    total_at_risk = sum(x["blocked_premium"] for x in ranked)
    total_blocked_cases = sum(x["blocked_cases"] for x in ranked)
    premium_by_lob = {}
    for x in ranked:
        premium_by_lob[x["lob"]] = premium_by_lob.get(x["lob"], 0) + x["blocked_premium"]

    return dict(
        asof=asof.isoformat(),
        cycle_time=dict(total_closed=len(closed), overall_pct_within_sla=overall_attain,
                        worst_lob=worst_lob, by_lob=by_lob, by_source=by_source, matrix=matrix),
        bottleneck=dict(open_defects=len(defects), total_blocked_cases=total_blocked_cases,
                        total_at_risk=total_at_risk, premium_by_lob=premium_by_lob, ranked=ranked),
    )


def print_report(m):
    ct, bn = m["cycle_time"], m["bottleneck"]
    print(f"\n=== CYCLE-TIME vs SLA  (as of {m['asof']}, {ct['total_closed']} closed cases) ===")
    print(f"Overall within SLA: {ct['overall_pct_within_sla']}%   |   Worst LOB: {ct['worst_lob']}")
    print(f"{'LOB':<12}{'Target':>7}{'Avg':>7}{'Median':>8}{'% within SLA':>14}")
    for lob, d in ct["by_lob"].items():
        print(f"{lob:<12}{d['sla_target']:>7}{d['avg_days']:>7}{d['median_days']:>8}{d['pct_within_sla']:>13}%")
    print("By source: " + " | ".join(f"{s}: {d['pct_within_sla']}% within SLA, avg {d['avg_days']}d"
                                      for s, d in ct["by_source"].items()))
    print(f"\n=== BOTTLENECKS / $ AT RISK  ({bn['open_defects']} open defects, "
          f"{bn['total_blocked_cases']} blocked cases) ===")
    print(f"Total blocked written premium at risk: {_money(bn['total_at_risk'])}")
    print(f"{'Incident':<11}{'LOB':<12}{'Cases':>6}{'Blocked $':>14}{'Days open':>11}")
    for x in bn["ranked"]:
        print(f"{x['incident']:<11}{x['lob']:<12}{x['blocked_cases']:>6}{_money(x['blocked_premium']):>14}{x['days_open']:>11}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="input-files")
    ap.add_argument("--asof", default="2026-06-09")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    m = analyze(a.data, date.fromisoformat(a.asof))
    if a.json:
        print(json.dumps(m, indent=2))
    else:
        print_report(m)
