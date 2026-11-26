# Deepread: lxord — LPDDR6 ecc.run Link-ECC 规范符合性分析

- session: `1794472682549_lxord` (eva1li@10.129.2.14, mc=10, 215KB/53msgs, mtime Nov 12)
- ssh ALIVE (r723 验证): `/home/eva1li/.cline/data/sessions/1794472682549_lxord/1794472682549_lxord.messages.json`
- ledger: shard A, status=claimed, domain=verification (r723 claim)
- 真实 ecc.run 路径: `/rundata/dejoa/V0/simdir/verilog/eva/eva_test/lpddr6_dejoa/dejoa/Regressions/ecc.run` — **e0031982 from .75 无读权限 (Permission denied)**, 故 A 档资产需从 trace 引文忠实重建（结构真实, 同 r714/r720 B-档合成模式）。
- KG 路径: `/apps/imctf/cad/ai/agent/system_config/v0.2.0/skills/lpddr6-jedec-kg/_internal/instances/` (可读, colinxu:cad)

## 一、用户真实意图（原话）

U#1 (skill preamble): 加载 `lpddr6-jedec-kg` skill (LPDDR6 JEDEC 知识图谱查询: 8 YAML — commands/mode_registers/dramconfigs/timing_parameters/states/rules/procedures/counters)。
U#2 (核心任务): 「[lpddr6-jedec-kg] 分析一下 @/rundata/dejoa/.../Regressions/ecc.run 里的流程符合 link ecc 的规范吗？将结果保存到 @/rundata/.../ecc_run_analysis」
U#3 (重申, 因 U#2 后 agent 已给口头结论): 同 U#2，明确要求**保存到文件**。

**真实交付意图** = 用 lpddr6-jedec-kg skill 查询 JEDEC KG, 核对 ecc.run 回归脚本里的 Link ECC 流程是否符合规范, 产出**结构化符合性分析报告**并保存到文件。这是 **analysis-Q&A + retrieval** 任务（11-15 任务初衷下合法）。

## 二、agent 流水线（实际做了什么）

1. `read_files` 读 ecc.run (截断) → `skills` 调 lpddr6-jedec-kg → 读 docs/LPDDR6.md
2. `list_allowed_files` 探 KG 实例目录 → 发现实例在 `v0.2.0/` 而非 `current/`
3. `editor` 写 `query_linkecc.py` (查 mode_registers 含 ECC/EDC 的 MR) → `run_approved_command` (python-runner) 跑 → 发现 MR 名是 "MR23" 非 "WECC"，改用 name 前缀匹配
4. `editor` 改 `query_linkecc.py` 加 `show_mr` + 查 MR23/MR97 detail + rules 里 Link ECC ForbiddenRules → 跑 → 拿到 MR23(OP0=WECC/OP1=WEDC/OP2=RECC-REDC, MA=17H, Table121) + MR97(OP1/OP2/OP3 故障位 read-only, MA=61H, Table228)
5. `editor` 写 `query_linkecc2.py` 查 SetExclusionRules 含 ECC/EDC → 跑 → 拿到 3 条排除规则 (见 §三)
6. `log_usage.py` 埋点失败 (PermissionError: /apps/.../current/ 不可写, 环境限制非数据问题)
7. 给出口头结论 (MSG 33)
8. U#3 要求存文件 → 尝试 `editor` 写 /rundata/... → policy 拒 (writableRoot 仅 /home/eva1li) → 改写 `/home/eva1li/ecc_run_analysis` (成功) → `read_files` 校验 → 告知用户 policy 限制 + cp 迁移指引

## 三、KG ground truth（r724 check.py 的真值来源，已 ssh 核实）

**MR23 (MA=17H, Table 121, subchannel, is_fsp=true)**:
- OP[0] Write Link ECC Mode, write_only, default 0B
- OP[1] Write Link EDC Mode, write_only, default 0B
- OP[2] RECC/REDC (Read Link ECC/EDC Mode), write_only, default 0B
- OP[4] CS ... (非 ECC, 略)

**MR97 (MA=61H, Table 228, subchannel, is_fsp=false)** — 全 read_only:
- OP[0] PRAC limit exceeded
- OP[1] Write Link ECC MBE Fault / Write Link EDC SBE/MBE Fault
- OP[2] Write Link ECC SBE Correction Attempted
- OP[3] On-die ECC MBE Fault

