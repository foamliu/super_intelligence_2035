# 设计上下文与已验证事实（PrimeTime STA signoff）

## 设计
- 模块 `addr_to_rowcol_v7`（纯组合，107 实例 / 116 网络，DRAM 工艺 cxmtG5_CIP）。
- 布线后网表 `postroute.v`（Innovus 23.32 saveNetlist -excludeLeafCell，**无 PG 版本**）。
- 寄生 SPEF `routed.spef`（StarRC W-2024.09，116 个 D_NET）。
- 约束 `mapped.sdc`（set_max_delay 0.5 ns，N[8:0] → row/col/valid）。
- 时序库 `data/ss_text.db`（库名 `SS_0p98_m40c`，93 个单元，由 lc_shell U-2022.12-SP6 从 ss_text.lib 编译）。

## 已验证环境事实（须在交付脚本/launcher 中正确编码）
1. **`link_path` 必须设为库名 `SS_0p98_m40c`**（或 db 路径），**不得为 `"*"`** —— 在此 PrimeTime (U-2022.12-SP5) 中 `link_path "*"` 配合 `read_db` 会 link 失败（LNK-049/LNK-005）。
2. **用 `read_db` 加载 .db**，**不得用 `read_liberty`** —— 此 PT 无 `read_liberty` 命令。
3. **launcher 须 `env -u LD_PRELOAD`** 后再启动 pt_shell —— 受污染的 LD_PRELOAD 会导致 PT/StarRC 启动异常。
4. **license 环境变量**：`SNPSLMD_LICENSE_FILE=27000@hfds4:12000@hfds4`，`LM_LICENSE_FILE` 同值。
5. **corner 不匹配须在 README 如实披露**：提取用的 nxtgrd 是 **TYP 98C**，而 Liberty 库是 **SS_0p98_m40c (-40°C)** —— 二者角点不一致，报告须标注（正确配对应是匹配角点的库或 98C 的 nxtgrd）。

## 须产出的标准 signoff 报告（写入 $OUT_DIR）
- `pt_global.rpt`：report_global_timing（全局 setup/hold WNS/TNS/NUM）。
- `pt_timing.rpt`：report_timing -max_paths ≥5 -input_pins -path_type full（关键路径含 cell/net delay 拆分）。
- `pt_crit_path.rpt`：report_timing -max_paths 1 -path_type full_clock_expanded -nets（最差路径明细）。
- `pt_design.rpt`：report_design（设计/角点/约束属性）。
- `pt_viol.rpt`：report_constraint -all_violators -max_delay（所有违例端点 + slack）。
- report_annotated_parasitics（寄生回注覆盖，日志走 parasitics_command.log）。

## 流程顺序
read_db → set_app_var link_path → read_verilog $NETLIST → current_design $DESIGN → link_design → read_sdc $SDC → read_parasitics -format spef $SPEF → report_annotated_parasitics → report_global_timing → report_timing → report_design → report_constraint -all_violators → exit。
