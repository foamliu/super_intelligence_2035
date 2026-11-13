# Deepread: sid 1794473178282_cg2xj — SPICE 电容行筛选 (schematic_netlist)

## Trace meta
- **session**: 1794473178282_cg2xj
- **user**: byliu  · **host**: hfeg0pkn002 (10.129.2.11)
- **mc**: 20  · **keywords**: netlist:27;analog:10;.gds:2
- **size**: 133721 bytes / 40 msgs (NTURNS: 7 user turns, many repeated)
- **scan src**: ssh_eda_search_20261113_131349/summary.tsv
- **path**: /home/byliu/.cline/data/sessions/1794473178282_cg2xj/1794473178282_cg2xj.messages.json
- **source file (real)**: /rundata/commonIP/v1/lp5x/v0/simdir/anasim/byliu/DDGOA/PDN_SIM/Chip_Power_Model_SubCircuit_1109_new.sp.inc (5927 lines, read-only, owner byliu → 不可被 e0031982 读取)

## 用户意图（逐字）
- USER#0-6 (重复 7 次): 「帮我把 Chip_Power_Model_SubCircuit_1109_new.sp.inc 里同一行包含C_与-10，或者C_与-11，或者C_与-12,并把这些加粗显示在原文件中」
- USER#26 (vdiv 变体): 「同时也许要包括vdiv,帮我把这些筛选出来放到一个txt文件里」→ 16 行命中
- USER#34 (最终任务): 「帮我把这些筛选出来放到一个txt文件里」(去掉 vdiv) → 966 行命中

## 助手工具链
1. read_files (1-60行) → 识别 SPICE 网表结构 `C_x_y <n1> <n2> <value>`
2. editor 写 find_cmatch.py → run → stdout 含全部 966 命中行 (res_18, 47KB)
3. editor 写 make_bold_copy.py (ANSI bold) → run → bold 副本 (因原文件只读)
4. editor 写 filter_vdiv.py → run → 16 行 vdiv 命中 (res_30)
5. editor 写 filter_C.py → run → 966 行 C_+-10/-11/-12 命中 (res_38)

## 金标准（实测）
- 文件总行数: 5927
- 含 C_ 的行: 1577
- 含 C_ 且含 (-10/-11/-12) 任一: **966** (主任务)
- 含 C_ 且含 vdiv 且含 (-10/-11/-12): **16** (vdiv 变体)
- 输出格式: `lineno | C_x_y n1 n2 value` (如 `77 | C_6_1 n43 vss<9> 8.41637270328e-10`)
- 匹配语义: **子串匹配** (`any(t in body for t in targets)`)，故 `e-12` 命中 `-12`，`-110` 命中 `-10`

## 合成计划 (case: EDA-Eval-DesignFlow-SpiceCapMatchFilter-001)
- **domain**: schematic_netlist (D) · **grade**: B · **difficulty**: L1 (纯 stdlib 离线)
- **SUT 交付**: `spice_cap_filter.py`，接受 `<输入spice> <输出txt>`，筛选 C_ + (-10/-11/-12)，输出 `行号 | 原行`
- **asset A (visible)**: A_Chip_Power_Model_sample.sp.inc (45行, 29命中) — 真实 966 行子集 + 真实结构填充 + 4 陷阱行
- **hidden B**: B_Chip_Power_Model_hidden.sp.inc (39行, 23命中) — vdiv 16 行 + 填充 + 陷阱 (与 A 真实行不相交)
- **hidden C**: C_Chip_Power_Model_alt.sp.inc (35行, 20命中) — 另 14 行 + 填充 + 陷阱 (反硬编码泛化测试)
- **陷阱行**: (1) R_ 行含 -11 但无 C_ → 不命中; (2) C_ 行含 -13 不命中; (3) C_ 行含 -110 → 命中(-10子串); (4) X 行含 -10 无 C_ → 不命中
- **check.py**: 14 条件 a-n (zip合法/脚本存在/运行exit0/输出非空/行数=gold/格式合法/行号递增在范围/内容满足条件/内容=B原行/集合=gold_B/反硬编码C=gold_C/反硬编码A标记/行序不变性/空输入鲁棒)
- **3 negatives**: empty(空壳) / print_only(打印金标准串) / hardcode_a(硬编码A) → ALL FAIL
- **§4.9 三假**: empty/print_only/core_removed → ALL FAIL
- **自验**: ref PASS 14/14, 3 neg + core_removed ALL FAIL, negative_selftest 4/4 OK
- **k_rationale = k_check = 14 ≥ 8 ✓**

## 命中判定
- clean produce-task ✓ (单轮明确需求 + 产脚本 + 产 txt + 用户接受 966 行结果)
- 真实 trace ✓ (cg2xj, byliu, 966 行实测)
- D 域 ✓ (schematic_netlist, SPICE 网表解析)
- L1 ✓ (纯 stdlib 离线 Python)
