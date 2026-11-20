# Trace deepread — 1790669053939_jw8ya (tongfanl @ hfhds201)

**Session**: `1790669053939_jw8ya` (dir-based, 68 msgs, 787KB, mtime Sep 30 10:08 / Oct 1 18:12)
**User**: tongfanl · **Host**: hfhds201 (10.129.32.75, .75 本机, cron 盲区)
**Domain**: spice_sim (DDR6 vecgen_local testbench, sim_vector)
**Shard**: B (spice_char) · **Track**: A-faithful · **Level**: L1
**Case**: EDA-Eval-DesignFlow-MrrTaskSignatureExtract-001

## 选轮 (A-档)
- **U#1 (idx 0) 任务说明轮**（逐字作 prompt）:
  `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local`
  `分析一下上述路径，告诉我task MRR的书写逻辑。`
- 用户提出需求（"分析 task MRR 的书写逻辑"），**无根因/无修复方向** → 符合 A-档选轮 ✓
- 后续轮 U#3 (psd_cmd_sync 追问)、U#49+ (xrun NWRKDRA 报错根因调试) **不入 prompt**（已含根因/修复）

## 金标准 (assistant 分析)
assistant 用 list_allowed_files + read_files + run_commands(grep) 分段读取 vecgen_local 目录与 ddr6_test.sv，最终在 **A#45** 给出完整 MRR 书写逻辑分析：

### 目录结构
DDR6 向量生成 (vecgen) 验证环境 (DSCQA V0)：
- `ddr6_test.sv` (~10361 行): 主测试模块, 所有命令 task 定义 (MRR/MRW/ACT/WR/RD/REF/SRE)
- `ddr6_tasks.sv`: 底层 pin 操作 (loadonepin/loadca/loaddq/loadcs/drive_cmd)
- `ddr6_package.sv` / `ddr6_specdef.sv` / `ddr6_interface.sv` / `ddr6_timing.sv` / `compare_tasks.sv` / `ddr6_genvector.sv`
- `bin/` (vsim 脚本) · `config/` · `cfg_files/` (pattern 配置) · `log/` · `.dsim_vec/`

### MRR Task 定义 (ddr6_test.sv ~line 2823)
**签名 (15 参数)**:
1. `reg[MODEMA_BITS-1:0] ma` — Mode Register 地址 (bit[7]=0 direct, =1 page)
2. `bit termit=0` — 是否终止后续期望数据
3. `bit cw=0` — Control Word (DRAM 是否忽略此命令)
4. `reg[MODEOP_BITS-1:0] mrr_exp=0` — 用户自定义期望 MRR 数据
5. `reg[MODEOP_BITS-1:0] mrr_psd1_exp=0` — PSD1 期望数据 (1P 模式)
6. `bit[1:0] mrr_expf=1` — 期望数据来源 flag (2=用户定义/1=shadow register/0=忽略输出 z)
7. `bit wo_exp=0` — 只写期望值 (DDR6 暂未用)
8. `integer rank=0` — 目标 rank
9. `bit parity_errinject1=0` / 10. `bit parity_errinject2=0` — CA 总线 parity 错误注入
11. `integer enops=0` — 强制 NOP 数覆盖
12. `bit cmdcancel=0` — 命令取消 (CS 高阻)
13. `bit get_lock=1` / 14. `bit put_lock=1` — semaphore lock 获取/释放
15. `bit[1:0] ca43=1` — 1P 模式下控制 PSD 访问 (0=None/1=Self/2=Other/3=Both)
- 行尾注释: `// TODO: ca43 is not used!!!!!`

**begin:MRR_task 块 (19 个局部变量)**:
ca_tmp, mrr_op, mrr_op_psd0, mrr_op_psd1, mrr_op_psd0_exp, mrr_op_psd1_exp,
val (reg[MAX_BURST_LEN*DQ_BITS-1:0]), ca_parity_en, rl, bl, wpst,
ca_valid (bit[2:0]), MR0_mode_reg_page (bit[1:0]), par1, par2, nops (int),
cmd_info (string), fsp_state, fsp_wr

**TODO 注释 (3 条)**:
1. `ca43 is not used!!!!!` (签名行尾)
2. `can not use ca34=0/3 in 1P6 page MRR right now, not sure if NOP and Both is needed for MRR in the future.` (body)
3. `For FSP MRs, MRR is read from FSP_WR registers.` (body)

