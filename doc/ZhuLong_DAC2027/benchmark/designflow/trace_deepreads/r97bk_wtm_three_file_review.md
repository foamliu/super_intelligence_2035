# Deepread: r97bk — WTM 三文件静态审查 (WtmFileReview-001)

## Trace
- session: `1792049688397_r97bk` (tongfanl, hfhds201, dir-based, 18 msgs, 362KB)
- A-档选轮: U#0 (提出需求 "帮我检查下这三个文件写的有没有问题", 无根因/修复 → A-faithful CLEAN ✓)
- U#16/17 follow-up (用户粘贴 WTM004 编译报错 PAANAP/FASMTP L37-38) = 后续轮, **不入 prompt**

## 金标准 (assistant A#15 完整审查报告)

### WTM001_normal_check.v — 基本正常
| 行 | 发现 |
|:--:|:-----|
| L5 | `reg [48*6 -1:0] wtm_wr_data[]` = 288 bits (非X1P12高144位闲置) |
| L262 | `L_data = {5'b11111,seed}` — 5 bits padding (前5次迭代 DQ0 MSB 被 padding 占据) |
| L780 | `new_bit0 = L_data[23] ^ L_data[19] ^ L_data[10] ^ L_data[4]` — 多项式 x^24+x^20+x^11+x^5+1, taps [23,19,10,4] |
| L70 | `Load_Mode(.ma(8'hDE)...op_mark(8'b0000_1111)...)` — MR DE 首个 op_mark |
| L64 | `for (int i=1;i>=0;i--)` — 2 次迭代 |

### WTM002_normal_check.v — 冗余 + 重复
| 行 | 发现 |
|:--:|:-----|
| L38-39 | **Dead Code**: `lfsr_seed[23:5]=$urandom; lfsr_seed[4:0]={...}` 在 for 循环前算了一次, 循环内(L133+)又重算 → 前一次从未使用 |
| L39 | 冗余字面量 `1'b1^1'b1` (恒等于 1'b0) |
| L212 | `task gen_wtm_write_data_002(...)` — 与 gen_wtm_write_data 内容完全一致 (renamed duplicate) |
| L62 | `for (int i=5;i>=0;i--)` — 6 次迭代 |
| DE op_mark | `8'hff` (全 mask, 与 WTM001 的 8'b0000_1111 不同) |

### WTM004_block_check.v — 严重问题
| 行 | 发现 |
|:--:|:-----|
| L31 | `pattern_name="WTM001_normal_check"` — **与文件名 stem WTM004_block_check 不匹配** (审查报告标为"Task名称错误") |
| L180 | `task gen_wtm_write_data_004(...)` — 又一份重复 |
| L140(报告) | 提前 endtask → 编译错误 (U#16/17 证实 PAANAP/FASMTP) |

### 跨文件
- gen_wtm_write_data 在 3 文件各定义一份 (WTM002=_002, WTM004=_004) — 重复维护

## 合成 (WtmFileReview-001, spice_sim A-faithful L1, k=18)
- 通用化 `wtm_review.py --wtm1 <f1> --wtm2 <f2> --wtm3 <f3> -o out.json` 静态提取:
  data_width_bits (eval `N*M`), pattern_name + filename_stem 匹配, first_for_loop_iterations (N+1),
  lfsr_padding_bits (`{N'bXX,seed}`), lfsr_feedback_taps (`new_bit0=L_data[a]^..[d]`),
  first_de_op_mark (首个非注释 Load_Mode 8'hDE op_mark), write_data_task_name + duplication (后缀),
  has_redundant_xor_literal (`1'b1^1'b1`), has_dead_seed_before_loop (循环前 indexed 赋值 + 循环内再赋值)
- A = 真实节选 A_wtm1/2/3.v (verbatim real lines: width 288, taps[23,19,10,4], padding5, loop2/6, op_mark 8'b0000_1111/8'hff, dead code, 1'b1^1'b1, gen_wtm_write_data_002/004, WTM004 pattern_name=WTM001_normal_check mismatch)
- hidden B = 合成 BWTM001/002/004_normal_check.v (不同: width 32*6=192, taps[22,18,9,3], padding4, loop3/4, op_mark 8'b0000_0010/8'h0f, 无 dead code, 无 1'b1^1'b1, 无 duplicate task, BWTM004 pattern_name 匹配 stem)
- 判分 18 断言 (a-r): 含交叉输入守卫 (B 值全不同→硬编码 A 必 FAIL) + A-only 泄漏闸门 (quoted-token markers) + 3 次幂等 sha256

## 自验
- ref on A: 288/[23,19,10,4]/5/loop2/8'b0000_1111/dead_code True/1'b1^1'b1 True/dup True/WTM004 mismatch ✓
- ref on B: 192/[22,18,9,3]/4/loop3/8'b0000_0010/dead_code False/redundant False/dup False/BWTM004 match ✓
- check.py REF candidate: PASS (18/18) ✓
- 4 negative (naive_hardcode_a / always_pass_stub / core_deleted / empty) 全 FAIL distinct ✓
- negative_selftest NEG_RC=0 ✓
- §4.9 三假 (空壳=core_deleted FAIL / 打印期望=naive_hardcode_a FAIL on B / 删核心=core_deleted FAIL) ✓
- 断言闸门 k_rationale=18 == k_check=18 (a-r) >= 8 ✓
- jsonl test==disk check.py roundtrip sha fa31ca60641f4005 ✓ → 追加 EDA-Eval-DesignFlow_B.jsonl (159→160) + mark ledger (case 161→162, spice_sim 125→126)
