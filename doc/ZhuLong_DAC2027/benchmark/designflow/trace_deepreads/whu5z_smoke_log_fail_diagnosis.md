# whu5z — smoke.log FAIL root-cause debug-Q&A 深读笔记

**round**: r641 (DEBT 1 — deepread only, synthesis next round r642)
**session**: 1792133360129_whu5z  · **user**: lorikx  · **host**: 10.129.2.13  · **mc**: 22  · **domain**: verification (shard A)
**trace_source**: lorikx / 10.129.2.13 / 1792133360129_whu5z.messages.json (1,018,055 B / 54 msgs / 29 user·25 assistant) — trace EXISTS on remote host, stable, re-fetchable
**model**: glm-5.3-flash · **agent**: lead · **cwd**: /home/lorikx/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC
**ledger**: parked → claimed (r641, 2026-11-16 18:02)
**revival**: from `parked_reaudit_A.tsv` REVIVABLE_QA row (旧 r311 peek parked "sim-failure debug Q&A (smoke.log FAIL)" — 旧 weak 筛子误杀，11-15 令复活)

## 1. 用户真实意图（逐字）

U@0 (prompt): `<user_input mode="act">请在smoke.log文件查找FAIL，并根据仿真文件查找原因，有任何不缺定的可以问我</user_input>`

U@46: `请继续`

用户对 agent ask_question 的回应 (msg52): `方案C：只要这份分析报告，暂不改代码`

**意图判定**: debug-Q&A / 根因诊断，**交付物 = 结构化诊断报告（analysis-only，不改 RTL/TB 代码）**。这是真实用户意图，按 11-15 任务初衷合法可造。C-A debug-Q&A 模板适用（参考 r599 SacapSignalMissingDiagnose-001-v2、r639 VerdiFsdbLoadDiagnose-001）。

## 2. trace 全貌（agent 工具链）

工具调用: read_files×11, search_codebase×3, run_approved_command×6, editor×4, ask_question×1, get_agent_policy_status×1, list_allowed_files×1。agent 无 write 仿真文件、无改 RTL/TB（仅创建临时诊断脚本 `csrc/diag/grep_fail_smoke.py`，独立于仿真流程）。符合 analysis-only 交付。

## 3. 完整诊断结论（来自 trace msg 51/53，已闭环 + 数值验证）

### 3.1 FAIL 清单（smoke.log 8341 行，5 处含 "FAIL"，4 个真实错误）
| 行号 | 内容 | 子测试 |
|---|---|---|
| 8186 | `MEM_FAIL [4658000] addr=5 actual=…X…3c expected=…X…3c`（%h 显示串相同） | 38b (CRSRA=1) |
| 8196 | `MEM_FAIL [4685000] addr=5 actual=X@nib16…96 expected=X@nib17…96` | 38c (CRSRA=2) |
| 8206 | `MEM_FAIL [4712000] addr=5 actual=X@nib16…db expected=X@nib17…db` | 38d (CRSRA=3) |
| 8295 | `MEM_FAIL [4973000] addr=6 actual=X@nib16…fff expected=X@nib17…fff` | 38j (CRSRA 0→2) |
| 8333 | `TESTS FAILED: 4 errors` | 汇总 |

所有 FAIL 集中在 **Test 38: CM=1 2-bit Group CR Repair**；Q 功能读（`PASS Q=…`）与 spare 检查全 PASS。日志中数百条 "Timing violation" 为 TV=1 模式 specify 块预期打印，不计入 errors。

### 3.2 根因：TB 与 DUT 对 CRSRA 引脚语义不一致（位号 vs 组号）

