# 深读笔记 — sid 1790128216866_kbs81 (e02141 @ hfeg0pkn002, mc=96)

- **用户**: e02141，主机 hfeg0pkn002（IP 10.129.2.11/10.129.35.75/172.16.8.131）
- **session**: 1790128216866_kbs81.messages.json（141 msgs, 83 tool_use, ~718KB）
- **关键词**: 18 pyAether, 8 virtuoso, 8 netlist, 8 hspice, 8 "lang":"pyAether", 5 spectre, 5 calibre, 2 schematic, 2 innovus, 1 "lang":"skill"
- **agent**: cline (deepseek + glm 模型对比场景)

## 用户意图轮（3 轮 genuine text input）
1. **[msg 0]** `帮我配置 swb-python-api` — 初始需求：配置 Sentaurus WorkBench Python API (swbpy2)
2. **[msg 60]** `帮我创建一个名为try0923的新 SWB 项目，路径是 /home/e02141/devops/，添加 sprocess、sdevice 和 svisual 三个工具，sprocess 上添加参数 Lg（扫描 0.15、0.25、0.35）和 NWell（扫描 1e17、5e17），然后保存。` — **核心任务**（唯一明确意图轮）
3. **[msg 96]** `bash collect_env_info.sh > env_info.txt 2>&1` — 用户自己跑命令（非意图）

## Agent 工具链
- `list_allowed_files` (35) — 探查 /home/e02141 目录结构
- `read_files` (17) — 读 .bashrc, AgingFlow.py, automation_tools_launcher.py, cxmt_lookup_app.py, SKILL.md
- `editor` (9) — 写文件: .bashrc (env), swb_python_api_env.sh, **create_try0923.py** (msg76→84), **run_create_try0923.sh** (msg91), collect_env_info.sh (msg126+)
- `search_codebase` (9) — 搜 swb/sentaurus/gpythonsh
- `SandBox_MCP_Server__run_code` (4) — pyAether sandbox Hello World 测试
- `run_approved_command` (1) — 检查 gpythonsh/STROOT/STRELEASE

## 关键产物（gold standard）
- **create_try0923.py** (msg 84 最终版, ~110 行): gpythonsh 脚本, `from swbpy2 import *` + `from swbpy2.gtree import Deck`, `Deck('/home/e02141/devops/try0923/')` → `getGtree()` → `AddTool("sprocess","sprocess")` / `AddTool("sdevice","sdevice")` / `AddTool("svisual","svisual")` → `AddParam("sprocess","Lg",["0.15","0.25","0.35"])` / `AddParam("sprocess","NWell",["1e17","5e17"])` → `deck.save()` → `deck.finalize()`。含 ImportError 守卫（非 gpythonsh 环境提示 exit1）+ 项目概览打印（实验组合数 3×2=6）。
- **run_create_try0923.sh** (msg 91): bash wrapper, source env → load_sentaurus 2025.06 → mkdir → gpythonsh → 验证 gtree.dat/gtooldb.tcl/gscens.dat

## 失败模式（B 档合成用）
1. ①交付形态/位置错 — 不打包 zip / zip 内多文件 / 非 .py
2. ②硬编码 A 配置 — 不从 JSON 读，跨 B 必失败（路径/工具/参数错）
3. ③漏关键 API 调用 — 漏 save() / finalize() / getGtree() / AddTool 顺序错
4. ④无错误处理 — 缺参数/坏 JSON/文件不存在 不 exit1
5. ⑤实验组合数算错 — 不打印或打印错误

## 域判定
trace 关键词 pyAether(18) 为主，agent 用 SandBox_MCP_Server (pyAether) 测试。核心任务为 SWB (Sentaurus WorkBench) 仿真流编排 (sprocess→sdevice→svisual + 参数扫描)，属设计流编排。归 **layout_aether**（pyAether trace + EDA flow orchestration）。
