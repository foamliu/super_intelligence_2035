# 深读笔记 · xjxxj · DDR6 DSCQA Aging Pre↔Step2 vdbias 一致性检查

> session: `1795165067187_xjxxj.messages.json` · user: `tongfanl` · host: `hfeg0pkn002` (10.129.2.11) / `hfeg0pgn072` (10.129.35.171)
> mc=619 (netlist:527 analog:82 verilog:7) · domain: `schematic_netlist`（D-pure，si.inp = spectre netlist, vdbias = analog .param）
> 台账: claimed r1139 (2026-11-22 20:08) · trace: 570KB / 97 msgs / 51 user / 46 assistant · 工具: editor×15 / run_approved_command×14 / read_files×7
> 深读者: GLM-5.2 / opencode loop shard D · 2026-11-22 20:10

## 一、真实用户意图（从 user 消息提取）

**核心任务**：DDR6 DSCQA Aging 仿真正确性检查（提交长时间仿真前必查）。
1. **Pre↔Step2 文件夹对应**：step2 子目录去掉 `_step2` 后缀与 Pre 一一对应；ODT 对 `ODT_Pre`，普通对 `Pre`。
2. **vdbias 一致性**：每个 step2 `si.inp` 的 `.param pvdias=` 必须等于对应 Pre 的值。
3. **4 种应力类型分组核对**：RDBI / HTOL / LTOL / Normal 10yr / THB，每类下 step2 与 Pre 是否对应。
4. **12 项 CheckPoint**（依序）：COMPRESS force、PostStress009 MBIST、PostStress003 Tssref、Step1→Step2 eageba 链接、.MOSRA simmode/reltotaltime/radegfile、Aging001 CPU 核数、电源文件 Pattern_Power_*.sp、Force 文件、全局网表电源、runscript 完整性、快速验证命令、环境与工具版本。

**用户关键澄清**（U#38/U#41）："Step2 就是使用正常电源，只有 step1 需要使用特殊的电源（如 Pattern_Power_rdbi/hltol/THB）"。
**用户关键澄清**（U#45）：PostStress003 刻意去掉 AG_TSSrefTop（在 finesim_ignore 里，与 Pre 一致）。

## 二、真实脚本（assistant 产出，可作参考解基础）

| 脚本 | 作用 |
|---|---|
| `aging_step2_vs_pre.py` | si.inp strict diff（strip `Created On:` + Aging block），找 pvdias shifts / vdbias→i_dlybias structural swaps / ONLY_STEP2 / ONLY_PRE sets / 空 RDBI dirs |
| `fix_vdbias.py` | 两文件夹接口，`--apply`/`--backup`，修 vdbias 不匹配（修了 3 个真实 bug：off-by-one Aging-block trim / backup rename window / mkstemp→os.replace clobber mode→shutil.copy2+os.chmod） |
| `aging_check_grouped.py` | 按应力类型分组核对 step2↔Pre 对应 |
| `cp12_check.py` | 12 项 CheckPoint 检查 |
| `cp_aggregate.py` / `stat_3650hr.py` / `probe_aging.py` / `cp3_poststress003.py` / `cp7_step1.py` / `locate_tssref.py` / `grep_matrixrun.py` | 各 CheckPoint 专用辅助 |

**真实数据路径**（.75 内网，/rundata 共享盘）：
- `/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_SpfBA_20261106PM_DDR6TOP_PowerFill_V0d9_Rev02_t01_COMPRESS_Aging_Aging001_step2_3650hr_bls/`
- `/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_SpfBA_20261106PM_DDR6TOP_PowerFill_V0d9_Rev02_t01_COMPRESS_Aging_RDBI_1008hr_step2_bls_2/`
- 文件名样例：`primesim.CRG001_Sec47_24_PR...`、`si.inp`

## 三、si.inp 结构（从 trace 推断）

spectre netlist 格式，关键字段：
- `.param pvdias=<值>` ← vdbias，Pre 与 Step2 必须一致
- `Created On: <时间戳>` ← 比对前必须 strip（时间戳不同但语义相同）
- Aging block ← 比对前必须 strip（Step2 独有，正常差异）
- 电源 include：`Pattern_Power_*.sp`（step1 用特殊电源 rdbi/hltol/THB，step2 用正常电源）
- `.MOSRA simmode= / reltotaltime= / radegfile=`
- `finesim_ignore` 列表（如 AG_TSSrefTop）

## 四、Case 设计草图（下轮合成用 · L1 离线 Python）

**case_id**: `EDA-Eval-DesignFlow-AgingVdbiasPreStep2Check-001`
**domain**: schematic_netlist (analog_context)
**真实场景**：用户提交一批 DDR6 DSCQA Aging 仿真前，需要检查 Pre↔Step2 的 vdbias 是否一致 + 文件夹是否对应（按应力类型分组）。

