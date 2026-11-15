# trace_deepread: otonl LFGating circuit-find + power-saving mechanism explain

## Trace 来源
- session: `1793082623350_otonl` (snapshot: `/home/e0022089/.snapshot/hourly-new.2026-11-14_1700/.cline/data/sessions/1793082623350_otonl/1793082623350_otonl.messages.json`)
- user: `e0022089`
- host: `hfeg0pkn004` (10.129.2.11)
- match_count: 110
- msgs: 142
- domain: schematic_netlist (netlist-grounded circuit-find + mechanism-explain)

## 用户原话 (verbatim)
- U#0: 「请在DEJOA找到LFGating相关的电路，同时告诉我cm1_fc_LFGating是如何通过gating 省功耗的」
- U#8: 「继续」

## 助手行为 (assistant tool chain)
1. 探索工作区环境 → 搜索 DEJOA 库与 LFGating 相关内容
2. 发现工作区有提取出的电路文件，但未见 DEJOA 本体 → 进一步搜索
3. 读取探索脚本 → 发现是通过 OpenAccess 库路径 `/proj/ddcpb/V0/libs` 解析 `sch.oa` 提取电路
4. 查 `/proj` 下项目 → 仅 `shdc` 可见
5. 穷举检索 `/proj/ddcpb/V0` 全部 20 个库 × 每个 cell 的 `sch.oa` + `symbol.oa`（约 1.5 万文件）
6. `lfgat` 大小写不敏感搜索 → **0 命中**
7. 找到 ddcpb V0 中承担门控职能的电路体系
8. 生成分析报告 `/home/e0022089/Desktop/LFGating_gating_分析报告.md` + 检索脚本 `/home/e0022089/Desktop/find_dejoa.py`

## 关键发现 (gold answer, MSG 141)

### 一、DEJOA 检索结论
- 当前环境**无法访问名为 DEJOA 的库**，可读 OA 数据库中**不存在 "LFGating" 字符串**
- 推断：DEJOA = **ddjoa**（前代 DDR PHY 项目 OA 库），被 ddcpb 原理图引用但未挂载本机
- ddcpb 原理图大量引用老项目符号：ddjoa/dcpa/dcpma/dcpna/mq06a1/JKL/work_jkl
- 实证：`ddcpb_stdcells/latmux2GF01DPmux` 和 `CommonIP_G5analog/AG_lvlshftVcc2VpcsgRstL` 引用 `ddjoa` master

### 二、当前工程 (ddcpb V0) 中找到的 gating 电路
1. **ClkGating16T** (`ddcpb_digital/ClkGating16T`, 注释 zizhaoxi_ClkGating) — 集成时钟门控 ICG:
   - 端口 `Clk/Rst/Out/OutB/InPre`
   - 内部 `latsqGFx1/latrqPFx1` 使能锁存器 + `nand2/nand3/nor2/nand3/aoi21/oai21` 构成
   - 含 CA0/1/2+CS 命令译码、`Write16i/Write32i`、`Read0T~4T`、`ClkWrRd/ClkOther` 选择
   - 被 `WrnWRLatCtrl`(门控 ClkRdAp)、`AutoPreCtrlM5`、`MskRdCmdCtrlM5`(门控 ClkMskRd) 例化
2. **PhClkGat_ut** — 相位时钟门控 (`ClkIn/ClkEn/ClkInD/ClkOut`)，被 `ClkFstGen` 使用
3. **低频/低速门控配置组** (`LowSpeedCtrl`): `cm1_gc_LowSp800En/LowSp1600En/LowSp3200EnN`(800/1600/3200 速率档低速使能)、`cm1_io_SpGrd<2:0>`、`cm1_fc_WCKFlag<1:0>` — 本工程 "LF(Low-Frequency)Gating" 等价实现
4. **命令总线门控**: `cm1_io_CsgatingCaDis`(CS 无效时门控 CA 捕捉通路)，存在于 CMCenterL/R、CMDqL/R、CsPad、ddcpb_top
5. 含 "gating" 的单元共 37 个

