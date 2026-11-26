# Deepread — muf2k → RedBistForceReleaseInstAnomalyDiagnose-001（✅ r674 合成落地）

## trace

- session: `1793186643056_muf2k`
- user: `thomas1w` @ `hfeg0plg98` (10.129.8.x cluster)
- mc: 156（innovus/verdi/vcs/uvm 关键词，但实为 verification debug-Q&A）
- model: deepseek-v4-flash (provider `thomas`)
- 150 msgs / 9 user-text-turns / 72 assistant msgs，2026-10-28 ~ 11-11
- size: 869KB messages.json / 7.6M input tokens（含大量 RAG + read_files 工具结果）
- status: completed (exit_code 0)
- agent policy-engine enforcing; profileIds: python-runner, shell-runner
- log 路径（用户私有 /rundata，沙盒不可达）：`/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/log/log.regression_dft_20261028_161817/tm_redbist_part.x16`

## 9 个用户轮（逐字原文，trace-faithful）

| msg | 用户原话（节选） | 意图 |
|---|---|---|
| 0 | `[DEBUG_RELEASE ...] bg=1011 inst_name=I24 ... bg=1312 inst_name=I23 ... UVM_ERROR: set: unable to locate hdl path (...BankTopX2B1312.I24...) ... bg=89 inst_name=I23 ... UVM_ERROR (...BankTopX2B89.I24...) ... 这个路径下的 log文件，给出这样的打印，但是我期望bg=89 inst_name应该等于I23，但是有一处不是这样的，麻烦帮我看下为什么` | **主意图（debug-Q&A）**：解释 log 里 bg=89 的 inst_name 异常 |
| 69 | `中文回答` | 语言偏好 |
| 71 | `...tm_redbist.x16 的 log文件中，fork @(...net119); #10ms; join_any disable fork; redbist_common_task 应该是阻塞调用，需要等到@(posedge ...net119)，才会执行后续的，但是波形中这两次 force注错时间很近，都是在net119拉高之前，看下这里是为什么` | 第二意图：force 注错时序不阻塞 |
| 88 | `...tm_redbist.run 中的这一段代码，rdf=new(); assert(rdf.randomize()); col_single_bit_force(...); redbist_common_task("col_test3",...); ... 每次 force和 release应该是一次，你看这个时间戳都很近，第一次net119拉高前，所有的force和release都做过来` | 第三意图：force/release 配对与时间戳 |
| 92 | `先把更改的方法展示给我` | 要修复方案 |
| 102 | `不要直接更改我的文件，在同路径下备份一个，然后修改在备份文件中` | 备份后改 |
| 120 | `我上午表述有误，在...tm_redbist.x16 这段代码好像没有执行，log也咩有打印` | 修正：test2 段未执行 |
| 128 | `test2也是住错，这时候电路的数值已经变成1了，用0来住错` | test2 err_val=0 注错方向 |
| 134/142/146/148 | 波形路径 / 仿真太慢 / net119 拉高两次正常 / RdEn Pre 在 net119 第二次拉高前都拉高了 net025 一直为1 | 波形证据补充 |

## 真实根因（深读复核，基于用户 msg[0] 内联 log 实读）

**msg[0] 子片 = 最干净的单意图 debug-Q&A**，可独立造题。log 关键行（用户内联粘贴，逐字）：

```
[DEBUG_RELEASE row_single_bit_force ] bg=1312 inst_name=I23   ← force 用 I23（正确）
[DEBUG_RELEASE row_single_bit_force ] bg=23   inst_name=I24
UVM_ERROR: set: unable to locate hdl path (TOP.Chip.I_C_Top.I_Array16GTop.I_SpineTop.I_BankTopX2B1312.I24.IBankTop_W.I_BankLogic_17.I_RowRed768Top_34.I_RowRed768.I_RowRed_S1.I_RowRed2_S18.I_RedLatCom_S1_12_.Out)
[DEBUG_RELEASE row_single_bit_release] bg=1312 inst_name=I24   ← release 用 I24（与 force 不一致）
[DEBUG_RELEASE row_single_bit_force ] bg=89  inst_name=I23    ← force 用 I23（正确）
[DEBUG_RELEASE row_single_bit_force ] bg=1514 inst_name=I24
UVM_ERROR: set: unable to locate hdl path (...BankTopX2B89.I24...I_RowRed_S6...I_RedLatCom_S1_6_.Out)
[DEBUG_RELEASE row_single_bit_release] bg=89  inst_name=I24    ← release 用 I24（用户指出的"有一处不是这样"）
```

**3 类可检测 bug**（用户期望 bg=89→I23，但 release 行 + UVM_ERROR hdl path 都用了 I24）：

