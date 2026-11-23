# r1077 deepread — 5qlqi (lorikx@hfeg0pkn002) — SRAM 组选择逻辑结构分析 produce-task

## trace 来源
- scan: `ssh_eda_search_20261123_064315/summary.tsv` (.75, 2026-11-23)
- session: `1793618006543_5qlqi.messages.json` (356KB / 43 msgs / 3 user Q&A 轮)
- host: 10.129.2.11 = hfeg0pkn002 ; user: lorikx ; mc=13 (rtl:25 + verilog:4 + schematic:1 主导 A-pure digital；schematic:1 为 SRAM 宏例化上下文，非 layout)
- 归因: A=29 (rtl+verilog) vs C=0 (无 aether/virtuoso/layout/gds/drc/lvs) vs B/D=1 (schematic:1) → 强 A-pure digital
- ledger 状态: fresh (4-shard ledger diff；5qlqi 无 case 无 ledger → r1077 claim)
- scp 路径陷阱: 文件在子目录 `/home/lorikx/.cline/data/sessions/1793618006543_5qlqi/1793618006543_5qlqi.messages.json`

## 用户原话（3 Q&A 轮，逐字）
- U#0: "请阅读 @SramNoBistGrp3_modified.v ,分析里面的selection逻辑，结构是怎么样的，该如何操作"
- U#25: "画个模块结构图"
- U#41: "用文字再叙述一下如何控制这些例化模块"

## trace 调查结论（assistant，SRAM 组选择逻辑四级结构）
顶层 `SramNoBistGrp3` 例化 **27 个 SRAM 宏（i0~i26）**，规格/位宽/端口各异（1PRF 单口 / spsram 伪双口 / 2PRF(HC/HD) 真双口 / HD1PS / HDSPS 共 6 类分组），但选择/使能控制逻辑共用同一模板，最终汇成 16bit 字 `Q`。四级选择数据通路：

1. **实例解码层**：`decoder #(.WIDTH(5))` 把 `ISEL[4:0]` 展成 32 位 one-hot `inst_selection`（`out = 1'b1 << in`）；每实例 `sel_iN = inst_selection[N]`。bit0~26 used，bit27~31 unused。
2. **实例使能门控层**（每实例同模板）：
   - `en_iN = (SELALL | (sel_iN & sel_g3))` — 实例总使能（高有效）
   - `reb_iN = ~(en_iN && ~REB)` — 进宏 CEB/REB（低有效）
   - `web_iN = ~(en_iN && ~WEB)` — 进宏 WEB（低有效）
   - 单选(SELALL=0,sel_g3=1) / 全选(SELALL=1) / 整组休眠(SELALL=0,sel_g3=0)
3. **局部字选择层**：宽字宏接 `vmux<wide>to16`（vmux144to16/vmux160to16/vmux72to16/vmux40to16）按 `WSEL` 切 16bit `Q_ws_iN`；窄字宏直接 `assign Q_ws_iN = Q_iN`。
4. **全局输出选通层**：`wsmux27to1`（`isel=ISEL[4:0]`）选 N 个 `Q_ws_iN` 之一送 `Q`。ISEL 身兼解码选块 + 输出选路两职。

assistant 交付：SVG 矢量结构图 + markdown ASCII 结构图 + 文字叙述（控制信号职责表 + 操作流程）。

## 造题转化 (11-15 令 analysis-Q&A → produce-task)
用户三轮都在问"selection 逻辑结构 + 如何操作"。提炼为通用 produce-task：
- `structure.md` — 结构分析文档（模块定位 + 四级选择数据通路 + 各级机制 + 控制信号职责 + 如何操作 + ASCII 结构图）
- `verify_structure.py <verilog> <output_json>` — 通用结构提取器，正则解析任意同模板 SRAM-group Verilog → JSON：module_name / isel_width / instance_count / decoder_width / onehot total-used-unused / vmux_modules / output_mux name+d_count+isel / enable_template

## 关键牙点（anti-hardcode）
- **A (visible)**: `SramNoBistGrp3_modified.v` = trace-faithful 真实 SRAM 组模块（1157 行，27 实例 / decoder WIDTH=5 / vmux144to16+160to16+72to16+40to16 / wsmux27to1 / ISEL[4:0]）+ `decode.v` 子模块。
- **hidden B**: `SramNoBistGrpB_modified.v` = 合成的同模板 SRAM 组模块（326 行，16 实例 / decoder WIDTH=4 / vmux64to16+vmux32to16 / wsmux16to1 / ISEL[3:0] / onehot 16 全用 0 unused）。A/B 的 module_name / instance_count / decoder_width / vmux_modules / output_mux_name 全不相交。
- solver 必须真解析 Verilog 文本（正则抽取 sel_iN / decoder WIDTH / vmux / wsmux .out(Q)+.isel / enable assigns），不能硬编码 A 答案。硬编码 A（27/wsmux27to1/WIDTH=5）在 B 上输出 B 期望的 16/wsmux16to1/4 全错 → FAIL。
- **check k=17**(①-⑰): ① zip+md/py 非空 ② py_compile+parse/main def+re/open 真解析(反空壳) ③ B exit0+JSON ④ module_name==SramNoBistGrpB ⑤ isel_width==4(非5) ⑥ instance_count==16(非27) ⑦ decoder_width==4 ⑧ onehot 16-16-0 ⑨ output_mux_name==wsmux16to1(非wsmux27to1) ⑩ d_count==16 ⑪ isel 含 ISEL+3:0 ⑫ vmux_modules=={vmux32to16,vmux64to16} ⑬ enable_template en/reb/web 非空+en 含 SELALL+sel_g3 ⑭ md≥4 机制词 ⑮ 3x 确定性 ⑯ A-only token 不泄漏+isel_width≠5/instance_count≠27 ⑰ B-only token 必出现(反 print-only-A)

## 自验全过
- ref PASS 17/17 (reference_submit.zip = structure.md + verify_structure.py)
- ROUNDTRIP_OK (从 case JSON test 字段提取 check.py 独立跑 PASS)
- neg_selftest: neg_empty(neg: structure.md too short) / neg_print_only_A(neg: module_name=SramNoBistGrp3 硬编码 A) / neg_core_deleted(neg: isel_width=None 核心抽取删除) 全 FAIL
- §4.9 三假 (空壳/只 print A/删核心) 全 FAIL ✓
- anti-hardcode 牙: B 的 module_name/instance/decoder/vmux/wsmux 全≠A + A-only token 检查 + B-only token 必现
- build: cases/A/SramSelLogicAnalyzeProduce-001.json (32KB), k_check=k_rationale=17, domain=digital, ROUNDTRIP_OK
