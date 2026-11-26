# 深读笔记: 6sxh5 — Characterization Deck 文件目录盘点 (deck-grounded file-catalog Q&A)

## trace
- session: `1792131163281_6sxh5`
- user: e0045488 @ 10.129.2.11 (mc=82)
- size: ~596KB / 97 msgs / 多 user 轮 (U#0「hi」+ U#2 关键轮)
- 工具调用: 文件读取 / shell 探目录为主
- trace_source: `host=user session_file=session_msgs real_task_summary=deck-grounded file-catalog QA`

## 用户意图
U#2 原话逐字：
> I did characterization flow of one cell here /proj/lacaa/V0/workdir/e0045488/k_lib/. The generated deck is under /proj/lacaa/V0/workdir/e0045488/k_lib/char_dir/deck_DBCP51H180L6W25T5LVT/. Please help me understand files under this deck.

意图 = 「我跑完一个标准单元的 characterization，生成的工作 deck 在那个目录，帮我搞懂这个 deck 里都有什么文件、各自干啥、按 arc 怎么组织」。
= **deck-grounded 文件目录盘点 Q&A**（不是逻辑生成、不是仿真调参、不是 report 写作；是「读真实文件→结构化解释」的 answer-extraction 任务）。

## assistant 工具链（trace 中的真实行为）
1. 探 `/proj/lacaa/V0/workdir/e0045488/k_lib/char_dir/deck_DBCP51H180L6W25T5LVT/` 顶层：拿到 `key` / `library` / `spice_sim_info.csv` / `bsub_auto_index.cdb` / `ArcInfo/` / `AN2D1DBCP51H180L6W25T5LVT/`（per-cell 工作区）
2. 读 `library`（liberty 模板头）→ 提取 nominal_voltage / voltage_map / 工艺角
3. 读 `key`（run id hash）→ `1683a920`（短哈希）
4. 读 `spice_sim_info.csv` → 全 arc 的 pass/fail + wall/CPU time 汇总
5. 读 `bsub_auto_index.cdb` → characterization 数据库（auto_index 元信息）
6. 进 `ArcInfo/` → `.arc.gz` 每个 arc 一个压缩包（含 arc metadata）
7. 进 `AN2D1DBCP51H180L6W25T5LVT/` per-cell 工作区：
   - `leakage_0/leakage_power_0.spi` = leakage arc id 0 的 SPICE testbench
   - `Z/vector_0/A1_Z_cell_rise_1.spi` = A1→Z cell_rise arc id 1 的 testbench
   - `Z/vector_0/A1_Z_cell_rise_1/` = per-sim job 目录（`.log`/`.mt0`/`.measure`/`.warn`）
   - `A1/hidden/hidden_power_fall_5.spi` = A1 上的 hidden_power_fall arc id 5
8. 读各 `.spi` 头部 `$ cell:... id:N pin:X related:Y when:"..." <type>` 注释行 → 抽 cell name / pin / arc id / when 条件
9. 读 `.spi` 的 `.include '<path>'` → 抽 model include 路径（LPE / model_ss）
10. 读 `.spi` 的 `.measure <name> ...` / `.param <name>=...` → 抽 measure/param 名
11. 汇报：顶层文件清单 + per-cell 工作区按 arc 组织 + 每 arc 的 sim job 文件 + 真实证据标识符

## 关键产物（用户接受的结果）
结构化英文 walkthrough：
- **顶层文件**：`key`(run id) / `library`(liberty 头) / `spice_sim_info.csv`(arc 汇总) / `bsub_auto_index.cdb`(char DB) / `ArcInfo/`(压缩 arc metadata) / `AN2D1DBCP51H180L6W25T5LVT/`(cell 工作区)
- **per-cell 工作区**：cell name = `AN2D1DBCP51H180L6W25T5LVT`（2-input AND, drive D1, LVT 工艺）
- **arc 清单**：leakage(id 0) / cell_rise(id 1, A1→Z, when "A2") / hidden_power_fall(id 5, A1)
- **per-sim job**：每个 timing arc 下 `vector_0/<input>_<pin>_<type>_<id>/` 四件套（.log/.mt0/.measure/.warn）
- **证据标识符**：cell name / pin names / arc ids / `.include` 路径 / `.measure` 名 / `.param` 名 / when 条件

## A-faithful 判定
**完全可行**：deck 源在 .75 (10.129.32.75) 上的 `/proj/lacaa/V0/workdir/e0045488/k_lib/char_dir/deck_DBCP51H180L6W25T5LVT/` 可达；deck 是纯静态文件（.spi/.cdb/.csv/.gz/小文本），无 live SPICE、无 license、无 GUI 依赖；文件结构标准化（Empyrean Liberal 流程产物，目录命名约定稳定）。→ **A 档 verbatim**。

## reframe（design_flow 契约）
design_flow 契约要求候选在隐藏 B 上跑 → reframe 成 **deck-grounded file-catalog tool** `deck_catalog.py`：
- CLI: `python3 deck_catalog.py <deck_dir> <question_file>`
- 扫 deck_dir 递归 → 按 extension/dir-naming 约定分类（.spi/.mt0/.log/.measure/.warn/.cdb/.csv/.arc.gz/library/key）
- 识别 cell 工作区（`find_cell_dir`: 优先含 .spi 的目录，回退到含 `leakage_0`/`Z`/`A1` 等 marker 的目录）
- 推断 arc inventory（`leakage_0/` = leakage arc; `<pin>/vector_0/<input>_<pin>_(cell_rise|cell_fall)_<id>.spi` = timing arc; `<pin>/hidden/hidden_power_(fall|rise)_<id>.spi` = hidden_power arc）
- 抽 `cited_identifiers`（**必须真实出现在 deck 文件里的字面子串**：cell name / `id:N` / `pin:X` / `.include 'path'` / `.measure name` / `.param name=` / `when:"..."` / `voltage_map (VDD` / arc type keyword）
- 输出 JSON: `{question, deck_summary{cell_name,tool,nominal_voltage,...}, top_level_files[{name,category,role}], arc_inventory[{id,type,path,sim_files,input_pin,output_pin}], cited_identifiers[]}`

## B 变体（反硬编码五轴）
| 轴 | A | B1 | B2 | B3 |
|---|---|---|---|---|
| cell name | AN2D1DBCP51H180L6W25T5LVT | ND2D2XYZP34H160L4W18T5SVT | INV1D0XYZP22H90L2W12T5ULVT | (无 cell) |
| 工艺/阈值 | LVT | SVT | ULVT | — |
| nominal VDD | 0.75 | 0.6 | 0.9 | (none) |
| 温度 | (A 真实) | 85°C | -40°C | — |
| arc 数 | 3 (leakage+cell_rise+hidden_power_fall) | 7 (leakage+cell_rise+hidden_power_fall+...) | 3 (leakage+cell_rise+cell_fall) | 0 |
| 顶层文件 | key/library/spice_sim_info.csv/bsub_auto_index.cdb + cell/ArcInfo | 同 | 同 | 仅 key/library（无 cell 工作区，无 cdb/csv/ArcInfo） |

B3 = 优雅降级测试（deck 残缺，只有 key+library，无 cell 目录 → arc_inventory=[] / top_level_files 仅 2 项 / 不崩溃）。

## check.py 15 条断言 (a-o)
a) zip 合法含 deck_catalog.py 无泄题（不含 check.py/reference/hidden/jsonl/negative/hidden_manifest）
b) py_compile 通过
c) B1 退出 0 + 合法 JSON + 5 顶层键（question/deck_summary/top_level_files/arc_inventory/cited_identifiers）
d) B1 top_level_files 含 key/library/spice_sim_info.csv/bsub_auto_index.cdb
e) B1 deck_summary.cell_name == ND2D2XYZP34H160L4W18T5SVT
f) B1 arc_inventory >=3 且每 arc 含 id/type/path/sim_files
g) B1 arc types 含 {leakage,cell_rise,cell_fall} 至少一种
h) B1 cited_identifiers 非空且每标识符是 B1 deck 某文件内容的真实子串（grounding）
i) B2 退出 0 + 合法 JSON + cell_name == INV1D0XYZP22H90L2W12T5ULVT
j) B2 arc_inventory >=2 + cited_identifiers 在 B2 grounded
k) 反硬编码：A 专属标识符（AN2D1DBCP51H180L6W25T5LVT / DBCP51H180L6W25T5LVT / 1683a920 / amberh / LPE_0813_LVT / 0820_write_verilog_debug / lacaa / A1_Z_cell_rise / MMMM4 / 0.031040 / 0.75）不泄漏进 B1/B2 输出
l) B3 退出 0 + 合法 JSON + arc_inventory==[] + top_level_files 仅 key/library
m) B1 question == B1 问题文件逐字
n) 数据驱动：B1 cell_name != B2 cell_name 且 B1 arc 数 != B2 arc 数
o) 3 次重跑 B1 sha256 一致（确定性）

