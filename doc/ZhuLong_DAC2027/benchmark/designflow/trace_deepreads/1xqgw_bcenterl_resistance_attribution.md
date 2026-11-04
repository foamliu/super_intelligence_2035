# 深读笔记 — trace 1xqgw (steveny @ hfeg0plg77/10.129.35.77, mc=72)

- session_file: `1790217333942_1xqgw.messages.json` (577KB, 130 msgs: 67 user/63 assistant)
- agent: lead
- keywords/tools: 50 calibre / 40 virtuoso / 27 dbGet / 11 pyAether / 11 cellview / 5 hspice / 6 dbCreateInst
- 工具使用: 43 run_commands / 5 editor / 4 read_files / 4 list_allowed_files
- editor 写: `BCenterL_resistance_reduction_analysis.md` (idx20, 3778 chars) / `BCenterL_flow_analysis_report.md` (idx108, 5305 chars)

## 真实意图（A-档 seed）
**USER#1 (idx0)** 是一段超长 "Context summary" 承接上轮（continuation note），不是干净的目标提出。
**USER#2 (idx1)** `<user_input mode="act">你有能力分析这个电阻降低是由什么导致的吗？</user_input>` — 提出目标，未给根因（A-档合格）。
**USER#3 (idx19)** `<user_input mode="act">分析报告写一下，保存在我的home下</user_input>` — 明确交付：写分析报告存到 home。
后续 USER#4-11 为 follow-up（flow3 实验 / CA 单元 / 自动 vs 人工差异 / EM 电流密度盲区 / 总结报告 / 材料清单）= hint 不进 prompt。

## 真实 agent 行为
1. run_commands (idx2): `grep -v '^LV+RSView' .../RSDB_vss!/vss!.rvn | head` 读 baseline 与 via4 优化后的 rvn 文件头
2. run_commands (idx4/6): python heredoc load rvn → 按 (net,layer,x,y) key 取每段 max R → join baseline vs via4 → 算降幅
3. run_commands (idx8/10/12/16): grep via cell 名 in GDS 数 SREF 引用；grep PowerFill 0-shape 证据 in tryRun.md；ls via cell layout 目录
4. editor (idx20): 写 `BCenterL_resistance_reduction_analysis.md` (3778 chars) — 电阻降低归因报告
5. editor (idx22): sed 修复笔误 BCenderL→BCenterL
6. 多轮 run_commands 读 BCenterCA (Flow3) 数据 + 人工版 sep23 数据 → editor (idx108) 写 `BCenterL_flow_analysis_report.md` (5305 chars) — 综合报告（归因+数据核查+能力边界+EM盲区）

## 真实 gold（人工复核，从 idx20 editor new_text 提取）
报告 `BCenterL_resistance_reduction_analysis.md` 关键定量结论（必须与 rvn 数据对账）：
- **结论先行**：电阻降低完全由 AutoVia 新增层间 via 引起（PowerFill 无贡献）
- **基线 maxR**: vdd1!=62.3938 / vss!=293.036 / vcc!=0
- **优化后(via4) maxR**: vdd1!=6.63342 / vss!=7.55538 / vcc!=0
- **max-R 降幅**: 1 − 7.55538/293.036 = 97.42% ≫ 30% targetReduction → 通过
- **最恶劣点**: vss! M4 @ (-12936.60, -348.69) baseline 293.0 → via4 7.555 (-97.4%)
- **PowerFill 产物**: PG.gds = 68B stub / 0 shape（无贡献证据）
- **新增 via cell**: 3 个 `BCenterL_rscalc_V2AV1AV5V4V3V2V1CT_{vdd1,vss,vcc}_VIA`，via 栈 V2A·V1A·V5·V4·V3·V2·V1·CT（CT→V5 完整垂直栈）
- **机制**: 单径串联高阻 → M1–M5 全层并联 + 纵向 via 网格 → 等效 R 暴跌 ~38×
- **逐 rvn 节点**: 20/22 共同点降幅 ≥30%；2 个亚欧姆次级点(~0.60Ω/0.44Ω)降 24–29%（仍下调无上升）
- **收敛**: failCount=0（按 50 check_point 口径）

## gold 依赖
- live `.rvn` 文件（RSDB_vss!/vss!.rvn 等，Calibre RsCalc 输出，内网 /rundata/train/V0_Austin/...）
- live GDS（数 SREF 引用 via cell）
- live tryRun.md（PowerFill 0-shape 记录）
→ A-档 faithful 不可行（内网数据不可达）→ **B-档 synthesized L1-boundary**（离线 rvn fixture + 流程元数据 → 归因报告生成器，stdlib-only，确定性）

## 合成方案
合成 `bcenterl_resistance_attribution_gen.py`（标准库，确定性无随机）：
- 输入: `--baseline-rvn` / `--opt-rvn` / `--flow-meta`（JSON: powerfill_shapes, via_cell_names, via_stack, target_reduction, cell_name） / `--out`
- 解析 rvn（CSV: 跳 LV+RSView 行，列 net,layer,x,y,R，按 (net,layer,x,y) 取 max R）
- 计算: baseline/opt maxR per net、max-R 降幅、逐节点降幅 join、瓶颈点 top-N、收敛判定（降幅≥target）
- 输出: 归因报告 markdown（结论先行 + 数据来源表 + 瓶颈点 top10 + 归因(PowerFill 0-shape / via cell 新增 / 机制) + 收敛判定 + 附注）

资产 A 忠实（fixture rvn = 从真实 vss!.rvn 头部提取的列结构 + 真实坐标/数值；flow_meta = 真实 via cell 名/栈/PowerFill 68B/0-shape/targetReduction=0.3/cell=BCenterL_rscalc；prompt = USER#2+#3 逐字 + task_brief ≤3 行接口）
hidden B（同结构不同命名/数值：cell=DDRTop_rscalc / via 栈 V3A·V2A·V1A·V5·V4·V3·V2·V1·CT / PowerFill 142B/0-shape / targetReduction=0.25 / 不同坐标与 R 值）杀硬编码 A 的 BCenterL/293.036/7.55538。

## 正交性
现有 physical_verify case 无 "RsCalc 电阻降低归因报告" 子主题。RsCalcAgentGen-001（rscalc agent-script inlining）、AutoViaLayoutMerge-001（via→layout merge）是流程编排/生成；本案 = 流程结果的**归因分析报告生成**（读 rvn 数据→定量归因→结构化报告），首次覆盖"流程结果归因分析"子主题。steveny 首个 1xqgw trace。