**交付物（outputs/submit.zip）**：
1. `aging_check.py` — 主脚本：输入 Pre 目录 + Step2 目录 + 应力类型，输出 JSON 报告
   - 解析 si.inp，strip `Created On:` + Aging block
   - 提取 `.param pvdias=` 值，比对 Pre vs Step2
   - 检查文件夹对应（step2 去 `_step2` 后缀匹配 Pre，ODT↔ODT_Pre，普通↔Pre）
   - 按 4 应力类型分组（RDBI/HTOL/LTOL/Normal 10yr/THB）报告 aligned/misaligned
   - 输出 JSON: `{stress_type, pairs:[{step2_dir, pre_dir, aligned:bool, pvdias_step2, pvdias_pre, diff_blocks:[]}], summary:{total, aligned, misaligned}}`
2. `report.json` — 在给定输入上跑出的结果

**assets（A 档，SUT 可见）**：
- `assets/<id>/pre/` — 3 个 Pre si.inp（Normal_10yr / RDBI_1008hr / HTOL_500hr），含 `.param pvdias=` + `Created On:` + Aging block + 电源 include
- `assets/<id>/step2/` — 3 个 Step2 si.inp（对应 3 个 Pre，其中 1 个 vdbias 故意不匹配）

**hidden B（不进 SUT 沙箱）**：
- `assets/<id>/hidden/` — 2 个新应力类型对（LTOL_2000hr / THB_3000hr），pvdias 取值与 A 不同，且 1 对有 structural swap（vdbias→i_dlybias），测背题

**A'（anti-hardcode，check.py 内联生成）**：
- 第三组 corner si.inp（Normal_10yr_2），pvdias 取值不同，SUT 不可见，击穿 B-hardcode

**check.py 断言（≥8，k_check=k_rationale）**：
1. zip 内 2 文件齐全（aging_check.py + report.json）
2. aging_check.py py_compile exit 0
3. report.json 合法 JSON，含 stress_type/pairs/summary 顶层键
4. pairs 数量 = 应力类型数 × 对数（与 A 输入一致）
5. A 档：Normal_10yr 对 aligned=true（pvdias 匹配）
6. A 档：RDBI 对 aligned=false（pvdias 故意不匹配，pvdias_step2 ≠ pvdias_pre）
7. A 档：si.inp strip 正确——`Created On:` 不出现在 diff_blocks，Aging block 不算 diff
8. **B 运行**：aging_check.py 在 hidden B 上 exit 0 + 合法 JSON
9. **B**：LTOL 对 pvdias 匹配 aligned=true
10. **B**：THB 对 structural swap 检出（vdbias→i_dlybias），aligned=false 且 diff_blocks 含 structural 标记
11. **B**：B 的 pvdias 值 ≠ A 的（token 结构性不相交，击穿 hardcode）
12. **A' 运行**：aging_check.py 在 A' 上 exit 0 + 信号数/pvdias 匹配 A' oracle（击穿 B-hardcode）
13. 随机化：3 seed 在 B 上随机抽 si.inp 子集，结论一致
14. 文件夹对应规则：step2 去 `_step2` 后缀 = Pre 名，ODT 对 ODT_Pre（断言对应逻辑而非子串）

**3 negatives**：
- `print_only`：aging_check.py 只 print 期望 JSON 不做真实解析 → 断言 8/9/10 FAIL
- `core_deleted`：删 si.inp 解析逻辑只留空壳 → 断言 3/5/6/8/9/10 FAIL
- `hardcode_a`：把 A 的 pvdias 硬编码 → 断言 9/10/11/12 FAIL（B 值不同）

**test_rationale**：`13 条断言：①zip 2 文件齐全 ②py_compile exit0 ③report.json 合法含 3 顶层键 ④pairs 数与 A 输入一致 ⑤Normal_10yr 对 pvdias 匹配 aligned=true ⑥RDBI 对 pvdias 不匹配 aligned=false ⑦si.inp strip 正确 Created On+Aging block 不入 diff ⑧B 运行 exit0+合法JSON ⑨B LTOL 对 pvdias 匹配 aligned=true ⑩B THB 对 structural swap 检出 aligned=false ⑪B pvdias 值≠A 击穿 hardcode ⑫A' 运行匹配 A' oracle 击穿 B-hardcode ⑬3 seed 随机子集结论一致`

## 五、DEBT（下轮交付）

- **本轮**：深读完成 + claim 落台账，**未合成 case**（r1139 预算 ~30min 不足以合格合成 + 自验）。
- **下轮**：按本笔记 §四 草图合成 `EDA-Eval-DesignFlow-AgingVdbiasPreStep2Check-001`，合成 si.inp 样本（compact synthetic，含 .param pvdias / Created On / Aging block / 电源 include），跑齐 §4 质量闸门（8+断言 / hidden B / 3 neg / 随机化 / anti-hardcode A'）。
- **xjxxj 已 claim**，下轮直接 mark case 即可（不重复 claim）。
- 注意：si.inp 样本须 compact（<2KB/个），避免 huge asset；pvdias 取值 A 与 B 必须结构性不同（非换文件名）。
