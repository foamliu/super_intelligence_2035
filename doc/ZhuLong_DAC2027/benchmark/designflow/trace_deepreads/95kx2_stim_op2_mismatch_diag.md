# Trace deepread: 1790998236503_95kx2 (tongfanl @ hfhds201) — StimOp2MisMatchDiag

## 选轮
- U#0 任务说明轮逐字作 prompt（提出需求「为啥 OP2 设置为1但激励 OP2 没为1」，无根因/修复 → A-faithful 选轮 ✓）
- U#87/91/102/141/158/162 后续澄清/追问轮不入 prompt

## trace 基本信息
- session 1790998236503_95kx2, tongfanl, hfhds201, dir-based, 170 msgs, 1.68MB
- spice_sim 域（DDR6 DSCQA vecgen WTM002 stimulus 抽激励诊断）

## 金标准（assistant 多轮诊断，最终 M#169 完整）
1. **WTM002_normal_check.v MR222(0xDE) 调用清册**：`for(int i=2;i>=0;i--)` 循环 3 次，每轮 2 个 MR222 调用点：
   - line 44: `.op({4'b0000,1'b0,1'b1,$urandom,pattern_select})` → OP[7:4]=0000, OP[3]=0, **OP[2]=1**, OP[1]=$urandom, OP[0]=pattern_select
   - line 75: `.op({4'b0000,1'b1,1'b1,$urandom,pattern_select})` → OP[3]=1, **OP[2]=1**, OP[1]=$urandom
   - 共 6 次 MR222 执行，**全部 OP[2]=1**
2. **op_int 合并逻辑**（ddr6_test.sv:2769）：`op_int = rstall ? (op) : (op_org&(~op_mark) | (op&op_mark));`
   - rstall=0, op_mark=8'hff → `op_int = (op_org & 0) | (op & ff) = op` → OP[2]=1 被正确设置
3. **根因① timing_desync**（ddr6_test.sv:2781）：`sim_addr.op <= #(toffset) op_int;` 带延迟非阻塞赋值 → stimulus.vec/list 采样 PSD_OP 时 sim_addr.op 可能仍是上一个 MRW 的旧值，MA 与 OP 字段时序错位
4. **根因② sampling_source_bug**（ddr6_genvector.sv:423）：PSD1_OP 采样源 ifdef
   - `ifdef DUALSC sc1.sim_addr.op / `elsif SC0 8'hz / `elsif SC1 sc0.sim_addr.op`
   - SC1-only 模式下 PSD1_OP 采的是 `sc0.sim_addr.op`（错 sc，应为 sc1）→ 显示的不是 WTM002(SC1) 的 OP
5. **结论**：代码逻辑正确（OP[2]=1 确实写入），问题出在 analog vector 采样/显示（时序延迟 + 采样源 bug）

## 合成
- 通用化 `diag.py`（读 A_wtm2.v/A_test.sv/A_genv.sv，写 out.json）：
  - 解析 WTM MR222 Load_Mode `.op({...})` 拼接字段 → 逐 bit 值（字面量 0/1 或符号）+ 检测 `for(int X=N;X>=0;X--)` 循环次数 + 调用点/迭代/总执行数 + 每 bit 汇总（all_one/all_zero/varies）
  - 解析 ddr6_test：op_int 合并 expr + `sim_addr.op <= #(<var>) op_int` 延迟变量
  - 解析 ddr6_genvector：PSD1 op ifdef 分支 + 检测单-SC 分支采错 sc 的 bug
  - root_causes 两条 + code_logic_correct=True
- A = 真实 trace-time 节选（A_wtm2.v 循环+2 MR222 调用点 / A_test.sv op_int 合并+sim_addr.op+toffset / A_genv.sv PSD1_OP ifdef SC1→sc0）
- hidden B = 合成（B_wtm2.v 循环 5 次 j=4..0 + 2 调用点 OP[3]=1,OP[2]变化 / B_test.sv delay var=tdelay / B_genv.sv SC0-only 采 sc1 bug）→ 目标位 OP[3]、延迟变量、采样 bug 分支均与 A 不同，挡硬编码

## 判分（17 断言 a-q）
- 含交叉输入守卫（候选 diag.py 在 A 跑得 OP[2] all_one=True，证泛化）+ A-only 标记泄漏闸门 + 3 次幂等 sha256

## 自验
- ref PASS 17/17 ✓ + 4 negative 全 FAIL distinct（naive_hardcode_a→d / always_pass_stub→o / core_deleted→k / empty_shell→b）✓ + negative_selftest NEG_RC=0 ✓ + §4.9 三假（空壳/打印期望/删核心）全 FAIL ✓ + 断言闸门 k_rationale=17==k_check=17≥8 ✓ + jsonl test==disk check.py roundtrip sha 0a858ae029af7289 ✓ → 追加 EDA-Eval-DesignFlow_B.jsonl(161→162) + mark ledger(case 163→164, spice_sim 127→128)
