# r973 深读笔记 — uysk2 (e0048255@hfeg0pkn004, mc41)

## Session 基本信息
- session: 1795137048657_uysk2.messages.json
- user: e0048255, host: hfeg0pkn004
- keywords: rtl:148;systemverilog:3;synopsys:2;verilog:1 → A-pure digital/verification
- trace: 289KB / 71 msgs / 3 user text msgs (2 trace_ids: 715b... + f00d...)
- agent: lead (zhulong)

## 用户意图

### U#0 (Context summary, msg_compact):
Context carry-over: 修复 io_top_par_wrap 测试套件 T1/T3 失败, 避免改RTL(仅TB问题改代码), TB生成Python脚本输出到test目录. 已完成T1/T3诊断, 确认RTL APB地址解码不匹配(RTL bug, 保留不改, TB规避).

### U#1 (msg_mwolzzqa, 逐字):
「T3的测试还是有fail /proj/lacaa/V0/workdir/wenjun/SOC_MPW/IP_Dev/io_top_par_wrap/test/sim_t3.log
如果是TB 问题直接修改脚本并regen tb,
如果是RTL 问题 用文字描述给我」

### U#2 (msg_mwor3cg7, 逐字):
「对于scan=0 的场景 通过pad force驱动来做测试，
只有rb_scan=1 时通过直接apb下  pad 控制引脚（io_i ^ io_en ^ cfg_* 全部控制位）的 XOR .来驱动scan_in」

## Trace gold (U#1 诊断过程, M2-M61)

### Step 1: 读sim_t3.log → 提取FAIL
- 5928行, FAIL count: 66 (含VCS Warning-[STASKW_SFRTMATR]重复行)
- 32 unique failures: 全部 `rb_scan=0` (got=00000001, exp=00000000)
- 其他readback (rb_cpum/rb_nandtree/rb_bsd/rb_spis) 的 1和0 全PASS
- FAIL格式: `[FAIL] T3[k]rb_scan=0  <timestamp>  got=00000001 exp=00000000`

### Step 2: 追RTL scan回读路径
- `sel_scan = is_mode_atpg & ~is_mode_bsd` (L10211)
- `test_scan_in_i[N] = sel_scan ? pad_data_i[N] : 0` (hcmux2 u_scanin_N, L10220+)
- `pad_data_i = pad_data` (顶层net, 来自 io_top_ao_* 的 pad_data_o)
- **关键**: L2232 `pad_data_o = is_mode_atpg ? q_scandff : io_o`
  - q_scandff 是**时钟ed observe flop**: `d_scandff = XOR(io_i, io_en, cfg_IES, ...)` 采样于 scan_ck
  - 即: ATPG模式下, pad_data_o = q_scandff (锁存的XOR值), 不是直接PAD

### Step 3: 根因分析
- TB force PAD=0 → 期望 test_scan_in_i=0
- 但 pad_data_o = q_scandff (observe flop锁存XOR=1) → pad_data_i=1 → test_scan_in_i=1
- 即: PAD force不能直接控制scan回读路径, 因为RTL中间有observe flop
- T4(pass)只测 scan_in=1, 省略=0 case — 印证RTL设计限制

### Step 4: 结论 = **RTL issue** (非TB可修)
- 按用户要求: 用文字描述, 不改RTL
- 32 fails全rb_scan=0, 根因=RTL scan回读用q_scandff observe flop而非直接PAD

## U#2 (M63-M67): 用户指定新scan测试方法
- scan=0: pad force驱动
- rb_scan=1: 通过APB下pad控制引脚 XOR(io_i, io_en, cfg_*) 驱动scan_in
- trace未完成实现(止于M67 grep_scanck.py调查scan_ck门控)

## Case 合成方向

**提炼为通用诊断脚本** `diagnose_test_fail.py`:
- 输入: sim_log + rtl_readback_file
- 解析sim_log: FAIL计数/dedup/failing_signal/expected/got/other_signals_pass
- 解析RTL: 找回读路径, 判断是否observe flop(d_scandff/q_scandff) vs 直接pad
- 分类: observe flop → RTL issue; 直接pad但force无效 → TB issue
- 输出: JSON {total_lines, fail_count, unique_fails, failing_signal, failing_value, expected, got, other_signals_pass, classification, root_cause, fix_approach}

**A(visible)**: sim_t3_A.log(32 rb_scan=0 fails, observe flop RTL) → classification=RTL
**Hidden B**: sim_t3_B.log(16 rb_cpum=0 fails, 直接pad RTL) → classification=TB
