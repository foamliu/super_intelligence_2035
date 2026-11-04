# deepread — 1793244287787_11tjs (stephens@hfeg0pkn002, mc=139)

- **domain**: waveform (FineSim Monte-Carlo measure CSV analysis)
- **track**: A-faithful (U#0 逐字原文 = 提需求轮，未给根因/修复方案)
- **case**: EDA-Eval-DesignFlow-VmMhlAlterStats-001 (L1-boundary, 15 asserts)
- **session**: `/home/stephens/.cline/data/sessions/1793244287787_11tjs/1793244287787_11tjs.messages.json` (158 msgs, 699KB)

## U#0（任务说明原文）
> 读取这个路径下的.csv文件，分析每个.alter下VMHL和VMLH的min值和max值
> /rundata/ddgoa/V0/simdir/finesim/workdir/stephens/simulation/ddgoa_cmos_work_TB_domino_Receiver_rst0_stephens_schematic_ALPS/output_compare_final_mc2p2sigma

## trace 演进
- U#0 提需求（min/max per .alter）→ agent 写 report_vm.py：定位 `mc_index` 表头行，按 `alter#` 列分组，对 `vmlh`/`vmhl` 算 min/max/mean。
- U#38 用户要求核实 alter 3/4/5/6 温度（agent 之前误判全 25°C，实际 -40/130°C 混合）→ 修正。
- U#54 用户要求结合 control_mc_FS.sp 把 .alter 映射到 model corner → agent 加 corner/temp/VCC 映射表（超出 U#0 范围，属后续轮次演进）。
- U#90 用户要求去掉 vmlh_lv/vmhl_lv 两列。
- U#116 用户要求汇总成一张表。
- U#124 用户要求画散点图 → plot_vm_scatter.py → vm_scatter.png 保存到 /proj/ddgoa/.../ALPS/。

## 金标（用户接受的真实产物）
agent 的 `report_vm.py`（已 scp 读取，存 .75 workdir dump）。核心逻辑：
1. 读 CSV，跳过 `$`/`.` 开头行，定位 `mc_index` 表头；
2. `cm={h:i}` 按列名索引（非位置）→ 对 `alter#`/`vmlh`/`vmhl` 列；
3. 按 `alter#` int 分组，每组算 min/max/mean；
4. 输出汇总表（含 corner 映射，来自 .sp 解析）。

## 固化为 case
A-faithful 范围只取 U#0 的 min/max-per-alter 核心；corner 映射/画图属后续轮次，不进金标。
- 金标 = `analyze_vm_ref.py`：`python3 analyze_vm.py <csv>` → 写 `vm_alter_stats.csv`（alter#,N,vmlh_min,vmlh_max,vmlh_mean,vmhl_min,vmhl_max,vmhl_mean，alter# 升序）。
- 资产 A：合成 FineSim mt0.csv（6 alters × 120 rows，列 mc_index/alter#/run/vmlh/vmhl/vmlh_lv/vmhl_lv/temper，带 $/. 注释行）。
- 隐藏 B：8 alters × 80 rows，**mc_index 仍首列**（FineSim-faithful），但 alter#/vmlh/vmhl 移到非典范位置 + 额外 ramp 列 → 位置解析器读错列；取值/alter 数/行数全不同。
- check.py 15 条件 a-o：zip/compile/run+csv/header/8行升序/N==80/alter1 4 个 min-max/alter5 vmlh_min/alter8 vmhl_max/alter3 vmlh_mean（击败只算 min/max 的 stub）/跨输入护栏（B 8 alters 非 A 6、A 专属值不泄漏）/确定性 sha256。
- 6 negative 全 FAIL（empty→c / naive_hardcode_A→e / minmax_only→m / positional_parse→e或数值错 / no_output→c / syntax_err→b），§4.9 三假{empty,naive_hardcode_A,minmax_only} distinct{c,e,m}=3。

## 自验
- ref PASS 15/15；6 neg NEG_RC=0；test==disk sha256 roundtrip OK；k_rationale=k_check=15≥8 GATE PASS。
