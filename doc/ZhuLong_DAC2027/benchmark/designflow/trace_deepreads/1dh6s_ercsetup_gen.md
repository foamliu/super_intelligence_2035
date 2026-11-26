# 1dh6s — ERC ercSetup.tcl 生成（e0031668 / hfeg0pkn003, mc=389）

trace: `/home/e0031668/.cline/data/sessions/1790064242187_1dh6s/`，220 msgs / 9 substantive user turns / agent=cline / 模型 deepseek。

## 用户意图演进（逐字原话，仅掩码）

- **U[0]**（act）："我现在有一份已经填好电压值的表格`/home/e0031668/work/ERC/drcpa/res/volt.csv`，包括 path，net，netName，voltage，part；我会给你一个示例 ercSetup.tcl`/apps/imctf/cad/cck_utility/projsets/drcpa/V0/ercSetup.tcl`，该示例 tcl 仅提供格式参考，该 tcl 里的数据都不可信，不可参考数据；我需要你结合输入表格内容和示例 tcl 格式，在 `res/` 下产生一份符合该表格内容的 ercSetup.tcl，要求内容完全符合电压表格，不要进行编造，不要对输入的两个文件做任何修改。"
- **U[24]**（act，纠正）："你生成的 ercSetup.tcl 里面的 cellName 是怎么确定的，我看到里面还有 i0 这样的，光靠 drcqa_volt.csv 能完成吗，我给你提供 spice netlist`/home/e0031668/work/ERC/drcpa/netlist`，你一定要按照 netlist 里的 cell，port，net 名来写这个 tcl，示例 tcl 只是让你参考下语法，不要参考任何数据和变量。"
- **U[76]**（plan）："这是 cck 带着之前你写的 res/ercSetup.tcl 跑的时候报错错误 log：`/proj/drcpa/V0/simdir/erc/DDR5TOP_20260819_AI/run_erc2.log`，你检查下现在这个 tcl 还有没有问题，如果有的话在 res/下再写一个 ercSetup_check.tcl。"
- **U[128]**（plan，加约束）："我现在希望每个 cell 尽量少地使用 intNet，希望把 intNet 的 pin 能够找到其下面的 cell 出 pin 单独写一条出来，即尽量写成单个 cell 单个 pin，在调整的时候，你还是要保证所有 cell，port 都严格遵照之前给你提供的 spice netlist。"
- **U[184]**（plan，解释）："好的，我想让你给我讲讲，你是怎么从 csv 的 net 找到对应的 cell 和 port 的，可以按行给我举几个例子。"

## 真实 artifacts（仍在 .75 /home/e0031668/work/ERC/drcpa/）

- `res/volt.csv`：160 行（1 header + 159 data），列 `num,Path,net,netName,voltage,Part,`（尾逗号）。Path 是实例层次路径（点分），netName 是网络名，voltage 形如 `0.5V`/`541mV`/`5`/`0V/1.8V`/`0/1.17V`/`-0.2V`/`652.57mV`。
- `netlist`：36MB / 353k 行 SPICE 网表（含 `.subckt` 定义 + `Xinst nets... cell` 实例）。
- `res/ercSetup.tcl`（最终版 125 行）：`set forceVoltDict { ... }` 字典，每条 `cellname { port { net1 v1 net2 v2 ... } }` 或 `cellname { port {...} intNet { net v } }`。共 117 cells / 169 port 条目 / 1 intNet 条目（`r_sanenc_sactrol_neg_drv` 的 `vdleqenn`，无法下钻）。
- `res/ercSetup_check.tcl`（125 行）：同上 + 头注释记录 "117 cells, 169 port entries, 1 intNet entry"。
- 助手产出脚本：`/tmp/gen_erc.pl`（仅 csv，U[24] 前被否）→ `/tmp/gen_erc2.pl`（csv + netlist，正解，已清）。

## 核心算法（从 trace 还原 gen_erc2.pl）

1. **解析 netlist**：`%cell_ports{cell}{port}=1`（`.subckt NAME ports...`），`%inst_cell{parent\x00inst}=child`（`Xinst nets... cell` 行，实例名去前导 X）。继续行（`+` 开头）拼接。
2. **解析 volt.csv**：逐行 `(num,Path,net,netName,voltage,Part)`。
3. **voltage 归一化**：`541mV→0.541`、`0.5V→0.5`、`5→5`、`-0.2V→-0.2`、`0V/1.8V→{0 1.8}`、`0/1.17V→{0 1.17}`、`652.57mV→0.65257`。
4. **(cell,port) 解析（intNet 最小化）**：沿 Path 实例链下钻；在每一层判断 `netName` 是否为当前 cell 的 port；若是 → 用 `(cell, netName)`；若否 → 找当前 cell 内连接到 `netName` 这个父级 net 的子实例（按位置映射到子 cell 的 port 名），下钻到子 cell 继续判断；若钻到底仍无 port → 在叶子 cell 上记 `intNet{netName}=voltage`。
5. **聚合**：同一 `(cell,port)` 多行 → 若电压一致则标量，若不一致则范围 `{v1 v2}`。
6. **cellname 归一化**：小写、去前导 `I_`、去 `_IPD`/`_243`/`_221` 等数字/IPD 后缀（实例→cell 名取自 netlist `.subckt` 名，已是小写）。
7. **emit**：`set forceVoltDict {\n\t\tcell { port { net v ... } }\n\t\t...\n\t}`，cell 字典序，port 保 .subckt 原始端口顺序。

## 选料判断

- **domain**：schematic_netlist（SPICE 网表解析 + 层次实例下钻）。
- **level**：L1（离线 Python 解析网表 + csv → 生成 tcl，不调 EDA 商业工具）。
- **track**：B（合成缩比 netlist + 派生 csv，保真算法与格式；真实 netlist 36MB 不宜直接做资产）。
- **金标准**：trace 末尾用户接受的 `ercSetup.tcl` + `ercSetup_check.tcl`（真实产物，已 scp 回）。算法按 gen_erc2.pl 还原。
- **断言只对事实**：tcl 字典结构 / cell 集合 / port 分布 / intNet 计数 / 电压归一化值 / 范围聚合 / 下钻解析正确性。🚫 不对措辞。

## 合成缩比 netlist 设计（A/B 各一份）

需覆盖的行为：① netName 是叶子 cell 的 port → port 条目 ② netName 不是叶子 port 但能下钻到子 cell port → 下钻 ③ netName 是中间层 cell port → 中间层 port ④ netName 钻到底无 port → intNet ⑤ mV/V/裸数/负数归一化 ⑥ 同 (cell,port) 多电压 → 范围 ⑦ cell 字典序 ⑧ port 保序。