1. **force vs release inst_name 不一致**：force 行对 bg=89/1312 正确打印 `inst_name=I23`，但对应的 release 行打印 `inst_name=I24`。说明 release 代码路径用了硬编码 I24，未走 bg→inst 映射。
2. **UVM_ERROR hdl path 硬编码 I24**：`uvm_hdl_force/release` 构造的 hierarchical path 对 bg=89/1312 仍拼 `...BankTopX2B<bg>.I24...`，而物理上这两个 bank 的目标实例是 `I23`（force 行已证实）→ path 不存在 → `unable to locate hdl path`。
3. **bg→inst 映射规则**：从 log 可归纳 `bg ∈ {89, 1312} → I23`，其余（1011/23/1514）→ I24。release/hdl-path 代码漏了这条映射，统一用 I24。

**assistant 诊断（msg[145] 终答，部分正确）**：agent 主要追到 `A_Summary.rpt` col_single_bit_force FAILED(DQ_Err:2) + Test2(err_val=0) 列未真正 force + net119 done 未被 monitor 处理；但对 msg[0] 的 force/release inst_name 不一致 + hdl path 硬编码 I24 这一**最直接根因**未明确点出（被后续多轮 test2/net119 时序问题带偏）。**这正是题的"牙"**：候选需独立识别 3 类 bug，不能只复述 summary。

## 造题计划（下一轮合成 · DEBT 1）

- **case_id**: `RedBistForceReleaseInstAnomalyDiagnose-001`
- **domain**: verification（shard A）
- **A 档不可行**：log 在 /rundata 私有路径（沙盒 Permission denied）+ 波形 ncsim.shm 二进制不可解析；用户 9 轮多意图不可单题还原。
- **B 档合成**：mini `redbist_log_proj/` 还原可检测结构：
  - `debug_release.log`（含上述 DEBUG_RELEASE force/release + UVM_ERROR 行，bg/inst_name/RowRed_S*/I_RedLatCom_S*_* 真实值）
  - `redbist_force_release.sv`（force/release task 源码，含硬编码 I24 的 hdl path 拼接 + 正确 bg→inst 映射函数）
  - `bg_inst_map.cfg`（bg→inst 映射表：89→I23, 1312→I23, 1011→I24, 23→I24, 1514→I24）
- **B 隐藏变体** `redbist_log_v2/`（base64 内联 check.py）：同 3 类 bug 但标识符全异（bg→bank_id, inst_name→inst, I23→J23, I24→J24, BankTopX2B→BankGrp, RowRed→RowRdc, RedLatCom→RLatC, DEBUG_RELEASE→DBG_REL, UVM_ERROR→UVM_ERR, force→inj, release→rel, hdl path 段名全异, bg 数字集 {77,1408,990,31,1502}）。
- **交付**：`analyze_force_release_inst_anomaly(project_dir)` 通用代码搜索函数 — os.walk + re 检测 (a) force vs release inst_name 不一致 (b) UVM_ERROR hdl path 硬编码 inst (c) bg→inst 映射规则。输出 `redbist_force_release_diagnosis_report.json` 含函数 source。
- **check 计划（≥12 条 a-l）**：report 结构+函数执行+返回 dict；fn 含 os.walk+re；B 上 3 类 bug 全覆盖；force/release 不一致行号证据；UVM_ERROR hdl path 硬编码 inst 证据；bg→inst 映射规则提取（{89,1312}→I23 vs 其余→I24 的 B 变体版）；反硬编 A 文件名；B 分析证明（≥3 B 标识符）；3-seed 确定性；bugs_found_on_input 非空≥3 且 3 类别；A 上也找出 3 类别；无重复 (category,file)；描述非套话。
- **自验计划**：ref PASS + 3 neg (naive_hardcoded_A/empty_stub/wrong_facts) 全 FAIL + §4.9 三假全 FAIL + negative_selftest + e2e jsonl PASS。k_check=k_rationale≥12。

## 后续轮（msg[71/88/120] 子片）

msg[71]（redbist_common_task 阻塞性 + net119 时序）、msg[88/120]（test2 段未执行 + err_val=0 注错方向）是另外 2 个可独立造题的子片，留作后续 DEBT 候选（verification debug-Q&A）。

## 判定

- parked_reaudit 旧判 "templated-no-deliverable" 按 11-15 新标准**作废**：这是真实用户 debug-Q&A，有内联 log evidence anchor，可写有牙 check()。**REVIVABLE，可造**。
- 本轮因 trace 大（150 msgs/869KB/9 turn）+ 预算紧，仅深读，DEBT 1，下一轮 r674 合成 msg[0] 子片。
