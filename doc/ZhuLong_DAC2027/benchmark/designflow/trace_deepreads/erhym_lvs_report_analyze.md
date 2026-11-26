# Deepread: erhym (fhwang) — LVS 报告分析 + 报告生成

**trace**: 1792223414540_erhym.messages.json / fhwang @ 10.129.2.14 / mc=50
**keywords**: mosfet:405;analog:400;calibre:190;aether:52;schematic:31;pyaether:28
**n_msgs**: 134 / 5 user turns / 70 assistant tool_use
**domain**: schematic_netlist (LVS = layout vs schematic netlist verification)

## 用户意图（5 轮）
- U#0 (msg#0): 「你的功能目前有哪些」— 能力询问（铺垫，非 produce）
- U#1 (msg#16): 「帮我分析一下这个结果路径下LVS的结果文件错误类型，并附带解决方案方向 /proj/drcpa/V0/ver/lvs/YDEC_Power_Rscalc/Array3G_TOP_L」— **★ CLEAN PRODUCE**: 分析 LVS 结果 + 解决方案方向
- U#2 (msg#77): 「把上述你的分析方案生成文本文件放到 /proj/drcpa/V0/ver/lvs/YDEC_Power_Rscalc/Array3G_TOP_L 这个路径下」— **★ CLEAN PRODUCE**: 把分析写成报告文件
- U#3 (msg#128): 「/skill-creator」— skill 创建指令（生产工具化）
- U#4 (msg#132): 「上面我询问你的结果中连线错误是否可能只是2个block cell 输出和下一级输入的2个信号接错了位置导致的」— **用户给出根因假设**（A-grade rule#2 排除：不得用作 A 档任务说明）

**A-grade 选轮**: U#1 + U#2 合并（提出需求 + 表达目标，无根因/无修复方案）= 「分析 LVS 结果错误类型+解决方案方向，生成文本报告文件」。

## 助手工具链（70 tool_use）
1. `read_files` 读 LVS 报告 (.lvs.report / .lvs.report.ext / _calibreLVS.rule_)
2. `run_approved_command` (shell-runner profile) 跑 grep/head/tail/sed/wc 提取报告关键段
3. `editor` 写 `analyze_lvs.py`（Python 解析脚本，分多次 insert_line 增量构建）
4. `editor` 写 `analyze_lvs.sh`（shell grep 统计脚本：missing smashed mosfet count、Incorrect count、Property Error count、ERC summary）
5. `editor` 写 `analyze_lvs2.sh` / `analyze_lvs3.sh`（深入 property errors + cell comparison 段）
6. `editor` 写 `write_report.sh` / `write_report.py` / `write_report_final.py`（把分析结果写成 LVS_ANALYSIS_REPORT.md 到目标路径，分多块 cat >> 累加）
7. 最终产 `LVS_ANALYSIS_REPORT.md`（结构化 Markdown 报告）到 `/rundata/drcpa/V0/ver/lvs/YDEC_Power_Rscalc/Array3G_TOP_L/`

## 金标准产物结构（LVS_ANALYSIS_REPORT.md）
- `# LVS 结果分析报告 — Array3G_TOP_L`
- `## 基本信息`（表格：Top Cell=Array3G_TOP_L, LVS Result=INCORRECT, 报告 260.7MB/1986972 行, Layout/Source, 运行 264s/287s, Calibre v2020.1_36.18）
- `### Rule 关键设置`（RECOGNIZE GATES=NONE, FILTER UNUSED OPTION=NONE, VIRTUAL CONNECT COLON=NO, EXECUTE ERC=YES, SPICE ALLOW FLOATING PINS=YES）
- `## 总体错误摘要`（Connectivity errors 有, Property errors 有, 1224 Unbalanced smashed, Overall=INCORRECT）
- `## 错误类型详细分类`
  - 1️⃣ Connectivity errors（no similar net, 集中在 VblhActLogic 模块 VblhActBank_0/VwlpDetectF/VwlpDetectLBuf）
  - 2️⃣ Property errors（W 交叉匹配：Layout 2.717u ↔ Source 1.476u，diff 84.1%/45.7%，MP(ptn)）
  - 3️⃣ 提取警告（.ext 表：Open circuit 2[SecEnGapN,vap2!], Unattached label 5[viso!,VncsgnEn,vncsgn!], Unattached port 6, Virtually connected 4[vap2!,vmwln!], Stamping conflict 1[vss! 19470 nets]）
- `## 根因分析`（4 根因：Smashed MOSFET 匹配混乱 / Property W 交叉匹配 / 层次信号交叉 / Power net 同名冲突）
- `## 解决方案方向`（针对 Open circuit/Unattached/Virtually connected/Stamping/Property/Connectivity 各给修复建议）

