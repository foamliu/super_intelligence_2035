# hdhfh — cg_t timing meet_exactly 未命中 bin 筛选 (deepread)

**session**: `1789718897680_hdhfh` · user `t0002470` @ `10.129.2.11` · mc=5 (verilog:18;drc:13;systemverilog:4;cadence:2;rtl:1)
**session json**: 1,053,770 B / 59 msgs · model glm-5.2 (cxmt-glm52) · 2026-09-18 08:08 → 09-20 01:31 (status=failed, exit 1, terminal_marker=failed_external_process_exit)
**liveness**: r794 标 ALIVE(flat-path) → r803 标 rotation-NOFILE reconfirm(11-19 17:14) → **r815 复测推翻:r810 path-bug**,subdir `/home/t0002470/.cline/data/sessions/1789718897680_hdhfh/*.messages.json` = ALIVE (1,053,770 B .messages.json + 2,597 B .json,mtime Sep 18)。r803 的「rotation 蒸发」结论同 r760/r761/r773/r794 一并作废 = path bug 非真枯竭。

## 真实用户意图(逐条原话)

- **U0** (ts 1789718898537): `加载这个skill /home/t0002470/workspace/skill/ddr5-coverage-analysis-skill`
  - agent 用 list_allowed_files + read_files 读 SKILL.md(1204 行)+ skill-creator 注册。skill = DDR5 DRAM coverage 根因分析(illegal violation / 空 bin / command encoding error 三类)。
- **U1** (ts 1789719863902): `将这个覆盖率报告/home/t0002470/workspace/html_18-09-2026_10~26~40里的所有cg_t相关的timing中没有命中meet_exactly的bin筛选出来`  ← **核心任务**
- **U2/U3** (ts 1789721265688 / 1789721346689): `继续完成未完成的任务` (×2)
- **U4** (ts 1789721368639): 重复 U1 原话(用户重发,因前序未交付)

## agent 工具链与产物

1. list_allowed_files `/home/t0002470/workspace/html_18-09-2026_10~26~40` (depth 2) → 发现 IMC 报告三层结构: `table1.json` / `table2/itemN.json` / `table2/table3/itemN.json`,以及 `16Gb/` `24Gb/` Legacy/PRAC 子目录 + `*_Failedregs_Rpt_File` 报告。
2. read_files `table1.json` (分块 1-1080 行) + `table2/item0.json` + `table2/table3/item1/10/100.json` + `cov_report_parser.py`(skill 自带解析器)→ 理解三层 JSON 层次。
3. search_codebase `cg_t` → 定位 cg_t timing covergroup 段(约第 495 行起,580+ 个 timing covergroup)。
4. read_files table2/table3 样本(item1414/item2264 等)→ 理解 bin 级结构:
   - **简单 3-bin covergroup**: 1 个 coverpoint `cp_delta_min_vs_constraint_min`,3 bin(`meet_exactly` / `safe_within_half` / `safe_beyond_half`)。
   - **大型 covergroup**(如 Table_334_339): 3 coverpoint(3+16+48=67 bins),`meet_exactly` 出现在 `cp_delta_min_vs_constraint_min` 与 `cross_speed_min` 中(标题 `meet_exactly;SPEED_*`)。
   - `illegal_bins` 不计入 total;3-bin 组 0/3→meet_exactly 必未命中,3/3→必命中,仅 1/3、2/3 需查 table3。
5. **editor ×7** 写 `/home/t0002470/workspace/skill/ddr5-coverage-analysis-skill/filter_meet_exactly.py`(分块 new_text/old_text 增量构建):遍历 cg_t* covergroup → 下钻 table2/table3 → 收集 title 含 meet_exactly 且 Hits==0 的 bin → 输出 JSON + Markdown(stats: total_timing_cgs / total_meet_exactly_bins / hit / not_hit / cgs_with_not_hit)。
6. run_approved_command(profile=hello_world) → **被 agent-policy-engine 拒(UID 不匹配)**;run_commands(`python3 filter_meet_exactly.py`) → **同样被策略引擎禁**;get_agent_policy_status → 无可用执行通道。
7. **fallback**: 改用 read_files 逐块读 table1.json(504-560/560-620/.../860-940)手工筛非 100% cg_t 条目,session 终因 failed_external_process_exit 中断,U2/U3/U4 重发未竟。

## 关键产物字段(agent 脚本揭示的 IMC schema)

- covergroup: `{title, Source, "All Cov", items_json}` (items_json = 相对 report_dir 的 table2 路径)
- coverpoint: `{title, Source, "All Cov", items_json}` (items_json = table2/table3 路径)
- bin: `{title, Source, Hits, Total, Coverage, illegal_bins}`
- timing 判定: title 去 `::` 前缀后以 `cg_t` 开头
- meet_exactly 判定: title 含子串 `meet_exactly`(含 `meet_exactly;SPEED_*`)
- 未命中: `Hits == 0`

## 选料判定

- **域**: verification(功能覆盖率分析,verilog:18 主导,IMC coverage report 解析)。
- **A-pure**: 是(无 finesim/hspice/PEX/virtuoso layout 等 C/D 工具,synopsys/drc 命中系 IMC 报告内 drc covergroup 字面量非 calibre DRC 工具调用)。
- **可造**: 是。用户意图单一明确(筛 meet_exactly 未命中 bin),deliverable 清晰(脚本 + JSON),check() 可写「牙」(结构化断言 + 隐藏 B + 反硬编码)。
- **A 档可行性**: 原报告 `/home/t0002470/workspace/html_18-09-2026_10~26~40` 11-19 复测 **已被 rotation 删除**(No such file)⇒ B档 synthesized(§5 produce-task reframe),用 agent 揭示的 IMC schema 重建合成 report_A/report_B,保留用户原话作 prompt。

## case 合成(r815)

- **case_id**: EDA-Eval-DesignFlow-CgTimingMeetExactlyFilter-001
- **档**: B档 synthesized · domain=verification · §5 produce-task reframe + hidden-B 真跑 + 反硬编码
- **交付**: `filter_meet_exactly.py`(CLI: `<report_dir> <output_json>`,stdlib only),遍历 cg_t* covergroup 下钻 table2/table3,收集 meet_exactly 且 Hits==0 bin,输出 JSON(report_dir/stats{5键}/results)
- **A**: report_A(12 covergroup:9 cg_t timing + 3 非 cg_t + 1 `::` 前缀 + 1 大型 cross_speed `meet_exactly;SPEED_DDR5_3200/4800/LP4_2400`);ground truth: 9 cgs/12 bins/5 hit/7 not_hit/6 cgs_with_not_hit
- **B(hidden)**: report_B(12 covergroup:10 cg_t + 2 非 + 1 `cfg::cg_t` 前缀 + 1 大型 cross_speed `meet_exactly;SPEED_LP5_6400/LP5_5500/DDR4_3200`);ground truth: 10 cgs/13 bins/6 hit/7 not_hit/6 cgs_with_not_hit
- **check.py**: 19 独立断言(oracle 独立解析 B 计算 expected,subprocess 真跑候选,断言 stats 5 值/results 长度/每条 bin_title含meet_exactly/hits==0/cg_t过滤/集合精确匹配/3 seed 确定性/反硬编码 A-token不现+B-token必现/必需字段)
- **自验**: ref PASS 19/19 + 5 neg 全 FAIL(neg_empty/neg_print_only/neg_core_deleted/neg_hardcode_a/neg_invert_filter) + §4.9 a/b/c 全 FAIL + e2e embedded-check PASS
- **落库**: cases/A 424→425; build_jsonl --shard A → A.jsonl 405→406; ledger hdhfh parked→case
