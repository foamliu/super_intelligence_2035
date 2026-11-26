# 7huyr — aocao @ hfeg0plg227 (hfhds227) · mc=129 · verification

> shard A r314 deepread (DEBT:1 → r315 build). trace_source: aocao/hfhds227/1792053769843_7huyr.messages.json, mc=129, systemverilog:1776;verilog:166;netlist:25;cmos:20;schematic:16;drc:15;analog:7;aether:5. A-faithful diagnosis trace. live path readable; /rundata source code permission-denied (owned by aocao) — all code facts below extracted FROM THE TRACE (user pastes + agent read_files tool_results + agent bug report).

## USER#1 (逐字原文, A-faithful task — 提出症状未给根因 ✓)
> 帮我检查下面路径中的代码逻辑有无问题，目前我对照波形暂没看到问题
> /rundata/decqa/V0/simdir/verilog/aocao/decqa/wave_mirror/cyclic_xyz/RM/cyclic_xyz_prac_mirror_SLT128_RWL_decqa_burty_num=1_x_num=1_y_num=1_z_num=1031_sim_time=100

## 项目背景
DRAM RowHammer Relief (RHR) 行为级仿真测试平台 (Cadence irun, SystemVerilog)。验证 RHR 策略在循环地址攻击 (cyclic_xyz) 模式下的 hammer count 监控效果。文件: top.sv (TB top), rhr_driver.sv (driver), rhr_monitor.sv (monitor), simulation.pat (pattern), irun.log (sim log, 巨大)。

## 代理动作 (A#2-36, 全 read_files/run_commands/list_allowed_files/search_codebase, 0 writes 至此)
读 top.sv / rhr_driver.sv / rhr_monitor.sv / simulation.pat / irun.log (反复 tail/分段读, log 极大)。无代码产出，纯审查。

## 代理诊断 (A#38 代码逻辑审查报告) — 根因
**问题1 (严重 Bug): `addr_q` 队列越界访问 (仿真日志已证实)**
- irun.log 充斥大量警告: `ncsim: *W,RTSVQI (./simulation.pat,106|29): SystemVerilog queue index 114712 is beyond the queue's writable range [0:65760]`
- `addr_q` 在 top.sv 中初始化大小 = `ROW_COUNT = 65760` (索引 0~65759)
- 但物理地址 `addr_phys` 可达 114719 (RWL 地址 `17'h10000 ~ 17'h1C01F`) → `addr_q[addr_phys]` 在 `addr_phys >= 65760` 时越界
- 17-bit 物理地址空间 = 0 ~ 131071 (2^17 = 131072 entries)

### 出错代码 (top.sv ~行133-141, USER#42 逐字粘贴):
```systemverilog
prac_aci_en = 1;
for (int i=0; i < ROW_COUNT; i++) begin  // AC q init,ROW_COUNT=65760 WL(65536)+RWL(224),loop 65760
    toggle_rfsh_pre();
    temp_q.addr = (i<ROW_COUNT_NORMAL) ? i : RWLaddr_array[i-ROW_COUNT_NORMAL];
    temp_q.count = init_count; // random init_count
    temp_q.rhr_select = 1'b1;
    addr_q.push_back(temp_q);
    toggle_rfsh_post();
end
```
- ROW_COUNT = 65760 = WL(65536) + RWL(224)
- ROW_COUNT_NORMAL = 65536 (normal WL 地址)
- temp_q.addr = (i<65536) ? i : RWLaddr_array[i-65536]  (RWL 部分用 RWLaddr_array 映射到 17-bit 物理地址)
- addr_q 仅 push_back 65760 项 → 索引范围 [0, 65759]

### 越界索引点 (rhr_driver.sv, USER#94 引用):
```systemverilog
if(addr_q[clear_add].rhr_select==3'b100)begin
    addr_q[clear_add].count++;  //reset ac
```
- `clear_add` (= addr_phys) 可达 114719 → `addr_q[clear_add]` 越界

## USER#39 / USER#42 (用户给修复方向 — 非 A-faithful task, 但约束明确)
> 刚刚top.sv中到这段代码帮我修改，从而修复bug，要求保留原本到逻辑，比如我期望aci到时候目前到for循环内部出来push操作其他的要传递给电路的操作直至行64760次，但是push线性执行，比如我没用到某个地址，但是也执行，这样就可修复bug，我知道最简单的修改是不区分i的范围，直接把i扩展到131072，同时temp_q.addr = (i<ROW_COUNT_NORMAL) ? i : RWLaddr_array[i-ROW_COUNT_NORMAL];改成temp_q.addr = i；但是这样会增加电路aci到时间，不符合实际

用户约束: ① 保留原逻辑 ② ACI 循环仍 65760 次 (电路时序准确) ③ push 线性执行 (未用地址也 push) ④ 🚫 不要简单把 i 扩到 131072 (会增加 aci 时间, 不符合实际)

