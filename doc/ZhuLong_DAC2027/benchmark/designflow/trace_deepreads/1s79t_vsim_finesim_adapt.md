# 深读笔记 · 1s79t · mike @ hfeg0plg49 · lpddr6 vsim→finesim TB 脚本适配

> 2026-11-12 02:3x · shard B rescan_1112_r409 候选 peek · mc=517 spice grep · 760KB / 6 user msgs / ~67 tool_use
> **判定：CLEAN spice_sim produce-task（脚本适配/重构类，L1-adjacent）· 已 claim（DEBT:1 待合成）**

## trace 源
- host: 10.129.8.86 (hfeg0plg49) · user: mike
- session: `/home/mike/.cline/data/sessions/1794378055746_1s79t/1794378055746_1s79t.messages.json` (759964 B)
- match_count: 517 (spice grep) · mtime ≥ 11-10 · rescan_1112_r409 candidates line 9

## 用户意图（6 条 user message，原话）
- **U1**：`/ai_sandbox/dscqa/V0/agentdir/mike/sos_manage_lpddr6_random 这是lpddr6 tb，你理解下 vsim脚本，我要生成一个finesim的tb 但是可能脚本要适配下`
- **U2**：贴 `vsim -a lpddr6 -p decqa -c finesim` 运行输出，含 `grep: .../verilog.lpddr6.decqa.finesim/config/tbconfig: No such file or directory`（/proj 路径不可达）
- **U3**：`你先理解下vsim脚本 我来告诉你怎么维护脚本，我要把一些冗余删掉，然后告诉你咋适配`
- **U4**：`lpddr4 lpddr5相关的全删掉，默认 DECQA/V0`
- **U5**：`如果vsim -c 用的绝对路径，那就从 vsim的目录下拿文件生成tb，不然就用默认路径，你之前的补丁可以删了`
- **U6**：`你直接把vsim给改了`

## assistant 工具链（67 tool_use 概览）
- **探查**：list_allowed_files × 多 · read_files 读 `lpddr6_tb/bin/vsim`（Perl，~2000 行，分段读 250-520/520-950/950-1238/1238-1622/1622-1950/1710-1860/1502-1578 等）+ `sourceme`/`tbmanage`/`top.sv`/`lpddr6_test.sv`/`A_Pattern_Sim.v`/`config/tbconfig`
- **分析脚本**（Python，写 `/home/mike/lpddr6_*.py`）：`lpddr6_grep.py`（grep finesim/si.env/form.rc/ANALOGVEC）、`lpddr6_vsim_analyze.py`（列 sub 名）、`lpddr6_filelist_check.py`（隔离 lpddr6 块的 filelist）、`lpddr6_grep2.py`（grep lpddr4/lpddr5/DBRMA/mq06/mq08）、`lpddr6_refactor.py`（difflib 块查找 + 替换）、`lpddr6_balance.py`（花括号/括号平衡检查）、`lpddr6_dirnametest.py`（dirname 路径推导）、`lpddr6_show_region.py`（行号区间打印）
- **重构产出**：
  - `lpddr6_vsim_local_fallback.patch`（unified diff `@@ -484,6 +484,19 @@`，插入 local workarea fallback 块：`/proj/<tbproj>/<dbv>/sim/verilog/` 不可达时回退到本地 sos_manage workarea）
  - `vsim.decqa`（重构后的完整 vsim 脚本，存 `/home/mike/vsim.decqa`）
  - `deploy_vsim.py`（backup 原 vsim → `vsim.orig`，用 vsim.decqa 覆盖 sandbox vsim）
  - `fix_help.py`（help 文本 `DBRMA/V0` → `DECQA/V0`）
  - `regenerate_diff.py`（生成 `vsim.decqa.diff` = vsim.orig vs vsim.decqa 的 unified diff）
  - `check_dbrma.py`（验证 dbrma 引用已清除）
- **skill 调用**：`skills: gen-finesim`（lpddr6 finesim TB generation）
- **ask_question**（T23）：问用户交付形态——独立脚本 / 改造 vsim / 两者 / 先给要点清单

## 交付物（DoD）
重构后的 `vsim` Perl 脚本（vsim.decqa）+ unified diff（vsim.decqa.diff），满足：
1. 删除 lpddr4 / lpddr5 / DBRMA 相关引用（U4）
2. 默认 `DECQA/V0`（U4，help 文本 `(i.e. DBRMA/V0)` → `(i.e. DECQA/V0)`）
3. 新增 local workarea fallback（`/proj/<tbproj>/<dbv>/sim/verilog/` 不可达时用本地 sos_manage 目录）（U2/U5）
4. `vsim -c` 用绝对路径时从 vsim 目录取文件，否则用默认路径（U5）
5. 花括号/括号平衡保持（`lpddr6_balance.py` 验证）

