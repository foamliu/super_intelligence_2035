# Deepread: pot5o — xwchang APT Routing usage analysis

**session**: 1793942429427_pot5o · **user**: xwchang @ 10.129.2.14 · **mc**: 16
**agent**: lead · **msgs**: 82 (45 user / 37 assistant) · **date**: 2026-11-06

## User intent (逐字)

- U#0: `/home/xwchang/APT/APT_Routing_usage_20260302-20261031.xlsx`
- U#1-3: `请分析APT使用的项目数及每个项目使用人数及次数`
- U#36: `显示完整列表`
- U#42: `列表加上人均次数`
- U#52: `请按月总结`
- U#58: `使用次数增加到28428次，按比例分配到各个月份及项目`
- U#64: `使用次数增加到28428次，使用人数增加262人，按比例分配到各个月份及项目`

## What the agent did

- `list_allowed_files` /home/xwchang/APT → found APT_Routing_usage_20260302-20261031.xlsx
- Wrote `read_excel.py` (pandas) → read sheet names, columns: id, project_code, user_account, trigger_time
- Wrote `analyze_apt.py` → groupby project_code: usage count, unique users, per-capita
- Wrote `analyze_full_list.py` → full 40-project list with per-capita
- Wrote `analyze_monthly.py` → groupby trigger_time year-month: usage, active users, active projects
- Wrote `analyze_scaled.py` → scale to 28428 uses (factor 28428/23037=1.2340)
- Wrote `analyze_scaled_both.py` → dual scaling: 28428 uses + 958 users (696+262)

## Real data (from assistant output)

- 23,037 records, 696 users, 40 projects, 74 versions
- Date range: 2026-03-02 ~ 2026-10-31 (8 months)
- Top project: degpa (103 users, 5,944 uses, 57.7 per-capita)
- Monthly: 2026-03 (3033), 04 (2185), 05 (1824), 06 (3429), 07 (3003), 08 (3587), 09 (3386), 10 (2590)
- Scale factor usage: 1.234015; user: 1.376437

## Reframe (mock-behavioral)

Real xlsx (pandas, path-dependent on user's machine) → mock CSV (stdlib csv module)
+ JSON report. Asset A = 75-row CSV (8 projects, 20 users, months 3-6); hidden B
= 51-row CSV (6 different projects, 14 different users, months 4-7). B fully
disjoint from A (anti-hardcode). solve.py computes overview / per-project /
monthly / proportional scaling in pure stdlib. check.py has 15 conditions (a-o)
verifying B's computed stats against an independent oracle built from B's CSV.

**Domain**: physical_verify (EDA-tool-usage-log analysis; APT = Advanced Process
Tool, routing tool usage audit). Reframe note: real xlsx+pandas → mock CSV+stdlib
csv/json, execution-environment substitution (path-dependent xlsx on user
machine → portable CSV fixture).

## Case built

- **case_id**: EDA-Eval-DesignFlow-AptUsageReportGen-001
- **k_check**: 15 (a-o), k_rationale: 15 — GATE PASS (≥8)
- **self-test**: 15/15 PASS · **negatives**: 3/3 FAIL distinct (c/d/i)
- **round-trip**: 15/15 PASS (jsonl test field byte-identical to reference check.py)
- **§4.9 degenerate**: empty shell FAIL(c), print-expected FAIL(d), delete-monthly FAIL(i)
