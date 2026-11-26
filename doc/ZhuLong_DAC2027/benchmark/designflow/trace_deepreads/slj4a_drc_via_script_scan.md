# 深读笔记 · slj4a · DRC/Via 辅助脚本库检索

- session: `1794529920818_slj4a` · user: t0002729 · host: hfeg0pjn181 (10.129.40.190) · mc=341
- model: deepseek-v4-flash · cwd: /ai_sandbox/ddgoa/V0/agentdir/t0002729 · 2026-11-13 00:32→02:53
- domain: physical_verify (kw: aether:1284; drc:1263; pdk:779; calibre:501; pyaether:416; cmos:105; lvs:61; .gds:35)
- 150 msgs / 13 user turns · 探索性会话：用户测试 agent 在 aether 下的能力

## 用户意图（逐轮）

| 轮 | 用户原话 | 意图 |
|----|---------|------|
| U#0  | 查下你当前有没有接入我的aether | 连通性确认 |
| U#11 | 你能协助我在aether下做什么工作 | 能力盘点 |
| U#13 | aether脚本在哪接入使用 | 脚本入口查询 |
| U#19 | 查下公司现有的版图编辑脚本目前能实现的功能，查几个就行 | **脚本功能检索（分析）** |
| U#27 | 这些是用户自定义的还是底层脚本 | 脚本性质问答 |
| **U#40** | **帮我看看有没有修drc的辅助脚本，最好是修via错的** | **★ 核心任务：DRC/via 辅助脚本检索 + 分类汇报** |
| U#57 | 我想测试下你能做什么，你能知道我现在进入的版图的路径吗 | 能力测试 |
| U#63 | 帮我切成可编辑操作 | 模式切换 |
| U#71 | 跑一下calibre的DRC | 跑 DRC |
| U#97 | 你不能跑吗，还是只能我自己运行 | 能力边界问答 |
| U#119 | 我现在跑了一次drc，你能读结果没 | 读 DRC 结果 |
| U#132 | 3 | 菜单选择 |

## ★ 核心任务 U#40 真实交付（assistant #56，gold）

用户问「有没有修 drc 的辅助脚本，最好是修 via 错的」。agent 检索公司 `le/`、`veri/`、`ut/`、`script/` 多个目录后，给出**结构化分类报告**：

**结论**：公司目前**没有**专门的"自动修 DRC（尤其是修 via 错）"的一键脚本。

**分类**（共 15 个相关脚本 + 4 个间接）：

1. **DRC 运行与结果查看**（跑 DRC，不是修）
   - `IMCleRunDRC.py` — 从 Aether 里直接跑 DRC，GUI 选 rule/设参数
   - `IMCleRunRVE.py` — 读取 DRC 结果并在版图上高亮
   - `IMCleReadDRC.py` — 从 DRC 结果文件提取 check name/坐标
   - `CXMTleFindMarker.py` — 查找/删除 DRC Marker，支持批量
   - `CXMTleFerrari.py` — Ferrari (RVE) 集成，查看 DRC/LVS/LVL 结果

2. **Via 相关操作脚本**（编辑 via，不是自动修 DRC 错）
   - `CXMTleConvertCreateViaCTType.py` — 转换选中 via 类型（LICON↔CT↔V1↔V2↔V3↔V4）
   - `CXMTleConvertViaRotationRowColumn.py` — 交换 via 行/列 + 旋转
   - `IMCleViaPlusMinus.py` — +/- 调整 via 行数/列数
   - `IMCleTrimWire2Via.py` — 将 wire 修剪对齐到 via 边缘
   - `IMClePlugLiconFill.py` — 填充 LICON（plug overlap M0）
   - `CXMTleAddMetalUnderPin.py` — 在 Pin 下方加金属

3. **可能间接用到**
   - `CXMTleFindFloatingMetal.py` — 查找浮空金属
   - `CXMTleDanglingNetCheck.py` — 检查悬空 net
   - `IMCleRuleSnap.py` — 规则对齐（grid snap）
   - `CXMTleDetourRoutingCheck.py` — 绕线检查

末尾建议可帮用户写自动修 via DRC 的 pyAether 脚本，并追问具体 via 错类型。

## reframe 设计（档 B）

**原 gold** = 一份关于真实公司脚本库的 markdown 分析报告（free-text，依赖真实 `/apps/...` 脚本文件，沙盒无）。
**reframe** = 把"检索脚本库 + 分类 + 答结论"的能力固化成**离线脚本库扫描器** `drc_via_script_scanner.py`：给定一个 EDA layout 脚本库目录（递归扫 .py），解析每个脚本的模块 docstring + 函数定义，按关键词分类（drc_run_view / via_operation / indirect_drc / unrelated），检测是否存在"自动修 via DRC"专用脚本，输出结构化 JSON（scripts + conclusion + summary）。

- **visible A** = `script_lib_A/`（17 个 .py，基于真实 trace 脚本名/docstring 重建，**无** auto-fix-via 脚本 → conclusion.has_auto_fix_via=False）
- **hidden B** = `script_lib_B/`（16 个 .py，**不同**脚本名/分类/docstring，**含** `AutoFixViaSpacing.py` → conclusion.has_auto_fix_via=True，防硬编码 A 的结论）
- check() 在 B 上独立跑 SUT 扫描器，验 JSON 结构 + 分类正确性 + 结论 + 无幻觉 + 确定性 + 非零退出 + 不硬编码 A 标识符

## trace_source
- user: t0002729 · host: hfeg0pjn181 · session_file: 1794529920818_slj4a.messages.json · match_count: 341
- real_task_summary: 检索公司脚本库中修 DRC（尤其 via 错）的辅助脚本并分类汇报，结论为无专门自动修 via 脚本
