# Deep-read: sid 1787884599302_xoriz — rscalc_flow 5-report skill-documentation + workflow-advantages

- **trace_source**: user=`e0014566`, host=`hfeg0pkn001` (10.129.2.10), session_file=`1787884599302_xoriz.messages.json`, match_count=158, domain=layout_virtuoso (B-档 synthesized candidate).
- **file**: 582 KB / 81 msgs (49 user / 32 assistant), agent=`lead`. 直接在 .75 上读 `/home/e0014566/.cline/data/sessions/1787884599302_xoriz/1787884599302_xoriz.messages.json`（**注意：cline 新格式是 `<sid>/<sid>.messages.json` 目录式，非 flat 文件**；旧扫描 summary 的 session_file 是目录内 basename）。
- **真实工具链**: `read_files`×7（读 4 个 SKILL.md + prompt_flow.md + 结果 CSV/Report）、`run_commands`×16（cat/ls flow_15/16/17 结果数据）、`editor`×24（写 5 份 markdown 报告到 `/home/e0014566/test_doc/`）。**无真跑 EDA 工具** —— 纯「读 skill 源 + 读结果数据 → 写报告」，属 **L1-boundary**（含定量数据提取，非纯散文）。

## 用户轮（逐字原文，仅掩 key/token）
- **UI#0 (idx 0, mode=act, 唯一意图轮)**：『帮我出这样的5份报告：1）请你仔细研读  ../test_layout_rscalc_flow_17/virtuoso-rtext-checkpoint-designer  这个skill, 然后出一份详细的说明报告。2）请你仔细研读  ../test_layout_rscalc_flow_17/virtuoso-rscalc-runner  这个skill, 然后出一份详细的说明报告。3）请你仔细研读  ../test_layout_rscalc_flow_17/virtuoso-autovia-runner  这个skill, 然后出一份详细的说明报告。4）请你仔细研读  ../test_layout_rscalc_flow_17/virtuoso-powerfill-runner  这个skill, 然后出一份详细的说明报告。5）请你结合  ../test_layout_rscalc_flow_15 , ../test_layout_rscalc_flow_16 , ../test_layout_rscalc_flow_17 , 这里面的结果，详细论述一下这个workflow 的优势，可以结合如下几个方面：a) 仔细总结这个workflow的优势，例如自动打点RTEXT 和 RNODE，利用AI分析layout, 自动寻找出需要计算电阻的点；流程自动化，串联起若干个agent skill 化的工具，且粒子化agent skill 可灵活配置到不同的workflow 中；利用agent 自身的优势，可以应付流程运行过程中可能出现的一些问题，出现问题、分析问题、解决问题、重跑流程，一站式解决。可配置迭代过程，一轮轮自动迭代，直到完整指定的目标，可对结果给出详尽分析。b) 对结果数据做出简明清楚的罗列，主要给出两组比较数据：第一组，优化前后的优化效果；第二组，比较优化后和一开始给出的原始layout的电阻情况，因为原始layout是人工优化的，需要突出workflow的优化比人工优化的要好。这个第5份报告一定要精明扼要，控制字数。a)这部分控制在250字，差不多总结出5点优势，每一点50个字左右。b) 直接给出两组数据的比较，并且简明扼要给出比较结果。』—— **纯需求 A-档 seed 候选**（只给目标 + 严格格式约束，未给根因/修复）。
- **UI#1 (idx 34, mode=act, 修正轮)**：『报告中不能有中文等乱码』—— 交付形态约束：无 mojibake / 编码乱码。**不作 A-档任务说明**（修正轮）。

## 真实产物与事实
- **4 个 skill 源**（agent 实读，路径 `/home/e0014566/test_layout_rscalc_flow_17/<skill>/SKILL.md`）：
  - `virtuoso-rtext-checkpoint-designer/SKILL.md`（27 227 B）—— 自动打 RTEXT/RNODE + checkPoints 设计，10 条已知陷阱规则，dbGetTrueOverlaps 验证。
  - `virtuoso-rscalc-runner/SKILL.md`（9 354 B）—— RsCalc 引擎跑电阻，common.config 单一参数源，多轮迭代 + 收敛判断 + bestCell 选择。
  - `virtuoso-autovia-runner/SKILL.md`（8 101 B）—— AutoVia via 插入，读 common.config 映射工具词汇。
  - `virtuoso-powerfill-runner/SKILL.md`（11 578 B）—— PowerFill fill，独立可配 + 可独立运行。
  - `prompt_flow.md`（19 702 B）—— workflow 总 prompt（串联 4 skill）。
- **结果数据**（flow_17，agent 实读用于 Report_5）：
  - `baseline_rpoints.csv`（26 行，24 非零，max=164.519，mean_nonzero=100.039，sum=2400.946）
  - `optimized_rpoints.csv`（26 行，24 非零，max=13.700，mean_nonzero=9.894，sum=237.455）
  - `original_input_rpoints.csv`（43 行，41 非零，max=50.706，mean_nonzero=12.851，sum=526.911）
  - CSV 行格式：`"net"_"layer"_x_y,value`（电阻值 Ohm）。
  - flow_17 即 BCenterCA：baseline max 164.52 → optimized 13.70（-91.7%）；optimized 13.70 vs original(manual) 50.71（-73.1%，workflow 显著优于人工）。
