# mk098 — spice_sim HSPICE AC-capacitance .lis result parser

> 深读记录：本轮(11-10 23:4x) shard-B 交付轮。11-05 令 hspice-dominant top-250
> diff（broader filter: hspice≥10, no ratio gate）→ 12 un-ledgered → peek top 10
> by mc → mk098 CLEAN produce-task。前 4 候选(of6ff/my769/27c6f/i6fn6)全 reject
> (consultation/devops)，后 6 候选 peek → mk098 CLEAN。

## 候选筛选

cand_hspice_top250（hspice≥10, top-250 unique, summary.tsv 20261109_224902）diff
ledger_B → 12 un-ledgered：my769(27c6f/i6fn6/of6ff/mw3vr/ki1x0/mk098/nrep6/tpnqx/
q5xew/h14an/zh03r)。peek 10：
- my769 (e0017906@pkn002, mc=620)「你对模拟电路有没有什么好的分析方法」→ consultation, reject
- 27c6f (jason17w@pnd002, mc=187) DDR/LPDDR run-regression skill 优化 → devops, wrong-shard, reject
- i6fn6 (jcgu@pin003, mc=184)「你能获取到当前我打开的aether进程吗」→ consultation, reject
- of6ff (mengxind@pjn185, mc=89)「请帮我分析昨天的仿真状态」→ consultation, reject
- nrep6 (thqu@hfeahpc503, mc=1) DOE tapered driver optimization skill 设计 → meta-skill, reject
- tpnqx (thqu@hfeahpc503, mc=1) DOE 结果汇总表 → viable but 与 nrep6 同项目, 次选
- q5xew (kenwang@plg16, mc=2) DRC pattern QA SKILL 生成 → layout, wrong-shard, reject
- mw3vr (sophiaw@plg09, mc=28)「提交tck_clk.sp 仿真」→ 与 ayl62 同项目 dup, reject
- ki1x0 (chengk@plg74, mc=27)「梳理代码逻辑整理流程图」→ code review, reject
- **mk098 (yazhuok@hfeahpc501, mc=21, hspice:61) CLEAN produce-task ✓**

## mk098 深读（yazhuok, 67 msgs, 336KB）

### 会话结构
- U#0 (msg0) 原话：「@model_check_DRDXQ.sp 我用这个单管仿真激励跑完之后的结果在 result_wibls/ 文件夹中，
  我该如何阅读以及查看我的结果，请把我的结果整理成文本的形式」= CLEAN produce-task ✓
- assistant msg1-34：探查 result_wibls/ 目录（result.ac0/ic0/lis/pa0/st0）+ data_wibls + model_check_DRDXQ.sp，
  写 parse_wibls.py（parse_data_file + find_index_blocks + parse_block + merge + build_report），
  run_approved_command(python-runner) 跑通，修 2 bug（测量值 trailing space + 双块去重合并）
- U#35 (msg35)「把 result_wobls 也一并解析，二者都生成我可以直接复制的文档」
- assistant msg36-64：泛化 parse_sim_results.py（处理 wibls+wobls，输出 *.txt + *.csv + wibls_vs_wobls_cap.csv），
  跑通生成 5 文件
- U#65 (msg65)「这些结果是从哪个文件中提取出来的？」→ 回答 result.lis（咨询收尾）

### 仿真内容
- HSPICE 单管 AC 电容仿真：器件 ntk_hwl_m（W=0.050u L=0.055u nf=1, tt 角, temp=98°C）
- 模型库 /proj/drdqp/V0/model/current_PF_v0d1_Rev06/model.sp (tt_array)
- AC 分析 100kHz 单频点，测 Cgg/Cgd/Cgs/Csg（.print ac cgg_dut_ ...）
- .DATA data_wibls / data_wobls：11 点 (vbl, vnc, vwl) 负载线扫描（亚阈值→强反型）
- result.lis：每 data index 两块 = ①工作点块(+0:d/+0:g/+0:s 节点电压 + **** mosfets 段 vgs/vds/vth/id/gm/gds/cgs_m/cgd_m/cdtot/cgtot/cstot) ②AC 测量块(cgg_dut_/cgd_dut_/cgs_dut_/csg_dut_ name 行 + 下一行 freq+value)

### 可提取确定性交付物
**HSPICE AC 电容 .lis 结果解析器**：读 .DATA 偏置文件 + result.lis → 按索引合并双块 → 输出文本报告 + CSV。
纯文本解析，不真跑仿真。gold standard = parse_sim_results.py（双块合并 + report + csv）。

## case 设计：EDA-Eval-DesignFlow-SimCapLisParse-001

- domain: spice_sim / synthesized / L1 k=15
- deliverable: sim_cap_lis_parse.py（CLI 4 参 `<data_file> <result.lis> <out_report.txt> <out_csv>`）
- 资产 A: data_wibls(11 点) + result_wibls.lis(11 索引×2 块) + task_brief.md + output_format_spec.txt
- 隐藏 B1: data_b1(9 点不同偏置) + result_b1.lis(9 索引)
- 隐藏 B2(反硬码): data_b2(同 B1 偏置) + result_b2.lis(电容值经 1.15/0.85/1.10/0.90 缩放, ≠ B1)
- reference: sim_cap_lis_parse_ref.py（parse_data + find_index_blocks + parse_block + merge_blocks + build_report + build_csv, stdlib only）
- check.py 15 断言(a-o: zip含py/py_compile/B1 exit0+report+csv/B1 header 12列/B1 9行/B1 cgg/cgd/cgs/csg match _expected/B1 vgs/vds/vth/id match/B2 exit0/B2 cgg match _expected_b2 反硬码/B2 cgd match/missing input non-zero/determinism 3x md5)
- subprocess 真跑 B1+B2+det×3，_expected 用 model() 独立重算（同 gen_assets 公式）
- 自验: ref PASS 15/15 + 6neg(naive_empty/hardcoded_a/only_print/ref_core_deleted/empty_shell/no_merge)全 FAIL NEG_RC=0 + §4.9 三假(empty_shell/only_print/ref_core_deleted)全 FAIL + 断言门 k_rationale=k_check=15≥8 ✓ + test 字段与盘上 check.py 字节同步(sha1 e5c8a90d8df2, 9746B)
- claim+mark mk098 case；jsonl B 245→246, ledger covered 246→247(spice_sim 198→199), claimed 1→0
- 真实 result.lis 在 /rundata/drdxq（e0031982 无权限）→ 按文档化 .lis 结构 + 确定性电容 model 合成代表性资产