## 域归属 & 可移植性评估
- **域**：spice_sim（finesim = SPICE 类仿真器；交付物使能 lpddr6 finesim TB 生成流程）。borderline 但 finesim/simulator 关键词密集（SPICE_KW=380），B shard 可接。
- **难度**：**L1-adjacent**（交付物是脚本重构/静态文本变换，check 验静态属性 + `perl -c` 语法检查，不需真跑 finesim 仿真）。TASK §5 偏好 L2/L3，但本 trace 真实工作即是 Perl 脚本重构（非跑 .sp deck），L1 是 trace 本性。可加 `perl -c` 真执行升 L2-adjacent。
- **可移植性**：⚠️ **高预算**——真实 vsim 脚本 ~2000 行 Perl，含 `/proj/decqa/V0/sim/verilog/...` + `/ai_sandbox/dscqa/V0/agentdir/mike/...` 私有路径。A 档 trace-faithful 需：
  1. ssh scp 完整 vsim 脚本（10.129.8.86:/home/mike/vsim.orig 或 sandbox vsim）
  2. 脱敏：/proj/decqa → 占位、/ai_sandbox/.../mike → 占位、lpddr6 业务名可留
  3. A/B 双盲：A 用原 vsim（含 lpddr4/5/DBRMA + /proj 路径），B 用变体（不同 legacy 引用集 + 不同默认 proj，如 `DBRMA/V0` 默认 + mq06/mq08 legacy）
- **B 档 synthesized 备选**：若 A 档脱敏预算过高，可合成 ~150 行代表性 vsim-like Perl 脚本（含 lpddr4/5 refs、DBRMA 默认、/proj 路径、help 文本、花括号结构），check 验重构变换。B 档理由：真实 vsim 2000 行 + 私有路径脱敏高预算；合成脚本忠实捕获关键重构模式（legacy removal / default change / fallback insertion / brace balance）。

## 下轮合成计划（DEBT:1 · 首事）
1. **评估 A vs B 档**：先 ssh 抓 `vsim.orig`（10.129.8.86:/home/mike/vsim.orig）行数 + 私有路径密度；若 <500 行可脱敏 ⇒ A 档；若 >1000 行 + 密集 /proj ⇒ B 档 synthesized。
2. **case 设计**：`EDA-Eval-DesignFlow-VsimFinesimAdapt-001`，spice_sim / L1（或 L2-adjacent with perl -c）/ A-faithful 或 B-synthesized。
3. **check.py ≥8 断言**（预设）：
   ① 交付 zip 含 refactored vsim 脚本 + diff
   ② lpddr4 引用已删（grep -ic lpddr4 == 0 on refactored）
   ③ lpddr5 引用已删（grep -ic lpddr5 == 0）
   ④ DBRMA 引用已删或改写（grep -ic dbrma 在 help 区为 0）
   ⑤ 默认 proj 文本为 DECQA/V0（help 区含 "DECQA/V0"）
   ⑥ local fallback 块存在（含 "fallback" + "/proj" 不可达判定逻辑）
   ⑦ 花括号平衡（count '{' == count '}'）
   ⑧ `perl -c refactored_vsim` 语法通过（L2-adjacent 真执行）
   ⑨ diff 为 unified diff 格式（`^@@` hunk 头 + `^---`/`^+++`）
   ⑩ A 与 B 输出 distinct（B 的 legacy 集/默认 proj 与 A 不同 ⇒ 删的行集不同）
4. **负样本**：空壳 vsim（原样返回）/ 只删 lpddr4 不删 lpddr5 / 不加 fallback / 删过头破坏花括号平衡 → 全 FAIL
5. **自验**：perl -c on refactored（.75 有 perl）+ negative_selftest + §4.9 三假

## 备注
- 本 trace 是 rescan_1112_r409 首个 genuinely-viable B-domain CLEAN candidate（前 02:1x 轮 peek 4 全 0 viable，本轮 peek 7 得 1 viable）
- 6 reject 已 park（n70dr consultation / zdztp consultation / p1isl wrong-domain netlist / fnxke near-dup op8wj / ngnm2 wrong-domain waveform / 0fuy7 near-dup r73sm）
- rescan 余 6 unpeeked（jjrpj/bwtk9 e0030760 同 2kwms file-mgmt 嫌疑 / tef8l yinyus / jlgfx yohannw / 5p2v2 thomasz / nm5op rongjiez 同 bwlcp waveform 嫌疑）—— 下轮 peek