**SetExclusionRules (3 条, 已 ssh 核实)**:
1. `rule-exclusion-write_link_ecc-write_link_edc` → excluded_states=[state-mr23-op0-write_link_ecc-enabled, state-mr23-op1-write_link_edc-enabled]  **(写 ECC ⊥ 写 EDC, MR23 OP0 与 OP1 不可同置 1B)**
2. `rule-exclusion-write_link_ecc_edc-disabled-mr97_op1_write_link_ecc_mbe_or_edc_fault_detected` → [state-write_link_ecc_edc-disabled, state-mr97-op1-...-detected]  **(WECC/WEDC 关闭时 MR97 OP1 不应有故障)**
3. `rule-exclusion-write_link_ecc_edc-disabled-mr97_op2_write_link_ecc_sbe_correction_detected` → [state-write_link_ecc_edc-disabled, state-mr97-op2-...-detected]  **(WECC/WEDC 关闭时 MR97 OP2 不应有纠错)**

**ForbiddenRules (切换态, agent 引用未完整 ssh 核实, r724 补)**: `rule-forbidden-link_ecc_edc-switch-{write_link_ecc|write_link_edc|read_link_ecc_edc}-during-{all_banks_not_precharged|read_burst_output_valid|write_burst...}` → MR23 切换必须 Idle 且 DQ 空闲。

## 四、ecc.run 结构（从 trace 引文重建, r724 的 A 资产）

- 5 组 MR23 配置组合 `w=0..4`（每轮 `Deselectn(50)` 收尾回 Idle 后写 MR23）:
  - w=0: WECC_EN + RECCREDC_DIS (仅写 Link ECC)
  - w=1: WECC_DIS + RECCREDC_EN (仅读 Link ECC/EDC)
  - w=2: WECC_EN + RECCREDC_EN (写 ECC + 读 ECC/EDC 同开)
  - w=3: WEDC_EN (op_mark=OP_WEDC_BITS|OP_WECC_BITS, 顺带清 OP0) + RECCREDC_DIS (仅写 Link EDC)
  - w=4: WEDC_EN (op_mark 含 WECC 位) + RECCREDC_EN (写 EDC + 读 ECC/EDC)
- L22-25: `randwrerr_en=1` / `randwrdqerr=1` 错误注入在全部 5 模式**全局开启且不复位**
- `LoadModeWLRL(.mrchange(0))` 不刷 WLRL
- 宏映射: MA_WECC→MR23 OP0, MA_WEDC→MR23 OP1, MA_RECCREDC→MR23 OP2, 故障→MR97

## 五、agent 报告结论（r724 check.py 须能区分的真伪判定）

**符合项 ✅ (3)**:
1. MR 字段映射正确 (MA_WECC→MR23 OP0, MA_WEDC→MR23 OP1, MA_RECCREDC→MR23 OP2, 故障→MR97; Table121/228)
2. 写 ECC ⊥ 写 EDC 互斥合规 (w=3/4 op_mark 清 OP0, 无同开)
3. 切换态合规 (Deselectn(50) 回 Idle 后写 MR23)

**合规风险 ⚠️ (1)**:
4. 错误注入 (randwrerr_en=1) 在 w=1 (WECC/WEDC 关闭) 仍开启 → 若该窗口 MR97 OP1/OP2 置位则违反排除规则 2/3。建议注入收敛到 WECC/WEDC 开启窗口 (w=0/2/3/4)。

**覆盖盲点 (2, 非硬违规)**:
5. MR97 未读回断言 (只写 MR23, 未 MRR(MR97) 断言 OP1/OP2/OP3)
6. ECC_0/ECC_1 引脚侧行为未在流程显式体现

**时序提醒**: RL 等参数依赖 read_link_ecc_edc 开/关, LoadModeWLRL(.mrchange(0)) 不刷 WLRL, 需确认 w=0/3 vs w=1/2/4 的 RL 刷新。

## 六、r724 合成计划（produce-task 化, k≥8）

**case_id**: `EDA-Eval-DesignFlow-EccLinkConfAnalyze-001` (verification, A-faithful analysis-Q&A)

**通用工具**: `analyze_linkecc_conformance.py <ecc_run_file> <kg_dir> <output_report.json>` — 解析 .run 的 LoadMode(MR23,...) 调用序列 + 读 KG (mode_registers.yaml + rules.yaml) + 跑 4 类符合性检查 (MR 字段映射 / 互斥 / 切换态 Idle / 错误注入窗口 vs WECC-WEDC 状态) + 输出结构化 JSON 报告 (mr_mapping, exclusion_check, switch_check, injection_risk, blindspots, timing_note, overall_verdict)。