**DUT 侧** (`CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC.v`，自动生成、自洽):
- 头注释 (行 23/91/400): `CM=1 -> SPARE_WIDTH=2, 2-bit group repair (**CRSxA=group index**, pin -1 bit)`、`CRSxA directly indexes 2-bit GROUP (0..NB/2-1)`
- 行 406: `CR_PAIR_SIZE = (CM==1) ? 2 : 1`；`CR_ADDR_WIDTH = clog2(144)-1-1 = 6`（6 bit 寻址 36 个组）
- 写路径 (行 2726/2791): `a_r = crsre_eff ? CRSRA : -1` → `pair_a_r = a_r` —— **引脚值不做换算，直接当组号**。X 落在组 `CRSRA`（mem_R 局部位 `[2·CRSRA+1 : 2·CRSRA]`）

**TB 侧** (`tb_sp_2pram.sv` Test 38, 行 3989/3993/4003/4007/4017/4021):
- 引脚驱动 `cr_config_right(1/2/3)` 把 CRSRA 当 "缺陷**位**号"
- 期望模型 `expected_cr_right_2bit(pat, defect)` 内部 `g = defect/2` —— **期望 X 落在组 `defect/2`**

**结果**: 仅 CRSRA=0 时两者一致 (38a/38e/38j 第一段 MEM_PASS)；CRSRA=1,2,3 时 X 被放在 TB 预期组的两倍位置：

| 子测试 | CRSRA | TB 期望组 | DUT 实际组 | 结果 |
|---|---|---|---|---|
| 38a | 0 | 0 | 0 | MEM_PASS |
| 38b | 1 | 0 | **1** | MEM_FAIL（首个差异位 V[72]=mem_R[0]） |
| 38c | 2 | 1 | **2** | MEM_FAIL |
| 38d | 3 | 1 | **3** | MEM_FAIL |
| 38j | 2 | 1 | **2** | MEM_FAIL |

**38b 为何 %h 显示串相同仍 FAIL**: `check_mem` (tb 行 419-436) 用 `!==` 做 **4 态比较**——TB 期望 `mem_R[3:0]=4'b00xx`（X 在组0），DUT 实际 `4'bxx00`（X 在组1），%h 都显示 `X` 但按位不同。

**为何功能 Q 全 PASS、Tests 9-15 不受影响**: DUT 读路径 (`CRReadDownShift`) 与写路径用同一 `pair_a=CRSRA`，互为逆映射、自洽，端口级功能完全正确；只有 `check_mem` 用层次引用直查 `mem_R/mem_L` 阵列才能暴露差异。Tests 9-15/24/37 只查 Q 和 memoryIO，从不调 `check_mem`。

### 3.3 同一根因附加表征
- TB `CR_AW=8` 位 > DUT `CR_ADDR_WIDTH=6` 位：38k "OOB" 测试发 CRSRA=72（TB 认为超 max 71 非法），但 DUT 端口截断为 `6'b001000=8`（合法组号），DUT 侧无告警、读写照常——TB 的 max-valid 校验 (`NB2_R-1=71`) 也是位号语义。

### 3.4 数值验证（agent msg 47-50，Python 逐位复算）
agent 用 Python 独立复现 TB 模型 (`expected_cr_right_2bit`) 与 DUT 行为 (`CRWriteDownShift`, pair_a=CRSRA)，对全部 7 个用例精确再现 smoke.log 字符串（TB:OK / DUT:OK 全通过），4 个 MEM_FAIL 首个差异位全部指向 "TB 组号=defect/2 vs DUT 组号=CRSRA 原始值"。验证脚本: `/home/lorikx/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC/csrc/diag/grep_fail_smoke.py`。

## 4. 证据资产清单（A 档 trace-embedded，从 trace read_files tool_results 抽取，行号剥离还原）

trace 在 .75 eda_flow workdir 已抽取 20 份 evidence 文件（r641 session, 见下 workdir 路径，可能被回收 → 优先从 remote 10.129.2.13 重抽）。**A 档合成所需关键 excerpt**（按 read_files 调用记录的精确行范围）:

