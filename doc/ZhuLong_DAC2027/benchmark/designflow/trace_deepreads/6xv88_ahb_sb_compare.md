# trace_deepread · 6xv88 · AHB VIP scoreboard compare/convert2string

- session: `1792637822804_6xv88.messages.json`
- user: e0045140 @ hfeg0pnd001 (10.129.32.189) / hfeg0pnd002 (10.129.32.190)
- match_count: 33 (systemverilog:183 .def:13 verilog:6 synopsys:2 dominant)
- size: 808 KB / 139 msgs (74 user / 65 assistant), 7 轮真实迭代
- domain: verification (UVM testbench / scoreboard)
- ledger: r403 → case `EDA-Eval-DesignFlow-AhbSbCompareGen-001`

## 用户真实意图（逐条 user_input）

1. (msg 0) 「目录下有个 AHB 的 VIP，包含 include 和 src 以及 example 部分，帮我分析 code 完成 example 的修改，只改 example 即可，master 和 slave 1 对1 对打，有不确定的先确认」
2. (msg 26) 「1. 只改 example」
3. (msg 48) 「scoreboard 里面的 compare 和 convert2str 没有实现 可以比较么」 ← **核心需求 1**
4. (msg 53) 「checkz 中的 data 是动态数组 每beat都需要比较」 ← **核心需求 2**
5. (msg 108) 「master seq 帮我改回 random」
6. (msg 134) 「makefile 你该了什么」
7. (msg 138) 「不要做任何修改，为啥现 example 执行，master seq 有发出，但是 master driver 没有 get 到，可能是什么原因」← 诊断咨询（无产物）

## agent 工具链

read_files（example/env/seq/tb/test + include + src 大量 SV）→ list_allowed_files →
run_approved_command（VCS 编译，遇 LD_PRELOAD ld.so 报错但仍 exit 0）→
edit（cxmt_ahb_env.sv / cxmt_ahb_scoreboard.sv / tb_top.sv / seq / Makefile）→
write_file compile_and_run.sh / check_makefile.py / fix_makefile.py（修 Makefile line 38 的 `\x13` 控制字符）。

## 三个核心修复点（scoreboard，本轮 produce-task 的来源）

### 1. compare() 字段逐个比较（msg 58/64/68 edit cxmt_ahb_scoreboard.sv）
- 标量字段用 `==` 累积到 `bit match`：`match = (exp.xact_type == act.xact_type);`
  `match &= (exp.addr == act.addr);` … burst_size / burst_type / hprot
- **response_type 不比较**：注释「NOTE: response_type is NOT compared because the
  master monitor does not capture it from the bus — it only fills all_beat_response[]」
  ← 这是 trace agent 自己给出的根因，是关键 nuance。

### 2. data 动态数组逐 beat 比较（msg 68，回应用户 msg 53「每beat都需要比较」）
```systemverilog
if (exp.data.size() != act.data.size()) begin
  match = 0;
end else begin
  foreach (exp.data[i]) begin
    if (exp.data[i] !== act.data[i]) match = 0;
  end
end
```
即先比 size 不等则 match=0，再 foreach 逐元素 `!==`。**不能只比 size 或只比首元素。**

### 3. convert2string() 用 $sformatf 拼字段（msg 58/64）
命中/不命中分支用 `exp.convert2string()` 打印；convert2string 把事务字段格式化成字符串。

## 计数器

`num_checked++`（进入即增）/ `num_passed++`（match 命中）/ `num_mismatch++`（不命中 + uvm_error）。

## A-faithful 判定

用户给了**需求**（compare/convert2str 没实现、data 动态数组每 beat 比）但**未给实现**；
agent 自己设计 field-by-field + foreach 方案并给出 response_type 排除根因。
按 §3 A-faithful 口径（用户给根因才不合格），此处用户给需求非根因 → 边界。
但 deliverable 是 SV 实现 + 沙盒无 VCS（trace 内 VCS 即报 LD_PRELOAD 错），
无法真跑 → 选 **B 档 synthesized**：deliverable=Python 生成器从规格 JSON 动态生成 SV，
check.py 结构化解析，L1-static+subprocess（与 A 域 actual_tool_demand 1.0% drive 一致）。

## B 档合成 plan（已交付 r403）

- case: `EDA-Eval-DesignFlow-AhbSbCompareGen-001`（verification L1 k=15）
- deliverable: `gen_scoreboard.py`（--spec/--out，纯 stdlib）
- A 档（可见）：ahb 事务 5 标量（xact_type/addr/burst_size/burst_type/hprot）、
  动态数组 data、排除 response_type、计数器 num_checked/num_passed/num_mismatch
- B 档（隐藏）：axi 事务 6 标量（axi_id/axi_addr/axi_len/axi_size/axi_burst/axi_cache）、
  动态数组 wdata、排除 axi_resp、计数器 cnt_chk/cnt_pass/cnt_fail
  → 类名/字段名/数组名/排除字段/计数器名全不同，反硬编码
- check.py 15 条件（a-o）：脚本存在/语法/B 退出 0/输出非空/compare 定义/
  convert2string 定义/每标量进 ==/排除字段不比/size 检查/foreach !==/match 累积/
  计数器 ++/convert2string 含全字段+size/纯 stdlib/跨输入反硬编码+确定性
- 自验：ref PASS 15/15；4 neg（naive_empty/print_only/core_removed/excluded_compared）全 FAIL；
  §4.9 (a)空壳 (b)print-only (c)core-removed 全 FAIL；断言闸门 k=15✓

## 其他 trace 事实（不进 case，备查）

- tb_top.sv 物理连线缺失（master_if/slave_if 未连）是 agent 另一发现，但属 tb 修改非 scoreboard。
- Makefile line 38 有 `\x13` 控制字符，agent 用 fix_makefile.py 清除。
- master seq 改回 random（msg 108→112 edit seq）。
- 末轮 msg 138 是诊断咨询（master driver 没 get 到 seq），无 produce 产物。
