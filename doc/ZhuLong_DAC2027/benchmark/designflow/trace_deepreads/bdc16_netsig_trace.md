# Deepread — 1788932274598_bdc16 (pjli / hfeg0plg06 / mc=159)

**domain**: schematic_netlist  **track**: A-faithful  **case**: EDA-Eval-DesignFlow-NetSigTrace-001

## 选轮
- U#2 (首轮真实需求): `top.Chip.I_PRAC_Performance_TB_0.I_RH_DLUT_FULL_PRAC_new_0.I_DLUT_CONTROL_PRAC_0.I_DLUT_PRAC_RHR_POINTER_LOCK_0.CKTBuf / 我想看这个信号，在这个网表里 /rundata/degpa/V0_CMOS/simdir/verilog/aocao/degpa_prac/wave/.../rhr_netlist.sv 和哪个(instance,cell)相连。请你用python实现`
- 干净 A-faithful「提出需求」轮（非根因/非修复）。后续 U#45/U#60/U#136/U#147 为增量增强（输入信号/hierarchy/def4/stdcell 底层），本 case 只取 U#2 核心交付。
- 金标准 = U#2 交付并被用户接受的核心 trace_signal.py（U#42 跑通，U#43 用户问"你把代码放在哪里了"=接受并使用，之后转入增强轮）。

## 深读要点 (163 msgs)
- 网表 `rhr_netlist.sv` 是 Cadence 风格门级结构化 Verilog：每个 `module` = 一个 cell，设计例化用 `CELL INST ( .pin(net), ... )` 语法；含 `specparam CDS_LIBNAME = "..."` 库名元数据。
- 层级映射: `top` → `Chip` (= 网表根单元 `PRAC_Performance_TB_shell`，在 top.sv 中例化为 Chip，top.sv 不在网表内) → `I_PRAC_Performance_TB_0` → ... → `I_DLUT_PRAC_RHR_POINTER_LOCK_0` → leaf cell `DLUT_PRAC_RHR_POINTER_LOCK`，目标 net `CKTBuf`（leaf 内部 net，非端口）。
- agent 实现路径: grep module / read_files 分段读 12k 行网表 → editor 写 `/home/pjli/Desktop/trace_signal.py`：
  1. `parse_netlist` 剥注释、正则匹配 module/endmodule、input/output/inout 端口、wire、`CELL INST(.pin(net))` 例化（连行合并到 `');'`）、`specparam CDS_LIBNAME`
  2. `find_root_modules` = 未被任何单元例化的 module
  3. `resolve_signal` 沿路径逐级 `modules[cur]['insts'][seg]` 匹配例化名→子模块；容许网表外前缀（`top`/`Chip` 在 root 段时入 external_prefix）
  4. `find_net_connections` 在 leaf module 枚举所有 inst 的 `.pin(expr)`，用 `net_references`（word-boundary，兼容 bus bit select `sig[2]`）匹配 net
  5. `pin_direction` 优先 cell 模块端口声明，回退 OUTPUT_PINS/INPUT_PINS 启发表
  6. `split_connections` 按 direction 分 drivers/loads/others
  7. CLI `--netlist --signal`，打印 hierarchy resolution + connections + total
- 后续增强（不进本 case 核心）: `@dataclass Connection`、`instance_input_signals`/`all_driver_input_signals`（U#45）、`resolve_net_hierarchy`/`build_hierarchy_scope`/`external_prefix`（U#60）、`directly_connected_signals`（U#136 def4）、`find_stdcell_drivers`（U#147 stdcell 库 'stdcells' 子串判定 + 非stdcell 下钻）。
- 真实 trace_signal.py 最终 715 行，已 scp 到 .75 workdir 参考。

## 资产合成（代表重建，真实网表 12k 行在 .75 不可移植）
- **A** `assets/.../netlist.sv`：根 TB_shell (→ext top.Chip) → PRAC_Block(I_PRAC_0) → DLUT_Leaf(I_DLUT_0)；叶单元内 `bufx2 I_buf0(.Y(CKTBuf),.A(n1))` 驱动 + `invx4 I_inv0(.A(CKTBuf))`/`ffsqx1 I_ff0(.D(CKTBuf),.Ck(clk))`/`nand2x1 I_nd0(.A(CKTBuf),.B(rst_n))` 负载 + `latrqx2 I_lat0(.Q(result),.D(n2),.Lat(clk),.vcc,.vss)` 次级网 + stdcell 定义带 `CDS_LIBNAME="stdcells_core"`。信号 `top.Chip.I_PRAC_0.I_DLUT_0.CKTBuf` → 4 连接(driver=1,load=3)。
- **hidden B** `hidden/netlist.sv`：根 PERF_Top (→ext top.Core) → SchedBlock(I_SCH_0) → LatchCell(I_LATCH_0)；`invx1 I_invx(.Z(SIG_RH))` 驱动 + `dffrqx1 I_dlatch(.D(SIG_RH))`/`mux2x1 I_mux(.S0(SIG_RH))` 负载；`CDS_LIBNAME="stdcells_io"`。信号 `top.Core.I_SCH_0.I_LATCH_0.SIG_RH` → 3 连接(driver=1,load=2)。结构/命名族均不同 → 跨输入护栏。

## check.py — 13 条件 a-m（k_check=13）
a zip+py_compile | b parse≥9模块含关键名 | c root=TB_shell唯一 | d resolve leaf/net/walked | e external_prefix top.Chip | f driver I_buf0/bufx2/Y/output | g 3负载 | h split 1/3/0 | i B roots/leaf | j B 驱动+A名不泄漏守卫 | k 3次确定性 | l 次级网 result→I_lat0/Q | m CLI端到端

## 自验
- ref（核心 trace_signal.py，参数化 parse/resolve/find）PASS 13/13
- 4 negatives ALL-FAIL distinct: fake_empty→b.1 / fake_print_fixed(硬编码A)→i.1(跨输入B守卫) / fake_core_deleted(find返回[])→f.1 / naive_no_dir(pin_dir恒unknown)→f.2；NEG_RC=0
- §4.9 三假 (a)fake_empty (b)fake_print_fixed (c)fake_core_deleted → b.1/i.1/f.1 distinct ✓
- test==disk roundtrip EXACT (sha 36de16d3...)
- k_rationale=k_check=13 ≥8 ✓
