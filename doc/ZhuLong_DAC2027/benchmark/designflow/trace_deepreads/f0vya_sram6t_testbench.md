# trace_deepread — 1793174925139_f0vya (e0030760 @ hfeg0plg74, mc410)

- **session**: 335 msgs, 1.76MB, scp ssh cat (e0031982 默认身份可读 e0030760 home)
- **domain**: analog_context (SRAM 6T bitcell, Iread/Iwrite, RNM/WNM) — shard D
- **A-faithful 提需求轮**: U#0 (msg#0)「我需要根据现有的model建立简单的一个SRAM 6T单元的testbench，并仿真PMOS不同VDD对Iread和Iwrite的影响，应该怎么做？」干净表达目标，无根因/无修复方案 → 选为任务说明
- **user turns (3)**:
  - U#0 (msg#0): 提需求 — SRAM 6T testbench + PMOS VDD 扫描 vs Iread/Iwrite
  - U#2 (msg#43): 「用中文跟我交流」语言偏好（非交付）
  - U#3 (msg#146): 扩展 — 读 /proj/lacaa model，VDD 0.75→0.5，加 WNM/RNM/Iread/Iwrite，存 /home/e0030760/Documents/SRAM_6T_testbench，不改 lacaa（refinement，不进 A 档 prompt）
- **agent 工具链 (178 tool calls)**: list_allowed_files → read_files → run_approved_command(hspice) → editor 写 .sp/.py。两阶段：
  - 阶段1 (msg#0-145) /home/e0030760/Desktop/hspice_test/sram_iv/：sram_read.sp/sram_write.sp/sram_vtc_read.sp/sram_vtc_write.sp/run_sram_iv.py — 6T cell(psvt_fs PU nfin=1 / nsvt_fs PD nfin=3 / nsvt_fs PG nfin=2)，VDD 0.75→0.50 扫描，hspice 跑瞬态+VTC 蝶形，compute_snm 45°旋转最大内接方
  - 阶段2 (msg#146-334) /home/e0030760/Documents/SRAM_6T_testbench/：run_puvdd_sweep.py(426行) + 6Ttestbench_PUvdd.sp + bitcell_ch336_pu.sp — PU rail 独立扫描 0.85→0.40，hc_pu_fs/hc_pd_fs/hc_pg_fs，WSNM 走 write-trip VCELL-Vtrip
- **gold 抓取**: ssh cat 阶段1 5 文件 (sram_read.sp 45行 / sram_write.sp 45行 / run_sram_iv.py 190行 / 6Ttestbench.sp) + 阶段2 run_puvdd_sweep.py 426行。/proj/lacaa model 路径 e0031982 无权读 → 不依赖具体 model
- **接受**: U#3 后 189 msg agent 工作无用户再纠正 → 隐式接受最终 SRAM_6T_testbench 产物
- **case 合成**: EDA-Eval-DesignFlow-SRAM6TSweep-001 (L1-boundary, track=faithful, domain=analog_context)
  - 资产 A (SUT 可见): prompt.txt(U#0 原文) + task_brief.md(≤3行交付接口) + config_A.json(gold 真参: psvt_fs/nsvt_fs, nfin 1/3/2, VDD 0.75→0.50, /apps/imctf/35H lib, sram_metrics_vs_vdd.csv)
  - 隐藏 B (不进 SUT): config_B.json(结构不同: hc_pu_fs/hc_pd_fs/hc_pg_fs, nfin 2/4/3, VDD 0.90→0.60 7点, /proj/sramlib/B06 lib, sram_metrics_vs_puvdd_B.csv, tran 0.02n/50n)
  - ref: gen_sram6t_tb.py 参数化生成器，读 config.json → outdir 输出 5 文件(4 sp + run_sram_iv.py)，run_sram_iv.py 含 tofloat/parse_mt0/compute_snm(45°旋转)/wtrip/write-trip/7列CSV
  - check.py 15 条件 a-o，ref PASS 15/15 · 4 negatives ALL-FAIL distinct{empty→c / print_fixed_A→d / core_deleted→i / naive_no_sweep→h} · §4.9 三假(c/d/i) distinct ✓ · k_rationale=k_check=15 ✓
- **去重**: D.jsonl 65 行无 SRAM6T 主题，无同 session → 无重复
