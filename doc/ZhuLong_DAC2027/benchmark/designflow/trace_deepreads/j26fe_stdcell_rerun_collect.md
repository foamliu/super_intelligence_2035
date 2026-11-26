# 深读：1793605193788_j26fe · e0039602 @ hfeg0plg103 · mc=460 · schematic_netlist

## 会话概况
- nmsgs=385, 2.4MB。cline 目录式存储 `sessions/1793605193788_j26fe/1793605193788_j26fe.messages.json`
- 工具关键词：netlist 795 / schematic 10 / pyAether 1（项目=verilog_lib_trans stdcell 网表→SV 转换工具）
- 用户 e0039602 在 hfeg0plg103，项目根 `/home/e0039602/Documents/verilog_lib_trans_v1.4.2/`

## 用户轮（关键）
- U0: 「请你学习这个项目，然后对比以下两个sv：module ffqnCSx1_m ...」— 让 agent 学习项目并对比两个 ffqnCSx1_m SV 写法（V1 vs V2，谁对谁错）
- U20: 「module and2CSx1(A,B,Y,...) ...」— 第二个对比：and2CSx1，V1（and+2×inv_base）vs V2（and+1×inv_base），判断哪个对
- U31（**真需求/本轮 A 档候选**）:「/home/wellesc/runStdCellTB/test_dut2/sim_runs/_FAIL_Report.md 这是经过我们工具检查 /home/e0039602/Documents/verilog_lib_trans_v1.4.2/outputs/result_map_20261030_171822_5576.txt 之后输出的错误的，请你将所有错误的result都收集到一个文件里，这个文件要在每个model前面用注释的形式写明错误的原因，好让后续AI读取这个的时候可以看到错误的原因，然后构建一个新的rerunpy文档，这个文档可以读取到之前收集的错误的文件的那个文档，然后跟以前的规则一起构成新的prompt，让AI重新再跑一遍，把这些错误的根据错误原因重新改，你有什么问题先和我交流，交流明白后开始执行」
- U44（确认 5 点）: 「1.按你说的来 2.复用现有的 3.按照ruleprompt来，要生成完整的model 4.可以，你自己能解析明白就行 5.输出结果就是按照之前的resultmap一样的格式就行，在名字里再加一个rerun放进outputs里」

