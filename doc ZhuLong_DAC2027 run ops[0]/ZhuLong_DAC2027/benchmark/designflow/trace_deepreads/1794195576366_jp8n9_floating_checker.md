# Deepread — 1794195576366_jp8n9 (xiwang @ hfeg0pkn002, mc34, spice_sim)

**Source**: real cline trace, scp 自 hfeg0pkn002:/home/xiwang/.cline/data/sessions/1794195576366_jp8n9/1794195576366_jp8n9.messages.json (121 msgs / 471KB)
**旧判定**: parked (r435, 2026-11-11, "consultation floating-tool") → r618 reaudit 复活为可造
**拟造形态**: tool-building（离线 Python CDL/SPICE 浮空网检测器 + Aether 薄封装）
**合成 case**: EDA-Eval-DesignFlow-FloatingNetChecker-001

## 用户真实意图

- U#1: 「现在有检查floating的工具吗？」(mode=act)
- 经 ask_question 澄清，用户选: 「悬空节点/网 (floating net)：网表里无驱动的浮空网，net 上端子数只连了1个或看图悬空」
- **真实意图 = 建一个 floating net 检测工具**（不是查文档、不是纯 Q&A）

## agent 工具链路

1. `list_allowed_files` + `get_agent_policy_status` 摸工作区 → 发现 collector.py/check_reach.py/validate_csv.py/analyze_csv.py/fullmap.json 都非 floating 检测
2. `search_codebase`(floating/noConn/unconnected) + `RAG_MCP_Server__search_apis`(floating net/terminal/pin) 查 pyAether API
3. `SandBox_MCP_Server__run_code` 试 pyAether → Connection refused（沙箱 down）
4. 探盘 `_explore_netlist.py` via `run_approved_command` → 设计库是 OA(*.oa)，只 TECHLIB primitive 有网表 view 落盘
5. 查到 Aether 内置 `aeGetIncompleteNets(layout)` 专用 incomplete net 检测器
6. `editor` 多次写 check_floating.py（先纯 Python 解析器 tokenize_lines/parse_cdl/find_floating/_elems_nodes，再加 Aether 封装 run_layout/run_schematic，再 main + _selftest）
7. `run_floating.sh` wrapper（unset PYTHONHOME/PYTHONPATH 清环境）
8. 自测 `_selftest` → 检出 inv.FLOAT1/DECAP，**初版误判 rpoly 为 floating**（电阻模型名被当 net）
9. 收紧 `_elems_nodes`：R/C/L/D/K/V/I 只取前2节点 drop model → 自测通过
10. `py_compile` + import 校验通过
11. `_cleanup.sh` 清理 scratch

## deliverable（verbatim 还原到 reference/check_floating_ref.py）

- `check_floating.py`：纯 Python CDL/SPICE 解析器 + 浮空网分析 + Aether 薄封装 + main CLI + _selftest
- `run_floating.sh`：清环境 bash wrapper

## check() 设计（23 断言）

- A 档 trace-faithful：任务说明=真实用户原话 + A 样例网表(inv/top)=真实 agent 自测样例 verbatim
- hidden B = synthesized INVX2/LATCH/TBUF/TOP（cross-input，A 不可见）：LATCH floating={NCF,QF}；TOP floating={N2} port_unused={OUT}；TBUF port_unused={EN}；INVX2 clean
- 独立复算（check.py 自带 parser，不 import candidate）逐 subckt 比对
- guards: cross-input genericity / A-leak(10 token) / R-C-2terminal model 不误判 / globals skip / floating_total=5 / run_floating.sh 形态
- 4 假提交回归：empty_shell / print_only / hardcode_a / hardcode_b 全 FAIL
- ref 23/23 PASS, 4 negs 全 FAIL（本地验证）

## 复活池变现 #46
