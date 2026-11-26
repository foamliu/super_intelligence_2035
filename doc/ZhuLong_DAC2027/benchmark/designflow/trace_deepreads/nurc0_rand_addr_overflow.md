# nurc0 — random 策略地址越界 debug-Q&A 深读笔记

## trace_source
- session: `1793241105381_nurc0.messages.json`
- user: shanliny / host: hfeg0pkn005 (10.129.2.14) / mc=9 (systemverilog:598;verilog:3;synopsys:2)
- trace on .75: `/home/shanliny/.cline/data/sessions/1793241105381_nurc0/`
- agent: lead / deepseek-v4-flash / 10 msgs / 1 user turn / status=failed
- parked_reaudit_A.tsv L246: REVIVABLE_QA yes, analysis-Q&A, EXISTS

## 用户原话 (U#0)
> 替我看看这些代码，告诉我为什么我在使用 `make DEPTH=8 DATA_WIDTH=16 MUX=1 build_rand all` 命令时，random 策略随机出的地址会超过我设置的最大限制 depth=8？

+ 13 个附件 (uploads/): driver.sv / env.sv / file.list / interface.sv / makefile / monitor.sv / package.sv / ref_model.sv / strategy_base.sv / strategy_ext.sv / top.sv / transaction_base.sv / transaction_ext.sv

## agent 工具链
1. search_codebase (6 queries) → 全部 30s timeout
2. read_files transaction_base.sv + strategy_ext.sv (partial)
3. read_files transaction_base.sv L4-90 + ...
4. read_files makefile
5. 产出最终文本报告（msg9）

## agent 最终结论（msg9，**部分错误**）
- 逐层追踪参数链：makefile `+define+USER_DEPTH=8` → top.sv `DEPTH=8, ADDR_WIDTH=$clog2(8)=3` → env.sv `sram_environment #(3,16,8)` → strategy_ext.sv `random_strategy #(3,16,8)` → transaction_base.sv `rand bit [2:0] addr` + `constraint addr < 8`（自动满足）
- **结论**：「代码参数链本身正确，addr 是 bit[2:0] 物理上不可能 >=8，问题在编译环境（旧 simv / 环境变量覆盖）」
- **但沿途识别了 2 个真实潜伏 bug**（当作"改进建议"列出，未当作根因）：
  1. ref_model.sv L160: `memory[bit [ADDR_WIDTH:0]]` 多一比特（应为 `ADDR_WIDTH-1:0`），允许索引 0..15 超过 DEPTH=8
  2. strategy_ext.sv L55: `total_weight = read_weight + write_weight + idle_weight + bitwrite_weight` **缺少 `+ redundancy_weight`**

## 真实根因（深读复核）
### Bug 1: strategy_ext.sv L55 — total_weight 漏算 redundancy_weight
```systemverilog
// L37: redundancy_weight = 5;
// L55: int total_weight = read_weight + write_weight + idle_weight + bitwrite_weight;  // ←缺 +redundancy_weight
// L65: int rand_val = $urandom_range(0, total_weight - 1);
// L67-89: 4 个 else-if 分支，最后一个是
// L89: else if (rand_val < read_weight + write_weight + bitwrite_weight + redundancy_weight)
```
**机制**：`rand_val ∈ [0, total_weight-1]`，但 L89 上界 = `total_weight + redundancy_weight` > `total_weight`。故 idle 分支（L82-86 之后到 redundancy 之前）永不触发，而 redundancy 分支（L89）在 idle 区间被错误激活。redundancy 分支调用 `column_redundancy_transaction`，其 addr 语义不同（使用 crs0a/crs1a 列冗余地址 + base offset 驱动 vif.addr），导致驱动到 DUT 的地址可能超过 DEPTH=8。

### Bug 2: ref_model.sv L149/160 — memory 索引多一比特
```systemverilog
// ref_model.sv L149: protected logic [savelinelength:0] memory[bit [ADDR_WIDTH:0]];
// 应为 bit [ADDR_WIDTH-1:0]
```
**机制**：`bit [ADDR_WIDTH:0]` = `bit [3:0]` 允许 0..15，超过 DEPTH=8。当 ref_model.write/read 被调用时，memory 数组接受 8..15 的索引，与 DUT 行为不一致，ref_model 比对时产生地址越界现象。

### Bug 3（次要）: transaction_base.sv — addr 约束自动满足
```systemverilog
rand bit [ADDR_WIDTH-1:0] addr;   // bit[2:0], max 7
constraint valid_addr { addr < DEPTH; }  // addr<8, 永远成立 → 约束无牙
```
**机制**：`addr < DEPTH` 在 `ADDR_WIDTH = $clog2(DEPTH)` 时永远成立，约束无效。若 ADDR_WIDTH 因任何原因变宽（如 DEPTH 非 2 的幂），约束才会生效。当前 DEPTH=8=2^3 时不影响，但是脆弱设计。

## 交付形态决策
- **A 档不可行**：原始 13 个 SV 文件含 SRAM 验证 IP（44KB strategy_ext.sv / 30KB ref_model.sv），且 uploads/ 路径绑死 shanliny 私有目录
- **B 档合成**：mini `sram_rand_proj/` 5 文件忠实还原 3 类 bug 的可检测结构
  - makefile (DEPTH→+define+USER_DEPTH)
  - top.sv (DEPTH/ADDR_WIDTH=$clog2 参数链)
  - transaction_base.sv (rand addr + constraint + crs0a/crs1a)
  - strategy_ext.sv (random_strategy: total_weight 漏算 + 4 分支)
  - ref_model.sv (memory[bit[ADDR_WIDTH:0]] off-by-one)
- **隐藏 B 变体**：同 3 类 bug，标识符全异（DEPTH→MEM_DEPTH, ADDR_WIDTH→AW, redundancy_weight→repair_wt, total_weight→tot_wt, memory→mem_arr, crs0a→col_ra, read_weight→rd_wt...），≥8 维全异

## case 计划
- case_id: `EDA-Eval-DesignFlow-RandAddrOverflowDiagnose-001`
- domain: digital / mode: design_flow / entry: outputs/submit.zip
- 交付: `rand_addr_overflow_diagnosis_report.json` 含 `analyze_rand_addr_overflow_fn` (通用 Python 源码) + `bugs_found_on_input`
- check: 在隐藏 B 上 exec fn → 找到 3 类 bug (total_weight_missing_term / memory_index_off_by_one / constraint_auto_satisfied) + file:line 证据 + anti-hardcode + 3-seed
- k ≥ 12 条独立断言
