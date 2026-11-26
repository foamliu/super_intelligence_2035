# Trace deepread — 1787538576102_r9m9l (RvnDistReport-001, layout_virtuoso)

- **session**: `1787538576102_r9m9l` · user `e0014566` @ `hfeg0pkn001` · mc=233 · model glm-5.2 · 6 top-level msgs (1 lead agent, 1040 content blocks)
- **cwd**: `/home/e0014566/test_layout_rscalc_flow_17` · cell `BCenterCA_rscalc` (lib `auto_austin_case1`, 1p5m1x3y1z)
- **tools (match)**: 174 virtuoso + 23 calibre + 13 cellview + 12 SKILL + 7 dbGet (Virtuoso RsCalc 电源网络电阻优化流)

## 用户意图轮（A-档 seed）
- **U#0**: 「请你将 test_RScalc/test_skills_7/rscalc.config 中的checkPoints 同步到这里的配置中。」→ config 同步（49 checkPoints 搬运），简单预处理。
- **U#16**（主任务意图）: 「read the prompt_flow.md and do the job in it. 基线的电阻分布一定要重新算，不要用已有的。并且出以下5个报告：1) 优化前基线电阻分布完整报告（英文，无乱码）2) 优化后电阻分布报告 … 3) … 4) 优化 vs 基线 5) 优化 vs 原始输入」→ 跑基线 RsCalc（重算）+ 优化循环（AutoVia/PowerFill）+ 出 5 份英文报告。
- **U#510**: 「好的，你再检查一下，是不是完整的5份报告都结果无误。」→ 验证阶段（本 case 的 seed）。

## assistant 工具链（关键）
1. 读 `prompt_flow.md` / `common.config` / `rscalc.config` / SKILL.md 理解流程。
2. **Step 0.5 门控**：SKILL `dbOpenCellViewByType("auto_austin_case1" "BCenterCA_rscalc" "layout")` 数 RTEXT 标签（RTEXT_COUNT=2）+ 检查 checkPoints 存在 → 通过才跑。
3. **Step 1 基线 RsCalc**：`gen_rscalc_agent.py` 生成 agent 脚本 → `nohup virtuoso -nograph -replay ...` 跑 → 等待 GDS strmOut(193MB) → LVS → RsCalc 引擎(rsmakepreview/rscalcac/rscalcresist) → 产 `RSDB_vss!/vss!.rvn`、`RSDB_vcc!/vcc!.rvn`（Calibre NodeList 格式）。
4. **踩坑**：首次 `pwrNets=""` 自动检测 → 处理了所有 net（vss!/vcc!/vddqca!/CK_c…），vcc!.rvn 仅 3 行（原 20）。修正 `pwrNets="vss! vcc!"` 重跑。
5. **优化循环**：AutoVia + PowerFill SKILL → 改 layout → 再跑 RsCalc → 优化后 .rvn。
6. **报告生成 + 验证（#511-571，本 case 核心）**：从 .rvn 第 12 列提电阻，`awk -F, '{sum+=$12+0}'` 算 avg，排序取 median（23 点 → 第 12 值）；逐点交叉校验报告 vs .rvn 源；修 avg/median 错值（vss! avg 99.35→103.43、median 95.634→95.606）；ASCII 校验（无乱码）；报告间一致性（同一基线值在 Report_1/4/5 一致）。

## .rvn NodeList 格式（金标准）
```
LV+RSView:NodeList,3
idx,nodeId,"net","layer",x1,y1,x2,y2,"net",checkPointX,checkPointY,resistance,,,,,,,,,0
```
- 第 12 列 = 电阻(ohm)；第 10/11 列 = 检查点坐标（与 rscalc.config checkPoints 对应）。
- A 真实数据：vss!.rvn 23 行(19 M4 + 4 M5)，vcc!.rvn 3 行(M4)；rscalc.config pwrNets="vss! vcc!"，49 checkPoints(vss! 25 + vcc! 24)。

## 本 case 重构（B-档 faithful-seed synthesized）
抽 U#510 验证子任务 → 通用 `.rvn` 电阻分布报告生成器 `rvn_resist_report.py`：
- 输入：rvn 目录 + rscalc.config → 输出结构化 JSON（per-net count/max/min/avg/median + by_layer 拆分 + pwrNets/rvn nets 一致性 extra/missing + checkPoint 覆盖率 matched/unmatched + 逐点明细 points）。
- A = 真实 trace .rvn/config；隐藏 B = 合成(vss! 20[14M4+6M5]、vcc! 12[8M4+4M5]、gnd! 8[5M4+3M5] extra net，34 checkPoints 含 2 unmatched)。
- check.py 15 条(a–o)自包含（A+B 内嵌），独立重算期望 vs 候选 JSON。
- 与现有 RsCalc case 不重叠：ResistAttribReport=归因(为何 R 降)；RsCalcFlowReporter=4-skill workflow 对比；RsCalcCkPtAudit=checkPoint 规划审计(bbox/层)；RsCalcChkPtGen=RTEXT/checkPoint 生成。本 case = post-RsCalc 结果校验 + 分布统计。

## 选料踩坑
- 候选池顶部 6qt0a(harrywu, netlist+hspice+schematic 偏 sim)、jason17w(netlist 1455 偏 netlist 生成) 均非纯 layout，按 cand2.py 过滤(sim>2×layout 跳过)后选 r9m9l。
- .75 (hfhds201) 上 session 是**目录** `1787538576102_r9m9l/` 含 `.json`+`.messages.json`（非平铺文件）；scp 从 hfeg0pkn001 取不到（文件在 .75 本机 /home/e0014566 下，非远端）。
- check.py 初版用 `HERE/../assets` 相对路径判分 → 评测 harness 把 test 字段拼进大脚本在他处执行会断；改 **A+B 内嵌**自包含（参照 DrcMatchRca-001 模式）。
