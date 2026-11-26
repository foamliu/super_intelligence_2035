# r558 deep-read: 1791972521290_aw79o (yzwang @ hfeg0plg06, mc=81)

- **domain**: physical_verify (drc:178; pdk:84; calibre:14; .def:16; lvs:1)
- **session**: 492KB, 110 msgs, 6 user turns
- **A档合格**: U#0 produce-task modify-existing（提需求未给根因/方案；U#2/U#3 才给连续变量全赋值修复 → A档任务说明用 U#0 原文）

## 用户意图演进
- **U#0** (msg 0): 找到所有 `CPU TIME = N REAL TIME = N`；若上一行有含 ≥2 下划线的变量，变量名截止到 `::` 前；按前缀聚合总 CPU/总 REAL。已有 `parse_rule_time.py`，对 `rundrc.log` 统计有问题 → **修脚本**。
- **U#1** (msg 44): 展示 DNW_CL_015_00 各变量（::<1>/<2>/check_CaveWidth_StepWidth<1>::X/Y/Z/TMP<86-89>）的 CPU/real time。
- **U#2** (msg 54): 连续变量行 Y(265413)+Z(265414)+CPU(265415, CPU=2 REAL=1)，规则把时间整条记给紧邻 CPU 行的变量(::Z)；用户决定：多个变量紧挨时，CPU 行的 CPU/REAL **均赋给所有变量**。
- **U#3** (msg 72): 修正——Y 和 Z 均 CPU=2 REAL=1（**不是平均**，各得完整值）。
- **U#4** (msg 86): 运行方式改 `python3 file parse_rule_time_fixed.py`，file=日志名(rundrc.log)用户手写，结果生成在当前路径。
- **U#5** (msg 94): 总时间用 `--- TOTAL CPU TIME = 650742 REAL TIME = 59303`（规则并行，不可逐条累加）；去掉 `Other/derived-layer CPU` 行；显示文件生成时间；去掉第 10 行 `Rank  Variable (before ':')`；CPU_total(s)/REAL_total(s) 首字母与下方数字最高位对齐。

## assistant 工具链
editor×多 写 parse_rule_time_fixed.py（多版迭代）+ inspect_prev/inspect_edge/inspect_names/show_dnw/show_dnw2/show_dnw_new 辅助调试 + read_files 读脚本 + run_approved_command 跑日志验证。

## 建模（B档 mock-behavioral）
把 live DRC rundrc.log 规则耗时聚合重构为纯 Python mock-log fixture，核心算法保留：
- 逐行扫描；`CPU TIME = N REAL TIME = N` 行（非 TOTAL）触发向上扫连续变量块
- 向上扫：遇变量行 `^\s*([A-Za-z0-9_]+)::` 继续，遇非变量行停；每变量全赋值（非平均、非仅末行）
- 前缀 ≥2 下划线过滤（AB_C 滤除）
- per-prefix 聚合总 CPU/REAL
- TOTAL 行取总（非逐条累加，规则并行）
- 降序排名（并列前缀升序）
- 输出 rule_time_summary.txt（DRC Rule Time Summary / Generated: / Log: / TOTAL CPU= REAL= / blank / CPU_total(s) REAL_total(s) / rows）

## case
- **case_id**: EDA-Eval-DesignFlow-DrcRuleTimeAggregator-001
- **k=16 a-p**，自验 GOLD B+B2 PASS 16/16✓；4 neg all-FAIL✓；§4.9 三假全 FAIL✓
- C.jsonl 339→340