### 三、cm1_fc_LFGating 如何通过 gating 省功耗
`cm1_fc_*` 是 cm1 配置寄存器组的**功能控制位**家族（127 个单元使用），训练/MRR 后写入的**准静态**模式位。`cm1_fc_LFGating` = "低频门控使能"，省功耗机理：
1. **静态使能 + 锁存式 ICG，无毛刺**：fc 位作为门控使能送入 ClkGating16T，使能先经电平敏感锁存器在**时钟低电平期间采样**，再经 nand/aoi 逻辑输出 — 保证门控后时钟只在时钟为低时启停，不产生毛刺/窄脉冲（ICG 与直接 AND 门的关键区别）
2. **切断时钟树动态功耗**：低频模式（`cm1_gc_LowSp800En/LowSp1600En` 场景）下高频专属电路时钟域整体关断，P = α·C·V²·f 翻转率 α→0，省该域 30%~70% 动态功耗
3. **下游逻辑静默**：时钟停转后后级译码/移位链不再产生毛刺竞争，消除短路电流和无谓总线充放电
4. **按命令/模式选择性门控**：ClkGating16T 以"有无 Wr/Rd 命令"译码作使能，配合 `cm1_io_CsgatingCaDis` 在 CS 无效空拍门控 CA 捕捉；LFGating 扩展为低频模式整域关断（DQS 振荡器、占空比校正、WCK 计时器等）
5. 省的是**动态功耗**（PHY 数字部分时钟占比极高）；漏电不受影响

### 四、交付文件
- `/home/e0022089/Desktop/LFGating_gating_分析报告.md`
- `/home/e0022089/Desktop/find_dejoa.py`

## Case 设计 (套 #238 v2 netlist-grounded circuit-find + mechanism-explain, 同族 l2vvy + bgrlw)
- **reframe**: circuit-find + mechanism-explain Q&A → netlist-grounded circuit-find + mechanism-explain tool
- **候选工具**: `lfgating_find.py` 读网表 + 问题 → 结构化 JSON
  - gating_analysis{present, gating_type(clock_gating/power_gating/none), latch_based, gating_circuits, enable_signal, clock_signal, cited_identifiers}
  - power_saving_explanation{mechanism(clock_tree_shutdown/power_rail_shutdown/none), dynamic_power_cut, downstream_silence, cited_identifiers}
  - identified_circuits + cited_identifiers + conclusion
- **结构检测**: clock_gating = 锁存器(lat/latch) + nand/aoi 门控逻辑 + 时钟信号; power_gating = PMOS header 大开关管串在电源轨; none = 否
- **source-type**: HSPICE 网表 (focused subset 从 trace 真实电路结构重建, 保留真实标识符)

## data-driven 2×2 + degenerate
- A: ClkGating16T latch-based ICG (clock_gating, latch_based=True, clock_tree_shutdown) — 真实标识符
- B1: clkgate_top latch-based clock gate 中性命名 (en_lat/ngate2/aoi_gate/cfg_lf_en) — clock_gating present, 正向变体
- B2: pwr_gate_top power-gating header switch (PMOS header/cfg_iso_en) — power_gating, mechanism=power_rail_shutdown (DIFFERENT, 测区分)
- B3: buf_chain 平凡反相器链 — no gating, 优雅降级 present=False

## 反硬编码
A 专属标识符 18 个 (ClkGating16T/latsqGFx1/latrqPFx1/cm1_fc_LFGating/cm1_gc_LowSp800En/cm1_gc_LowSp1600En/cm1_io_CsgatingCaDis/ddcpb/ClkWrRd/ClkOther/ClkMskRd/Write16i/Write32i/Read0T/Read4T/DEJOA/ddjoa/InPre) 不得泄入 B 输出; B 用中性命名逼数据驱动。

## check.py 15 条件 (a-o)
a) zip 含 lfgating_find.py
b) py_compile
c) B1 exit0 + 合法 JSON + 7 必需键
d) B1 present==True
e) B1 gating_type=='clock_gating'
f) B1 latch_based==True (ICG 锁存器检测)
g) B1 gating_circuits 非空 + cited grounded 于 B1
h) B1 mechanism=='clock_tree_shutdown' + dynamic_power_cut==True
i) B2 exit0 + 合法 JSON + 全键
j) B2 gating_type=='power_gating' (≠clock_gating, 区分)
k) B2 gating_circuits 非空 + cited grounded 于 B2
l) B3 exit0 + 合法 JSON (优雅降级)
m) B3 present==False (无假阳性)
n) 反硬编码 A 专属不泄入 B
o) 3-seed 确定性 + conclusion 一致性

## 自验
- REF PASS 15/15 ✓
- NEG 3/3 全 FAIL ✓ (neg1→g / neg2→d / neg3→c distinct)
- §4.9 退化 (empty→a / garbage→b / print-only→c) 全 FAIL ✓
- NEG_selftest 6/6 NEG_RC=0 ✓
- k_rationale==k_check==15≥8 ✓
- test field==disk check.py ✓
- 5 attachments 无 hidden 泄漏 ✓
