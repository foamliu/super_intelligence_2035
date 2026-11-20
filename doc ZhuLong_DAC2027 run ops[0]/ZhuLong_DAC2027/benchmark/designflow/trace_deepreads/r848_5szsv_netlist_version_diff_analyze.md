# r848 deepread — 1792043028504_5szsv (alanji @ hfeg0pgn145 / 10.129.35.244)

**session**: 1792043028504_5szsv.messages.json (subdir-path ALIVE 1.3MB / 1335817B, 143 msgs, agent=lead)
**mc**: 194 (keywords verilog:891 / netlist:844 / analog:58 / cadence:20) — scan keyword 误判域, 真实意图=netlist 版本差异比对
**domain**: digital (DDGOA LPDDR5 full-chip 仿真网表回归比对)
**liveness**: flat-path NOFILE 但 subdir `sessions/<sid>/<sid>.messages.json` ALIVE (r528 path-bug revival 第N例, r821-r825 同模式)

## 用户原话（核心意图）
- U#1: `/rundata/.../netlist, /rundata/.../netlist 分析上述路径下版网表的差异` (同路径 typo)
- U#12/U#24: `分析下面路径下两版网表的差异：1. .../Oct15.091314/.../V0_WOWTOP_2026Oct14.192957/netlist；2. .../Oct12.144620/.../V0_WOWTOP_2026Oct10.170427/netlist，输出差异点，并且分析合理性`
- U#31/U#34: `上述分析不够详细，分析报告要列出来所有的差异点`
- U#48 (子线程): xmelab `*E,TYCMPAT` elaboration 错误 (TOP.Chip 端口类型不匹配 arb_package::TYPE_*) — 独立子问题, 非主意图

**主意图** = 单轮 analysis-Q&A：比对两版网表，列出**所有**差异点 + 合理性分析（U#12/U#24/U#31/U#34 一致）。U#48 编译错误是后续子线程，未纳入本题（避免一题两意图）。

