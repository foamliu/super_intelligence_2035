# r1006 — 46vx0 (zhengc@hfeg0pkn004) — LPDDR6 stimulus.list 头部生成 produce-task

## trace 来源
- scan: `ssh_eda_search_20261122_172249/summary.tsv` (.75, 2026-11-22)
- session: `1795143264722_46vx0.messages.json` (315KB / 59 msgs / 27 asst)
- host: hfeg0pkn004 ; user: zhengc ; mc=63 (verilog:354 + systemverilog:7 主导 A-pure digital)
- 归因: A=361 (verilog+systemverilog) vs C=7 (aether/cadence/pyaether) vs B/D=131 (analog+netlist) → 强 A-pure
- ledger 状态: fresh (4-shard ledger 4172 sids diff 得 42 fresh, 46vx0 未 ledgered)
- zhengc 前 3 parked sessions (bxnc8/uqvno/axn69) 均非本 sid, 无 intent-dup

## 用户原话（逐字）
> 在这个/ai_sandbox/dscqa/V0/agentdir/zhengc/verilog.lpddr6.decqa.finesim/目录下分析，/ai_sandbox/dscqa/V0/agentdir/zhengc/verilog.lpddr6.decqa.finesim/log_test/test_t1119_SC0_RDQS_ENtENc_WLS_SetB_DBI_RD_EN_EDBI_WR_EN_tCH50_4b4g_BL1_14400_FF.x12/下的stimulus.list是怎么产生的？

## trace 调查结论（agent）
1. stimulus.list 不是脚本写死，而是 LPDDR6 SystemVerilog testbench `lpddr6_test.sv` 的
   `task analogvec_gen(integer fd_sim, integer fd_vec, integer fd_cspd, integer fd_probe)`
   在仿真运行时用 `$fopen("stimulus.list")` 打开、`$fdisplay(fd_vec,...)` 写入。
2. 头部由两段逻辑产生：
   - `string signal_name[`SIG_NUM]` 数组按编译宏 `SCSWAP` / `HIBYTE` 的不同分支赋值
     （CK/CS/CA/WCK/RDQS/DQ 的通道 0/1 顺序、DQ bit 的高低位顺序都受两宏控制；
     未赋值的下标保持空字符串）。
   - 写循环（逐字，lpddr6_test.sv:16103-16120）：
     ```systemverilog
     $fdisplay(fd_vec,"signal");
     for(int i=0;i<`SIG_NUM;i++)
         if(signal_name[i]) $fdisplay(fd_vec,"+ %s",signal_name[i]);
     $fdisplay(fd_vec,"+ A_cmd_string<127:0>");
     $fdisplay(fd_vec,"+ B_cmd_string<127:0>\n");
     ```
3. signal_name[] 赋值块逐字节提取自 trace read_files（lpddr6_test.sv:15925-16012，
   含 `ifdef SCSWAP` / `ifdef HIBYTE` 双分支 + `else` / `endif` 嵌套）。
4. 实际 test_t1119 x12 目录的 stimulus.list 头部 = 非 SCSWAP + 非 HIBYTE 分支
   （CK0_t 首、DQ0<11> 首、CS0PDN 在 CS1PDN 前、CA0 在 CA1 前），78 行。

## 造题转化
- archetype: trace 调查类（"X 是怎么产生的"）→ produce-task（"模拟写循环生成 X 的头部"）
- 任务: 通用 `solve.py [tb_snippet.v] [defines.txt] [out]`，模拟 `$fdisplay(fd_vec,...)` 写循环
  从 testbench 片段 + 宏定义文件生成 stimulus.list 头部。
- 关键牙点: tb_snippet.v 含**全部** ifdef 分支（SCSWAP/HIBYTE 双 × 双），fixture A 与
  hidden B **共用同一 tb_snippet.v**，仅 defines.txt 不同（A: SCSWAP=0/HIBYTE=0，
  B: SCSWAP=1/HIBYTE=1）→ solver 必须真解析 ifdef 嵌套，不能硬编码 A 答案。
- A/B 信号顺序全异（CK0↔CK1、CS0↔CS1、CA0↔CA1、WCK0↔WCK1、RDQS0↔RDQS1、
  DQ0<11..0>↔DQ1<5..0,11..6>、exp_* 同），anti-hardcode 锚充足。

## check.py (k=19)
- ① submit.zip 存在解压 ② 含 .py solver ③ py_compile 通过
- ④ A exit0 ⑤ A 写非空 ⑥ A md5==02c7759e18820a7caad4737291b977df（78 行逐字节）
- ⑦ B exit0 ⑦b B 写非空 ⑧ B md5==ed90a3b4257553ac68030d9629f1d1cd
- ⑨ B 首行==signal ⑩ SCSWAP: B 第2行==+ CK1_t ⑪ + CK1_t 在 + CK0_t 前
- ⑫ HIBYTE: + DQ1<5> 在 + DQ1<11> 前 ⑬ B 末两行==[+ A_cmd_string<127:0>,+ B_cmd_string<127:0>]
- ⑭ 反硬编码: A≠B md5 ⑮ SCSWAP: + CS1PDN 在 + CS0PDN 前
- ⑯ 确定性 3 次 md5 一致
- ⑰ §4.9 空壳: size>200 + def + import
- ⑱ §4.9 print-only: B 行数==78 且含 SCSWAP 锚 CK1_t + HIBYTE 锚 DQ1<5>
- ⑲ §4.9 core-deleted: B 中 + CA1<3> 在 + CA0<3> 前（需真分支解析）

## negatives (§4.9 三假)
- neg_empty: 仅注释，无输出 → ⑤ FAIL
- neg_print_only: 硬编码 A 的 CK0_t 块无视输入 → ⑧ B md5 FAIL
- neg_core_deleted: 脚手架在但 collect_assignments 返回空，只输出 signal+两 trailer → ⑧ FAIL

## 自测
- `python3 negative_selftest.py` → ref PASS + 3 negs FAIL = ALL GOOD ✅
- reference solution solve_ref.py 在 A/B 下均逐字节匹配 expected_A.txt / expected_B.txt

## 交付物
- assets/EDA-Eval-DesignFlow-Lp6StimListHeaderProduce-001/: tb_snippet.v, defines.txt, task_brief.md
- reference/EDA-Eval-DesignFlow-Lp6StimListHeaderProduce-001/: solve_ref.py, check.py,
  expected_A.txt, expected_B.txt, hidden/(tb_snippet.v + defines.txt SCSWAP=1/HIBYTE=1),
  negative/{neg_empty,neg_print_only,neg_core_deleted}.py, negative_selftest.py
- A.jsonl: 463 → 464 (append EDA-Eval-DesignFlow-Lp6StimListHeaderProduce-001)
- ledger: 46vx0 claimed → case

## 选料注
42 fresh A-pure 池健康，本轮消费 1（46vx0），剩 41 fresh 仍可用，stop-loss 不触发。
46vx0 是 zhengc 新 session，与 r1004 4lezu(wenfeiz netlist-hier) / r1005 qedl8(max7c csv-sort)
无 intent-dup（LPDDR6 stimulus.list 头部生成是新意图）。
