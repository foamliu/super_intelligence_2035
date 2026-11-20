# Deepread — sid 1786066403760_tgnc6 (RsCalc+AutoVia+PowerFill 电阻削减流)

- trace_source: user=e0014566, host=hfeg0pkn001, session=1786066403760_tgnc6.messages.json, match_count=251, mc keywords=netlist:541/hspice:120/calibre:68 (tools col)
- N=140 msgs; agent cline lead; WORK_DIR=/home/e0014566/test_layout_rscalc_flow_9 (also _7/_8 referenced)
- USER#0 原文（唯一意图轮）: `read the prompt_flow.md and do the job in it.` — 其余 user 轮为 tool_result 回灌 / "继续"。任务全文在 /home/e0014566/test_layout_rscalc_flow_9/prompt_flow.md（用户编写的 flow spec）。
- 真实任务（来自 prompt_flow.md）: **Resistance-Reduction Flow** — 降低 power-net layout 寄生电阻（IR drop），循环 RsCalc(测当前 R) → AutoVia(插 via, 写 via-merged cell) → PowerFill(填 power rail, 写 final merged cell) → RsCalc(复测)，直到**每个 check point** R_i(p) <= R_0(p)*(1-targetReduction) 或达 maxIterations。最终交付 = 电阻显著降低的新 layout cell + 报告。
- 关键产物（agent 实写）:
  - `adaptive_tuner.py` — 自适应参数调优（解析 .rvn → per-check-point R；分析 layout；生成 adaptive_plan_iter<N>.json；多维调优：net 覆盖/via 升级/fill 升级/平台检测/并行度/divMetRatio）
  - `gen_final_report.py` — 最终报告（load baseline_rpoints.csv + iterN_rpoints.csv → 逐点收敛判定 → best cell 选择 → 表格输出）
  - `baseline_rpoints.csv` / `iter1_rpoints.csv` / `iter2_rpoints.csv` — 每 check point 的 `key,resistance`（key=net_layer_x_y）
  - common.config (targetReduction=0.3, maxIterations=3, cellName="testpg1_opt2" 末态), rscalc.config, run_autovia_config.il, run_powerfill_config.il
- **.rvn 格式**（真实 RsCalc 输出, /proj/train/AI_Virtuoso/ver/rscalc/e0014566/testa/RSDB_*/<net>.rvn）:
  ```
  LV+RSView:NodeList,3
  1,38,"vdd","M1",5.5498,-2.1450,5.5503,-2.0200,"vdd",5.5500,-2.0825,16.7159996,,,,,,,,,0
  ```
  CSV, 跳过 `LV+RSView` 头；field[2]=net, field[3]=layer, field[4]=x, field[5]=y, field[11]=resistance（R, Ohm）。key=`net_layer_x_y`（awk $3_$4_$5_$6 即 field[2]_[3]_[4]_[5]）。
- **收敛判定**（prompt_flow.md §3 + gen_final_report.py）: for EVERY check point p, R_i(p) <= R_0(p)*(1-targetReduction)。failCount = 超 threshold 的点数；converged = total - fail。best cell = failCount 最小的 iter（bestFailCount）；failCount==0 → 全收敛 SUCCESS。
- **教学点 / 失败模式**（用于判分设计）:
  1. .rvn 解析必须跳 `LV+RSView` 头 + NF>=12 + col12 非空（错解：正则文本匹配 / 漏跳头）
  2. key 必须用全 key（net_layer_x_y），不可只 net_layer（会合并不同 y 的点）— gen_final_report.py 注释明确
  3. 逐点收敛（不是只看 max R）— prompt_flow.md §3 "Every check point must be optimized, not just the max"
  4. best cell = 最小 failCount（不是最小 max_R）；回归 iter 不影响 best
  5. 空 .rvn（仅头行，单节点 net 零 check point）→ 0 点，不报错
  6. baseline 有但 iter 缺的 key（新点）/ iter 有但 baseline 缺的 key → 收敛判定处理
  7. 跨输入守卫：B 用不同 design/nets，验 stdout/报告不含 A 专属 token（testa/austin_rscalc2/M1 那组点）— 防 hardcode A
  8. 确定性：同输入两次 JSON 逐字节一致
  9. 退化：仅 baseline 无 iter / 坏 .rvn（col12 非数字）→ 跳行不崩
- 选 trace 理由: pg_layout 域最低覆盖(20/135)，e0014566 是非 xinqiaoz 用户（去 diversify，前 12 条候选多为 xinqiaoz PDK QA），真实多工具 L2/L3 layout flow（virtuoso RsCalc/AutoVia/PowerFill + .rvn 真实格式）。合成 B 档 L1（判分用真实 .rvn 格式离线解析，无需跑 virtuoso，确定性）。
- 域: pg_layout（power fill + IR drop 电阻削减流编排）。
