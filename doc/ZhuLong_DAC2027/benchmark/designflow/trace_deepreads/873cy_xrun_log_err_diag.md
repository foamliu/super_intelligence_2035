# trace deepread — 873cy xrun log error diagnosis

## trace
- session: 1793949945535_873cy (e0014036 @ hfeg0pkn004)
- 143 msgs, 571KB, dir-based, mtime Nov 6 16:12
- spice keyword matches: 1493 (finesim/fsdb/spice/simulator/vcs)
- 来源：11-05 重扫令 hfeg0pkn004 cron 盲区 _nil 212 候选 peek（本轮 newest 10 取 873cy）

## 用户轮（A-faithful 选轮）
- **U#1 (idx=0)** 逐字：「找到这个路径下的xrun.log文件 ；/rundata/drcoa/V0/simdir/verilog/e0014036/verilog.ddr5.drcoa.pte.1015/test_nt/noregression.x8」——提出需求/目标 ✓
- **U#3 (idx=4)** 逐字：「读取log内容，检测内部报错」——提出需求/目标 ✓
- U#5 (idx=26)「帮我修复对齐 monitor 接口」——给出修复方向（修复对齐 monitor 接口）→ 不入 prompt（符合 A-档选轮规则：凡用户已指出根因或给出修复方案的轮不得用作 A 档任务说明）
- U#1/U#3 均为「提出需求/表达目标」轮，无根因/修复 → 符合 A-档 ✓

## 金标准（assistant 末轮用户接受的结果）
assistant 用 check_xrun_log.py（正则 `*([EFWSE])\s*,\s*([A-Z0-9]+)`）解析 xrun.log（14223 行）：

### 错误统计
- **total *E = 68**
  - CUVUNF: 66（层次化路径查找失败，致命根因）
  - ELBERR: 1（elaboration 失败总结）
  - RUNERR: 1（xrun 退出）

### 根因：`*E,CUVUNF` — monitor 引用的接口字段不存在
66 条错误集中在 3 个信号，都是 monitor 代码通过层次路径往 `A_proj_monitors_if` 接口写字段时，接口里找不到对应字段：

1. **`tREFI3P9D` ×2** — 写入 `A_proj_monitors_if.refmonitors.tREFI3P9D` 失败
   - `proj_monitor/project_pump_monitor.sv:201`（在 `TOP.A_pattern_gen` 下）
   - `proj_special.sv:1952`（在 `...I_R_CBRCNTT_49.I_internal_monitor_cbr` 下）

2. **`ace_flag_count` ×32** — 写入 `A_proj_monitors_if.tbctrlmonitors.ace_flag_count` 失败
   - `proj_special.sv:6770`（32 个 bind 层次路径，I_BnkGTopX4_{Top,Bot}/I_BnkGTop_{AC,HF,BD,X4}/I_D_PracRWCBank_{0..3}/I_prac_uceace_cnt）

3. **`PracUE_Flg` ×32** — 写入 `A_proj_monitors_if.tbctrlmonitors.PracUE_Flg` 失败
   - `proj_special.sv:6771`（同上 32 个 bind 层次路径）

### 退出阶段
- xmelab elaboration 阶段报错退出
- 退出信息：`*E,ELBERR: Error (*E) or soft error (*SE) occurred during elaboration (status 1), exiting.` → `*E,RUNERR`

### 错误行格式
```
xmelab: *E,CUVUNF (./proj_monitor/project_pump_monitor.sv,201|102): Hierarchical name component lookup failed for 'tREFI3P9D' at 'TOP.A_pattern_gen'.
```

## 合成
- **通用化 reference**：analyze_xrun_log_ref.py <log> -o out.json，解析任意 xrun/xmelab 日志：
  - total_lines / error_summary{code:count} / total_errors / failed_stage(elaboration|compilation|simulation, 按 tool 前缀 xmelab/xmvlog/xmsim 推断) / exit_errors / root_cause_code(频次最高的非退出 *E 码) / missing_fields[{name,count,source_locations[{file,line}],hierpaths_count}](对 CUVUNF/TSFVRG/XMRWNG 式 "lookup failed for 'X'" 错误提取字段名+源码位置) / exited
- **A** = A_xrun.log（faithful 重建：header + compile 0 errors + 2 tREFI3P9D + 32 ace_flag_count + 32 PracUE_Flg + ELBERR + RUNERR = 68 *E，73 行）
- **hidden B** = B_xrun.log（结构不同：header + 20 dqs2_oe_n(TSFVRG,@proj_dqs_monitor.sv:445) + 20 wrlvl_done(TSFVRG,@proj_wrlvl.sv:890) + 8 zqcal_vref(XMRWNG,@proj_zq.sv:312) + ELBERR + RUNERR = 50 *E，55 行）——不同错误码、字段名、文件、行号、计数
- **判分 15 断言(a-o)**：含交叉输入守卫(n:在 A 上 total_errors==68 & root==CUVUNF & fields=={tREFI3P9D,ace_flag_count,PracUE_Flg})+A-only 泄漏闸门(o:候选源码不含 A 专属字段名硬编码)+3 次幂等 sha256

## 自验
- ref PASS 15/15 ✓
- 4 negative 全 FAIL distinct：
  - naive_hardcode_a FAIL e(total_lines 73≠55)
  - print_expected_b FAIL n(A total_errors 50≠68, 交叉输入守卫挡 hardcode-B)
  - empty_shell FAIL e(total_lines 0≠55)
  - core_deleted FAIL j(root_cause_code None≠TSFVRG)
- NEG_RC=0 ✓
- §4.9 三假提交全 FAIL distinct(e/n/j) ✓
- 断言闸门 k_rationale=15==k_check=15≥8 ✓
- jsonl test==disk sha 1b8425884a631ac2 ✓
- jsonl B 181→182
- mark ledger 183→184 covered, spice_sim 144→145
