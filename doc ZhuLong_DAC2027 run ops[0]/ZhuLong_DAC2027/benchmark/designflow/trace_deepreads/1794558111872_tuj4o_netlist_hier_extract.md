# 深读笔记 · 1794558111872_tuj4o · netlist hierarchical module extract

- trace: `1794558111872_tuj4o` / e04201 @ hfeg0pkn002 / mc=41
- keywords: netlist:236;verilog:61;cmos:19;analog:6;aether:4;schematic:3;pyaether:3;pex:2
- domain: **schematic_netlist**
- msgs: 47 / 3 substantive user turns (act mode)
- 原始 netlist: `/proj/ddjoc/V0/simdir/verilog/PTE/e0014408/verilog.lpddr5.ddjoc.avc_finial/netlist/V0_LP5TOP_2026Apr10.095011/netlist` (~102MB, 4919 module defs) — **私有不可复现**

## 3 个用户轮（逐字原文）
- U#0: 「读取netlis文件.../netlist，并提取TOP.Chip.I_Channel.I_ChanMid.I_Controller这个模块，另存为新的文件ddjocgpf」
- U#27: 「分析这个模块.I_Controller.I_AutoPreCtrlM5_176的功能」
- U#37: 「WrApLogicM5v2这个模块的功能是什么」

## assistant 工具链 + 关键产物
- 写 Python 脚本解析 Verilog 网表（`extract_module.py` / `analyze_autopre.py` / `extract_any.py`），用 `run_approved_command` (python-runner profile) 真跑
- **关键洞察（核心难点）**：netlist 中**不存在**名为 `I_Controller` 的 module —— `TOP.Chip.I_Channel.I_ChanMid.I_Controller` 是**实例层级路径**（每段都是实例名），需沿实例层次追踪：`LP5TOP` (top) → instance `I_Channel` type `Channel` → instance `I_ChanMid` type `ChanMid` → instance `I_Controller` type **`ControllerM5`**（叶子模块类型）
- 产出 1: 提取 `module ControllerM5`（行 247923–252109, 4187 行, 190KB）→ `/home/e04201/ddjocgpf`
- 产出 2: 定位 `I_AutoPreCtrlM5_176` 实例（在 ControllerM5 内行 4074）→ type `AutoPreCtrlM5`（190 行）+ 功能分析（自动预充电控制器）
- 产出 3: 提取 `module WrApLogicM5v2`（245142–245385, 244 行）+ 功能分析（写自动预充电 bank 地址延迟 + one-hot 译码）

## 金标准（trace 末用户隐含接受）
- 3 轮全 act 模式无 reject，assistant 完整交付提取文件 + 层次追踪 + 功能分析
- 核心能力 = **实例层次路径 → 叶子模块类型解析 + module 定义提取 + 功能解读**

## 合成方案（B 档 synthesized reframe, L2 真跑候选脚本）
- 原 102MB 网表私有不可复现 → 合成 Verilog 网表 A/B（嵌套 module 层次 + decoy 模块 + 实例名 ≠ 类型名 陷阱）
- 候选写 `extract_module.py` CLI：解析网表 → 沿实例层次路径追踪 → 解析叶子模块类型 → 提取完整 module 定义到输出文件 → 产 report.json（leaf_module / hierarchy_chain / extracted_file / total_modules）
- check.py 真跑候选脚本在隐藏 B 上判分（B 不同名称 + 不同层次深度反硬编码）；oracle = check.py 内独立 Verilog parser 重算
- B2 = 路径中含不存在实例 → 验优雅报错
- case_id: `EDA-Eval-DesignFlow-NetlistHierExtract-001`
