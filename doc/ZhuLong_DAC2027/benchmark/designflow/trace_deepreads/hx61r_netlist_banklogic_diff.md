# Deepread · 1794191339271_hx61r · jingc @ hfeg0pkn001 · 网表结构 diff (D_BankLogic drgqa→drgqx)

**trace**: `/home/jingc/.cline/data/sessions/1794191339271_hx61r.messages.json` (147 msgs, 595KB, mtime ≥ 2026-11-09 00:00, fresh-window 直扫发现)
**user**: jingc ｜ **host**: hfeg0pkn001 (10.129.2.10) ｜ **kw=9** (hspice/finesim/.SUBCKT/.connect/.measure)
**domain**: spice_sim ｜ **track**: A-faithful ｜ **case**: EDA-Eval-DesignFlow-NetlistDiffBankLogic-001 (k=14)

## 用户原话（逐字，A-faithful 任务说明）
- U#0: 「帮我分析两个网表的不同之处，判断修改了哪些电路」
- U#4: 「网表地址：/rundata/drgqx/V0/simdir/finesim/workdir/jingc/simulation/RAS_edit/」（drgqa_banklogic / drgqx_banklogic）

用户只提需求（分析 diff、判断改了哪些电路），**未给根因/未给修复** → 符合 A-faithful 选轮规则（10-31 令 ①2）。

## 助手工具链
editor×30, read_files×16, run_approved_command×15, run_commands×3, list_allowed_files×3, SandBox_MCP__run_code×2 → 真实 produce-task（非诊断/非 wrong-shard）。
- read_files 读两份网表（MSG8 含两份完整内容：drgqa 496 行、drgqx 494 行）
- editor 写 /home/jingc/compare_netlist.py（解析 .SUBCKT 端口 / XI 实例 / .connect）
- run_approved_command(python-runner) 跑 compare_netlist.py → 结构化 diff 报告
- editor 写 /home/jingc/gen_html.py → 生成 netlist_comparison.html（可视化对比）

## 金标准（用户接受的结果 = compare_netlist.py stdout + HTML 报告核心发现）
**文件**: A=drgqa_banklogic (496 行, lib drgqa_cmos_digital, cell D_BankLogic) ; B=drgqx_banklogic (494 行, lib drgqx_cmos_digital, cell D_BankLogic)

**一、端口差异**:
- 仅 A（删除 30，命名 8）: EqMsaN_B0o, EqN_B0o, Iso_B0o, OcEnN_B0o, OcNcs_B0o, OcPcs_B0o, SanEn2_B0o, SapEn2_B0o (+22 内部总线)
- 仅 B（新增 34，命名 10）: BLEnN_B0o, PreEqN_B0o, STBN_B0o, SanOC_B0o, SanSense_B0o, SapOC_B0o, SapSenseN_B0o, SelRHR, POINTER_SKIP_FLAG, NcDly1st<5:0> (+24 内部总线)

**二、器件实例差异**: A=93, B=94
- 新增 1: `+ XI_switch_4_11 vss! GrEn_SlandB_B0o switch_close`
- 修改 2: XI_R_RasBnkLogic（端口 EqMsaN/EqN/Iso/OcEnN/OcNcs/OcPcs/SanEn2/SapEn2 → BLEnN/...）, XI_Array（model drgqa_Array→drgqx_Array）

**三、.connect 语句差异**:
- 仅 A（删除 23）: EqMsaN(3)+EqN(3)+Iso(3)+OcEnN(3)+OcNcs(3)+OcPcs(3)+SanEn2(2)+SapEn2(3)
- 仅 B（新增 18）: BLEnN(2)+PreEqN(3)+STBN(3)+SanOC(3)+SanSense(2)+SapOC(2)+SapSenseN(3)
- changed = 0

**核心发现 5 类**:
1. SA 控制重构: SanEn2/SapEn2 → OC(失调消除) + Sense(检测) 双相
2. 均衡/预充电简化: EqMsaN+EqN → PreEqN
3. 隔离→位线使能: Iso → BLEnN
4. OC 整合: 独立 OC 端口移到 SA 内部
5. 新增功能: STBN(选通)/SelRHR(RHR 选择)/POINTER_SKIP_FLAG(指针跳过)/NcDly1st<5:0>(延时调整)

## 资产获取
- 原始 /rundata/drgqx/... 路径对 e0031982 权限拒绝（pkn001 + .75 均拒绝）
- 从 trace MSG8（read_files tool_result）重建两份完整网表 → 与金标准行数(496/494)/.SUBCKT/.ENDS 完全一致
- A 档资产用**忠实缩减网表**（保留真实端口名/真实 .connect 链/真实器件名，counts 8/10/23/18 与金标准一致），遵循 NetlistStructDiff-001(faithful) 既有口径（小网表，非 43KB 全量专有网表）

## case 设计
- 可见 A: netlist_A1.sp(drgqa)/netlist_A2.sp(drgqx)，diff = 8 删/10 增端口, +XI_switch_4_11, XI_R_RasBnkLogic+XI_Array 改, .connect 删 23 增 18
- 隐藏 B（cross-input guard，2 对）:
  - B1 = ClkBuf: 1 删/1 增端口, +XI_sw, XI_buf 改, .connect 删1/增2/改1
  - B2 = DiffAmp: 1 删/2 增端口, +XI_bias, XI_diff+XI_load 改, .connect 删1/增2/改1
  - B1/B2 ground truth 不同（PORTS_ADDED 1 vs 2, DEVICES_MODIFIED 1 vs 2）→ 反硬编码
- check.py: 14 条独立断言(a-n)，subprocess 真跑候选于 B1+B2+反序B2，§4.9 三假(空壳/print期望/删核心) + 2 naive 全 FAIL (NEG_RC=0)
- L1（离线 Python 解析真实 FineSim 网表，无 EDA 工具需真跑；subprocess 候选 = §4.2 真跑候选）