## 合成判定（A vs B 档）
- **A-faithful 不可行**：
  - 真实 LVS 报告 260MB 不可附加（assets 体积红线）
  - 报告在 `/rundata/drcpa/` 私有路径，不可移植到沙箱
  - live Calibre RVE / svdb 可视化依赖不可移植
- **B-grade synthesized 重述**：构造小型合成 LVS 报告片段（含真实结构：Cell/Result/Rule/Comparison/Property Error W/missing smashed mosfet/.ext 警告段/ERC summary），让候选 `analyze_lvs.py` 解析三类输入 → 生成 `error_summary.json` + `lvs_analysis_report.md`，判分验**结构 + 计数 + 跨输入**而非文本相似。L1 离线可验（纯文本解析+subprocess，无 EDA 工具依赖）。

## case 设计
- **case_id**: EDA-Eval-DesignFlow-LvsRptAnalyze-001
- **A 输入**（可见）: lvs_report_A.txt (Array3G_TOP_L, INCORRECT, Calibre v2020.1, 1224 smashed, W 2.717u/1.476u) + lvs_report_A.txt.ext (SecEnGapN/vap2!/viso!) + erc_summary_A.txt
- **hidden B**（不同设计，INCORRECT）: DDR5_PHY_TOP, Calibre v2022.4, RECOGNIZE GATES=ALL, VIRTUAL CONNECT COLON=YES, 856 smashed, W 0.840u/0.420u, vcore!/vref!/vbias!/vddq!/vssx!, open_circuit=7, unattached_label=12, stamping_conflict=2
- **hidden B2**（CORRECT 通过 case）: AES_CORE, CORRECT, 0 errors, 0 ext warnings — 测候选能否处理"通过"报告（不能总报 INCORRECT）
- **反硬编码五轴**:
  1. design 全不同: Array3G_TOP_L(A) / DDR5_PHY_TOP(B) / AES_CORE(B2)
  2. Calibre 版本不同: v2020.1(A) / v2022.4(B/B2) — 硬编 v2020.1 者 e FAIL
  3. W 值不同: 2.717/1.476(A) / 0.840/0.420(B) — 硬编 A W 值者 h FAIL
  4. smashed 数不同: 1224(A) / 856(B) / 0(B2) — 硬编 1224 者 j FAIL
  5. 信号名全不相交: SecEnGapN/vap2!/viso!(A) / vcore!/vref!/vbias!(B) — 硬编 A 信号者 n FAIL
  6. B2 CORRECT case: 总报 INCORRECT 者在 B2 上 m FAIL（跨输入守卫）

## check.py 16 条件 (a-p)
- a: zip 防泄漏 + py_compile
- b: B-run exit0 + 2 文件 (lvs_analysis_report.md + error_summary.json)
- c: error_summary.json 含 7 顶层键
- d: B lvs_result == INCORRECT
- e: report 含基本信息节 + top_cell + tool_version
- f: report 含 Rule 设置 (RECOGNIZE GATES + FILTER UNUSED + VIRTUAL CONNECT COLON)
- g: B ext_warnings 计数 (open_circuit==7, unattached_label==12, stamping_conflict==2)
- h: B property_errors 3 元素 + W 值 + diff_pct≥50
- i: report 含错误分类 (Connectivity + Property)
- j: B missing_smashed_mosfet == 856
- k: report 含根因分析节
- l: report 含解决方案节 + 可操作建议
- m: B2 跨输入守卫 (CORRECT + 0 errors + 0 ext)
- n: 反硬编码 (无 A 标记 + A-run top_cell≠B)
- o: 确定性 3x sha256
- p: error_counts 是 dict + 含三键 + smashed==856

## 自验结果
- ref PASS 16/16 (a-p) ✓
- 6 negatives 全 FAIL (NEG_RC=6, n_pass=0) ✓
  - empty_shell → b (B-2files 缺输出)
  - print_expected → e (硬编 A top_cell，B 上不匹配)
  - core_deleted → e (无 tool_version)
  - naive_hardcode_a → e (硬编 A top_cell)
  - naive_no_correct → e (无 tool_version，且 m 也会 FAIL 因总报 INCORRECT)
  - naive_wrong_smashed → e (无 tool_version，且 j 也会 FAIL 因 smashed 计数错)
  - 2 distinct first_fail labels (b, e)
- §4.9 三假 (empty_shell/print_expected/core_deleted) 全 FAIL ✓
- 断言闸门: k_rationale=16 == k_check=16 ≥ 8 ✓
