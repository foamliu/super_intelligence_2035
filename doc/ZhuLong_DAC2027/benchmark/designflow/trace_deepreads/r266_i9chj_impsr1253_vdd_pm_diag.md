# r266 deepread — i9chj (alan3zh@hfeg0pkn001) Innovus IMPSR-1253 VDD_PM diagnosis

- **trace**: `1793621923074_i9chj` (alan3zh, hfeg0pkn001/10.129.2.10, mc=121, kw=665 netlist+634 innovus+157 dbGet)
- **size**: 868KB, 86 msgs, 52 user turns (3 real user turns: U0 context-resume, U1 IMPSR-1253 query, U42 read-log-for-failure)
- **agent**: lead deepseek-v4-flash; tools: read_files/editor/run_approved_command(python-runner)/search_codebase/SandBox_MCP(run_code, refused)

## 用户真实意图（A-faithful eligible）
- **U1**（提出需求，未给根因）:「进入./apr/logs查看inv_fp.log，其中有告警：Begin power routing ... **WARN: (IMPSR-1253): Unable to find any standard cell pin connected to the VDD_PM net. 查询问题原因」
- **U42**（后续，新一次 run 失败）:「读取./apr/logs/inv_fp.log，查找失败原因」→ 诊断 Job 807801 Exited（permission-denied SEGV，与 IMPSR-1253 不同类）
- U0 是 session-resume handoff（continuation note），不可作 A 档任务说明

## grounding（agent 真实产物 + 证据链）
1. **log 结构**: `apr/logs/inv_fp.log` 861 行，含**两次追加的 LSF 运行**：行 1~450 = 11/2 旧运行（Job 549666，IMPDB-1216 + assignIoPins 报错，FAILED）；行 ~453+ = 11/3 14:04 新运行（Job 768479，DONE）。IMPSR-1253 在行 774（新运行）。两次 "Begin power routing"（行 328/773）。
2. **netlist 解析** (`_grep_netlist_pm.py` on `synth/results/dc_2026-11-02-20.29.45/hl22_porting_test_chip_v1_postsyn.v`, 6041 行):
   - `count '.VDD(' = 1985`, `count '.VSS(' = 2007`, `count 'VDD_PM' = 535`
   - 顶层端口 `..., VDD, VSS, VDD_PM`（16 top pins，IO 检查 "0 unplaced of 16"）
   - PM 子树: `PMArrayPart(TOPPMBLK) → PMVDDIMatrixPart(PM_VDDI_Inst) → 21×PMVDDIRowPart(PMColBLK_Blk40xx) → 21×INVD8(PMRowBLK_Blk40xx)`
   - **关键**: `PM_VDDI_Inst` 实例化端口名是 **`.VDD_PM(VDD_PM)`**（不是 `.VDD`！）；PM 行单元 `PMRowBLK_Blk40xx`（INVD8 反相器）的 `.VDD` 接**模块局部 `VDD_PM` 网**，经层次端口一路链到顶层 `VDD_PM`
   - 441 个 `PMRowBLK_*` leaf（INVD8）**只**存在于 `PM_VDDI_Inst` 子树内（21 RowPart × 21）；PM 阵列其余单元全部 `.VDD(VDD)` —— 网表级隔离真实且干净
3. **GNC/VERIFY 输出** (新运行): 21× `IMPDB-1280: "Existing connection to pin VDD of ...PMRowBLK_Blk40xx is Verilog-defined. Try override"`；GNC `VDD_PM` 的 VERIFY 只有 **1 个 pin**（网表自带的层次端口 pin，非 leaf std cell pin）
4. **根因结论**: IMPSR-1253 = 「新 DC 网表已自带 VDD_PM 隔离，但 fp 阶段没有任何 leaf 标准单元 pin 直接挂在 VDD_PM special net 上」的必然结果 —— **在 fp 阶段属预期现象**，不是新错误。GNC 找名为 `VDD` 的 pin → PM 子树 pin 都叫 `VDD_PM` → 一个都没连上 → VERIFY 的 "1 pin" 是层次端口 pin。
5. **U42 失败诊断** (Job 807801, 15:39, Exited): `apr/work` 目录对作业**瞬时失去写权限** → `IMPSYUTIL-96 ×3` (innovus.log/logv/cmd Permission denied) → `S2A-105 ×2` (SDC 转换临时文件) → saveDesign 在 `tcmModeCmd::writeModeCommand` **SEGV 段错误**崩溃 → exit 1。9 errors = 3 IMPSYUTIL-96 + 2 S2A-105 + 4 IMPCTE-2/27（两个 SDC 都没读进去）。**与 IMPSR-1253 完全不同类**（permission/env 失败 vs 预期 power-routing 现象）。随后 16:00 Job 816941 重跑成功（日志被覆盖，但 agent 在覆盖前已抓到失败证据）。
6. **修复** (innovus_fp.tcl 5 处 edit): 分代网表感知 —— 新网表跳过会落空的 GNC、VERIFY 区分 leaf pin 与层次端口 pin、TODO 附现成 leaf 改接命令；同步 README + 更新 `_apr_setup_validate.py`（旧 revision `dc_2026-10-29-19.16.52` → `dc_2026-11-02-20.29.45`）。验证器 ALL CHECKS PASSED（含 441 保护实例计数独立佐证）。

## case 设计（B-synthesized, L2, pg_layout）
- **为何 B 档 / 离线 L2**: 真实 Innovus/LSF/OA 不可沙盒复现；可离线化核心 = **解析 Innovus fp log + 解析 DC postsyn netlist → 判定 IMPSR-1253 是预期 fp 现象还是真失败**（纯 stdlib python，subprocess 真跑候选 → 结构化诊断报告）。L2（非纯文本断言）。
- **DISTINCT from 现有 pg_layout 系**: r224 InnovusPwrRtDiag（power routing 诊断但不同告警/结构）、r246 LefFromPinList、r238 LayoutFloorplanGen —— 本案首次 ground on「Innovus IMPSR-1253 + GNC + VDD_PM special net + 分代网表自隔离 + leaf-vs-hier-port VERIFY + 与 permission-SEGV 失败分类区分」。
- **A 输入**: inv_fp_A.log（2 runs，IMPSR-1253 ×1，DONE）+ postsyn_A.v（VDD_PM，441 INVD8，PM_VDDI_Inst port `.VDD_PM`）+ prompt（U1 原话）+ task_brief
- **隐藏 B**: inv_fp_B.log（3 runs：1 FAILED + 1 PERMISSION_FAILURE Job 807801 SEGV + 1 DONE with IMPSR-1253 ×1）+ postsyn_B.v（VDD_RTC，32 INVX4，RTC_VDDI_Inst port `.VDD_RTC`，结构不同）+ golden_B.json + hidden_manifest
- **判分**: check.py subprocess 跑候选 on B（+ A smoke），断言结构化字段（runs=3, impsr1253_count=1, leaf_count=32≠441, leaf_family=INVX4≠INVD8, pm_net=VDD_RTC≠VDD_PM, port_binding=.VDD_RTC, verdict=MIXED, failure_runs 含 Job 807801 IMPSYUTIL-96+SEGV）—— cross-input guard 杀 naive_hardcode_a/fake_print_expected。

## 断言清单（k_check = 15, a-o）
见 reference/InnovusImpsr1253Diag-001/check.py