- **gold = 5 份报告**（agent 实写，`/home/e0014566/test_doc/`，用户接受）：
  - `Report_1_virtuoso-rtext-checkpoint-designer.md`（10 519 B）
  - `Report_2_virtuoso-rscalc-runner.md`（10 682 B）
  - `Report_3_virtuoso-autovia-runner.md`（7 756 B）
  - `Report_4_virtuoso-powerfill-runner.md`（9 150 B）
  - `Report_5_Workflow_Advantages.md`（4 805 B）—— **objective 核心**：
    - section a：5 点优势（每点 ~50 字，AI 自动打点 / 流程串联 / skill 粒子化复用 / 自愈错误处理 / 可配置迭代），用户约束 ≤250 字。
    - section b：两组比较 —— Group1 baseline vs optimized（3 flow 的 max/total R + 减幅% + 收敛率 + via 数）；Group2 optimized vs original-manual（max/total R + 减幅% + 逐点改善）。结论：workflow 匹配或超过人工（flow15/17 超过，flow16 持平）。
    - 无 mojibake。

## A-档 vs B-档判定
- UI#0 是纯需求 seed + 严格格式约束，末轮 UI#1 仅编码修正约束，**有用户干净接受的最终产物**（5 份报告）→ **A-档 feasible**。但本 shard 走 **B-档 synthesized**（与 r131/132/133 一致，单 Python deliverable + 10 hidden bundle），以获得强客观判分（散文报告 1-4 难客观打分，故 B-档把交付收窄为「读 bundle → 生成 5 报告」的脚本化形态，断言对准 Report_5 的格式 + 数值 + 编码 + 跨输入守卫）。
- 真 L2（真跑 Virtuoso + RsCalc）沙盒不可复现 → **L1-boundary**。

## 合成 case 设计（B-档，单 Python deliverable）
- **case_id**: `EDA-Eval-DesignFlow-RsCalcFlowReporter-001`
- **deliverable**: `rscalc_flow_reporter.py`（单文件 Python，CLI `<bundle.json>` / `--help` / 无参 exit 1）。读 bundle JSON，生成 5 份 markdown 报告到 stdout/`--outdir`。
- **bundle schema**：
  ```json
  {
    "flow_id": "test_layout_rscalc_flow_17",
    "design_name": "BCenterCA",
    "skills": {
      "virtuoso-rtext-checkpoint-designer": {"summary":"...", "key_tokens":["RTEXT","RNODE","checkPoints","dbGetTrueOverlaps"], "functions":["RL_IsAutoViaOrPowerFill","RL_FindAllCellsWithAutoCells"]},
      "virtuoso-rscalc-runner": {"summary":"...","key_tokens":["RsCalc","common.config","maxIterations","bestCell","targetReduction"],"functions":[...]},
      "virtuoso-autovia-runner": {"summary":"...","key_tokens":["AutoVia","via","common.config"],"functions":[...]},
      "virtuoso-powerfill-runner": {"summary":"...","key_tokens":["PowerFill","fill","common.config"],"functions":[...]}
    },
    "csvs": {
      "baseline": [["vss!","M4",-8466.4203,-565.33,118.611], ...],
      "optimized": [["vss!","M4",-8466.4203,-565.33,2.62753], ...],
      "original_input": [["vss!","M4",...,2.62757], ...]
    },
    "convergence": {"checkpoints_total":26,"converged":24},
    "vias_inserted": 0
  }
  ```
- **A（SUT 看）**: `inputs/prompt.md`（场景 + 5 报告规格 + section a ≤250字/5点 + section b 两组比较 + 无乱码 + CLI/退出码契约）+ `task_brief.md`（≤3 行交付接口）+ `bundle_A.json`（**真实** 4 skill summary/key_tokens + **真实** flow_17 三 CSV 行 + convergence/vias）。skill summary 从真实 SKILL.md 抽取（保留原 key_tokens，不造假），CSV 用真实行。
- **hidden B（10 个，嵌入 check.py，不进 SUT 沙盒）**：B1-B10，结构 ≠ A：
  - skill 名换成 `auto-via-inserter`/`rsmeter-engine`/`pwr-fill-runner`/`rnode-placer` 等（跨输入守卫：report 1-4 必须用 bundle 的 skill 名，不能硬编码 A 的 4 个 skill 名）；
  - CSV 数值集不同（不同 net/layer/x/y/value 分布）→ Report_5 Group1/Group2 数值必须从 B 的 CSV 算出；
  - 变体覆盖：clean-reduction / all-zero-baseline / saturated-vias(0) / bad-bundle(缺 csvs) / missing-skill / single-flow / 三 flow 不同 design_name / 收敛 100% vs 部分 / 原始优于优化的反转（验结论方向正确，不能盲报"workflow 优于人工"）。
