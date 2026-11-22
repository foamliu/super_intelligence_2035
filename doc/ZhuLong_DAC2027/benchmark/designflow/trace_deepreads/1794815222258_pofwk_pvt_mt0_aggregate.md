# Deepread — 1794815222258_pofwk — Multi-PVT FineSim deck gen + 3-level setup/width mt0 aggregation

- **session**: `1794815222258_pofwk.messages.json`
- **user / host**: reedchen @ hfeg0pkn002
- **match_count**: 127 (keywords netlist:173;hspice:15;cmos:813;schematic:494)
- **domain**: spice_sim (shard B)
- **case_id**: `EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001`
- **round**: r1037 (2026-11-22)

## Real task (trace summary)

reedchen 在 hfeg0pkn002 工作目录 `/proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_work_TB_DbusRcvLat_schematic_ALPS/` 下，要为 domino-receiver testbench `ddgoa_cmos_work_TB_DbusRcvLat` 生成多 PVT FineSim 仿真环境：

1. 依据共享模板 `template/template.sp` + PVT 矩阵 `/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/PVT_HighVolt.csv`（列 corner,vcc,temp），为每个 PVT 点生成一个 FineSim deck。模板含占位符需按 corner 替换：
   - `.lib 'model.sp' mos_<corner>` 对所有 corner 保留。
   - passive 库 `bjt_<corner>`/`res_<corner>`/`nicap_<corner>`/`diode_<corner>` 只在 tt/ff/ss 存在（incFile_lp 只有这三家 passive section）；sf/fs 这四行 `.lib` 注释掉（`* ` 前缀）。
   - `<corner>_array` 段（模板里的 `tt_Array` block）只有 TT 才有；非 TT 去掉/注释。
   - `.param ptemp=<temp>` / `.param pvcc=<vcc>` 按 PVT 行替换。
2. 每个 PVT 仿真产出 mt0（含三档 setup/width 测量 `TSetupLow/Mid/High` + `TSampWidthLow/Mid/High`）。
3. 参考一次 smoke-run 的 `sim_smoke/output/output.mt0.csv`，把其测量值作为 `ref_*` 列并进每个 PVT 行，聚合成 per-PVT 汇总表（列 `setup@low/width@low/setup@mid/width@mid/setup@high/width@high` + 6 个 `ref_*`）。

FineSim 版本 V-2023.12-1。agent 写了 `gen_multipvt_decks.py` + `parse_pvt_table.py` + runscript + SKILL.md，并对照真实 sim_pvt 9 corners 验证。U#124 后续把模板从单档升级到三档（low/mid/high setup/width），解析器重写输出 12 个测量列。

## Session flow (156 msgs)

- U#0：提需求（multi-PVT env 生成 + per-PVT mt0 聚合表）。
- agent 探目录、读 template.sp / SKILL.md（参考 `ddgoa_cmos_work_TB_domino_Receiver_rst0/skill/SKILL.md`）/ PVT_HighVolt.csv。
- 写 `gen_multipvt_decks.py`：corner block 替换（mos_<corner> 全保留；bjt/res/nicap/diode_<corner> 仅 tt/ff/ss，sf/fs 注释；`tt_Array`→`<corner>_array` 仅 TT，非 TT drop）+ runscript。
- 写 `parse_pvt_table.py`：聚合 FineSim `$DATA1` mt0.csv。
- U#124：模板升级三档 setup/width（low/mid/high），sim_smoke ref mt0，parser 重写输出 `setup@low/width@low/.../setup@high/width@high` + ref 列，对照 sim_pvt 9 corners 验证。

## Sandbox reachability

e0031982 @ hfhds201 无 `/proj` PDK 读权限 → L1 reframe：SUT 解析提供的 mt0 资产，不跑真实 FineSim/HSPICE。

## Reframe (case contract)

`pvt_flow.py`（纯 Python 标准库）两子命令：

- `gen --template T.sp --pvt P.csv --outdir decks/`：逐 PVT 行替换占位符、设 ptemp/pvcc、按 corner 启用/禁用 passive+array 段，产 `deck_<corner>_<vcc>_<temp>.sp` + `run.sh`。
- `parse --mt0dir mt0/ --ref ref.mt0.csv --outdir out/ --output pvt_table.csv`：从每个 `mt0_<corner>_<vcc>_<temp>.csv` 的 `$DATA1` 表头行定位信号名、读下一行数值，抽 6 个 TSetup*/TSampWidth*，每文件一行，加 6 个 ref 列，按文件名排序。

## A / B design

- **A**（visible, dir_A）：7 corners（TT 0.8/25, SS 0.9/-40, SS 0.85/130, FF 0.82/-40, FF 0.74/130, SF 0.9/-40, FS 0.85/130）；template_A：netlist-include `netlist`、.tran 100p 100n、阈值 0.4/0.6/0.8；7 mt0 + ref_A.mt0.csv + example_output（decks + pvt_table_A.csv）+ task_brief.md。
- **hidden B**（reference/inputs_B）：6 corners **全异**（TT 0.75/85, FF 0.88/0, SS 0.72/125, SF 0.88/0, FS 0.72/125, TT 0.92/-25）；template_B：netlist-include `netlist_rx`、.tran 50p 80n、阈值 0.375/0.5625/0.75；6 mt0 + ref_B.mt0.csv。**anti-hardcode**：A 的 46 个 mt0 数值 token 无一出现在 B（程序校验 leak=[]）。

## check.py (k=10)

①pvt_flow.py 在 zip 内 ②py_compile 通过 ③gen 在隐藏 B 实跑 exit0 且产 6 deck + run.sh（击破 empty stub）④TT deck 保留 mos_tt+bjt_tt+tt_array ⑤SF deck 的 bjt/res/nicap/diode 四行 `*` 注释且无活动 _array 行 ⑥parse 在 B 6 mt0 上实跑产 6 行（击破 print-only）⑦表含 12 个 setup/width+ref 列（击破 core-removed 漏 ref）⑧B 的 TT_0.75_85 setup@low ≈ 1.111e-10（A 的 1.234e-10 不在 B，击破 hardcode-A）⑨gen+parse 连跑 3 次 md5 一致（确定性）⑩所有 deck 无残留 `@CORNER@/@PVCC@/@PTEMP@/@PASS_/@ARRAY_LINE@` 占位符。

## Self-verify

- ref solution `pvt_flow.py` → check.py **PASS 10/10** ✓
- 3 negatives (empty / print-only / core-removed) → 全 FAIL (2/10, 2/10, 2/10) ✓
- anti-hardcode leak check：A 46 tokens vs B 文本 → leak=[] ✓
- 3-seed 确定性 ✓（assertion 9）

## Distinctness

vs 现存 PVT/Mt0-named cases（32 个）：本 case 是**端到端 deck-gen + 三档 mt0 聚合 + ref 列并表**的组合，区别于单点 mt0 解析或单 PVT deck 生成。

## Ledger

`trace_ledger_B.tsv`: 1794815222258_pofwk claimed → case `EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001`. B.jsonl 525 → 526.