## 代理修复 (A#57-A#93) — 金标准 fix
**方案: 分离预初始化与 ACI 循环**
1. ACI 循环之前, 快速线性预初始化 `addr_q` 为 **131072 项** (覆盖整个 17-bit 物理地址空间), 无电路时序 (无 toggle_rfsh_pre/post)
2. ACI 循环保持 **65760 次迭代** (含 toggle_rfsh_pre/post 电路操作), 但改为**直接按索引更新已存在条目** (direct index assignment), 而非 push_back

修改后代码 (top.sv ~行133-155, A#93):
```systemverilog
// Pre-init addr_q: linear init to full 17-bit address space (131072 entries), no circuit timing
for (int i=0; i < 131072; i++) begin
    temp_q.addr = i;
    temp_q.count = init_count;
    temp_q.rhr_select = 1'b1;
    addr_q.push_back(temp_q);   // linear, fast, no toggle_rfsh
end
// ACI loop: 65760 iterations WITH circuit timing, update existing entries by direct index
prac_aci_en = 1;
for (int i=0; i < ROW_COUNT; i++) begin
    toggle_rfsh_pre();
    addr_q[i].addr = (i<ROW_COUNT_NORMAL) ? i : RWLaddr_array[i-ROW_COUNT_NORMAL];
    addr_q[i].count = init_count;
    addr_q[i].rhr_select = 1'b1;
    toggle_rfsh_post();
end
```
(原路径只读, 代理写到 /home/aocao/Desktop/top.sv)

## r315 PIVOT 设计 (diagnosis-generator, 匹配 acaey/SvHierRefDiag-001 模式)
- **deliverable**: `gen_rhr_diag.py` (spec-driven 生成器, stdlib) + `spec_a.json`
- 生成器 emit `diag_rhr_bounds.py` (读 spec + 结构化 codebase) 静态推导根因:
  ① queue 声明 (name/decl_size/decl_line) ② max 索引值 (从 indexing expr + address_space_max 推导) ③ 越界判定 (max_index >= decl_size) ④ log 警告码 (RTSVQI) + 位置 ⑤ 根因分类 (queue-bounds-violation) ⑥ 受影响索引点 (file/line/expr) ⑦ fix_strategy (separate pre-init full-space + keep ACI loop direct-index) ⑧ fix_target (the push_back for-loop) ⑨ 用户约束 (keep loop count, no i-extend-to-full)
- 输出 `root_cause.json` (~12 派生字段) + `diag_report.md`
- **check.py ~12-14 conds**: a(zip+gen+spec_a) b(gen py_compile) c(gen on spec_b emit diag) d(diag py_compile) e(diag on spec_b → root_cause_b.json+report) f(JSON 合法+必需字段) g(queue decl 派生==spec_b) h(max_index 派生) i(越界判定派生) j(log warning 派生) k(根因分类) l(fix_strategy+target 派生) m(用户约束识别) n(反硬编码A: B 特异 queue_name/index_expr/warning_code present, A 特异 absent) o(反平凡 ≥3 函数 + 读 spec json)
- **A=spec_a faithful** (aocao/decqa/cyclic_xyz/addr_q/ROW_COUNT=65760/RTSVQI/114712/131072/RWL 17'h10000-1C01F)
- **hidden B=spec_b isomorphic** (不同项目: 另一 RHR/wave_mirror variant; queue_name=q_addr, decl_size=32768, address_space=18-bit=262144, max_index=258999, warning=RTSVQI @ different file/line, ROW_COUNT_NORMAL 不同, RWL 范围不同)
- 自验: gold PASS 14/14 + 4 negatives (noop/hardcode_a/stub/keep_bug) 全 FAIL + §4.9 (空壳/print/core-deleted) 全 FAIL
- 断言闸门: k_rationale=k_check=14≥8 ✓

## 选料教训 (r314)
- **all-shard dedup 是硬要求**: 本轮用 shard-A-only exclude (319) 过滤候选, top produce 候选 us0hd 实为 shard-D **RegrCaseFilter-001** (同 e0039102/同 session_file), wuuc7 也是同任务 dup。r313 lesson 重现。**下轮起 filter2.py 必须用全 4 shard ledger (2220) 做 exclude** (当前仅 embed shard-A 319)。已 park 7adgf(dup of 7huyr)+wuuc7(dup of RegrCaseFilter)。
- **9th produce-scarcity 确认**: top-80 A-dominant fresh 候选绝大多数 analysis-only (检查/分析/How-to) 或 cross-shard dup。clean A-faithful produce 在 fresh digital 池仍稀缺 (r295/r296/r299/r300/r309/r311/r312/r313/r314)。7huyr 是 diagnosis → PIVOT 是可行路径 (acaey 模板)。
