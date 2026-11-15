# Deepread: qo7xn — src_py3 静态代码分析

- session: `1791945162141_qo7xn`
- user/host: yansonw / hfeg0pfn108
- mc: 35, domain: spice_sim
- trace file: `.cline/data/sessions/1791945162141_qo7xn/1791945162141_qo7xn.messages.json` (337KB, 31 msgs, 子目录下)
- 旧判定: parked (U#0 "analysis coding in src_py3 folder vague premise-missing reject")
- r618 reaudit: 复活为可造（analysis Q&A → 电路/脚本分析报告）

## 用户真实意图
一句模糊指令 "analysis coding in src_py3 folder" —— 要求 agent 真实读取 `/home/yansonw/work/tools/AutoModelSimulation/src_py3/` 全部 .py 源码，做一次结构化代码分析。这是 spice_sim/characterization 域的真实用户意图（分析自己写的 characterization 工具代码）。

## 真实 trace 流（4 个实质性 user turn，agent 31 msg）
1. user[0] "analysis coding in src_py3 folder"
2. agent: list_allowed_files(AutoModelSimulation) + get_agent_policy_status → 列出 src_py3 树
3. agent: list_allowed_files(src_py3 depth3) + run_approved_command(shell-runner 失败: 需要 filePath)
4. agent: editor 创建 _analyze_tmp.py 想统计行数 → run_approved_command(python-runner) 失败(No module named 'encodings' 环境 locale 坏) → 改用 read_files 批量读
5. agent: read_files 批量读 config/models/templates/netlist/parser/statistics/utils/writer/main/mc_main/launcher 等 15 个模块（分多轮 read_files）
6. agent: editor 清理 _analyze_tmp.py
7. agent[30]: 输出完整结构化分析报告（见下）

## agent 最终报告结构（msg 30）
1. **What this package is**: Z-Model 半导体器件模型参数提取/表征工具的 Python 3 重写，驱动 HSPICE，提取 Vt/Ids/Gm/Gds/电容/BJP/环形振荡器/Monte Carlo/mismatch 统计。14 模块清单表（含 Perl 对应物）。
2. **Architecture & data flow**: launcher→main→(MOS_MC)→mc_main；ConfigParser→NetlistGenerator→HspiceRunner→LisParser→ResultWriter。bug-for-bug 兼容 Perl 风格。
3. **Strengths**: 干净分层 / 防御性解析 / 动态捕获 / 跨平台 / MC suffix 表驱动。
4. **Issues**: utils.sigma 数值不稳定两步公式 / statistics._get_mismatch_type 重复表 / _block_corner_vdd 脆弱 / special-etest 正则三处重复 / mc_main._compute_vt0 返回 {} 桩 / vt0.parse_swp_data NotImplementedError / MC 路径输出格式不一致。
5. **Suggested improvements**: 统一 special-etest 正则单一来源 / 补全 MC 路径 / 替换 sigma 公式 / 锚定 block label / 文档审计。

## 选为 case 的理由
analysis/Q&A 型真实用户意图；agent 产出结构化报告但**无文件产物** → A 档不可行（无 checkable artifact）→ B 档 synthesized：把"结构化代码分析"做成**通用静态分析脚本**生成 JSON 报告，判分器独立 AST 复算逐字段比对。15 个真实 .py 模块 verbatim 作为 A 输入，合成 7 模块变体（ReliabilityAgingSim）作为隐藏 B。

## 交付
EDA-Eval-DesignFlow-SrcPy3Analyze-001（spice_sim L1，结构化代码分析报告生成器，9 顶层字段全量 cross-input guard，34 断言，4 negative 全 FAIL）。
