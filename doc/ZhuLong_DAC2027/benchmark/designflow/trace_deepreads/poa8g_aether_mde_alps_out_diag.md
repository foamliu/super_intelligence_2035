# Deepread — poa8g · Aether MDE alps.out 缺失根因诊断

## trace 来源
- session: `1793192893935_poa8g` (subdir `1793192893935_poa8g/1793192893935_poa8g.messages.json`)
- user: yixiaow @ hfeg0pkn002 (10.129.2.11)
- mc: 112 · keywords: aether:1747; schematic:404; netlist:332; mixed-signal:125; analog:103; virtuoso:72; spectre:65; cellview:46
- ledger 历史：r537 peek REJECT (Q&A/sim/run-existing/done)；2026-11-15 reaudit 后 debug-Q&A/env-config 合法 → r849 revival via mark --force（跨 B shard parked wrong-domain 已订正为 C physical_verify）

## 真实任务
47 msgs / 2 真实用户轮（U#0「Aether」单字开场触发 aether-tool-qa skill；U#3 核心问句）。

**U#3 逐字**：「Aether MDE platform 报alps。out 不存在是什么原因。」

助手走 aether-tool-qa skill → search_codebase + read_files 多个 references (part_VI/VIII_Mixed-signal_Design_Environment.md, part_XIII_FAQ.md, aether_tool_qa.md) → 在 #46 给出 free-text 根因诊断 prose（2200 字）。

## gold 诊断 (#46) 结构
- 背景：Aether MDE 集成 Alps SPICE 仿真器；alps.out 是仿真器标准输出/结果文件
- 8 条可能原因 + 排查步骤：
  1. 仿真未能成功运行（最常见）— 查 Run Summary / Show Log File，看 sim err / netlist err 状态码
  2. 网表生成失败（Netlisting Failed）— netlist err 状态码；schematic 未连接节点/悬空引脚/器件参数错/层次引用缺失；Check & Save 修复
  3. 仿真选项未正确配置输出保存 — Outputs 面板勾选 Save + 设输出信号 v(net)/i(port)
  4. 仿真工作目录问题 — Run Summary 找结果目录，检查存在+写权限；右键 Results → Open Terminal
  5. ALPS 仿真器配置/路径问题 — Simulator Options 中 ALPS 路径指向安装位置
  6. License 问题 — ALPS 需有效 license，无 license 直接失败不生成输出
  7. 模型文件缺失或配置错误 — Model Setup / Corner Setup 模型文件路径不正确或不存在
  8. 磁盘空间不足 — 输出目录所在分区已满，ALPS 无法写入
- 7 步排查操作表（Run Summary → Log File → SP File → Outputs 设置 → Model Setup → Netlist View List → 重新 Netlist And Run）
- 快速检查清单（6 项 checkbox）

## 判分牙评估
A 档 gold = free-text 诊断 prose（依赖 live references 文档不可达，无 ≥8 独立硬断言牙）→ 档 B reframe 为离线纯 stdlib 根因诊断器 `alps_out_diag.py`，输入 MDE 仿真上下文 JSON（error_message/run_status/log_error_codes/outputs_save_enabled/outputs_signals/model_file_path/model_file_exists/license_available/disk_free_gb/simulator_path/simulator_exists/netlist_view/schematic_has_errors/output_dir_writable），按 8 条规则识别 identified_causes，按优先级选 primary_cause，输出结构化 JSON + recommended_steps + checklist。

## 意图审计
**keep** — yixiaow 真实意图（诊断 Aether MDE alps.out 不存在的根因）完全保留，reframe 是 grounding 非加难。2026-11-15 reaudit 后 debug-Q&A/env-config 合法第 N 例。与 BridgeConnDiag (TCP 桥接连接根因) / DrcQaRunDiag (DRC QA 工具运行失败双层根因) / DrcRuleModSem (DRC 规则 modifier 语义提取) 正交：本案 = Aether MDE 仿真输出文件缺失根因（仿真失败/网表/输出保存/工作目录/仿真器路径/license/模型/磁盘 8 轴诊断）。
