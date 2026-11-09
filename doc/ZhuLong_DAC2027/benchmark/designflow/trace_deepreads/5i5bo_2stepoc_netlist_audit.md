# 深读 · 5i5bo (zqzhan @ hfeg0pkn002, mc=155) — 2StepOC netlist audit

## trace
- session: `/home/zqzhan/.cline/data/sessions/1793857124040_5i5bo/1793857124040_5i5bo.messages.json`
- 134 msgs, dir-based; user zqzhan (drcpa DRAM 设计)
- tool footprint: schematic=301 netlist=217 dbGet=114 pyAether=98 hspice=15 spectre=7 (强 D, analog_context+schematic_netlist)

## user turns (goal-stating)
- U0「https://innotron.feishu.cn/docx/...这个文档你可以阅读吗」(飞书文档, 沙盒无外网, 失败)
- U22「我这边保存了相关文件 /ai_sandbox/drcpa/V0/agentdir/zqzhan/pyAether_API.md」(本地 API 文档)
- U32「你是不是可以检查电路的连接关系是否完整」(goal: connectivity check)
- U44「/proj/drcpa/.../2stepOC/Sim1103_HT101_LT010/TT_pvcc1p1_45C/input.sp 你可以先学习下这个仿真pattern文件」
- U48「先继续读 stimulus_2stepOC.sp / measure_2StepOC.sp，把这套"2stepOC"测试的激励和测量点也搞懂」
- U64「我这边最终目的是想让你帮我检查2StepOc功能，看看有没有什么优化的空间…2Step OC功能，就是SA的OC阶段，会分两步打开NCS和PCS，对应也就是SanEn和SapEn信号第一个pulse的上升沿是分步打开的」(核心 goal)
- U124「现在是暂停了吗」(追问, agent 中途停顿)

## agent 行为
- A1-A21: fetch 飞书文档 3 次尝试全失败 (fetch_web_content 禁用 / curl DNS 失败 / python-runner locale 故障)
- A23-A31: 读 pyAether_API.md (1507 行, 12 章 + 2 附录, Aether v2025.03, 640+ 函数)
- A33-A43: RAG 核对 dbSeCheckDesign* 签名 → 写 `check_connectivity.py` (4 层连接完整性检查: dbSeCheckDesignInfo/dbSeCheckCrossView/dbSeHierCheck/dbCheckCV)
- A45-A63: 读 input.sp (115 行, TT_pvcc1p1p1_45C corner, finesim_mode=promd, .include netlist+measure) / stimulus_2stepOC.sp (81 行, 5 组 Vnet 激励: SaNP HT/LT trim 关闭 + 2StepOC 核心控制 + SanEn/SapEn) / measure_2StepOC.sp (2052 行, N=0..255 共 256 个 .meas 窗口, 测 sapenbusec35→sanenbusec35 沿间延迟)
- A65-A133: netlist (netlist.presim) 结构挖掘:
  - `R_TwoStepOCtrimDly` (53069-53140): 4-bit 可编程 RC 延迟单元, binary-weighted 电容梯 (Cthin×1/2/4/8/16), trim bit 选 tap
  - `RasSim_2stepOcCtrl`: 温度选择 HT vs LT 两套 4-bit 延迟码 (2StepOcDly/2StepOcDly2 one-hot)
  - `RasSim_NcCtrl_LPwr` (53939-54007): NCS/PCS 时序控制核心, mux 延迟后 SecEnOn → SanEn/SapEn 分步打开
  - `R_SaCtrol`/`R_SaCtrol_Common_sub`: SA 控制通路, SanEn/SapEn 驱动
  - `mxi2LVx1`/`mxi2CSx2`: 延迟码选择 mux
- A133: 输出 2StepOC 完整链路还原 + 可优化点 (trim 码粒度 / cap 梯权重 / 温度码切换毛刺 / NCS-PCS stagger 余量)

## 关键产物 (真实)
- `check_connectivity.py` (pyAether 连接检查, 4 层)
- netlist 结构分析 (oc_dump.txt / oc_sactrol.txt 抽取的子电路)
- 2StepOC 链路还原报告 (A133 text)

## 私有路径
- /proj/drcpa/V0/... (用户私有 DRAM 仿真目录, 沙盒不可写不可复刻) → B-grade synthesized 自包含

## 合成方向 (B-grade synthesized, analog_context, L2)
- **TwoStepOcNetlistAudit-001**: 给一份合成 SPICE netlist (含 R_TwoStepOCtrimDly 4-bit binary-weighted RC 延迟单元 / RasSim_2stepOcCtrl 温度码选择 / RasSim_NcCtrl_LPwr SanEn-SapEn 分步 mux + .meas 窗口), 写 `analyze_2stepoc.py <netlist.sp> <report.json>` 解析 netlist 提取 2StepOC 延迟链结构事实 → report.json。A(可见) vs 隐藏 B(不同 corner/trim 码/cap 权重/meas 数) 反硬编码。
