# r946 deepread — 1795074289377_6ibes (pevave_tasks.sv 语义差异分析)

## trace 元信息
- session: 1795074289377_6ibes.messages.json
- user: e0039218 @ hfeg0pgn145
- mc: 342, keywords: verilog:338;netlist:8;analog:7;systemverilog:4 (ak342/ck0 strict A-pure)
- domain: digital (LPDDR6 PTE testbench, verilog 主导, 非 C/B/D 域)
- msgs: 18, file 259KB, ALIVE (subdir 路径 sessions/1795074289377_6ibes/)

## 用户意图 (U#0 逐字)
「进入/proj/dejoa/V0/simdir/verilog/PTE/e0039218/lpddr6_tb_1008目录 对比lpddr6_tb_1008与lpddr6_tb_1008_dejoa里面pevave_tasks.sv的区别」

单问 analysis-Q&A: 对比两份 pevave_tasks.sv (testbench task 文件, 含 loadsequencetable/cmd_trans/getpetablevalue task, 驱动 DQ/DQS/CA/CK 激励时序) 的区别。

## assistant 工具链 (msg1-13)
1. get_agent_policy_status + list_allowed_files (lpddr6_tb_1008 depth=2) → 定位 A_Pattern_Sim.v 等
2. read_files agent-policy.json + list_allowed_files (e0039218 depth=1) → 找到 _dejoa 兄弟目录
3. read_files 两份 pevave_tasks.sv (714行/756行)
4. editor 写 compare_pevave.py (difflib unified_diff)
5. run_approved_command python-runner → 41KB diff 输出
6. msg13 给出完整语义分析报告

## trace gold (msg13)
差异集中在 loadsequencetable task:
- **① dq_delay 默认公式不同** (loadsequencetable 内 ifndef NOCHIP 分支)
  - A (原版 714行): 首段 (t_val<190/2)?8*t:, 末段 :5*t; 断点 190/210/400/490/600/750/950 (7段)
  - B (_dejoa 756行): 首段 (t_val<190/2)?3*t:, 末段 :3*t/16; 断点 190/210/255/270/320/370/450/470/510/600/660/750/810/1000 (14段)
  - B 系数整体变小 (~0.19x~3x), 断点细化, 最大 950→1000
- **② DELAY 宏覆盖块被 /* */ 注释禁用**
  - A: `ifdef DELAY6...`elsif DELAY543...`endif 生效
  - B: `/*`ifdef DELAY6...`endif*/` 整块注释, DELAYxx 宏不再起作用
  - B 在注释块内新增 20+ 个 DELAY 宏 (DELAY485/487/483/351/321/341/32011/31611/3169/3167/3165/352/353/383/32013/343/387/31615/31613/32017/38069/354/3109/34033) 但未生效
- **③ `ifdef TEST 的 dq_delay=0 强制覆盖被删除**
  - A 有 `ifdef TEST assign dq_delay=0; `endif (在 $display 后)
  - B 移除
- **④ patfile 管脚别名表精简**
  - A 档去掉: rset, cs0_all, ck_t_a, ck_c_a, ca0_ab/ca1_ab/ca2_ab/ca3_ab
  - dq0 的 begin...end 特判块 (含 `ifdef DQINV 反相 + `ifdef DEBUG_INFO 打印) 改成普通 dq_out[0]<=#(dq_delay)... 赋值
  - B 档结构一致仅格式差异
- **⑤ 纯格式差异**: ifdef SEFF/SCSWAP 块 tab→空格对齐, 逻辑同
- cmd_trans / getpetablevalue / 末尾 一致

## U#1 (msg14, 未纳入 case)
「如何调整pevave_task.v文件里面ca的delay 现在感觉电路的采样提前了半个CK 周期」
trace 在 msg15-17 开始读 pattern 表 + pevave_tasks.sv 244-316 行定位 CA delay, 但 session 截断未给出完整答案. 故 case 只取 U#0 (完整 gold), 不纳入 U#1.

## case 合成决策
- A档 trace-faithful analysis-Q&A, 单问 (U#0), k=16/16
- fixture A = pevave_diff.txt (trace msg12 的 difflib unified diff 输出, 39437 chars / 5 hunks, verbatim)
  - 选 diff 而非两份 .sv 全文: 真实文件 /rundata/dejoa/... 经 .75 ssh Permission denied (e0039218 项目目录), trace msg8 read_files 结果在 export 中为空; diff 是 trace 中 agent 实际分析依据的完整产物 (41KB), 含全部变更行+上下文, 足以支撑语义分析; 与 trace workflow 一致 (agent 先跑 diff 再分析)
- hidden B = inlined HIDDEN_B (同构异值: lpddr5/lpddr5_tb_0908/rst_n/cs_all2/ck_t_b/ck_c_b/ca?_xy/DELAY475... 系数 6/2/4/2*t/16 断点 180/200/.../980), 仅 anti-leak
- check.py 动态解析 A 的 pevave_diff.txt 提取 ground-truth (行数/系数/断点/DELAY注释态/新增宏/TEST覆盖/被删别名/dq0特判), §4.2 subprocess 跑解析脚本提取系数签名, 16 断言 (a-p)
- 自验: ref 16/16 PASS + 3 neg 全 FAIL (empty 2/16, print_only 11/16, core_deleted 7/16) + §4.9 三假 FAIL
- A.jsonl 437→438, ledger 6ibes claimed→case
