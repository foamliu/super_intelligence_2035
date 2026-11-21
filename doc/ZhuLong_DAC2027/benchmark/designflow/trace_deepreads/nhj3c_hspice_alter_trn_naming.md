# nhj3c — HSPICE .alter .trn 文件名附带 alter 信息（spice_sim analysis-Q&A）

## trace_source
- user: hairuizh
- host: hfeahpc502 (10.129.33.25)
- session_file: 1794893451446_nhj3c.messages.json (54.6KB, 6 msgs)
- match_count: 9 (keyword hspice:186; aether:11; netlist:7; synopsys:4)
- trace 日期: 2025-11-16 (ts 1794893451446)
- 同 host 同 user 的 1ziwu (r981 delvto_ckt_wiring_patch) 为不同 session 不同任务，无 near-dup

## 用户原始意图（U[0]，全文）
> hspice仿真，如何让输出的波形文件.trn名字中附带有alter的信息，方便识别

意图类型：**analysis-Q&A**（用户问"如何让 X 实现 Y"，agent 查 AskEDA 后给文字解释）。
真实用户在 trace 里只想要一个 how-to 解释 → 合法真实意图（TASK 顶部"任务形态=用户意图"明确允许 analysis-Q&A）。

## agent 工具链
1. U[0] how-to → assistant thinking 判 EDA 题 → `skills/ask-eda` skill
2. AskEDA 查询 "hspice alter 输出波形文件 .trn 文件名 如何附带 alter 信息 识别"
3. AskEDA 返回（命中 hspice_cmdref.pdf），但返回内容主要是 LLM thinking（半成品）
4. assistant 用自身 HSPICE 知识整理结论：
   - 推荐做法：给 `.ALTER <label>` 命名 → 文件名变成 `design.<label>.trn`（**注：此部分不准确**，真实 HSPICE 不把 label 放文件名）
   - 不命名：自动编号 `design.1.trn`, `design.2.trn`（**注：也不准确**，真实是 `design.tr0`, `design.tr1`...）
   - `-o my_sim` 自定义前缀 → `my_sim.<label>.trn`（同上不准确）
   - 限制：`.ALTER` 内不能含 `.PRINT/.PLOT/.PROBE` 等 I/O 命令（**正确**）

## 关键观察：agent 的解释有部分错误
真实 HSPICE 行为（hspice_cmdref / HSPICE Reference Manual）：
- `.TRAN` 仿真输出波形文件命名规则：`<design>.tr0`（主仿真）, `<design>.tr1`（第一个 .ALTER）, `<design>.tr2`（第二个 .ALTER）...
- `.DC` → `.dc0/.dc1/...`, `.AC` → `.ac0/...`, `.IC`→`.ic0/...`
- `<design>` 由 `-o <name>` 选项指定，缺省 = 输入 deck basename
- **`.ALTER <label>` 的 label 不进入文件名**（label 只在 .lis 输出报告里用于识别）
- `.ALTER` 块内禁止 `.PRINT/.PLOT/.PROBE/.GRAPH/.MEASURE`（这些 I/O 命令只能在主块；.ALTER 只能改参数/模型/网表）

agent 给的 "design.<label>.trn" 形式是其推测/幻觉，并非真实 HSPICE 行为。但**用户真实意图是"如何让文件名附带 alter 信息"**，agent 的回答（给 .alter 命名）反映了用户层面对"识别"的需求 —— 即用户需要一种 mapping 把 filename ↔ alter case 对应起来。

## reframe 为 produce-task（参数化生成器）
将 analysis-Q&A reframe 成参数化 Python 生成器（同 r972 SimKbCompareGen/r970 GenguiToolkitProvenanceAnalyze 谱系）：

**form = `hspice_alter_predictor.py --deck <sp> [--output-root <name>] --out <json>`**
- 解析 HSPICE deck：识别 `.TRAN/.DC/.AC/.IC` 主分析类型、`.OPTION POST`、`.ALTER [label]` 块边界、`.ALTER` 块内的 `.PRINT/.PLOT/.PROBE/.GRAPH/.MEASURE` 违规命令、`-o` 自定义根（从伴随 config 读）
- 为每个 alter 段（主 sim 段 + 各 .ALTER 段）生成 expected trn filename：`<root>.tr<N>`（N=0 主, 1,2,3… 各 alter，**sequence-based 不是 label-based**）
- 输出 JSON：`{design_root, output_root, analysis_type, segments:[{index, source, label, trn_filename, warnings:[...]}], summary:{total_segments, alters_with_warnings}}`
- 该工具的"诊断价值"：用户拿到这个 JSON 就能 mapping filename ↔ alter case，并提前发现违规 I/O 命令