## assistant 真实做法
- list_allowed_files / run_approved_command(`diff`) 对两份 ~50MB / 百万行网表做 diff
- editor 写多个 extract 脚本，按类别抽取差异到 /home/alanji/diff_analysis/0[1-8]_*.txt
- 产出 10 类差异报告 (idx=82, 13498 chars)：
  1. TIMESTAMP 变更 (~165 cell 时间戳)
  2. VIEW 变更 (schematic↔schematic_debug_vlg)
  3. MODULE 增删 (新增 ~56 / 删除 ~18 / 内部改 ~230)
  4. PRIMITIVE 类型变更 (ntk→ntn_lv, ntn_lv/ntk_lv 带 mostype 属性新增)
  5. CELL/LIBRARY 引用变更 (commonIP→ddgoa_cmos_work 库迁移, cell 重命名/互换)
  6. PORT/INTERFACE 变更 (IOa,IOb→CCom,Vout; CPSelBrc→CPSelB2out/B3out; ColRedO 删除)
  7. WIRE 声明变更
  8. PARAMETER/ATTRIBUTE 变更 (mostype tranif1/rnmos; buf #(20,20) 延时删除)
  9. 大型结构重写区域 (~120 大 hunk)
  10. 合理性分析 (整体合理：Bot→Top 架构优化/命名规范/接口统一/库迁移/BIST 新增/primitive 精确化；⚠️ 需关注：debug_vlg 是否临时/ODT 路径变更功能一致/formal verif/Array 大改 signoff)

## A档不可行核验
真实网表在 `/rundata/ddgoa/V0/simdir/verilog/alanji/verilog.lpddr5.ddgoa.alanji.Oct15.091314/.../netlist`，eda_flow .75 (10.129.35.244) 实测 `ls` → **Permission denied** (cadmin 组权限, 同 r844 jeij7 /rundata/ddgoa 模式)。且百万行 50MB 网表不可 headless 自包含复现。→ B档 synthesized reframe。

## B档 synthesized reframe 忠实性
- 保留真实 10 类差异**结构**（assistant 的报告作蓝本），裁剪成自包含小型网表片段
- 片段语法忠实 trace 原文：`// Library / // Cell / // View / // Timestamp` 头 + `module ... endmodule` + primitive `ntk|ntn_lv|ntk_lv|ntn_m|ptn_lv|ptn` (带 `#(.mostype("..."))`) + `buf #(...)` 延时
- 真实差异点编码进 fixture：ntk→ntn_lv (DqFnlSwitchM5IP, 同 trace cell 名), commonIP→ddgoa_cmos_work, Array1G_Bot_E→Top_E + CPSelBrc→CPSelB2out/B3out + ColRedO 删 + buf #(20,20) 删, IOa,IOb→CCom,Vout, schematic→schematic_debug_vlg (SCmosDq), cmDpPW_Read_0820→cmDpPWGF_Read_1014, BistBlock 新增带 mostype tranif1
- hidden-B 用**完全不同** cell/port/primitive/library 名值 (VrefGen_0712/ClkBufM3IP/SenseAmp_Bot_W→Top_W/VblhMoscapIP/ZqTrimDac/RdOdtCtrlOld→New/LegacyTestWrap/ZqCalBlock, analogIP→ddr5_analog_work, ntk→ntn_m, IOa,IOb→CComN,VoutP, buf #(15,15), mostype rnmos) 且 **B 无 view 变化** + unchanged 控制模块 ZqTrimDac — 测 refuse-to-hallucinate + 反硬编

## 交付物
`outputs/submit.zip` = `analyze_netlist_diff.py` (CLI 比对两网表输出结构化 diff_report.json) + `diff_report.json` (可见 A 报告)

## check() 18 条独立断言（在隐藏 B 上跑脚本）
脚本跑通/键齐全/timestamp/library/primitive/module_added(ZqCalBlock)/module_removed(LegacyTestWrap)/cell_renames(SenseAmp+RdOdt)/port(VblhMoscapIP)/delay_buf(SenseAmp buf#15)/view_changes空(refuse-to-hallucinate)/added-removed真实性/反硬编B出现A不泄漏(ZqCalBlock/ntn_m/ddr5_analog_work 出现, BistBlock/ddgoa_cmos_work/SCmosDq/schematic_debug_vlg/Array1G_Top_E 不泄漏)/控制模块ZqTrimDac不变/reasonableness引用B/3次确定性

## 自验
- ref analyze_netlist_diff.py 在 A 上产出 10 类差异全捕获 (timestamp/library/primitive/rename×2/port×2/delay_buf/view/module_added BistBlock)
- ref 在 B 上产出全捕获 (view_changes=[] 正确, ZqTrimDac 不在变更列表)
- check.py REF self-check **PASS**
- 3 neg: empty→④(无输出) / print_only硬编A→⑦(timestamp错+反硬编) / core_del删primitive检测→⑧(primitive_changes空) **全 FAIL 命中不同断言组**
- §4.9 (a)空壳 (b)print期望A (c)删核心primitive检测 三假提交全 FAIL
- jsonl test sha == disk check.py sha == cases/A test sha byte-identical (ba5fb139...)
- k_check==k_rationale==18 ≥8 硬闸门过

## 落库
- cases/A/EDA-Eval-DesignFlow-NetlistVersionDiffAnalyzeProduce-001.json (source-of-truth)
- A.jsonl 418→419 (build_jsonl.py --shard A 重建)
- ledger A 5szsv parked→case (case 407→408, --force 覆盖 D 旧 parked「Q&A weak」, 11-15 reaudit analysis-Q&A 合法)
- pool_reaudit_A.tsv 5szsv 行 不可造(待深读)→可造(已造r848)
- eda_flow session r848: open + scp 5szsv.messages.json(1.3MB ALIVE) + close cleaned