## 验证状态
- refsol `deck_catalog_REF.py` → `reference_submit.zip`：**PASS 15/15** ✅
- negative_selftest（neg1 硬编码 A / neg2 stub / neg3 print-only / §4.9a empty zip / §4.9c empty py）：**NEG_RC=0（5/5 全 FAIL 如预期）** ✅
- A 专属标识符已逐个核对：A-only（B1/B2 = 0 命中）→ `AN2D1DBCP51H180L6W25T5LVT`/`DBCP51H180L6W25T5LVT`/`1683a920`/`amberh`/`LPE_0813_LVT`/`0820_write_verilog_debug`/`lacaa`/`A1_Z_cell_rise`/`MMMM4`/`0.031040`/`0.75`（注：`elpsinl` 因 B1/B2 共享 Empyrean LPE 路径前缀故移出 leak list；`MMMM8` 因 A 自身无命中故移出）

## 同族
- 同 #254 v2 answer-extraction pattern：i33cs (code-grounded script-catalog) / 14921 (netlist-grounded circuit-id) / 86g62 / 9imo1 / 7sgr2 / 636qr
- 本 case 是该 pattern 的 **deck-grounded 第 2 变体**（i33cs 为 code-grounded 第 1 变体）
- D shard 第 9 个 prototype-proven 已落 case（参考 pool_reaudit_D.tsv 统计行）
