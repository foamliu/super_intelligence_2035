# Trace deepread — sid_1793786351814_mmmtz — DcSynthAnalyze-001 (digital A-faithful L2-static)

**source**: hfeg0pkn003 `/home/<u>/.cline/data/sessions/1793786351814_mmmtz/1793786351814_mmmtz.messages.json` (213 msgs / 1.13 MB, user=e0046913, mc=169). Fresh from 11-05 snapshot (194-fresh pool, top digital-domain candidate kw=netlist:149/synthesis:43).

## 用户意图（verbatim, A-档任务轮 = U0）
> 分析cla_top的综合情况

- 纯需求轮（只给目标「分析综合情况」，未给根因/修复/具体方法）✓ A-faithful
- 单轮任务（U0 即任务轮，无前序铺垫），无后续用户追问纠正。
- domain = digital（Synopsys Design Compiler DC 综合分析：cla_top.mapped.qor.rpt + dc.log + check_design/check_timing + vt_group + power + area + sdc + mapped.v）。

## trace assistant 真实探索发现（grounding for reference）
1. **cla_top 是 16-bit 行波进位加法器**：综合后 netlist 仅 16 个 `FA1D2DBCP51H180L6W25T5SVT` 实例（全加器），命名 `intadd_0_U2..U17`，构成 CO→CI 链 → `is_ripple_carry=True`。
2. **时序 MET**：虚拟时钟 vclk 5ns，critical path slack **+1.02ns**，TNS=0，0 条违例路径（path_group=FEEDTHROUGH，levels_of_logic=16）。
3. **RPT-181 ×2 是核心症状**：dc.log 中 `Error: ... (RPT-181)` 出现 2 次，关联 `qor_data/compile/tables/vt_group_details.json` **缺失**（manifest 声明了 vt_group_details 表但 tables/ 目录下无对应 json 文件）→ 这是 A 的根因（vt group 详情表未生成导致 DC 报错）。
4. **SEC-51 ×1**（FuSa license warning，benign），UID-101/UID-348/TIM-211/TIM-212 warnings。
5. **VT 单一**：所有 16 cell 均 svt（100%），无 lvt/ulvt，cell_area=2.64384，ports=50。
6. **check_design** LINT-2 ×2，**check_timing** TIM-211/TIM-212 + UID-1515/UID-85。
7. assistant 全程未做任何修改，仅读 reports/results/data/logs/qor_data 各文件做分析（L2-static：解析报告不调 DC）→ 本 case 交付 `analyze_syn.py` 同样 L2-static。

## 金标准说明
reference 脚本 `analyze_syn_ref.py` 基于上述**真实 trace 探索发现**（regex 解析 DC 报告：qor/area/vt/power/check_design/check_timing/sdc/mapped.v/dc.log/qor_data.manifest），实现 U0 verbatim 需求「分析综合情况」，输出结构化 JSON。在真实 A 与合成 B 上自验均 PASS。prompt = U0 逐字原文（A-档 trace-faithful）。

## case 合成
- ID: `EDA-Eval-DesignFlow-DcSynthAnalyze-001` · digital · A-faithful · L2-static
- 交付: 通用 `analyze_syn.py <syn_flow_dir> <out_json>`（便携 Python，regex 解析 DC 综合流程目录）
- A = syn_flow_A（真实 cla_top 综合流程，从 trace tool_results 重建：reports/results/data/logs/qor_data/src_rtl；vt_group_details.json **故意缺失**复刻根因；dc.log 含 RPT-181×2 + SEC-51×1）
- hidden B = syn_flow_B（合成 pipe_mul4 4-bit 2 级流水乘法器，**结构性对立**于 A）：
  - 顺序器件 8 DFF（A 全组合 0 DFF）vs A 0 DFF
  - clk 真实时钟 2ns（A vclk 虚拟 5ns）
  - slack -0.12 **违例** 8 条（A slack+1.02 MET 0 违例）
  - svt+lvt 混合 20/12（A svt-only 16）
  - vt_group_details.json **存在**（A 缺失=A 根因）
  - RPT-181=0（A RPT-181=2）
  - is_ripple_carry=False（A True）
- A≠B ✓ 结构性对立覆盖每个被断言维度
- reference + check.py k=25 断言 a-y（含 5 条反硬编 A + 5 条 report_A 反伪造 + 3-seed 确定性 + 反作弊）+ negative/ 3 stub（neg1 stub/null、neg2 硬编 A 数、neg3 仅解析 design.name+clock.name 其余 stub）
- B 以 base64 gzipped tarball 嵌入 check.py（`_B_TGZ_B64` 常量 + `_extract_b()` 解压），check.py 自包含。
- §4.9 三 fake-submit 全 FAIL（neg1→cond(e) design.name=None、neg2→cond(e) design.name=cla_top 反硬编 q、neg3→cond(f) version=None）；reference PASS。

## trace 未覆盖的合成补充
trace 未触碰任何违例/多 VT/真实时钟的综合流程（cla_top 是最简单的全组合全 svt 满足时序的案例）；B 的违例/多 VT/流水/真实时钟/vt_group_details.json 存在 等情形由本 case 合成补全，验证候选解析器的**通用性**（非仅对 cla_top 这一特例 hardcode）。
