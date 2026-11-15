# 深读笔记: roznq — FineSim .md0 指标定位 + 多工艺角缺失诊断

**trace_source**: user=e0024852, host=hfeg0pkn002, session=1793589408208_roznq.messages.json, mc=553, domain=spice_sim
**trace 路径**: .75 → hfeg0pkn002:/home/e0024852/.cline/data/sessions/1793589408208_roznq/1793589408208_roznq.messages.json (632KB, 52 msgs, 32 user / 20 assistant)
**旧判定**: parked "SRAM bitcell PEX metric diagnostic (peeked 01:45 round); fuzzy deliverable reject" (2026-11-10)
**新判定**: 可造 (r618 reaudit: debug-Q&A 真实用户意图, 旧规则误杀)

## 真实用户意图 (3 轮)

1. **U#0** (主意图): "in /proj/lacaa/V0/simdir/finesim/workdir/e0012583/simulation/hd_CH252_bitcell/hd_CH252_bitcell_post_rev06/sim_result_pex_rev06_model_rev04_presim which one can be used for Analyze metrics such as Iread, Ilead, and SNM. and how to"
   → 哪个 FineSim 输出文件含 Iread/Ileak/SNM 指标 + 怎么解析
2. **U#16**: "tell me in chinese" → 用中文回答
3. **U#18**: "it means md0 is what i need and give me the code tell me in chinese" → 确认 .md0 + 要解析代码
4. **U#21**: "in this fold, where has other ff ss fs and sf corner" → FF/SS/FS/SF 工艺角结果在哪

## 助手诊断链 (真实工具调用)

1. `list_allowed_files` + `get_agent_policy_status` 探索 sim_result 目录
2. `read_files` 读 sim_bitcell_pvt_analyze.py / python.py / stimulus.sp
3. `read_files` 读 .sw0 / .log / .md0 → 确认 .md0 含 measure 列 (iread/ileak/iwrite/wnm_1/wnm_2)
4. 提供 `read_md0.py` Python 解析脚本
5. `list_allowed_files` 探索 simulation 目录 + 模型库路径
6. `read_files` 读 35H_DBCFS_Model_SRAM_v0d1_Rev04.lib → 找 *_sram_dbc / *_sram_fs 工艺角 section
7. 读 stimulus.sp 第 66-67 行: `.LIB ... tt_sram_dbc` + `pre_sim_dbc`, **无 .alter 块**
8. 结论: 只有 TT 工艺角被仿真, FF/SS/FS/SF 缺失因为 stimulus 只加载 tt_sram_dbc 且无 .alter 扫描

## 根因链 (可操作化)

- **指标源文件** = `.md0` (FineSim measure dump), 不是 .log/.sw0/.pd0
- **.MEASURE DC 语句** 在 stimulus.sp 中定义: Iread FIND I(V_READ) AT=VVDD/2, Ileak FIND I(V_STANDBY), Iwrite FIND I(V_WRITE), WNM_1/WNM_2 TRIG/TARG
- **加载工艺角** = tt_sram_dbc (从 .LIB 语句解析)
- **.alter 块数** = 0 (stimulus 无 .alter) → 单角运行, .md0 仅 1 行 alter#=1
- **可用工艺角** (model .lib 定义) = tt/ff/ss/fs/sf_sram_dbc (DBC 族) + tt/ff/ss_sram_fs (FS 族)
- **缺失工艺角** = ff/ss/fs/sf_sram_dbc (同族未加载, 4 个)
- **修复建议** = 加 .alter 块, 每块 .LIB 加载一个缺失工艺角, 重跑后 .md0 含 N 行 (每角 1 行)

## 合成决策

- **A 档 trace-faithful**: 保留真实用户名 e0024852 / 路径结构 / bitcell 名 hd_CH252 / 工艺角命名 tt_sram_dbc / .MEASURE DC 语法 / VVDD=0.75 / TEMP=25
- **真实文件未完整落盘** (.md0/.sp/.lib 内容在 trace 中被 assistant 读取但未全文转储), 按 trace 描述的结构忠实合成证据文件, 保留真实键名/格式/机制名
- **B 档 synthesized**: hidden B 用不同 bitcell (hc_CH318, FS 族) / 不同工艺角 (sf_sram_fs) / 不同噪声容限 (SNM vs WNM) / 不同 VVDD/TEMP / 不同 .lib 角集 → cross-input guard
- **新形态**: reaudit「FineSim .md0 指标定位 + 多工艺角缺失诊断」操作化首例 + .md0 列解析首例 + .MEASURE DC 语句提取首例 + .alter 缺失→单角运行根因首例 + 同族工艺角缺口计算首例

## case 产出

- case_id: EDA-Eval-DesignFlow-FineSimMetricCornerDiag-001
- domain: spice_sim, layer: L1 (离线 Python 解析附件产报告)
- 类型: debug-Q&A 根因诊断
- k=13 断言 (a-m), check.py 自包含 oracle
- 自验: ref 13/13 PASS + 4 negs FAIL (naive hardcode 仅 fail@m cross-input guard / always_empty fail@[b-l] / print_only fail@[a,b] / core_deleted fail@[j,k]) + §4.9 degenerate 全 FAIL + negative_selftest ALL GREEN