| A 文件 (拟定) | 源路径 (remote 10.129.2.13) | 行范围 | 内容 | 用途 |
|---|---|---|---|---|
| `smoke_fail_region.log` | /home/lorikx/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC/smoke.log | 8168-8341 | Test 38 全段 + 4 MEM_FAIL + `TESTS FAILED: 4 errors` | FAIL 清单 / 行号 / 子测试归属 |
| `smoke_header.log` | 同上 | 1-80 | config (NW=64 NB=144 CM=1 CD=1 CR=1 TV=1 FI=1) + make/vcs 命令 + filelist | 仿真配置上下文 |
| `dut_header.v` | /home/lorikx/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC.v | 1-80 | CM=1 / CRSxA=group index / NB=144 / SPARE_WIDTH 注释 | DUT 语义证据 |
| `dut_cr_core.v` | 同上 | 860-1020 | CR_PAIR_SIZE=(CM==1)?2:1 / CR_ADDR_WIDTH=clog2(144)-1-1=6 / "a = defect group index (CM=1) or bit index (CM!=1)" | DUT 组号语义 |
| `dut_write_path.v` | 同上 | 2700-2800 | `a_r = crsre_eff ? CRSRA : -1` → `pair_a_r = a_r` (行 2726/2791) | DUT 不换算直接当组号 |
| `tb_check_mem.sv` | /home/lorikx/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC/tb_sp_2pram.sv | 300-470 | `check_mem` task (行 419-436) `!==` 4 态比较 `{dut.mem_R[addr], dut.mem_L[addr]}` | 4 态比较机制 |
| `tb_expected_model.sv` | 同上 | 546-620 | `expected_cr_right_2bit(pat, defect)` 内部 `g = defect/2` | TB 位号语义期望模型 |
| `tb_test38.sv` | 同上 | 3966-4135 | Test 38 调用：`cr_config_right(1/2/3)` + `expected_cr_right_2bit` + `check_mem` | TB 驱动 + 期望 + 检查串联 |

(可选辅助: tb 1-120 header, filelist.f 1-30, dut 2230-2290, smoke 994-1060 Test 9 段)

**重抽命令** (next round 在 .75 上):
```
scp -o BatchMode=yes 10.129.2.13:/home/lorikx/.cline/data/sessions/1792133360129_whu5z/1792133360129_whu5z.messages.json ./whu5z.messages.json
# 然后用 read_files tool_result 抽取（query 字段含 path:行范围），或直接 ssh head -c / sed -n 抽源文件
```
注: 源文件路径 `/home/lorikx/CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC/` 在 remote 10.129.2.13 上，应仍存在（2026-10-16 仿真产物，非 /rundata 易蒸发路径）。

## 5. 合成计划（r642 落地）

### 5.1 case 元数据
- **case_id**: `EDA-Eval-DesignFlow-SmokeLogFailDiagnose-001` (C-A debug-Q&A 模板，verification)
- **trace_source**: {user: lorikx, host: 10.129.2.13, session_file: 1792133360129_whu5z.messages.json, match_count: 22, real_task_summary: "在 smoke.log 查找 FAIL 并根据仿真文件定位根因；用户选 analysis-only 方案C，交付诊断报告不改代码"}
- **mode**: design_flow / entry_point: outputs/submit.zip / test: check(deliverable, workdir)
- **prompt**: trace-faithful A 档，用用户原话「请在 smoke.log 文件查找 FAIL，并根据仿真文件查找原因，有任何不缺定的可以问我」+ 项目背景（CXN4HC2PS64X144M1B2C1R1W1BW1RE1_DBC, 64x144 CM=1 dual-PRAM DBC, VCS smoke test）+ 交付物要求（结构化 JSON 诊断报告，不要改 RTL/TB 代码）
- **attachments**: assets/<id>/{task_brief.md, smoke_fail_region.log, smoke_header.log, dut_header.v, dut_cr_core.v, dut_write_path.v, tb_check_mem.sv, tb_expected_model.sv, tb_test38.sv}

