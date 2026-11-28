# Deepread — 1795682504254_iz1k7 (gallopc@hfeg0pkn005, mc=231)

**Domain**: schematic_netlist (D). **User**: gallopc. **Trace**: 329 msgs (177 user / 152 assistant), 1.56MB.

## 真实任务

用户从 fullchip 仿真抽取某 bank (`XDecGap`) 的 PWL 激励文件 `xdecgap_bot.sp`（WaveView 导出，格式 `V<sig> <sig> 0 PWL(...) +)`），但信号名全是 **fullchip 顶层信号名**（`ra109_b2<3>` / `secg_i<6>` / `ctrl_near` / `mux_in<2>` / `ena_top` / `fnncspcs_edgesec0<7>` 等 115 个），不是 bank 输入 pin 名，无法直接用于 bank 单独仿真（`.SUBCKT XDecGap` 只认自己的 pin 名）。

## 根因 + 解法

激励信号名在 chip 顶层，bank pin 在好几层层次之下（`Array1G_Top_W → m1G_TOP_W/E → XIXDECGap`），名字对不上。映射须**沿网表层次一路往下追**：
- 网表里 `.SUBCKT <cell> <pin...>` 定义有序端口表，例化行 `XI<inst> <net...> <cell>` 的 net 列表与 cell pin 列表**按位置一一对应**；
- 在父层例化把 `net[k]` 连到子 cell 的 `pin[k]`；进到子 cell 内部，端口用 pin 名当 net 名；
- 从顶层信号 net 出发 → 找父层 net 列表含该名的例化 → 取该位置 pin → 进子 cell 用 pin 名继续追 → 直到例化 cell == `XDecGap`，该 pin 即信号驱动的 bank 输入 pin。

助手定位真正的 perbank fullchip 网表（119MB，含全部 115 激励信号名，在 `ddgoaF/MatrixRun_Netlist_Vcap_20261123PM/.../B2/.../netlist`），写 `trace_to_bank2.py` 层次追踪。

## 三种情况

1. **唯一映射**：一信号追到 1 个 bank pin（`ra109_b2<3>` → `Ra109Bot`，路径 `Array8G_W --XI_Array1GBK2--> Ra109_Near<3> --XI_m1G_TOP--> Ra109Bot<3> --XIXDECGap--> XDecGap.Ra109Bot<3>`）。
2. **多 pin 扇出**：同一波形同时驱动多个 bank pin（`secg_i<6>` 同时驱动 `SecGBot` + `SecGTop`）→ 改名文件里**每个 pin 复制成一个独立 PWL 源**（波形不变只改名）。98 信号映射到 150 个 pin（46 唯一 + 52 双 pin Bot+Top）。
3. **追不到**：信号经 mux `XI95<*>`（mx2Nx1 两输入）/ buffer 的器件级连接，纯层次追踪穿不过去（`fnncspcs_edgesec0<*>` 16 个 + `pwron3o`，共 17 个）→ **原样保留**原名。验证过 `XDecGap` 根本没有 `*edgeGap0*`/`*PwrOn3*` 这类 pin，它们是 SaCtrol 的上游信号。

最终改名激励 167 PWL 源（150 bank pin + 17 原样保留）+ `trace_report2.txt` 映射报告。

## Case 合成（synthesized-reframe, LIVE-NA, judge_layers=[L0,L1]）

把「沿 119MB 真实网表追层次改名」reframe 为 **spec-JSON 驱动纯 Python 层次追踪改名器** `rename_stim_signals(spec)->report`，无真实 EDA 二进制依赖。

- **spec schema**: `{target_cell, top_parent, hierarchy:{cells:{<cell>:{pins:[...]}}, instances:[{inst,cell,parent,nets:[...位置对齐 cell pins...]}]}, stimulus:[{name, pwl:[[t,v],...]}]}`。
- **trace**: 从 (top_parent, signal) 起，扫所有 parent 匹配的例化，net 命中位置 k → pin=cell.pins[k]；cell==target → 记 terminal；否则递归 (cell, pin)；收集所有 terminal（多 pin 扇出=多 terminal；dead-end=空）；(parent,net) visited 防环。
- **A**(visible, spec_A.json): 5 信号 / 3 层(ChipTop→ArrayBank→XDecGap)。`ra109_b2<3>`→`Ra109Bot`(唯一)；`secg_i<6>`→`{SecGBot,SecGTop}`(双 pin 扇出)；`ctrl_near`→`CtrlBot`；`mux_in<2>`→unresolved(经 Mux21 dead-end，原样保留)；`ena_top`→`Ena`。summary 5/4/1/6 blocks。含 distractor 例化 XI_XDec2(第二条 XDecGap，接 SecG→SecGTop 制造扇出)+XI_Mux(非 target，吃掉 MuxIn)。
- **hidden B**(spec_B.json, token-structurally 不同): 6 信号 / 4 层(SysTop→ArrL1→ArrL2→DecBuf)。`cas_i<1>`→`{CasB0,CasB1,CasB2}`(**tri-fanout** 3 pin)；`rst_top`→unresolved；其余唯一。summary 6/5/1/8 blocks。不同 cell/net/signal/pin 名 + U_Lat(Latch) distractor。A 硬编码器在 B 全错。
- **reference** `rename_stim_signals.py` 递归 DFS spec 驱动通用实现（_validate 必填→malformed valid=False+errors；_trace 递归+visited 防环+dedupe；_fmt_block `V<name> <name> 0 PWL( <t> <v>... +)`）。
- **check.py 15 conds(a-o)**：判分**独立 BFS 复算**(vs 候选递归) mappings+summary 再断言候选匹配：a zip 含 py ②b py_compile ③c A valid+errors空+字段齐 ④d A summary==GT(5/4/1/6) ⑤e A mappings==GT BFS 复算 ⑥f secg_i<6>→{SecGBot,SecGTop} ⑦g mux_in<2> unresolved pins空 ⑧h renamed_sp 可解析+块数==6+块格式 ⑨i 块名集合==期望(mapped pin 各一次+unresolved 原名一次) ⑩j 每块 PWL 点==源信号 pwl(波形不变) ⑪k malformed(stim 空/nets-pins 不匹配/缺 target_cell/inst 引用未知 cell)→valid=False+errors 非空不抛 ⑫l B valid+B mappings==GT BFS 复算 ⑬m B 反硬编码(B summary==GT 且 ≠A 8 vs 6+B mappings≠A) ⑭n 源码无 A 专属字面量 token ⑮o B report 无 A 专属字面量 token。
- **自验**: ref PASS check.py(15/15)；5 negatives 全 FAIL(distinct 首败标签 a/c/d/l，hardcode_a 走到 l B-反硬编码闸门)；check_sha256 三方同步(meta==test==disk)；k_check==k_rationale==15。