**为何此 reframe 合法（TASK 顶部铁律）**：
1. 用户真实意图 = "如何让文件名附带 alter 信息以便识别" → reframe 后工具正是给用户 mapping(filename ↔ alter) 的能力
2. check() 有牙：测试 SUT 是否正确实现 sequence-based 命名（HSPICE 真行为）vs. naively 实现 agent 文字里的"label-in-filename"（错解）—— 后者正是 neg_label_as_filename 的反向样本
3. 真实 trace 溯源：metadata.trace_source 全保留
4. 不脱敏：prompt 用真实用户名 hairuizh + 真实场景

## 难度判定
L1（离线 Python 复刻，纯文本解析无 EDA 二进制，无 sandbox run）

## A/B 资产设计
**visible A**（faithful 重建自 trace agent 给的示例风格 + 真实 HSPICE deck 结构）：
- `deck_A.sp`：DDR2 lvlshft 风格，`.TRAN 1n 100n`, `.OPTION POST=2`, 3 个 `.ALTER`（2 命名 + 1 不命名），`.PARAM vdd=1.0/1.2/0.8` 变化
- `config_A.json`：`{"design_root":"lvlshft_ddr2","output_root":null,"cli_output_root":null}` → 不带 -o

**hidden B**（anti-hardcode-A，全维度异）：
- `deck_B.sp`：vref_buf 风格，`.TRAN 10p 5n`, `.OPTION POST=2`, **4 个 .ALTER**（3 命名含特殊字符 + 1 不命名），其中 1 个 `.ALTER` 内嵌 `.PRINT`（违规 → 期望 warning），`.PARAM vref=0.6/0.7/0.8/0.9` 变化
- `config_B.json`：`{"design_root":"vref_buf_opamp","output_root":null,"cli_output_root":"sim_vref_corner"}` → 带 -o 自定义前缀
- 5 重 anti-hardcode：design_root 异 / alter 数量异(4 vs 3) / alter label 名字异 / -o 行为异(B 有 -o A 无) / B 含违规 .PRINT 段而 A 无

## check.py 断言清单（13 条 a-m，≥8 硬闸门）
1. **a** zip 存在且可解，含 predictor.py + predict.json
2. **b** predictor.py 语法正确（py_compile）
3. **c** predictor.py 在 B 上 subprocess 跑 exit=0
4. **d** predict.json 是有效 JSON，schema 含 design_root/output_root/analysis_type/segments/summary
5. **e** segments 数量 == 期望（主 1 + B 的 4 alter = 5），不是 A 的 4
6. **f** segments[0].trn_filename == "sim_vref_corner.tr0"（B 的 -o 自定义根 + 主 sim）
7. **g** segments[1..4].trn_filename == "sim_vref_corner.tr1".."sim_vref_corner.tr4"（**sequence-based NOT label-based** —— 核心齿，反 agent 文字里的"design.<label>.trn"幻觉）
8. **h** 至少 1 个 segment 的 warnings 非空且包含 "PRINT" 或 "PROBE"（B 的违规 .PRINT 段被检出）
9. **i** 命名 alter 段的 label 字段保留原 label 文本（即使 label 不进文件名，也要记录以便用户 mapping）
10. **j** analysis_type == "TRAN"（B deck 主分析是 .TRAN）
11. **k** `-o` override：所有 trn_filename 都以 "sim_vref_corner" 开头，不以 B 的 design_root "vref_buf_opamp" 开头（B 自定义前缀生效）
12. **l** anti-hardcode-A：predict.json 内不出现 A 的 design_root "lvlshft_ddr2"、A 的 alter label "case_vdd_1p2/case_vdd_0p8"、A 的数字 3
13. **m** 3-seed 确定性：subprocess 跑 3 次随机化输入顺序 → predict.json 完全相同（禁时间戳/random）

## §4.9 三假提交必须 FAIL
- (a) 空壳 submit（空 zip 或缺 predictor.py）→ a FAIL
- (b) 只 print 期望串（predictor.py 只 echo 固定 JSON）→ c 跑通但 l（anti-hardcode-A）FAIL（A 残留）或 e FAIL（segments 数错）
- (c) 参考解删核心（去掉 .ALTER 检测 → segments=1）→ e FAIL

## negative 样本（≥2 错解，必须全 FAIL）
- `neg_naive_single.py`：永远只输出 1 个 segment（不识别 .ALTER）→ e FAIL
- `neg_label_in_filename.py`：把 label 放进文件名（`<root>.<label>.trn`，按 agent 文字错误实现）→ g FAIL（filename 不匹配 sequence-based 期望）
- `neg_no_warnings.py`：不检测违规 I/O 命令 → h FAIL

## 自验计划
1. ref solution build_submit → check.py 跑 PASS 13/13
2. negative_selftest.py 跑 neg_naive_single/neg_label_in_filename/neg_no_warnings + §4.9 三假 → 全 FAIL
3. 3-seed 确定性：ref solution 跑 3 次 → 相同 JSON
