# Deepread: 1794208637739_ddprg — LPDDR5 testbench resetfuse 触发链路排查

- **session**: `1794208637739_ddprg.messages.json` (522,975 bytes, 54 msgs)
- **user / host**: daiweilu / hfhds209
- **match_count**: 53；keywords: verilog:1194;netlist:25;analog:12;.spi:4;systemverilog:3
- **domain**: digital (LPDDR5 testbench / Verilog task-event 触发链) — 但 session 性质是 Q&A/分析
- **status**: parked (Q&A-only, 无 clean produce-task 交付物)

## 会话性质
3 条真实 user_input turn（中文）：
- **U#0** (idx 0): 粘贴 `AF_EfuseCell` 模块代码 + 隐含提问（resetfuse 如何使用/连接）。
- **U#39** (idx 39): 「这个 def projectname 有别的含义吗 还是就是定义 projectname 这个字符串」— 宏含义 Q&A。
- **U#51/52** (idx 51/52): 「那我要使用 reset，只需要在 pattern 添加 resetfuse(); 吗」— 用法确认 Q&A。

其余 user msg 全是 tool_result。assistant 用 search_codebase / run_commands / editor(写 grep_resetfuse.py / grep_resetfuse2.py / find_projname.py 临时探针脚本) / read_files 排查 `resetfuse` 信号 → `ResetFuse` task → `tbresetfuse` event → `always @(tbresetfuse)` 触发链，最后给出 markdown 解释（idx 38, 53）。

## 选中任务？
**无 clean produce-task**。agent 的「交付物」是一段 markdown 解释（resetfuse 触发链路 + PROJECTNAME 宏来源 + ResetFuse 大小写修正）。临时 grep 脚本是探针，不是可复用交付件。3/3 user turn 全是 Q&A/确认，未给根因也未要求生成可验证产物 → A-faithful produce-task INFEASIBLE。

## B 档可行性
理论可合成「Verilog trigger-chain analyzer」（给定 SV testbench + 目标信号名 → 抽 task/event/always-block 链 → JSON），与 r427 CrCheckAudit（TB check-task 抽取）部分重叠但角度不同（r427 抽 check/expect task，本 idea 抽 trigger-event 链）。但：
1. 真实 testbench 资产 = `/proj/ddgoa/V0/simdir/verilog/daiweilu/verilog.lpddr5.ddgoa.1106/lpddr5_test.sv`（9321 行，私有 /proj 路径，沙盒不可达，与 npf2k/dnkz8 同类资产可达性阻塞）；
2. session 内仅含 testbench 片段（agent read_files 225-250 / 5311 区），不足以构造 trace-faithful 完整 A；
3. 本轮时间预算（r433, ~10 min 剩余）不足以完成 ≥8 条件 check.py + 4 negative + 自验 + 落库的高质量 B 档。

## 决定
**parked**：Q&A-only trace，无 clean produce-task；B 档理论可行但受资产可达性 + 时间双重约束，本轮不做。沉淀「trigger-chain analyzer」idea 供未来资产可达性解决后重开。

## P-002 复证（r433）
- mc≥10 A-dominant 候选 512 unique（a≥15, a>2c, a>b）；top-150 交叉 4-shard 当前台账(2676 anchor)后 **仅 4 fresh**；
- 4 fresh 全 weak：swhjl(stevenh, Q&A「task 复用性」, r421 已 peek weak) / 7hv1e(ruisongs, mc41, 待 peek) / ddprg(本轮, Q&A) / spcmy(e02141, synopsys:1003, 实为 analog/char 族)；
- 193 parked 全经筛查 unfit（analog/Q&A/duplicate/env-dependent/asset-inaccessible），无「check 难度非 trace 不合格」型可重开项（r431 c4vkj/r418 ppl5a 型已穷尽）；
- 结论：shard A mc≥10(11/09 快照) 池 **量质双枯竭** 2 次复证，与 r431 一致。后续扩样需新扫描快照或放宽 produce-task 定义（见 board P-002 CLOSED 结论）。