**执行流程**:
1. `cw=$urandom()`; 若 `ma==MR116` (ZQ code) 每 3 次读取注入 ZQ code 更新 (调 `MRSetting`)
2. `if(ca43==0||ca43==3) ca43=1`; `ShareDRIVER.task_running_num[sc]++`; `ca_valid=$urandom_range(7)`
3. `tb_message="MRR"`; `MR0_mode_reg_page=0`
4. `wait_2psdcmd_unlock()` → `read_lock()` → `Psd_mrr_wr_mutex_get(.mrr(1))`
5. `nops=cal_nops(.cmd("MRR"),.enops(enops))` → `psd_cmd_sync(.cal_nop(nops))` → `auto_wucs(.nops(nops))`
6. `Deselectn(.n(nops|enops))` → `check_in_even()`
7. 取 MR 值: `fsp_state`/`fsp_wr`/`rl`/`bl=24`/`wpst=2`/`ca_parity_en`
8. `sem_cmd.get(1)`; `sim_addr.ma<=#(toffset) ma`
9. MR4/MR86 特殊处理 (`load_ref_rate_exp`/`load_temperature_exp`)
10. 读 MR shadow register (`mr_direct`/`mr_direct_fsp`/`mr_page`/`mr_page_fsp`, 按 `ma[7]` direct/page 分支)
11. 格式化 `cmd_string` (`%0d_MRR`/`MRRCancel`/`MRR_Blocking`)
12. 4-cycle CA 总线驱动 (C0/C1/C2/C3, `loadcs`/`loadca`/`drive_cmd`)
13. exp 值组装 (`case(mrr_expf)`) → `val[]` → `load_exp_fifo`
14. 收尾: `sem_cmd.put(1)` → `let_2psdcmd_lock()` → `read_unlock()` → `ShareDRIVER.task_running_num[sc]--` → `endtask`

**被调子任务集合**: MRSetting, wait_2psdcmd_unlock, read_lock, Psd_mrr_wr_mutex_get,
cal_nops, psd_cmd_sync, auto_wucs, Deselectn, check_in_even, loadcs, loadca, drive_cmd,
load_ref_rate_exp, load_temperature_exp, Deselect, cmdcycle_cal, sem_cmd.get/put,
let_2psdcmd_lock, read_unlock

## 通用化 (合成)
`extract_mrr_task_meta.py <test.sv> -o out.json` — 解析任意 SystemVerilog `task <NAME>(...) ... endtask` 定义，提取:
- task_name · params[{name,type,width,default,has_default}] · param_count
- begin_block_name · local_vars[{name,type,width}] · local_var_count
- todo_comments[] · has_todo · called_tasks[] · has_endtask · conclusion

跳过 `//` 行注释中的 "task" 伪匹配; 按 `[]/()` 深度切分参数; strip `/* */` 后匹配局部声明;
合并连续 `//` 续行的 TODO; 子任务调用 = `IDENT(` 且前字符非 `.` (排除 port-arg) 且非关键字/参数/局部。

## 资产
- **A** = `A_test.sv`: 真实 MRR task 节选 (签名+19 局部+body 开头~line 3020 + 收尾 4550-4569 + endtask; 中段 ~1500 行 CA 驱动/compare/MCME 以 elision 注释省略)
- **hidden B** = `B_test.sv`: 合成 `task WR` (8 参数, begin:WR_task, 7 局部, TODO "WR does not support DBI yet", 调用 loadcs/loadca/drive_cmd/load_dq_fifo/write_compare; **不含任何 A 标记**)

## 判分 (16 断言 a-p)
含交叉输入守卫 (B→task_name=WR/pc=8, A→task_name=MRR/pc=15, 挡硬编码任一答案) +
A-only 泄漏闸门 (MRR/MRR_task/ca43/mrr_exp/MR116/MRSetting/Psd_mrr_wr_mutex_get/mrr_op 不入 B 输出) +
幂等 sha256。

## 自验
- ref PASS 16/16 ✓
- 4 negative (naive_hardcode_a FAIL f / print_expected_b FAIL i / empty_shell FAIL e / core_deleted FAIL g) 全 FAIL distinct ✓
- negative_selftest NEG_RC=0 ✓
- §4.9 三假 (空壳 FAIL e / 打印期望 FAIL i / 删核心 FAIL g) 全 FAIL ✓
- 断言闸门 k_rationale=16 == k_check=16 ≥ 8 ✓
- jsonl test==disk check.py roundtrip sha 44e04dd8509d7329 ✓ → 追加 EDA-Eval-DesignFlow_B.jsonl (157→158)
- mark ledger (159→160 covered, spice_sim 123→124)
