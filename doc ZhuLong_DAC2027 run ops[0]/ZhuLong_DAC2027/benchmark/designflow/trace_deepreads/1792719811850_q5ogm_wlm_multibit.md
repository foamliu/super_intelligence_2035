# trace 深读笔记 — 1792719811850_q5ogm（e0045128 / hfeg0pkn001 / digital·synthesis）

- **会话**：1792719811850_q5ogm.messages.json（v3 目录式 `<sid>/<sid>.messages.json`，1.03 MB / 205 msgs / agent=lead / 2026-10-29 06:20 终）
- **工具分布**：synthesis:171 / netlist:21 / pyAether:7 / schematic:1 / innovus:1 → digital/synthesis 域（shard A）
- **真实任务主线**：用户在 kaidi.wang 的 `flow_pa_cpu_merged_top` 综合 log 里发现多 bit 寄存器 0% banking，多轮追问根因。最终定位：本跑是 **WLM（非 topographical）模式**，该 flow 的多 bit 银行化依赖 topo 下的 `identify_register_banks`（被 `shell_is_in_topographical_mode` 闸门跳过）；叠加 MB 库仅 2/4 位、522 候选多为 32/64/66 位宽总线无匹配单元、控制位不匹配、`set_multibit_options timing_only + critical_range 0.1` 偏保守。
- **关键证据**（来自 dc.log，原路径 `/rundata/lacaa/TV1_digital/simdir/kaidi.wang/feint/flow_pa_cpu_merged_top/logs/dc.log`，权限拒，从 trace 内 assistant tool_result 取回）：
  - L478/479：`Loading db ...DBCP51H180L6W25T5_MB_SVT...db` / `..._MB_LVT...db`（MB 库已加载）
  - L10637：`compile_ultra -gate_clock -scan`（无 -spg → WLM）
  - L15306-15315：`if {[shell_is_in_topographical_mode]} { identify_register_banks ... }`（topo 闸门）
  - banking 报告：15307 单 bit FF / 0 多 bit FF / 0%
  - RTL 推断表统计：MB=Y 522 / MB=N 663（AR=Y 417 / 无控制位 238 / AS=Y 8）
- **A 档选轮**：#130 (idx 130) 逐字原文『给一份 无物理库下 WLM 模式开启多 bit 的完整命令段』—— 纯「提出需求」，未指出根因/给修复 → 合 A 档选轮规则。
- **金标准**：assistant #131 给出的可参数化 DC Tcl 命令段（`set_app_var hdlin_infer_multibit default_all` + `set_multibit_options -mode $OPT_MODE -critical_range $CRITICAL_RANGE` + `remove_dont_use [get_lib_cells ${MB_LIB_PREFIX}/${MB_CELL_PATTERN}]` + `compile_ultra -gate_clock -scan`（无 -spg）+ `report_multibit -hierarchical` + `report_multibit_banking -nosplit`）。
- **A/B 差异**：A 用真实环境变量（DESIGN=pa_cpu_merged_top / MB_LIB_PREFIX=DBCP51H180L6W25T5_MB_SVT / MB_CELL_PATTERN=MB[24]SDF* / OPT_MODE=timing_only / CRITICAL_RANGE=0.1 / REPORTS_DIR=reports）；隐藏 B 结构全异（DESIGN=pa_dmem_top / MB_LIB_PREFIX=STD_MB_SVT / MB_CELL_PATTERN=MB[24]SD* / OPT_MODE=area / CRITICAL_RANGE=0.5 / REPORTS_DIR=rpt_b）→ 跨输入守护验证变量驱动非硬编码 A。
- **后续轮（context，不进 prompt）**：#132「目前不是topo，如何保证多位寄存器替换」、#134「查看合并失败原因」、#140「set_multibit_options timing_only + critical_range 0.1 是什么意思」—— 均为追问/根因讨论，违反 A 档选轮规则。
- **资产**：dc_log_excerpt.txt（log 关键摘录）+ mb_lib_context.txt（MB 库上下文）+ common_setup.tcl（A 真实环境变量）+ task_brief.md（交付接口）+ prompt.txt（#130 逐字原文）。无合成说明性注解。
