# trace_deepread: la00c — Verilog 按 module 拆分为 per-cell functional 文件

- **session**: `1793600858808_la00c` (e0029308 @ hfeg0pkn001 / 10.129.2.10, mc=5367)
- **archive**: `/home/e0029308/.cline/data/sessions/1793600858808_la00c/1793600858808_la00c.messages.archive.json` (JSONL, ~1MB, 3127 msgs, 250 user msgs)
- **domain**: schematic_netlist (Verilog netlist 拆分)
- **A-faithful prompt 轮**: **U#9**（首个提需求轮，逐字原文）：
  > 我现在只有现成所有Cell放在一起的.V，没有一个一个Cell的functional文件，能帮我写个脚本批量生成AMS仿真需要的functional文件吗
  - 纯提需求（给目标：从合并 .V 批量生成 per-cell functional 文件），未给根因/修复。A 档前提成立 ✓
  - 后续澄清/转向轮（U#10 "说回AMS仿真"、U#12 选用 OCEAN、U#18 一键仿真、U#25 finesim 方案 A、U#37 ZN 不变、U#41 "我看了波形没问题"接受 finesim 仿真）**不进 prompt**。
- **trace 演化**：
  - U#0–U#8：用户先问 AMS 仿真网表识别 → OCEAN 批量方案 → 模板文档 → functional 文件位置/批量生成方法。
  - **U#9（A 档 prompt）** → agent 写 `split_verilog_to_functional.py`（M157，两模式：`--mode import` 调 Cadence ncimport/xrun -import；`--mode files` 纯 Python 按 module 拆分写 `<dest>/<CELL>/functional/verilog.v`；`--mode dry` 只列 module）。核心逻辑：`strip_comments`（去 `//` `/* */`）→ `split_modules`（regex `^module\s+(\w+)` / `^endmodule`，depth 计嵌套）→ 每 module 写一个 functional/verilog.v。
  - U#10–U#24：转向 OCEAN/Maestro 批量仿真（`AMS_OCEAN/run_ams.ocn`、`run_all.sh`、`cells.txt`），反复跑不通。
  - U#25–U#41：改用 finesim 真模拟（`finesim_AIOI21_run/aoi21.spi`、`.va`、`run_finesim.sh`），U#29 报 syntax error，U#31 跑通，U#34 保留 .tr0/.png，U#37 ZN 不变（模拟/数字未关联），U#39 VPI 方案，U#41 用户接受波形。
  - 后段（M649+）：agent 写 `split_cells.py`（更 elaborate 版：拆 module → `<base>/cells/<Cell>/verilog.vams` + 自动生成 `tb.v`/`ms.sp`(PULSE 激励)/`run_vpi.sh`，用于 finesim+VCS VPI cosim）。M1214 部署到 `/proj/lacaa/.../TEST/split_cells.py`，M1233 加 argparse 多文件输入 + 共享 UDP 抽取。

## 金标逻辑（取自 trace 真实产物，用于合成参考解）

**主金标 = `split_verilog_to_functional.py` --mode files 逻辑**（U#9 直接交付，最贴近 prompt）：
1. `strip_comments(s)`：去 `/* */`（find '*/'）与 `//`（find '\n'）。
2. `split_modules(text)`：逐行扫描，`MOD_START=^module\s+(\w+)`、`MOD_END=^endmodule`，depth 计嵌套 module；返回 `[(name, src_text), ...]`。
3. `--mode files`：对每个 module 建 `<dest>/<CELL>/functional/`，写 `verilog.v` = 该 module 的完整 `module ... endmodule` 文本。
4. `--mode dry`：只打印 module 名列表，不写文件。
5. CLI: `python split_verilog_to_functional.py --mode files --file <combined.v> --dest <dir>`。

**辅助金标 = `split_cells.py`（M649）核心**（更可验，多产物）：
- `split_modules`：regex `\bmodule\b` 找模块名 → 头部读到首个 `;` → 配对 `endmodule`（depth）→ 返回 `(name, header, body, full)`。
- `find_ports(header)`：从 `module NAME(...)` 括号内提取端口名（去 ANSI input/output/inout/wire/reg 前缀，去 bus `[...]`）。
- `find_directions(body, ports)`：从声明行 `input|output|inout` 提方向，默认 input。
- 每 cell 写：`<base>/cells/<Name>/verilog.vams`（module 全文）+ `tb.v` + `ms.sp`（PULSE 激励，输入≤8 二进制计数，>8 错峰单脉冲）+ `run_vpi.sh`（不存在才写）。
- CLI: `python split_cells.py <full.v> [--out <base>] [--vdd 1.8] [--tstop 1.0]`。

## 真实资产 & 合成计划（下一轮合成）

- **真实 combined .V**：用户称"所有 Cell 放在一起的 .V"，真实路径疑为 `/proj/lacaa/TV1_DBC_Virtuoso/.../STD_T_DBC_BASE_Verilog/...`（M152 list_allowed_files）。**permission 待验**（lacaa 项目路径可能拒绝）。agent 自造测试 fixture `test_full.v`（M657，2 module：`AIOI21` AOI 门带 specify 块 + `NAND2`）—— 可作为 format-faithful 合成参考。
- **合成 A**：format-faithful combined Verilog（多 module + `celldefine`/`endcelldefine` 块 + 注释 + specify 块 + bus 端口 + 嵌套注释干扰），例：5–8 个 std-cell module（AND/OR/NAND/NOR/AOI/OAI/INV/BUF），含 `//`/`/* */` 注释里假 module 名（验 strip_comments）。
- **hidden B**：不同 module 集（不同 cell 名 + 不同端口 + 不同 bus 宽度 + UDP primitive 块），结构 ≠ A，验反硬编码 + 跨输入。
- **参考解**：`split_verilog_to_functional_ref.py`（忠实 M157 --mode files 逻辑：strip_comments + split_modules + 写 `<dest>/<CELL>/functional/verilog.v`）。
- **check.py ≥8 条件**（草案 a–p）：(a) zip 含 .py 无泄漏 (b) py_compile (c) CLI B exit0 非空 (d) 产出 `<dest>/<CELL>/functional/verilog.v` 每 module 一文件 (e) cell 数 == B module 数 (f) 每 verilog.v 含 `module <name>` + `endmodule` (g) strip_comments：注释里假 module 名不被拆出（B 含 `// module FAKE` 注释） (h) 嵌套/指定块 specify 不破坏拆分 (i) bus 端口保留 (j) 跨输入 A cell 集 ≠ B (k) 反硬编码 B-only cell 出现 A-only 不出现 (l) 确定性 sha256 (m) --mode dry 只打印不写 (n) 无硬编码 /proj|/rundata 路径 (o) 不 import check|reference|negative|hidden (p) 输出目录结构精确。
- **negative**：empty / hardcode_A / no_strip_comments（被注释假 module 骗）/ print_expected / no_functional_dir / syntax_err / ref_delete_core / only_count（只数不写文件）—— 全 FAIL。
- **k 条断言**目标 16（①-⑯ 对应 a–p），k_check ≥8 GATE。

## 备注
- la00c 是 3127-msg 大 session（>600），本轮按 §3 例外**只深读**（DEBT:1），下一轮**第一件事合成交付** AmsFuncSplit-001。
- 该 case 为 **schematic_netlist L1**（离线 Verilog 解析，无 EDA 工具），可验性好（module 拆分 + 注释剥离 + 端口/方向 + 跨输入 + 反硬编码天然丰富）。
- 同用户 e0029308 此前无 D.jsonl case（新用户，扩覆盖）。
