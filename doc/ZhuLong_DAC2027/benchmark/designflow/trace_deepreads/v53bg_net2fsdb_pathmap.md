# trace_deepread: 1794897186406_v53bg (harrywu@hfeg0plg72, mc286, waveform/schematic_netlist)

**session**: `1794897186406_v53bg.messages.archive.json` (2.5 MB, 534 msgs)
**user**: harrywu @ hfeg0plg72
**keywords**: netlist:2323 / schematic:776 / analog:616 / waveview:443 / synopsys:... / cmos:619
**domain**: waveform (FSDB path mapping) + schematic_netlist (hierarchical netlist parse)
**ledger**: shard D, claimed r988, marked case `EDA-Eval-DesignFlow-Net2FsdbPathMapProduce-001`

## 真实用户意图（逐字）

**U#0（初始目标，act 模式）**：「做一个 python 可视化的工具 … 根据用户输入的两个信号 path 以及具体的边沿（rise0/rise1/fall0/fall1…），根据网表和波形逆向追踪整条信号链，需要将整条路径上的标准单元/模拟黑盒单元，每个单元输入输出的 delay 整理成表格 … FSDB 和 Netlist 路径映射 … FSDB 里面会一直追到上一次逻辑单元所在层级 …」

**U#514（聚焦子意图，act 模式，本案 A-faithful 取此轮）**：「重写 FSDB 和 Netlist 的信号 path 映射逻辑 / 如果在 Netlist 中，该信号在当前层下是作为 pin 脚进来的，那么 FSDB 地址里不会包含这一层，一直在 netlist 里面追到不是作为 pin 脚的那一层，才是 FSDB 真正的地址」

## assistant 工具链（关键产物）

- 复用 `/home/harrywu/.cline/skills/signal-chain-trace/net2fsdb.py`（FSDB 命名规律：`xi_` + cell 名小写去 `_lv` 后缀；信号名小写、bus `<n>` 保留）。
- 建 `TraceVizTool/{web.py, runner.py, trace.py, fsdb.py}`：
  - `trace.reverse_trace`：网表逆向追踪 + `on_node` 回调（进度面板）。
  - `fsdb.build_parent_index`：`sub -> (父 sub, 父实例对象)` 层次唯一索引。
  - `fsdb.fsdb_address`（U#514 重写核心）：**透传 pin 剥离 + 自顶层重建** — 只要 net 是当前层端口且层内 `find_driver` 为空（纯透传），就不进 FSDB 地址，向上追到真正驻留/被驱动层，自顶层重建地址（含顶层实例段 + 透传改名）。
  - `FsdbBackend.sample`：跑 finesim `.meas` over FSDB → `{rise:[...ns], fall:[...ns]}`。
  - 多输入标准单元/模拟黑盒的「判决」事件 → 前端高亮卡片。
- 解析 >8000 subckts（8201），start/end 信号解析（R_RasBase_lv,RasEnBnk / R_RasBnkLogic,SapEn2），导出 `web_standalone.html`。

## 验证（msg 526 测试输出，真实接受结果）

```
top.out      -> xi_top.out
leaf.zzz     -> xi_top.xi_leaf.zzz
leaf.inA     -> xi_top.y          # 透传 pin 剥离 + 改名为父层驱动网 y
```
`web_test.py` / `tests.py` 全通过；用户接受（msg 533 总结「已按你给的规则重写了 FSDB/Netlist 信号 path 映射逻辑」）。

## 合成 reframe 理由

- 真实网表 8000+ subckt（数 MB）+ 二进制 FSDB 不可入沙盒。
- 合成 5 级层级 SPICE 网表（A: INV_lv/NAND2_lv/STG_lv/MID_lv/TOP_lv；B: INVX/NOR2_lv/DRV_lv/CORE_lv/CHIP_lv），**保留真实结构特征**：位置引脚例化、`* output:` 声明驱动端口、透传 pin（输入端口且层内无驱动）、多级透传剥离、总线 `<n>`、FSDB `xi_` 命名规律。
- 判分范式：subprocess-on-B + exact-match-against-recomputed-ground-truth + 反硬编码（源码零 A/B 字面量 + 输出零 A-only token）+ 3-seed 确定性 + 退化守护。

## 与相邻 D case 区分

- r984 NetlistInstHierTrace：Verilog 网表 top-down 实例化父链追溯（named-port，找 path）。
- r985 DQDbusBitMapReconstruct：Verilog 网表位级映射参数推算。
- r986 SchHierParentLocate：schematic cell 库反向查父（DAG fan-in）。
- **本案 r988 Net2FsdbPathMap**：SPICE 子电路网表 → FSDB 地址映射，**透传 pin 剥离 + 自顶层重建**（方向：net→FSDB 地址；机制：driver-detected pass-through climb + 重命名 + 重建）；数据形态（SPICE .subckt 位置引脚）、算法（climb-to-driven）、输出（FSDB 地址串）均与上述不同。
