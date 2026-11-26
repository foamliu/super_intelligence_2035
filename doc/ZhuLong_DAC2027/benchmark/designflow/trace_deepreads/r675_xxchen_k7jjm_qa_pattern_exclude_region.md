# r675 deepread — xxchen@10.129.2.10 / 1794396010329_k7jjm (mc=322, physical_verify)

> 状态：**PARKED (teeth-fail)** · r675 · shard C

## trace 元信息
- session: `1794396010329_k7jjm` · user: xxchen · host: 10.129.2.10
- mc=322 · keywords: `drc:1350;.gds:489;pex:5;aether:5;rtl:1;pdk:1;lvs:1;gdsii:1`
- N_MSGS=213 · users=111 · asst=102 · editor writes=30 · run_approved_command=39 · read_files=24
- 注意：keywords 高 drc:1350/.gds:489 来自真实任务（DRC_pattern_tool QA deck 生成器），**非 path-substring inflation**（与 r663 5ax4p drcpa 项目名 / r668 wlw3b DrcQa.py 路径不同）——本次 drc/.gds 是 task content。

## 用户真实意图（U#1 + U#139，逐字）
- U#1: `### QA pattern debug: DNW_F_012_00  QACELL DNW_F_012_00 inside_surround_ring DNW->NW check {surround Nguardring} {excludeRegion ESD,DCSCR,X_DEC} 这里的excludeRegion 为什么没有生效`
- U#139: `### QA pattern debug: DNW_F_012_00 ... 问题：excludeRegion 这里的 good 生成的 exclude pattern 把所有的 excludeRegion都堆叠在了一起 查看GDS：QA.gds 需要的是 ESD 带上 一组 bad Pattern，占据一行 DCSCR 覆盖上一组bad pattern，占据下一行。X_DEC 覆盖上一组bad pattern，占据下一行。`
- U#0 (Context summary)：goal = 将 `excludeRegion` 泛化为全 function 统一机制，调整 exempt pattern 排版（exempt 独立第二行 Y 堆叠，只有新 pattern 种类按 X 摆放）。

## assistant 工具链
- 30 个 editor write，**28 个在 `temp_script_run/`**（grep_exclude.py / grep_config.py / grep_logs.py / inspect_dnw_*.py / scan_gds.py / flatten_dnw.py / run_full_repro.py / rewrite_exempt.py ×4 / verify_rows_new.py 等）= 诊断/复现脚本（gdspy 读 GDS、grep 源码、跑生成器复现）。
- **唯一真实源码 fix**：msg#173 → `QA_Pattern_tool/script/pattern_common.py`（exempt-pass 注释块 + 逻辑，把「全叠同一排」改为「ONE ROW PER EXCLUDE REGION」）。
- 4 个 doc 文件（update_history.md / PROJECT.md / tasks/lessons.md / tasks/todo.md）。
- agent 终态（A#212）：「已完成。根因=用户看的是陈旧 QA_DNW.gds(11-09，无 exempt)；QA.gds(11-12) 有 exempt。重构为每个 exclude 区域独占一行：ESD 一行(y≈-32.2) / DCSCR 一行(y≈-61.8) / X_DEC 一行，每行 7 个 bad pattern。」

## 判分可行性评估 = TEETH-FAIL
1. **deliverable = 私有 codebase 生成器 patch**：fix 在 `pattern_common.py` 的 exempt-pass（依赖 `PatternContextBase.add_exclude_rect/exclude_tail/exclude_label/exempt` + `PatternGeneratorBase.generate` 框架 + gdspy 渲染）。judge 进程无法跑真实 DRC_pattern_tool（需整个 framework + config + gdspy + 生成 GDS）。
2. **静态子串 check 违反 §4.3**：若仅查 pattern_common.py 含「ONE ROW PER EXCLUDE REGION」/3 个 exclude label 名，则是子串断言（§4.3 禁「仅子串出现」），且 fake_print_expected 可绕过。
3. **reframe 可行性**：理论上可 reframe 为纯 stdlib Y-offset 布局函数（给定 N 个 exclude region + M 个 bad pattern，算出每 region 独占 Y 行、行内 bad pattern 按 X 推进），mock-behavioral 家族（r645-r674）新子型 `qa-exempt-row-layout`。**但**需先 ssh 取 pattern_common.py 全文（理解 add_exclude_rect/exclude_tail 真实签名 + 调用点）+ 设计 16-cond check（3 region Y 互异 / 每 region 行内 bad pattern X 单调 / region 间无 Y 重叠 / cross-input guard hidden B 用不同 region 名+bad 数）+ 4 negatives + selftest + §4.9 fakes + 自验 → 估时 35-45 min，**超出 r675 剩余预算**（peek 已耗 ~28min/40min）。
4. **结论**：按 11-15 重审令排除标准②「写不出有牙 check」park（非 type-weak，任务本身合法 produce-task，仅 judge-side 不可验证）。留作后续轮若预算充足可 reframe（mock-behavioral qa-exempt-row-layout 子型，与 r645-r674 家族 distinct）。

## 同批 peek 其余 4 候选（均 park / off-C）
- **8du7m / fvpye / e0mmo**（e0014566 mc411/395/383, 10.129.35.82）：全 `read the prompt_flow.md and do the job` = run-existing Virtuoso skill flow（PowerFill / RsCalc / AutoVia 电阻优化流）。deliverable = flow 输出 log + GDS，需真实 Virtuoso/Calibre 验证 → teeth-fail（judge 不可跑真工具）。keywords virtuoso:779-1032 为真实 task content 非 inflation。
- **a5l6y**（chaor mc302, 10.129.8.233）：U#56/89/119 = 解析 SPF 写 SiliconSmart .inst 文件（characterization 流）→ **off-C（B shard characterization 域）**；keywords verilog:1875/netlist:1094/lvs:250 中 lvs 为 spf 解析副产物非 C 域 LVS 任务。