**A 档 (SUT 可见, 忠实重建)**:
- `assets/<id>/ecc_run_A.run` — 5 组配置 w=0..4 + Deselectn(50) + 全局 randwrerr_en=1 (上述 §四 结构, ~40 行)
- `assets/<id>/kg_A/mode_registers.yaml` — MR23 + MR97 (上述 §三, ~50 行)
- `assets/<id>/kg_A/rules.yaml` — 3 条 SetExclusionRule + 切换态 ForbiddenRule (上述 §三, ~40 行)
- prompt: 用户原话 (U#2 verbatim) + 真实路径

**B 档 (hidden, 不进 SUT 沙箱, check.py 内联独立 ground truth)**:
- ecc_run_B.run: **不同**配置 (e.g. 7 组, 含 1 组**故意互斥违规** OP0=1B+OP1=1B 同开; 含 1 组**缺 Deselectn** 直接写 MR23; 含 1 组 w=WECC_DIS 但注入关闭=合规)
- kg_B: **不同** MR 编号 (e.g. MR31/MR105) + 不同排除规则 (e.g. OP0⊥OP2 而非 OP0⊥OP1) + 不同 Table 溯源
- check.py 内联 `_build_b_run` + `_build_b_kg` + `_derive_b_truth` (独立重解析 B 跑出真值), 与 SUT 脚本输出比对

**check.py ≥8 断言 (a-?) 初拟**:
① zip 含可编译 analyze_linkecc_conformance.py (>200B)
② [B] exit0 + 合法 JSON + 顶层 6 段齐 (mr_mapping/exclusion/switch/injection/blindspots/timing/verdict)
③ [B] mr_mapping: 每个 MR 宏→正确 MR 编号+OP+function+Table 溯源 (反硬编码 A 的 MR23/MR97)
④ [B] exclusion_check: 检出 B 的故意互斥违规组 (OP0⊥OP1 同开), 标 violation (反漏报)
⑤ [B] exclusion_check: 合规组标 conform (反全标违规)
⑥ [B] switch_check: 检出 B 缺 Deselectn 的组为 violation (反漏报)
⑦ [B] injection_risk: WECC/WEDC 关闭窗口注入开启→标 risk (反漏报); 注入关闭窗口→无 risk (反误报)
⑧ [B] overall_verdict: 含违规时 verdict=non_conformant, 全合规时=conformant (反永远 conformant)
⑨ 反硬编码 A: B 输出无 MR23/MR97/MA_WECC/17H/61H/Table121/Table228 等 A 专属字面量
⑩ 空输入探针: 空 .run exit0 + verdict=conformant + 0 检查项 (反 print-expected)
⑪ [B] MR function 字段名 (Write Link ECC/EDC Mode 等) 用 B kg_B 的实际 function 串 (反套 A 字面)
⑫ [B] 3-seed 顺序稳定 (排序后 sha256 一致, 反随机)

**negatives (≥3)**: neg_empty (空脚本→①fail), neg_print_expected (硬编码 A summary→③/⑨ fail), neg_core_deleted (删互斥检查→④ fail), neg_no_switch_check (删切换检查→⑥ fail)。
**§4.9 三假提交**: fake_empty=neg_empty, fake_print_only=neg_print_expected, fake_core_deleted=neg_core_deleted。
**self-verify**: reference_submit.zip 跑 check.py PASS(12/12) + negatives 全 FAIL + negative_selftest OK + e2e(jsonl 内 test 字段提取跑 check) PASS 参考 + FAIL 负样本。

## 七、选料判定 & 域归属

- A-domain (verification): LPDDR6 JEDEC 规范符合性分析 = 验证域。verilog:11 keyword 偏低但任务实质是 verification conformance (KG 规则核对), 非 spice/layout。
- 11-15 任务初衷: analysis-Q&A + retrieval 合法 (非 weak)。
- 真实 trace 溯源: user=eva1li, session_file=1794472682549_lxord.messages.json, real_task_summary=见 §一。
- r712 已有 eva1li IrunWarnClassify (irun 日志 *W 警告分类, verification) — 不同 session 不同任务, 非重复。

## 八、r723 状态

- 本轮 = deepread + claim (DEBT:1, 合成留 r724)。理由: conformance-analysis case 需 KG YAML A/B + reference conformance 脚本 + check.py ≥8 断言 + negatives + fakes + 自验, r723 预算 (~20min 剩余) 不足以承担 full pipeline 不推 incomplete case 入 jsonl (§4.6 硬闸门)。
- r724 优先: 按 §六 计划全流水合成 EccLinkConfAnalyze-001。
