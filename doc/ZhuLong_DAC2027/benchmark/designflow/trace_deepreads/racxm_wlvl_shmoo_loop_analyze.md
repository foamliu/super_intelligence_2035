# trace_deepread: 1789633680645_racxm (ericw @ hfhds201) — WlvlShmooLoopAnalyze

## 选料来源
- 11-05 重扫令 · hfhds201 cron 盲区 top-200 by size diff ledger_B → 137 not-in-ledger
- peek 36 候选（含 16 real-spice-user + 20 内部账号）
- **racxm** ericw n=7 msgs last=assistant（COMPLETE）CLEAN A-faithful ✓
- 台账原 status=parked (2026-11-08 02:22, note="non-spice-domain:analog:23,drc:8,no-spice-keywords")
  → **park 原因 = summary 工具关键词代理误分类**（analog/drc 计数非 spice 关键词）
  → 实际内容 = spice_sim/sim_vector pattern 分析（prompt 含 finesim workdir 路径 + DDR5 write-leveling shmoo .v 文件循环分析）
  → 本轮 deepread 证实为 spice_sim 域 → mark --status case 覆盖 parked

## trace 结构（7 msgs）
- M#0 user (U#0 任务说明轮，逐字作 prompt):
  `Writeleveling001_external_writeleveling_preamble2_shmoo`
  `/proj/drgpx/V0/simdir/finesim/workdir/ericw/DDR5/DRCPA/analogsim/Writeleveling`
  `分析这个路径下的这个文件 里面的循环是干什么的 如何循环的`
  → 提出需求（分析循环作用+机制），无根因/无修复方向 → 符合 A-档选轮 ✓
- M#1 assistant: list_allowed_files + run_commands（run_commands 被策略禁用）
- M#2 user: list_allowed_files 结果 → 文件是 symlink，实际在
  `/home/coverage/DDR5/DDR5_Common_Pattern/analogsim/Writeleveling/Writeleveling001_external_writeleveling_preamble2_shmoo.v`
  （目录含 WTM001..007 + AWRP 等 7+ shmoo pattern 文件）
- M#3 user: run_commands disabled 错误
- M#4 assistant: read_files 真实 .v 文件
- M#5 user: read_files 工具结果（文件内容，31 行）
- M#6 assistant: **金标准 — 完整循环结构分析报告**

## 金标准（assistant M#6，人工复核 ✓）
真实 .v 文件 31 行，核心 for 循环（第 21 行）：
```systemverilog
for(int i=128*((modereg.cl_num/2-2)-5);i<=128*((modereg.cl_num/2-2)+7);i=i+32)begin  //-5<CWL<7
    if(i==128*((modereg.cl_num/2-2)-5)) begin
         Write (.bg(bg0),.ba(bk0),.col(cola),.dq(DATA_A), .wrlving_fine_step(i), .wrlving(1),.enops(15_000/timing.tCK));
    end else begin
         Write (.bg(bg0),.ba(bk0),.col(cola),.dq(DATA_A), .wrlving_fine_step(i), .wrlving(1));
    end
end
```
assistant 分析要点（与真实代码 1:1 核对 ✓）：
1. **循环变量 i** = write leveling fine step 延迟调整值，经 `.wrlving_fine_step(i)` 传给 Write task
2. **范围由 CAS Latency cl_num 决定**：base = `cl_num/2 - 2`（CWL 标称基准点）
   - start = `128 * ((cl_num/2-2) - 5)` → CWL-5
   - end   = `128 * ((cl_num/2-2) + 7)` → CWL+7
   - step  = `+32`
3. **迭代次数** = ((7-(-5)) * 128) / 32 + 1 = 1536/32 + 1 = **49 次**
4. **首迭代特殊处理**：if(i==start) 额外传 `.enops(15_000/timing.tCK)`（NOP 等待 ≈15ns，给 DRAM 稳定时间）；其余 48 次背靠背
5. **Write 调用参数**：.bg(bg0), .ba(bk0), .col(cola), .dq(DATA_A), .wrlving_fine_step(i), .wrlving(1)
6. **整体目的**：Shmoo 扫描测试 — 扫 write leveling fine step 延迟，找 pass/fail 边界绘 shmoo plot

## 合成（case = EDA-Eval-DesignFlow-WlvlShmooLoopAnalyze-001）
- 通用化脚本 `analyze_wlvl_shmoo_loop.py <svfile> -o out.json`：
  - 正则解析 for 循环 → var/start_expr/end_expr/step
  - 解析 `<scale>*((modereg.cl_num/2-2)<offset>)` → scale/start_offset/end_offset/base_expr
  - 计算 iter_count = ((end_offset - start_offset) * scale) // step + 1
  - 平衡括号匹配 if(var==start_expr) 分支 → diff if-branch vs else-branch Write 参数 → extra_param/extra_value
  - 解析 else-branch Write 调用 → params/dq_value/wrlving_value
- **A** = 真实 .v 文件（31 行原文，从 .75 cp 取 byte-exact，md5 6bf8c8b5d3a3d2192ab20232667c205f）
- **hidden B** = 合成 `Writeleveling010_external_writeleveling_preamble3_shmoo.v`：
  - var=j（≠i），scale=64（≠128），offsets -3..+9（≠-5..+7），step=32（同），iter_count=25（≠49）
  - 首迭代 extra_param=precharge_wait（≠enops），extra_value=20_000/timing.tCK（≠15_000）
  - dq=DATA_B（≠DATA_A），wrlving=2（≠1），preamble=3tCK（≠2tCK），dqmode=X8（≠X4）
  - 结构同型但取值/命名全异 → 挡硬编码
- 判分 15 断言(a-o)：含交叉输入守卫(m: 候选在 A 跑得 i/128/49/enops 证明泛化)+A-only 未泄漏闸门(n: outB 无 Writeleveling001/15_000/enops/DATA_A)+3 次幂等(o)

## 自验
- ref PASS 15/15 ✓（A: i/128/-5/7/32/49/enops/DATA_A；B: j/64/-3/9/32/25/precharge_wait/DATA_B）
- 4 negative 全 FAIL distinct：naive_hardcode_a→c(var i), empty_shell→b, core_deleted→h(iter 24), leak_a_tokens→j(enops) ✓ NEG_RC=0
- §4.9 三假：(a)空壳→b ✓ (b)只 print 期望→b(invalid JSON) ✓ (c)删核心(去+1)→h ✓
- 断言闸门 k_rationale=15==k_check=15≥8 ✓
- jsonl B 167→168，mark ledger parked→case
