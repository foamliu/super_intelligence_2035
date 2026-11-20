# trace_deepread · 1794981138434_k499q (e0039786 @ hfeg0pkn005, mc=439)

**session**: 1794981138434_k499q.messages.json (1.86MB, 515 msgs: 273 user / 242 assistant)
**user**: e0039786
**host**: hfeg0pkn005 (trace file lives on hfeg0plg54, accessible via .snapshot on pkn005)
**scan**: ssh_eda_search_20261120_145529/summary.tsv → summary_1120_reconstructed.tsv
**keywords**: hspice:499; pex:797; virtuoso:946; .gds:359; dbcreaterect:356; drc:168; lvs:159; calibre:89; techfile:53; netlist:104; cellview ( Glory PEX + Virtuoso layout + HSPICE characterization )
**domain**: spice_sim (B shard)

## 用户真实意图（任务流演进）

e0039786 在 CXMT 35H CFET DBC characterization 流上工作，搭建一个 **Glory 抽 DSPF 寄生网表 → HSPICE 仿真** 的闭环自动化工具，并配 GUI。session 是一个长迭代的构建过程：

1. **msg idx=0** (user): 上下文摘要 — 已完成 HSPICE 测试文件、DUT pcell、层号修正、GDS→IL 工具链
2. **msg idx=1** (user): 改 PARA_inverter2.il 修 DRC 报错
3. **msg idx=22** (user): 根据 /proj/lacaa/.../map 层定义 + 参考 .il 设计 DUT 实现不同电性测量
4. **msg idx=139** (user, 关键): 描述完整闭环 — glory 抽寄生网表(GDS→DSPF) → HSPICE 仿真 → 分析。要求 agent 自动生成 .il(打好 pin)→转 GDS→放 glory 路径抽 dspf→放 sp 路径跑 HSPICE
5. **msg idx=190** (user): 写交互式界面
6. **msg idx=344** (user): GUI 加 FS/DBC 模式选择 + GDS 选择 + sp 文件选择
7. **msg idx=425** (user, **本 case 焦点**): "在页面加一个选项：是否加*；如果勾选，则glory抽完网表后，会对网表中.SUBCKT + pin 这一行的行首加*, 以及把最后一行.ENDS 行首加*, 把这两行注释掉。"
8. **msg idx=474** (user): 修 bug — DBC gds 仿真却提交了 FS 的 run1
9. **msg idx=482** (user): GUI 加选择 run 文件路径选项

## 本 case 聚焦子任务 (msg idx=425)

用户要求在 GUI 加"是否加*"勾选，勾选后 Glory 抽完 DSPF 网表，把**外层 .SUBCKT（含 pin 行）**和**最后一个 .ENDS**的行首加 `*` 注释掉。目的：打开顶部子电路外壳，让 pin 名变成顶层节点，`.sp` 激励可直接引用。

### agent 实测 I/O 证据 (msg idx=435/439)

输入 `_sample.dspf` (8 行):
```
* DSPF 1.3
*|DESIGN sample
.SUBCKT sample_top G B        <- line 3 (first .SUBCKT)
C1 G B 1e-15
.ENDS sample_top
.SUBCKT nelvt_dbc G S D B W=1 L=1
R1 D S 1
.ENDS nelvt_dbc               <- line 8 (last .ENDS)
```

输出 `_comment_test.dspf` (line 3 + line 8 加 `*`，其余不变):
```
* DSPF 1.3
*|DESIGN sample
*.SUBCKT sample_top G B
C1 G B 1e-15
.ENDS sample_top
.SUBCKT nelvt_dbc G S D B W=1 L=1
R1 D S 1
*.ENDS nelvt_dbc
```

log: `comment_subckt: outer .SUBCKT@line3 and last .ENDS@line8 -> /home/.../ _comment_test.dspf (2 line(s))`

### 真实 Glory DSPF 实测 (msg idx=19 user 反馈)

```
[PASS] dspf: dbc_F3_removeV0G_removeM1_35H_DBC_PEX_GloryEX_Encrypted_V0d1_Rev07_TYPICAL.dspf
comment_subckt: outer .SUBCKT@line22 and last .ENDS@line554 -> /proj/lacaa/.../dspf (2 line(s))
[PASS] commented outer .SUBCKT/.ENDS in dspf
```

真实 DSPF 外层 .SUBCKT 在 line 22，最后一个 .ENDS 在 line 554（554 行网表，含大量寄生 R/C + 内层 device subckt 定义）。脚本只注释第一个 .SUBCKT 和最后一个 .ENDS，内层 device subckt 的 .SUBCKT/.ENDS 保持不动。

## 交付设计

- **case_id**: EDA-Eval-DesignFlow-DspfSubcktComment-001
- **deliverable**: `comment_subckt.py` (纯 Python stdlib)
  - CLI: `python3 comment_subckt.py <dspf> [--out <out>] [--no-bak]`
  - 找第一个 `.SUBCKT` 行 + 最后一个 `.ENDS` 行，行首加 `*`
  - 默认就地改 + `.bak` 备份；`--out` 写单独文件不动源；`--no-bak` 跳过备份
  - log 格式固定: `comment_subckt: outer .SUBCKT@line{N} and last .ENDS@line{M} -> {path} (2 line(s))`
  - 无 .SUBCKT/.ENDS → exit 1；文件不存在 → exit 2
  - 确定性（无时间戳/random）
- **asset A**: `dbc_F3_35H_DBC_PEX_GloryEX.dspf` (Glory 风格, .SUBCKT dbc_top G S D B @line7, 1 nested nelvt_dbc, last .ENDS @line22)
- **hidden B**: `fs_l6_35H_FS_PEX_GloryEX.dspf` (anti-hardcode-A: .SUBCKT nelvt_fs_l6 IN OUT @line9, 2 nested nelvt_fs/rpoly, last .ENDS @line25 — 行号/pin数/design名/nested数全异)
- **check.py**: 20 conditions (a..p3), ref 20/20 PASS, NEG 4/4 FAIL (naive_empty/print_only/core_removed/hardcode_a), 3-seed sha256 identical
- **layer**: L1 (纯 Python 离线复刻, 但 trace-faithful 于真实 PEX+HSPICE L2 流的子任务)

## dup 检查

4-shard ledger (load_all_shards) 排除后 k499q 仅 B 未动 (fresh)。user e0039786 在本 shard 此前无 case（NEW user for B shard）。
