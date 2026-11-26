# 9j9rp — reedchen@10.129.2.11 (mc141, n=163, analog_context)

## U#0 (msg#0) 逐字 — A-faithful 纯提需求
> 请你帮我总结这个目录下
> /proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_work_TB_domino_Receiver_rst0/
> 各个仿真目录的所有报告，统计成汇总性的报告
> 报告的内容包含
> 所有仿真版本扫描的尺寸集合
> 所有仿真版本中，每个PVT各自的vm标准，vm实际数据最小、平均、最大值以及通过率
> 汇总的各PVT通过率，并且报告是否有全部PVT都通过的尺寸组合
> 所有的数据都在报告里以表格形式呈现

U#44: `/proj/.../ddgoa_cmos_work_TB_domino_Receiver_rst0_1/` 现在要你在这个目录下做同样的事情
U#67: `/proj/.../ddgoa_cmos_work_TB_domino_Receiver_rst0_2/` 现在要你在这个目录下做同样的事情
（U#1-43, U#45-66, U#68-88 全是 tool_result，非真实 user 轮）

## trace agent 演化
- list_allowed_files 枚举 sim_root 子目录（Add_vcap_for_Pre_log / sim_regression_v2/v3 / sim_domino_adjst / sim_domino_adjst_opt 等），policy 重定向 /proj → /rundata。
- 每个仿真版本子目录含 `optimization_report*.txt`。check_grades.py 解析单报告：
  - `Corner: TT 0.8V 25C`（PVT corner：proc / volt / temp）
  - `Target Vm: 20...`（vm 标准/spec）
  - MOS params（p_width / n_width / nf）= 尺寸集合
  - 每 corner 实测 vm + Verdict（PASS/ACC/FAIL）
  - `PASS or ACC in ALL 5 corners: Count: X`、`passing ALL corners: Count: Y`
- 写 summarize_sim_reports.py（多次 editor insert/edit），输出 "DOMINO RECEIVER SIMULATION - CROSS-VERSION SUMMARY REPORT"：
  - 所有版本扫描的尺寸集合
  - 每 PVT：vm 标准 + 实测 min/avg/max + 通过率
  - 汇总各 PVT 通过率
  - Cross-corner: "PASS in ALL 5 corners" / "PASS or ACC in ALL 5"
  - 全部 PVT 都通过的尺寸组合
- 对 rst0_1（summarize_rst0_1.py）、rst0_2（summarize_rst0_2.py）重复。

## 关键事实（合成金标依据）
- 报告结构：header（version + MOS params）→ 多 Corner 块（Corner / Target Vm / Measured Vm + Verdict）→ footer（PASS-or-ACC-in-ALL / passing-ALL 计数）。
- vm = voltage margin（domino receiver 瞬态仿真测得）。
- PVT corner = (proc, volt, temp)，5 个 corner（TT/SS/FF × volt × temp）。
- "通过率" = PASS 数 / 总测量数（per PVT）。
- "全部 PVT 都通过的尺寸组合" = 某 version 的所有 corner Verdict==PASS。

## 合成决策
- 真实 /proj /rundata 报告经 policy 不可附加 → **B-grade synthesized**。
- 资产 A = 合成 sim_root/（多 version 子目录 + optimization_report_v*.txt，忠实结构）。
- 金标 gen_sim_summary_ref.py（CLI `<sim_root>` → stdout 表格汇总报告）：扫子目录 → 解析每报告 → 聚合 per-PVT vm 标准/min/avg/max/通过率 + 全部尺寸集合 + all-PVT-pass 尺寸组合 → ASCII 表格输出。
- 隐藏 B / B2：不同 version 集 / 不同 PVT corner / 不同 vm 值 / 不同尺寸，反硬编码 + 跨输入 guard。
- domain = analog_context（analog sim 测量聚合）；L1（离线 Python 解析报告）。
