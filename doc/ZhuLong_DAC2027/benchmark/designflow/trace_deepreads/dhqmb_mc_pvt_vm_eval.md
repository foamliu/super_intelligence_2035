# Deepread: dhqmb — reedchen Monte-Carlo PVT Vm 达标评估 (characterization)

- **Trace**: reedchen @ hfeg0plg93, session `1793082564833_dhqmb.messages.json`, mc=102, domain=characterization.
- **Size**: 503 KB, 121 msgs (69 user / 52 assistant). Single real user_input turn (rest tool_results).
- **Tool chain**: list_allowed_files / read_files / run_approved_command / editor — agent wrote `gen_sp_mc.py` + `parse_mc_passrate.py`.

## User intent (verbatim, A-faithful)
- **U#0 (msg 0)**: "帮我跑多个PVT的蒙卡仿真，收集Vm数据评估达标成果" — on domino Receiver `_rst0` PVT 蒙卡特征化任务，工作目录 `/rundata/ddgoa/.../ddgoa_cmos_work_TB_domino_Receiver_rst0_stephens_schematic_ALPS/`，输入件 template / vm_target.csv / netlist。先构建计划确认后执行。= CLEAN produce-task ✓ (proposes goal + spec, no root-cause given).

## Real accepted result (trace-documented; assets permission-denied to e0031982)
Agent produced two scripts (extracted via editor new_text):
- **gen_sp_mc.py** — 按 `vm_target.csv` 每个 corner 在 `template.sp` 上正则替换：`.temp` → temp, `.param ptemp` → temp, `pvcc`/`pvintbus` → voltage, `.lib` → corner lib, `.tran` sweep, `monte=N`, `.param mis_flag=1`, `sigmaflag=SIG`；产出 `mc_<tag>.sp` + bsub runscript；`tag=<corner>_<vt(voltage)>V<temp>C`（vt 规则: "0.8"→"8", "0.83"→"83", "1.2"→"1p2", "1"→"1"）。
- **parse_mc_passrate.py** — 解析 `output_<tag>.mt0.csv` 的 `VMLH_rst0`/`VMHL_rst0` 列，按 `vm_target.csv` 的 `[vm_min, vm_max]` 区间统计 pass（error 行计为不通过），输出 per-corner + TOTAL 报告。pass-rate 公式: `rate = 100 * pass / (valid + err)`。
- 真实资产在 `/rundata` reedchen 目录，e0031982 无权限读取 → 按 trace 记录的 deck 结构 + gen_sp_mc.py 输出日志合成代表性资产（B-track synthesized）。

## Case decision: EDA-Eval-DesignFlow-McPvtVmEval-001
- domain=characterization, track=B (synthesized; trace-faithful prompt), level=L1 (单文件 Python 脚本 gen/eval 两子命令, stdlib only).
- **Deliverable**: `mc_pvt_vm_eval.py` — CLI 两子命令：
  - `gen <template.sp> <vm_target.csv> <out_dir>` — 按 vm_target.csv 每个 corner 在 template.sp 上正则替换 → 产出 `mc_<tag>.sp`（tag 同 trace 规则）。
  - `eval <vm_target.csv> <output_dir> <out_report.txt>` — 解析 output_*.mt0.csv 的 VMLH/VMHL，按 [vm_min,vm_max] 统计 pass，error 行计不通过，输出 per-corner + TOTAL 报告 (rate=100*pass/(valid+err))。
- **资产 A**: vm_target.csv (5 corners: TT/FF/SS × 0.8/0.88/0.95/1.0/1.2 V, -30~120℃), template.sp (含 .temp/.param ptemp/pvcc/pvintbus/.lib/.tran monte/.param mis_flag/sigmaflag 占位), task_brief.md, output_format_spec.txt.
- **隐藏 B1**: 4 corners (TT_75V40C/FF_7V120C/SS_88V-30C/TT_9V85C) + 4 output_*.mt0.csv + template_b1.sp. 不同 V/T 于 A 的 5 corners.
- **隐藏 B2**: 3 corners (SS_95V-25C/FF_65V110C/TT_1p0V60C) + 3 output_*.mt0.csv + template_b2.sp. 反硬编码: N=500/SIG=6.0/queue=normal/prefix=run/model_B2.sp, values ≠ B1.
- **reference**: mc_pvt_vm_eval_ref.py (复刻 gen_sp_mc.py build_sp 替换逻辑 + parse_mc_passrate.py pass-rate 公式, stdlib only).
- **check.py**: 14 断言 (a-n): zip 含 mc_pvt_vm_eval.py / py_compile / B1 eval exit0 出报告 / per-corner pass-rate 正确(独立 _expected 重算) / TOTAL pass-rate 正确 / error 行计不通过 / B1 gen exit0 出 mc_*.sp / B1 gen tag 命名规则正确 / B2 eval (反硬编码, 3 corner ≠ B1 4 corner) 报告正确 / B2 gen tag 正确 / 跨输入 A≠B1≠B2 / 确定性 3-seed 一致. subprocess 真跑候选在 B1+B2, _expected() 独立重算不硬编码.
- **自验**: ref PASS 14/14 + 6neg (naive_empty/hardcoded_a/only_gen/empty_shell/ref_core_deleted/wrong_pass_formula) 全 FAIL NEG_RC=0 + §4.9 三假 (empty_shell/only_gen→ /hardcoded_a → /ref_core_deleted) 全 FAIL + 断言门 k_rationale=k_check=14≥8 ✓ + test 字段与盘上 check.py 字节同步 (sha1 4a5fcc55e050, 20522B).
- k_rationale = k_check = 14 ≥ 8 gate PASS.
