# 深读笔记 · 1794448818017_fppmi · witterfu · jitter sim deck 一致性检查

- **trace**: 1794448818017_fppmi.messages.json · user=witterfu · host=hfeg0pkn005(10.129.2.14) · mc=372 (hspice:128 netlist:45 schematic:45) · 56 msgs · 546KB
- **r481 post-1109 daily-log scan 发现**：11-10~11-13 daily log B-marker，去重 1109 summary 后 183 个 mc≥10 新 slug；fppmi 经 4-shard ledger+main jsonl 去重后 unledgered（真 fresh）。peek 3 个 fresh 候选：dgo3h(zhenglu mc355 pure-hspice-kw 但实为 PDK 库使用指南非 sim→parked 非 B)、fppmi(本条 真 B)、9lfys(未 peek 留下轮)。
- **domain**: spice_sim（HSpice/FineSim 仿真 deck 静态一致性检查，非 sim run）

## 用户意图（逐轮原话）
1. msg0: 「/proj/ddgot/V0/workdir/witterfu/simulation/wck/jitter/rj 这里面的文件是原来的 random jitter 的仿真文件，现在我修改出来了 12800 速率和 17600 速率的仿真文件，分别放在了 12800 和 17600 文件夹里面，帮我检查一下这个路径下的仿真文件的 run 文件（bash 脚本）sp 仿真文件和里面每个 corner 下的名称是否是对应的正确的，不正确的告诉我即可，不用自己修改」
2. msg10: 「我现在改完了，再见检查一下」（复查 → 全部正确）
3. msg14: 「同样的，我还有 psij 的仿真文件，同样在 12800 和 17600 文件夹里面 /proj/ddgot/V0/workdir/witterfu/simulation/wck/jitter/psij 帮我同样的要求检查一下」

## agent 工具链
list_allowed_files（列 rj/12800、rj/17600、psij/12800、psij/17600 目录树）+ read_files（读 run 脚本 + .sp 文件 + corner 文件）+ editor（无，用户要求不修改）。**无 run_approved_command**（用户明确「不用自己修改」「检查告诉我即可」→ 纯静态检查，不跑仿真）。

## 关键发现（agent 报告的不一致）
### rj/12800 目录
- `Rj_wr_12800.sp` 文件名标 12800，但内部 `drate=17600Meg`（第 102 行）→ 应为 `12800Meg`
- `run_Rj_rd` 引用 `Rj_rd_17600.sp`（17600 速率的 sp）→ 应引用 `Rj_rd_12800.sp`
- `run_Rj_wr` 引用 `Rj_wr_17600.sp` → 应引用 `Rj_wr_12800.sp`
### rj/17600 目录
- `Rj_rd_17600.sp` 的 drate 本来就是 12800Meg？(复查后全对)
### psij/12800、psij/17600
- 类似 drate-vs-filename、run-script-.sp-ref、corner-name 三类不一致

## 三类一致性检查维度（case 化核心）
1. **drate 参数 vs 文件名速率**：`<name>_<RATE>.sp` 内 `drate=<RATE>Meg` 必须匹配
2. **run 脚本 .sp 引用**：`run_<xxx>` 内引用的 .sp 文件名必须与本目录速率对应
3. **corner 名称**：run 脚本里 corner 名 vs 实际 corner 目录名一致

## case 化方案（下轮合成 · DEBT:1）
- **deliverable**: submit.zip{deck_consistency_checker.py}
- **Input A**: sim_tree（rj + psij，12800/17600 两速率，每速率含 run 脚本 + .sp + corner 目录），A 中植 2-3 处不一致（drate 错 / run 引用错 / corner 名错）
- **hidden B**: 同结构不同速率值（如 8000/9600）+ 不同 .sp 内容 + 植 3-4 处不同不一致
- **check.py**: subprocess 在 B 上真跑 checker → 断言输出 JSON 结构 + 逐条不一致命中（drate-mismatch / run-ref-mismatch / corner-name-mismatch）+ 一致文件不误报 + 总数正确。≥10 断言，check.py 独立复算 ground truth（非硬编码）
- **test_rationale**: 10 条断言：① zip 含 checker ② subprocess 在 B 真跑 exit=0 ③ 输出 JSON 有 inconsistencies 键 ④ drate-vs-filename 不一致被检出 ⑤ run-script-.sp-ref 不一致被检出 ⑥ corner-name 不一致被检出 ⑦ 一致文件被报 clean（无误报）⑧ B 不一致总数=N ⑨ 每条含 file+issue_type ⑩ rj 与 psij 两 sim 类型都被覆盖
- **难度**: L1→L2 边界（静态解析 .sp/run，无 sim run；但真跑 subprocess checker 在 B 独立复算，§4.2 满足）。域=spice_sim（HSpice deck 一致性是真 spice 工作流环节）
- **trace-faithful**: 用 witterfu 原话作任务说明（A 档），不改写

## 自验计划（下轮）
- ref 解（checker.py）在 A 上跑 → 报告 A 的 2-3 处不一致（与植的一致）
- check.py 在 B 上跑 → 报告 B 的 3-4 处不一致
- 3 §4.9 假提交（empty / print_expected / core_removed）全 FAIL
- 2 negative（hardcoded_A / always_pass）全 FAIL
