# Deep-read: 1792636294858_tzf35 (e0035227 @ hfeg0plg55) — layout_virtuoso

**session**: `/home/e0035227/.cline/data/sessions/1792636294858_tzf35/`  · mc=86 · status=completed · 144 msgs
**keywords**: `virtuoso:1901;pex:68;.spi:51;schematic:40;netlist:18;verilog:4;pyaether:4;lvs:2` (virtuoso-dominant → shard C / layout_virtuoso)
**tool-use**: run_approved_command×27, editor×25, list_allowed_files×6, read_files×5, run_commands×1, ask_question×2

## 用户意图（8 个真实 user 轮，逐字原文）

- U#0 `/proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/BK/e0029308/STD_T_DBC_BASE_Symbol，帮我整理这个路径下的所有cell`
- U#1 `/proj/lacaa/TV1_DBC_Virtuoso/.../STD_T_DBC_DFF,这个路径的也列出`
- U#2 `.../STD_T_DBC_DFF_Symbol，这个路径的也列出`
- U#3 `.../DBCP51H180L6W25T5_BASE_SVT 和 .../DBCP51H180L6W25T5_MB_SVT，这两个路径下的也列出`
- U#4 `.../e0035227/DBC_180_seq，这个路径下的也帮我列出来`
- U#5 `同路经下的这个库中的STD_T_DBC_Latch，列出所有cell`
- U#7（**CLEAN produce-task seed**）`从之前K 库的结果中，你能帮我把所有的输入、输出signal pin以及power、ground pin和他们的类型、方向帮我整理一下吗`
- U#8 `/proj/lacaa/V0_Virtuoso_test/workdir/e0035227/FS204klib/FS204test1010/char_dir/ ，在这个路径下找`

## assistant 工具链 / 关键产物

逐路径 `list_allowed_files` + `run_approved_command`(python-runner) 列出 cell；最终对 K 库结果文件
`FS204test1010/Lib/FSP51H204L6W35T6_MB_SVT1010_tt_v0p75_25c.lib`（Liberty 格式）用 `parse_mb_final2.py`
逐 cell 提取 pin，并与网表 `.spi` 的 `.subckt` 校验一致，输出 pin 表。

## 金标准（末尾 assistant 接受的结果）

12 个 MB（多位 DFF）单元，自 K 库 .lib 提取的 pin manifest：
- **PG pin（所有 cell 相同）**：VDD(primary_power/power) · VSS(primary_ground/ground) · VPP(nwell/power) · VBB(pwell/ground)
- **MB2 族（6 cell）**：MB2SDFQD{1,2} in[CP,D1,D2,SE,SI] out[Q1,Q2]；MB2SDFRPQD{1,2} in[CD,CP,D1,D2,SE,SI] out[Q1,Q2]；MB2SDFSNQD{1,2} in[CP,D1,D2,SDN,SE,SI] out[Q1,Q2]
- **MB4 族（6 cell）**：MB4SDFQD{1,2} in[CP,D1,D2,D3,D4,SE,SI] out[Q1..Q4]；MB4SDFRPQD{1,2} in[CD,CP,D1..D4,SE,SI] out[Q1..Q4]；MB4SDFSNQD{1,2} in[CP,D1..D4,SDN,SE,SI] out[Q1..Q4]

## case 合成（B 档 · synthesized）

- **id**: `EDA-Eval-DesignFlow-LibPinManifest-001` · layout_virtuoso · L1 · k=15 a-o
- **A（可见）**: 合成 Liberty `stdcell_mb_A.lib`（12 MB cells，结构同金标准）
- **B/B2/B3（隐藏，结构不同 ≠ 改名）**:
  - B `stdcell_seq_B.lib`: 8 cell（DFFQD/DFFRPQD/DFFSNQD ×{1,2} + LATQD{1,2}），4 pg pin
  - B2 `stdcell_buf_B2.lib`: 6 cell（BUF{4,8,16,24}+INV{4,8}），**仅 2 pg pin (VDD/VSS)**
  - B3 `stdcell_logic_B3.lib`: 10 cell（AND2/NAND2 ×{D1,D2,D4} + OR2/NOR2 ×{D1,D2}），4 pg pin
- **check**: 候选 `extract_pins.py <lib>` → JSON manifest；check 在 3 组 hidden 上跑，验 cell_count/名称/input/output/pg(含 pg_type+direction)/input-output 互斥/signal-pg 互斥/无重复
- **15 条件 a-o**，3 negatives（naive/print_only/deleted_core）+ §4.9 三假提交（empty_shell/print_expected/name_only）全 FAIL，ref PASS ✓
- 自验：`python3 check.py` → REF self-test PASS；`negative_selftest.py` → ALL FAIL ✓
