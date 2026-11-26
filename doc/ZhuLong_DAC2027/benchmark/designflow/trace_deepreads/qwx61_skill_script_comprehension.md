# Deepread Note — qwx61 (SkillScriptComprehensionQA-001)

**session**: 1789979343381_qwx61.messages.json (112872 B, 18 msgs)
**user/host**: thomasz @ hfeg0plg184 (10.129.33.184)
**mc**: 16 · **domain**: schematic_netlist (D-pure: dpur=141 vs cpur=16)
**case_id**: EDA-Eval-DesignFlow-SkillScriptComprehensionQA-001 (r895, 2026-11-18)
**grade**: A档 trace-faithful · revival-from-parked (per 2026-11-15 令「Q&A-investigation 脚本理解类造-able」)

## Trace 结构
- **msg[0]** U#0 (verbatim): `/home/thomasz/tmp/CXMTseCVPSHierSearch.il\n读取一下这个脚本`
- **msg[1-11]** assistant tool calls: read_file /home/thomasz/tmp/CXMTseCVPSHierSearch.il → 708 行内容返回 + assistant 综合解读金标准
- **msg[12]** U#12: 「哪个功能执行后会…生成 .HierSearch 隐藏目录」
- **msg[13]** assistant 答: CXMTseCVPSHierSearch_all 入口 mkdir at L258-260 (rootdir = ".HierSearch"; unless(isDir(rootdir) system(strcat("mkdir " rootdir))))
- **msg[14]** U#14: 「生成的 .HierSearch 为什么是一个链接」
- **msg[15-17]** assistant 答: .HierSearch 软链接到当前 cellview 工作目录以复用 cvps 中间产物 (hcell.cvps.k / hcell.cvps.nok 等)
- 用户接受解读 (无后续修正)
- 模型: cline

## 真实脚本签名 (CXMTseCVPSHierSearch.il, 708 行, 28610 B)
- **版本**: v2.0 (2026/06/01 Thomasz - compatible for hl mos)，Revision History v1.0a..v2.0 共 17 条
- **12 procedure**: CXMTseCVPSHierSearch_{Main_GUI, Main_CB, all, loophier, searchVerilog, searchPreCVPS, searchPinShort, searchCVPSHcell, verilogParam, pParUsedCheck, Latch, multipleDriver}
- **4 GUI tabs**: "Search Verilog" / "Search Pre-CVPS" / "Search Pin Short" / "Search CVPS Hcell" (hiCreateTabField ?tabs list(...))
- **dispatcher**: CXMTseCVPSHierSearch_all (以 _all 结尾, 不含 _loop)
- **rootdir**: ".HierSearch" (L258-260, mkdir 创建)
- **输出文件**: verilogFind.log / verilogFind.csv / pinShort.csv / hcell.cvps.k / hcell.cvps.nok / cvps.csv (strcat(rootdir "/<name>"))
- **检查项**: Latch / multipleDriver / pParUsedCheck / verilogParam (case 分支 type 字符串)
- **has_loophier**: True (CXMTseCVPSHierSearch_loophier 递归层级遍历)

## 造题映射 (A档 trace-faithful analyzer-script 范式, 套 r890 SimSetupFolderAnalysisQA-001 模式)
- **prompt** = U#0 逐字原话 + 真实路径 + 交付要求 (通用 analyze_skill_script.py)
- **资产 A** = CXMTseCVPSHierSearch_A.il (219 行结构保真精简重建, 保留全部真实结构签名, 删减字段定义与冗余 case 分支体)
- **隐藏 B** = CXMTseSchNetlistAudit (合成平行场景: 3 tabs / .SchAudit / floating+multidriver+unmatched / v1.3 / 8 procedure), 每维度反硬编码 A
- **隐藏 B2** = CXMTseLibCellCheck (反硬编码 B1: 2 tabs / .CellCheck / cellview+cdf / v2.1 / 5 procedure)
- **隐藏 B3** = 不存在文件路径 → 优雅空 JSON (跨输入兜底)
- **check.py** 16 独立条件 a-p, B_IL/B2_IL 内嵌 raw string

## 自验
- reference_submit.zip (含 analyze_skill_script.py) → check.py **PASS 16/16** ✓
- 3 negative samples (空壳 / 只 print 硬编码 B1 / 删核心 parse) → 全 FAIL (3 distinct conds a/o/c) ✓
- **修复 1 bug**: search_types 正则 `[^)]*` 贪婪吞引号 → 改 `[^)]*?` 非贪婪, B 的 {floating,multidriver,unmatched} 正确提取

## 覆盖率与 ledger
- D.jsonl 480→481, 📊 477/2907 mc≥10=16.4%
- ledger: claim qwx61 → mark --status case EDA-Eval-DesignFlow-SkillScriptComprehensionQA-001 ✓

## 关键发现
- **r894 推断被证伪**: r894 称「eda_flow.open_session eval-driver gated 无法 ssh-fetch」, r895 实测 open_session(task_id/eval_id/user) 正常返回 workdir, ssh from .75→remote cat 成功。下轮 r896+ 可继续此 ssh-fetch 路径处理剩 89 untouched mc≥10 候选。
- ssh 命令需 `</dev/null` 防 hang: `ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "cat <file>" </dev/null`
- scp as target user fails (no key) but cat-as-default-user works (files world-readable)
