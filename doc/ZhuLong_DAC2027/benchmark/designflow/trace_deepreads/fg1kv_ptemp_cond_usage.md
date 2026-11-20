# fg1kv deepread — ptemp 温度参数用法追踪 (r646)

- session: `1793084065593_fg1kv` (ghyang @ 10.129.2.12, mc33, eda_other)
- trace: 43 msgs / 4 user turns, 439KB. Fetched to .75 session workdir `fg1kv/messages.json`.
- 32 read_files results extracted to `fg1kv/extracted/` (key is `result`, not `text`).
- revival source: `parked_reaudit_A.tsv` row 114 (REVIVABLE_QA, trace EXISTS), old reason "SPICE analysis Q&A, weak".

## 用户原话（逐字, A 档 trace-faithful）
> /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_case4/sim_p1_pl3.sp这个文件中定义了温度，我想知道这个温度在哪里被作为判断依据起了作用

## 正确根因 (ground truth)
- `ptemp=-40` 定义 @ `sim_p1_pl3.sp:15` — `.param ptemp =-40`
- 仿真温度指令 @ `sim_p1_pl3.sp:41` — `.temp -40c`
- 引用链: `sim_p1_pl3.sp:10` `.inc "/proj/ddgoa/V0/workdir/ytzhu/simulation/setup/Pattern_Power_CRG.sp"`
- `Pattern_Power_CRG.sp` 结构: 7 个 pvcc band (0.9-0.92 / 0.92-0.97 / 0.97-1.0 / 1.0-1.1 / 1.1-1.2 / 1.2-1.4 / 1.4-1.5)，每个 band 内嵌 `.if (ptemp==-40) / .elseif (ptemp==98) / .else` 选择温度相关偏置电压
- 被控参数: pvwlp, pvblh, pvblhbk, pvmwln, pviso
- cold (ptemp==-40): pvwlp=2.8v, pviso=1.44v
- hot  (ptemp==98):  pvwlp=2.6v, pviso=1.36v
- 机制: ptemp 作为 decision criterion，在每个 pvcc supply band 内按温度分支选择 bias/supply 电压

## clean A 文件 (line numbers stripped)
- `clean_sim_p1_pl3.sp` — 208 行 / 7910 bytes (md5 .75 f6b782a24bffc0737cdcadfbd3b65c37)
- `clean_Pattern_Power_CRG.sp` — 438 行 / 15570 bytes (md5 .75 4d25a7a54de32b6a75d0b7316d066160)
- 本地副本 (用于 builder, 内联为 A_FILES): content 与 .75 一致 (trailing-whitespace 仅差 2 bytes, 不影响 token/regex)

## case 产出
- case-id: `EDA-Eval-DesignFlow-PtempCondUsageAnalyze-001`
- domain: eda_other, mode: design_flow, k=16 (a-p)
- A/B anti-hardcode 9/9 维全异 (project/ptemp/temp_directive/power_table/band_count/branch_values/controlled_params/cold_pvwl/hot_pviso)
- 交付: `ptemp_usage_analysis_report.json` (zip 内单文件, 10 顶层段)
- 自验: ref 16/16 ALL PASS + 5 negs + 3 §4.9 fakes 全 FAIL distinct [a,b,c,f,l,m,n]
- builder: `_ptemp_build/build_ptemp_case.py` (本地跑, stdlib only)
- A.jsonl: 350→351; ledger fg1kv→case; parked_reaudit fg1kv→r646 DONE

## 拒绝的候选
- p16i1: unresolved, weak evidence anchor — reject
- mss1b: vcim file doesn't exist on host, unresolved — reject
