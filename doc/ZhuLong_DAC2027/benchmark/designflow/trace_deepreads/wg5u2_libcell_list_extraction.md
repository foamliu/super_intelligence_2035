# wg5u2 深读笔记 — lib_cell.list 抽取（schematic_netlist 域）

- **trace**: `1791611498731_wg5u2.messages.json` · user `zjqiao` · host `hfhds201`(=hfhds211) · mc=728
- **meta**: model deepseek-v4-flash · cwd /home/zjqiao · status completed · 399 msgs(206 user/193 assistant) · 285 tool_use(read_files 126 / editor 37 / list_allowed_files 22 / run_commands 5 / run_approved 4 / RAG 4)
- **唯一实质性 user msg**（idx 0）：「我提供cell list文件和netlist，你帮忙输出lib_cell.list文件，文件格式为Library Cell，netlist内部格式为 `* Library : drvqa_cmos_io / * Cell : IO_DqLdMdl / * View : schematic`，输出文件为 `drvqa_cmos_io IO_DqLdMdl`，生成脚本，cell list 文件为 /proj/drvqa/V0/simdir/finesim/drvqaF/Netlists/netlist_lat，网表文件为 .../Netlist_Vcap_.../netlist，输出到 /home/zjqiao 下」——其余 205 user msg 全是 tool_result，无新指令。

## 真实数据格式
- **cell list** (`netlist_lat`)：每行 `* Cell    : <NAME>`，一行一 cell（latrqLx1 / latqLx1 / latrqGSx1 / latsqLx1 / latrq2_ckUnit / latsqnLx1 / latqIOLVx1 / ... 约 45+ 行 latch/ff 类 cell）。
- **netlist** (`.../netlist`)：147MB hspice/ALPS 格式，由 Empyrean `emy2netlist` 生成（`emy2netlist "drvqa_top" "WOWTOP_1C2A" "config_Vcap_trans" -t mhspice ...`）。每个子电路块前有注释头：
  ```
  * Library : drvqa_cmos_io
  * Cell    : IO_DqLdMdl
  * View    : schematic
  .subckt IO_DqLdMdl <ports>
  ... instances/MOSFETs ...
  .ends IO_DqLdMdl
  ```
- **netlist.log**（emy2netlist 日志，在 /rundata/.../simulation/.../netlist.log）含 `Exporting design "<lib>/<cell>/<view>"` 行，是另一份 lib→cell 映射源（80+ unique：drvqa_cmos_digital / drvqa_cmos_analog / stdcells_ac / TECHLIB / drvqa_cmos_io）。
- **库**：drvqa_cmos_io / drvqa_cmos_digital / drvqa_cmos_analog / stdcells_ac / TECHLIB（+ agent 后期凭命名猜的 drvqa_cmos_stdcells，未在 log 确认）。

## agent 流程（4 个脚本版本，逐版退化）
1. **build_lib_cell.py (idx 213)** — 正确雏形：读 cell list 收集 `* Cell :` 名；读 netlist.log 的 `Exporting design "<lib>/<cell>/<view>"` 建 cell→lib；cell list 中每个 cell 输出 `<lib> <cell>`，未找到输出 `UNKNOWN`；按 `sorted(cells)` 排序。**问题**：依赖 netlist.log（非任务指定的 netlist 文件）；UNKNOWN 不符合「只列存在项」；sorted 改了序。
2. **build_lib_cell_final.py (idx 306)** — 退化：放弃 log，改为**硬编码命名前缀**判库（latrqIOLV*/ffrqIOLV*→drvqa_cmos_stdcells，6 个 digital_cells→drvqa_cmos_digital，其余→stdcells_ac）。**这是陷阱**：前缀表是从 A 的具体 cell 名归纳的，换一批 cell 名立即失效。
3. **gen_output_list.py (idx 344/346)** — 同 v2 硬编码前缀，输出 `lib cell`。
4. 末尾反复 editor 写 `/home/zjqiao/lib_cell*.list`（lib_cell.list / lib_cell_final.list / lib_cell_clean.list / lib_cell_output.list）——agent 在对输出文件做手工修整/去重/排序，没再回到解析法。

## 关键洞察（合成 case 的牙）
- **正确解**：直接解析 netlist 文件的 `* Library :` / `* Cell :` 注释头，按 netlist 块序建 (lib, cell) 映射；对 cell list 中每个 cell，输出其在 netlist 中出现的所有 `<lib> <cell>` 行（块序、去重）；cell list 有但 netlist 无的 cell 略去。
- **陷阱牙**（agent 真踩）：硬编码命名前缀→库的映射在隐藏 B（不同 cell 名/库名）上必崩；print A 的固定输出在 B 上必崩；依赖 netlist.log 而非 netlist 文件→B 无 log 时崩。
- **结构牙**：每个输出 `Lib Cell` 必须对应 netlist 里一个真实 `.subckt <Cell> ... .ends` 块（结构一致性，非文本相似）。
- **歧义牙**：同一 cell 名可能出现在两个不同库（两个块）→ 必须输出两行 `LibA Cell` / `LibB Cell`，不能折叠。
- **排除牙**：cell list 有但 netlist 无 → 不输出；netlist 有但 cell list 无 → 不输出。

## 难度判定
- L1（离线 Python 解析真实 EDA 网表产物，无 calibre/hspice/Virtuoso 真跑）。faithful 的 L2 钩子不存在（任务本质是文件解析，无 EDA 工具调用）。
- 作为 schematic_netlist 域扩量#2（与 Schematic-001 的 abstract→physical cell 变换是不同子场景），属补牙扩量；§5 L1 配额偏高的取舍见 MEMORY。

## 合成方向（LibCell-001）
- A（可见）：cell_list_A.txt（12 cell，`* Cell :` 格式）+ netlist_A.sp（~15 个 `* Library/* Cell/* View` + `.subckt` 块，5 个 drvqa_* 库，含一个跨库 cell + 一个 cell_list 有但 netlist 无的 cell）+ task_brief.md（真实 prompt + CLI + 输出格式 + 纯标准库 + 错解清单 + 隐藏泛化提示）。
- B（隐藏，assets/hidden/，不进 SUT 沙箱）：cell_list_B.txt（8 cell，不同名）+ netlist_B.sp（~10 块，libX_* 库，含一个跨两库 cell + 一个 ghost cell + 额外非 list cell）+ hidden_manifest.json。
- reference：gen_lib_cell.py（解析法，纯标准库 ASCII）+ check.py（12 条件 a-l，subprocess 真跑候选于 B + 独立重解析对比 + 结构 .subckt 校验 + 3 随机种子子集一致性）+ reference_submit.zip。
- negative：naive_prefix（硬编码前缀→e/h FAIL）/ naive_emit_all（无视 cell list→g FAIL）/ naive_print_A（打印 A 输出→e FAIL）+ empty_shell / ref_core_deleted（§4.9 三假）+ negative_selftest.py。
