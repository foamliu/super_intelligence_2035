# Deepread: tsmkj — hier_cellname produce

- session_file: `1794982770571_tsmkj.messages.json`
- user: dechaoc / host: hfeg0pkn004
- mc: 33 / keywords: `netlist:183;verilog:42;drc:19;cadence:6;aether:6`
- domain: schematic_netlist (shard D)
- round: r1223
- case_id: `EDA-Eval-DesignFlow-HierCellnameTraceProduce-001`

## Real task (verbatim intent)

用户 dechaoc 手上有参考脚本 `/rundata/drcpa/V0/simdir/verilog/wenzhuod/0728/netlist/hier_sig`，
该脚本按**信号名**检索 Verilog 网表里的层次路径。用户要仿照它写一个新脚本 `hier_cellname`，
两处改动：

1. 改成按 **cell 名（module 类型名）** 检索——`./hier_cellname <网表> <cell名>`，
   找网表里所有 `module 类型 == 给定 cell 名` 的例化点。
2. 每条输出层次路径里把 `DDR5TOP` 替换为 `TOP.Chip`。

agent 产出的 `hier_cellname.py` 核心流程：
- 去注释 → 解析 `module ... endmodule` 块
- 解析例化语句 `Type [#(...)] inst [array] (...);`（Type 非 wire/reg/input/output/assign 等关键字，数组 `[3:0]` 原样保留）
- 建层次树（未被任何 module 例化的 = root）→ DFS
- `Type == cell 名` 则输出层次路径（root + 各级 inst 用 `.` 连接，`DDR5TOP → TOP.Chip`）
- 匹配例化继续向下递归不停止（多深度同 cell）

## 可离线判分内核（本 case 抽取的）

Verilog 网表 module/例化解析 + 层次树构建 + cell 名例化检索 + 路径拼接 +
`DDR5TOP → TOP.Chip` 替换 + 多深度同 cell 递归 + 例化数组保留 + 确定性。

## A/B 设计

| input | target cell | expected paths | 考察点 |
|---|---|---|---|
| A (visible) | `AG_VdbiasActCtrl_IPD` | `TOP.Chip.I_vbias_top`, `TOP.Chip.I_mid0.I_vbias_mid`, `TOP.Chip.I_mid1.I_vbias_mid` | 1 top-level + 2 under I_Mid siblings |
| B1 (hidden) | `IO_ZqTop` | `TOP.Chip.I_zq0`, `TOP.Chip.I_dq0.I_zq`, `TOP.Chip.I_dq1.I_zq` | 1 top-level + 2 under DQQuad siblings；含 LBDQ `I_lb[3:0]` 例化数组（非目标，必须不出现）|
| B2 (hidden) | `BiasGen` | `TOP.Chip.I_bg0`, `TOP.Chip.I_sub0.I_bg1` | 同 cell 在 depth1（I_bg0）和 depth2（I_sub0.I_bg1）；DAG 无自例化 |

A 与 B 的 target cellname / 层次形状 / 深度 / 例化数组存在性均不同 → 结构性不交叉，
`hardcode_a` 负样本在 B1 上必 FAIL（A 的 3 条路径 ≠ B1 期望）。

## 12 条断言（k_check=12）

①submit.zip 含 .py 脚本 ②B1 跑通 exit0 非空 ③B1 路径集合严格相等 ④B1 每行 `TOP.Chip` 开头
⑤B1 无 `DDR5TOP` ⑥B1 行数==3 ⑦B1 不存在 cell 名无输出（真过滤）⑧B1 三次 md5 一致
⑨B2 路径集合严格相等 ⑩B2 深层 `I_sub0.I_bg1` 存在 ⑪B2 浅层 `I_bg0` 存在（DFS 不停首匹配）
⑫B2 无 `DDR5TOP` 且每行 `TOP.Chip` 开头

## 自测

- reference `hier_cellname_ref.py`：12/12 PASS
- 4 负样本（empty_stub / print_only / core_deleted / hardcode_a）：全部 FAIL
- round-trip（提取 case JSON 的 `test` 字段为 wrapper → 调 check.py）：reference PASS、4 neg FAIL