### 5.2 交付物
单文件 `smoke_fail_diagnosis_report.json` (zip 内)，结构化 JSON，8 顶层段（参考 r639 VerdiFsdb 报告结构）:
1. `report_overview` (task, project, sim_env, fail_count_summary)
2. `fail_inventory` (5 条 FAIL: 行号/子测试/类型 MEM_FAIL|summary/内容)
3. `root_cause` (主根因: TB-vs-DUT CRSRA 语义不一致; TB=位号 defect/2, DUT=组号 CRSRA; CM=1 2-bit group)
4. `dut_analysis` (CRSxA=group index 注释, CR_PAIR_SIZE, CR_ADDR_WIDTH=6, 写路径 pair_a=CRSRA 不换算, X 落组 CRSRA)
5. `tb_analysis` (cr_config_right 驱动位号, expected_cr_right_2bit g=defect/2, check_mem !== 4 态比较)
6. `fail_mechanism` (为何仅 CRSRA≠0 FAIL, 为何 38b %h 相同仍 FAIL [4 态], 为何 Q 全 PASS [读写自洽逆映射], 为何 Tests 9-15 不受影响 [不调 check_mem])
7. `subsidiary_findings` (CR_AW=8 vs CR_ADDR_WIDTH=6, 38k OOB=72→截断 8, TB max-valid=71 位号语义)
8. `evidence` (≥5 条 {claim, source:"<A文件名>:<行/锚>", token}) + `conclusion` (confidence, summary, user_choice=方案C analysis-only)

### 5.3 check() 结构（k≥8，目标 k=14-16，k_check=k_rationale）
- **structure (a-b, 2)**: zip 内单 json 文件；8 顶层段齐全
- **fail_inventory (c-d, 2)**: 5 FAIL 行号正确 (8186/8196/8206/8295/8333)；4 MEM_FAIL + 1 TESTS FAILED summary 分类正确
- **root_cause (e-f, 2)**: 主根因 = CRSRA 语义 TB(位号/defect/2) vs DUT(组号/CRSRA) 不一致；CM=1 2-bit group repair 上下文
- **dut_analysis (g, 1)**: pair_a=CRSRA 不换算 + CR_ADDR_WIDTH=6 + CRSxA=group index
- **tb_analysis (h, 1)**: expected_cr_right_2bit g=defect/2 + check_mem !== 4 态比较
- **fail_mechanism (i-j, 2)**: 仅 CRSRA≠0 FAIL 的组号错位 (0/1/2/3 → 0/1/2/3 vs 0/0/1/1)；38b 4 态比较 %h 相同仍 FAIL
- **subsidiary (k, 1)**: CR_AW=8 vs CR_ADDR_WIDTH=6 / 38k OOB 截断 / Q 全 PASS 读写自洽（三选二以上）
- **evidence-verification (l, 1)**: ≥5 条 evidence 且每条 source 锚定 A 文件名:行/锚（与 A_FILES 交叉验证，非空泛）
- **B judge-self-check (m, 1)**: 内嵌 `_parse_b` 解析隐藏 B 变体 → B truth；A-report 关键事实与 B truth 在 ≥6 anti-hardcode 维度全异（见 5.4）
- **3-seed (n, 1)**: _parse_b 顺序无关 / evidence+b_files keys shuffle 稳定 / B truth sha256 稳定
- **conclusion (o, 1)**: confidence + summary + user_choice=analysis-only

→ k=15 (a-o)。A_FILES + B_SPEC base64 内联进 check.py（自包含，规避 write_file 转义腐蚀）。