## agent 工具链（U31 之后）
1. list_allowed_files(/home/wellesc/runStdCellTB/test_dut2/sim_runs) → 见 _FAIL_Report.md / _report.md / _results.json / 各 cell 子目录
2. read_files(_FAIL_Report.md, _report.md, _results.json) — 读 fail 报告
3. read_files(run.py) + run_approved_command(rules_prompt.py)（import 失败：`from . import simlib_lookup` ImportError）
4. search_codebase(build_prompt / 完整原文 / cell 转换) + read_files(parallel_worker.py)
5. read_files(report_writer.py, agent_client.py) + search_codebase(run_module / # ---- module:)
6. run_approved_command(output_validator.py) — exit0
7. read_files(run.py 473-512, rules_prompt.py 1-120 & 714-830) — 拿 result_map 块格式 + RULES 文本
8. editor 创建 _probe_env.py → run_approved_command → python3.7 / yaml OK / outputs 可写 / src imports OK
9. editor 创建 rerun_collect_fails.py（分多段，因 >6000 char 限制）— 内含 GROUPS 数据结构 + 收集逻辑

## 关键产物结构（从 MSG 43/51/68 还原）
### _FAIL_Report.md 结构（66 MISMATCH + 4 NODUT = 70，分 5 组 + xord2 + nodut）
- 组1 and2/and3: AND 做成 NAND（多余输出反相器 inv_base）— 14 cells — CONFIRMED-DUT-BUG
- 组5 or2/or3: OR 做成 NOR（多余输出反相器）— 8 cells — CONFIRMED-DUT-BUG
- 组3 FF: RN/SN 低有效复位/置位极性映射 — 9 cells (ffrsq/ffsq/ffsrq) — PENDING-GOLDEN
- 组4 mxi: 反相 MUX 极性 vs 模板 — 25 cells (mxi2/3/4) — PENDING-GOLDEN
- 组2 dlybias/dlybiasn: 模拟延迟单元 — 8 cells — PENDING-GOLDEN
- xord2: 2 cells (xord2DSx1, xord2LVx1) — PENDING-GOLDEN
- nodut: 4 cells (latrqLVSx1/2, passgtLVSx1/2) — 与 simlib_LVS.sv 库冲突，DUT 未必错

组4 mxi 25 cells（MSG 68 原文）:
mxi2CSx1, mxi2CSx2, mxi2DSx1, mxi2DSx2, mxi2GSx1, mxi2GSx2, mxi2LVSx1, mxi2LVSx1_pc60, mxi2LVSx2, mxi2LVSx2_pc60, mxi2LVx1, mxi2LVx1_pc60, mxi2LVx2, mxi2LVx2_pc60, mxi2Lx1, mxi2Lx2, mxi3DSx1, mxi3LVSx2, mxi3Lx1, mxi3Lx2, mxi4DSx2, mxi4GSx1, mxi4LVx2, mxi4Lx1, mxi4Lx2

组3 FF 9 cells: ffrsqDSx1, ffrsqLVx1_pc60, ffrsqLx1, ffrsqLx2, ffsqIOLVx1, ffsqIOLVx2_pc60, ffsqLVx1, ffsqLVx2, ffsrqLx2

### result_map.txt 块格式（MSG 51）
```
# ---- module: <name>
## 完整原文
<原始网表/SV 文本>
## cell 转换
<转换后 SV module>
```

### rules_prompt.py
- `build_prompt(netlist_path, simlib_path, module, missing_insts, ...)` — 给每 module 组 prompt
- 含 RULES 文本常量（转换规则 + 输出格式要求「生成完整 model」）
- `from . import simlib_lookup, netlist_parser`（包内 import，独立跑会 ImportError）

### 转换工具架构
- run.py → parallel_worker.run_module() → rules_prompt.build_prompt() → agent_client LLM → output_validator → xrun_check → 写 result_map
- agent 复用 parallel_worker + agent_client + config.yaml（token/网关）

## 用户契约（B 档合成依据）
1. 收集所有错误 result 到单文件，每 model 前用**注释写明错误原因**（供后续 AI 读取）
2. 构建 rerun.py：读取收集的错误文件 + 以前规则（rules_prompt）→ 构成新 prompt → 让 AI 重跑、按错误原因重新改
3. 输出 result_map 同格式，名字加 `rerun`，放 outputs/
4. 分层：确认 DUT bug（and/or/xord2）强制重跑；pending-golden（dlybias/ff/mxi）尝试修复标 review；NODUT 库冲突默认跳过
5. 按 rules_prompt 基底，生成完整 model

## 复刻判断
- 私有路径 `/home/wellesc/runStdCellTB/`（fail report）+ `/home/e0039602/Documents/verilog_lib_trans_v1.4.2/`（转换工具源码）不可复刻
- → B-grade synthesized：自包含合成 `_FAIL_Report.md`（5组+xord2+nodut，根因+fix+cell 列表）+ `result_map.txt`（每 error cell 的 `# ---- module:` / `## 完整原文` / `## cell 转换` 块）+ `rules_prompt.py`（RULES 文本 + build_prompt 骨架）
- 交付：`rerun_collect_fails.py` 单工具 → 产 `collected_errors.txt`（每 cell 注释头[family/confidence/cause/fix]+当前转换块）+ `rerun.py`（读 collected + rules_prompt → 每 cell 修复 prompt → 写 outputs/result_map_rerun.txt）
- A vs 隐藏 B：cell 名/族/组结构/数量全不同（B 用另一套 stdcell 族，如 nand/nor/xor/scan-flop/mux-t 组合），反硬编码

## trace_source
- user: e0039602（原始用户名，不 hash）
- host: hfeg0plg103
- session_file: 1793605193788_j26fe
- match_count: 460
- real_task_summary: stdcell verilog_lib_trans 转换错误收集+rerun 脚本：解析 _FAIL_Report.md(66 MISMATCH+4 NODUT，5 组根因)+result_map.txt，收集所有错误到单文件(每 model 前注释错误原因)，构建 rerun.py 读收集文件+rules_prompt 生成新 prompt 让 AI 重跑修复，输出 result_map_rerun 格式放 outputs
