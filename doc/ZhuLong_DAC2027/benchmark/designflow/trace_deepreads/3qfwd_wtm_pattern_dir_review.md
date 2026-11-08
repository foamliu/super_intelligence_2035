# Deepread: 3qfwd — WTM pattern directory review

**trace**: `1793857677982_3qfwd` (tongfanl@hfhds201, dir-based, 38 msgs, 319KB)
**domain**: spice_sim (DDR6 DSCQA analogsim WTM pattern static review)
**case**: EDA-Eval-DesignFlow-WtmPatternDirReview-001 (A-faithful L1, k=15)

## A-档选轮
- U#0 (任务说明轮, 逐字作 prompt): `<user_input mode="act">/home/tongfanl/DDR6/DSCQA/analogsim/WTM/\n帮我看下这里面的pattern有没有问题</user_input>`
- 提出需求，无根因/修复方向 → 符合 A-档选轮 ✓
- 后续轮（U#2 listfiles_result, U#12 python-runner stdout, U#18 deep_check stdout 等）为工具结果，不入 prompt

## 金标准 (assistant msg#37 完整审查报告)
assistant 用 list_files + read_files + python-runner (check_patterns.py / deep_check.py / nest_check.py) 审查 5 个 symlinked Verilog pattern 文件（WTM001-005），产出结构化报告：

### 基础结构检查（✅ 无问题）
| 文件 | 大小 | task/endtask | begin/end | ifdef/endif | 链接 |
|---|---|---|---|---|---|
| WTM001_normal_check.v | 48 KB | ✅ | ✅ | ✅ | 有效 |
| WTM002_normal_check.v | 50 KB | ✅ | ✅ | ✅ | 有效 |
| WTM003_normal_check.v | 1.4 KB | ✅ | ✅ | ✅ | 有效 |
| WTM004_block_check.v | 49 KB | ✅ | ✅ | ✅ | 有效 |
| WTM005_function_combine.v | 55 KB | ✅ | ✅ | ✅ | 有效 |

### 🔴 确认问题（7 项）
1. **WTM004:31 `pattern_name="WTM001_normal_check"`** — 复制粘贴残留（应为 "WTM004_block_check"）
2. **WTM004:74 调用 `gen_wtm_write_data`（WTM001 的函数）**，自身 `gen_wtm_write_data_004`（L180）从未被调用 → 死代码 + 跨文件依赖
3. **WTM001 错误注入配置与实际写入矛盾** — error_write bit9 但 Write[9] 注释掉 → 死错误注入；WTM004 同样注释 Write[9]
4. **WTM004 入参 `rowf` 全程未使用** — 两个 Active 均用 `.row(rowa)`
5. **`tmrr_wtm` 向下取整** — 三文件都有，作者留 TODO
6. **X1P12/X1P6 条件编译全被注释**，硬编码 X1P12 分支
7. **WTM004 缺少 PDE/PDX 初始化序列** — 只有 CLK_SYNC_OFF()

### 🟡 WTM003 单独说明（疑似未完成/遗留）
仅 28 行，与其他 4 个差异极大：用老接口 `WTM(...)`、无 pattern_name、无 PDE/PDX、seed_config=1 但 seed 范围窄、注释与代码矛盾

### 🟢 次要问题
- WTM002:50 `lfsr_seed[15]^lfsr_seed[9]^1'b1^1'b1` 冗余异或
- 错误 UI 掩码范围不一致
- WTM002 DE 写用 `op_mark(8'hff)`
- gen 函数名 vs $display 打印名不一致
- 非 ASCII 箭头（→）

### 🧹 环境提示
- `.WTM001_normal_check.v.swp` vim 遗留
- 5 个 .v 均为指向 `/home/sosadmin/sos/cache/Coverage.cac/Finesim/` 的符号链接

## 合成 + 落库
- 通用化 `review_wtm_dir.py <wtm_dir> -o out.json`：静态提取每文件 pattern_name+stem 匹配、gen_func 定义/调用（死代码+跨文件）、error_write bits vs commented-write-index（死错误注入）、PDE/PDX 初始化、rowf 使用、stub/老接口、.swp 检测
- **A=真实节选** A_wtm1/2/3/4/5.v（verbatim key marker lines，trim 保留 task/pattern_name/gen_wtm_write_data/error_write/Active/Write/PDE-PDX/CLK_SYNC/WTM()）
- **hidden B=5 合成 BWTM 文件 + .swp**（不同名/不同结构/不同植入问题）：
  - BWTM010_normal_check.v — CLEAN baseline（pattern_name 匹配 stem，PDE/PDX 齐全，gen_wtm_write_data_010 调用+定义，无死代码，rowf 使用）
  - BWTM020_block_check.v — pattern_name="BWTM010_normal_check"（植入 mismatch）+ 缺 PDE/PDX（仅 CLK_SYNC_OFF）+ rowf 未用（两个 Active 均用 rowa）
  - BWTM030_normal_check.v — stub（25 行 + 老 WTM() 接口）
  - BWTM040_block_check.v — 死代码（gen_wtm_write_data_040 定义未调用）+ 跨文件调用（gen_wtm_write_data_010）+ 死错误注入（error_write bit7 + Write[7] 注释）
  - BWTM050_function_check.v — CLEAN
  - .BWTM020_normal_check.v.swp — 植入 .swp
- 判分 15 断言 (a-o)：交叉输入守卫（A-only 标记不泄漏）+ 3 次幂等 sha256

## 自验
- ref review_wtm_dir.py 在 B 上跑 → 5 files / 10 issues / swp=[".BWTM020_normal_check.v.swp"] ✓
- ref 打包 submit.zip → check.py → **PASS 15/15** ✓
- 4 negative 全 FAIL distinct：naive_hardcode_a (d,e,f,g,h,i,j,k,l,m,n — A 名泄漏+交叉守卫) / always_pass_stub (c,d,e,f,g,h,i,j,k,l,m — 空 files) / core_deleted (f,g,h — 死代码/跨文件/死注入检测删除) / empty_shell (b — 无输出) ✓
- negative_selftest NEG_RC=0 ✓
- §4.9 三假：空壳 FAIL b / 打印期望(空 files) FAIL c+ / 删核心 FAIL f,g,h — 全 FAIL distinct ✓
- 断言闸门 k_rationale=15==k_check=15≥8 ✓
- jsonl test==disk check.py roundtrip sha 3e4e955545fef173 ✓
- 追加 EDA-Eval-DesignFlow_B.jsonl (160→161) + mark ledger (case 162→163, spice_sim 126→127)