### 5.4 隐藏 B 变体设计（anti-hardcode，≥6 维度全异于 A）
B = 同类根因的**变体 PRAM 配置**，让数值/位置/子测试全异，逼 agent 真诊断非背 A：
- **B 项目**: `CXN2HC8PS32X72M1B2C1R1W1BW1RE1_DBC`（NW=32 NB=72 CM=1，半规模 dual-PRAM）—— 仍是 CM=1 2-bit group repair，但组数 = 72/2 = 36 → 同 CR_ADDR_WIDTH=6（巧合）；改用 NB=72 → 局部位宽不同
- 或更安全: **B = CM=1 但 NB=80**（组数 40，CR_ADDR_WIDTH=clog2(80)-2=5）让组寻址宽度都不同
- **B 子测试集**: Test 38 的 FAIL 出现在 **38c/38d/38e/38k**（CRSRA=2/3/4/5），非 A 的 38b/38c/38d/38j
- **B FAIL 行号**: 改为 B smoke.log 的不同行号（如 9200/9210/9220/9310/9350）
- **B 组号映射**: DUT X 落组 CRSRA（同根因），TB 期望组 defect/2 → B 的错位数值全异（CRSRA=4→TB 期望组2 vs DUT组4）
- **B 4 态证据**: 38c 的 %h 显示串 + 4 态位串全异（B 数据 pattern 不同）
- **B OOB**: TB CR_AW=7 vs DUT CR_ADDR_WIDTH=5，38k OOB 值=40→截断 5
- **B config**: TV=0（非 TV=1）→ 无 Timing violation 噪声，附加区分维度
- **B evidence 文件**: b_smoke_fail_region.log / b_dut_header.v / b_dut_cr_core.v / b_dut_write_path.v / b_tb_check_mem.sv / b_tb_expected_model.sv / b_tb_test38.sv（数值全异，结构同构）

≥7 anti-hardcode 维度: project_name, NB/组数, fail 子测试集, fail 行号, 组号错位数值, 4 态位串, OOB/CR_AW 值, TV 模式。check() 条件 m 验证 ≥6 维度全异。

### 5.5 负样本（reference/<id>/negative/，≥2 + negative_selftest.py，全 FAIL）
- `empty.zip` → 条件 a FAIL
- `no_evidence.zip`（报告无 evidence 段）→ 条件 l FAIL
- `wrong_rootcause.zip`（根因写成 DUT bug / license / timing）→ 条件 e FAIL
- `core_deleted.zip`（root_cause 段空壳）→ 条件 e/f FAIL
- `b_overfit.zip`（hardcode A 数值，B judge 条件 m FAIL）

### 5.6 自验
- ref 解 → check() 15/15 ALL PASS
- 5 neg → 全 FAIL distinct (a/l/e/f/m)
- §4.9 三假 (empty / print-only / core-deleted) 全 FAIL
- e2e: 从 jsonl 抽 test field 独立跑 15/15 PASS
- ledger: whu5z claimed → case (`python3 designflow/trace_ledger.py --shard A mark --session 1792133360129_whu5z --status case --case-id EDA-Eval-DesignFlow-SmokeLogFailDiagnose-001`)
- parked_reaudit whu5z → done

## 6. 注意事项 / 风险
- B 变体数值需自洽（CM=1 2-bit group 语义、defect/2 vs CRSRA 错位、4 态比较）——合成时用 Python 复算 B 的 mem_R 4 态串与 smoke.log 字符串吻合（参考 agent msg 47-50 的数值验证方法），确保 B truth 可机械判定。
- A 文件行号剥离还原（trace read_files 结果带 `  N | ` 前缀，需 strip）；gaps 在共享 stdcell 区不影响诊断证据。
- prompt 须含 "方案C / 只要分析报告 / 不要改 RTL/TB 代码" 约束，否则 agent 可能产修复 patch（偏离用户意图）。
- discuss 配额: 距 r618 已 9 造题轮欠配额（r640 MEMORY 记 8，本轮 r641 +1 = 9），r642 须补发言。
- WAVEVIEW task2 仍等 vision 裁路径。

## 7. .75 eda_flow workdir（r641，证据备份，可能被回收）
`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/shardA_20261116-r641_whu5z-deepread_0`
内含 `whu5z.messages.json` (1MB) + `evidence_r00..r19_*.txt` (20 份抽取) + `bundle.txt` (8 关键 excerpt 合并 54KB)。
**若 workdir 已被回收** → 从 remote 10.129.2.13 重抽（见 §4 命令），trace 稳定。