- **gold 行为**：reporter 读 bundle → 报告 1-4 各引对应 skill 的 summary + key_tokens + functions（≥1 token 命中）；Report_5 section a 恰好 5 点 + section a 正文 ≤250 字符（中文按字符计）；section b Group1（baseline vs optimized，max/total R + 减幅%）、Group2（optimized vs original，max/total R + 减幅%）；结论方向由数据决定（optimized<original ⇒ workflow 优于；反之据实报）；无 U+FFFD/replacement char；exit 0 正常 / 1 坏 bundle + stderr / 2 AMBIGUOUS。

## 失败模式（教学点）
1. 硬编码 A 的 4 个 skill 名 → B 跨输入穿（report 1-4 用错 skill 名）。
2. 硬编码 A 的 flow_17 数值 → B 的 Report_5 数值与 B 的 CSV 不符。
3. section a 超过 250 字 / 不是 5 点。
4. section b 缺一组 / 数值算错（max vs mean 混淆 / 减幅% 公式错）。
5. 结论方向盲报"workflow 优于人工"（B 中反转 case 会穿）。
6. mojibake（U+FFFD / 乱码）未过滤。
7. 坏 bundle 未 exit 1。

## 断言清单（k≥8，与 check() 一一对应）—— 草案，落 jsonl 前对账
`12 条断言：①(a)zip 含 rscalc_flow_reporter.py + py_compile 通过 ②(b)--help exit0+usage；无参 exit1+stderr ③(c)B1 clean：生成 5 个 .md 文件名映射正确（Report_1..4 各对应 bundle 的 4 skill 名，Report_5_Workflow_Advantages）④(d)B1 报告 1-4 各含对应 skill 的 ≥1 key_token + skill 名（不硬编码 A）⑤(e)B1 Report_5 section a 恰好 5 点 + 正文 ≤250 字符 ⑥(f)B1 Report_5 section b Group1 baseline→optimized max/total R + 减幅% 与 B1 CSV 计算一致(容差) ⑦(g)B1 Group2 optimized vs original max/total R + 减幅% 与 CSV 一致 ⑧(h)B1 结论方向与数据一致(optimized<original ⇒ workflow 优于) ⑨(i)无 mojibake：5 报告无 U+FFFD、valid UTF-8 ⑩(j)跨输入守卫 B2(不同 skill 名 + 不同 CSV)：report 1-4 用 B2 skill 名 + Report_5 数值用 B2 CSV，stdout 不含 A 专属 token（virtuoso-rtext-checkpoint-designer/BCenterCA/164.519）⑪(k)B3 反转 case(original<optimized)：结论据实报"人工优于 workflow"而非盲报 ⑫(l)坏 bundle B4(缺 csvs) exit1+stderr+无 Report 行；确定性 B1 两次 stdout 一致。`

## 自验计划
- ref 解跑 check() PASS 12/12；§4.9 三假提交（空壳→a/只 print 期望串→c/参考解删核心[CSV 计算分支]→f）全 FAIL；negative_selftest 5 fake（fake_empty→a / fake_hardcode_a_skills→d / fake_hardcode_a_numbers→f / fake_always_workflow_better→k[B3 穿] / fake_section_a_overlong→e）全 FAIL。
- 随机化：B1/B2/B3 × 3 种子，verdict + exit + Report_5 数值稳定。

## 与既有区别
- RTextChkPlan-001（1787122756811_pj0ax，已落库）：RTEXT+checkPoints 配置生成（单 net 1 RTEXT + x 均匀分布 + rscalc.config patch），核心坑 label_layers vs metal_layers 选层。
- 本案 RsCalcFlowReporter-001：**5 报告生成**（4 skill 文档 + 1 workflow 优势对比报告），核心是 **Report_5 格式约束（≤250字/5点）+ 两组定量比较 + 跨输入 skill 名/数值守卫 + 结论方向**。主题/断言与 RTextChkPlan、AutoViaPwrFillRemove 完全独立。
- r133 AutoViaPwrFillRemove-001：autovia/powerfill cell 分类移除（case-sensitive VIA vs via）。本案不涉及 cell 分类。

## build checklist（下一轮 ~20 min 可完成）
1. 从 .75 拷 4 SKILL.md + 3 CSV 到 workdir，抽 summary/key_tokens/functions 构造 bundle_A.json（真实数据）。
2. 写 `rscalc_flow_reporter.py`（ref 解，~150 行：读 bundle、生成 5 报告、Report_5 算 max/total/减幅%、section a 5 点 ≤250 字、无 mojibake 过滤）。
3. 写 check.py（12 断言 + 10 hidden bundle B1-B10 嵌入）+ negative/（5 fake）+ negative_selftest.py。
4. 自验：ref PASS 12/12 + 三假 FAIL + negative_selftest NEG_RC=0。
5. 断言闸门对账：k_rationale=12 == k_check=12 ≥8 ✓。
6. 追加 EDA-Eval-DesignFlow_C.jsonl + mark --status case --case-id RsCalcFlowReporter-001 + 日报。
