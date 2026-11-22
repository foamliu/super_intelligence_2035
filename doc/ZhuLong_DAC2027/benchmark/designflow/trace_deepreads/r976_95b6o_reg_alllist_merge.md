# r976 — 95b6o · RegAllListMergeProduce-001 (verification, A档 trace-faithful produce-task + hidden-B)

## trace 定位

- **session**: `1795164661600_95b6o`
- **user / host**: `e0039102` @ `hfeg0pbn16`（10.129.32.75 同网段，hfhds201 系）
- **match_count**: 168（keywords `verilog:168` — 纯 A-pure verification 域，无任何 C/D 域杂质）
- **trace 体量**: messages.json 285KB / 33 msgs / 18 users / 仅 2 条非工具 user msg → 干净 2-turn produce-task
- **agent**: lead
- **shard_mc.A 池**: mc≥10（本 case mc=168，远超门槛）
- **fresh 来源**: 11-22 修复 sid 规范化（剥 `.messages.json` / `.messages.archive.json` / `.json` 后缀后再 `sed 's/.*_//'`）后，420 A-domain 候选 × 4-shard ledger 交叉得 4055 ledgered sids → 44 truly fresh A-domain 候选之一

## 用户真实意图（逐字，trace U#0）

> 「drgsa 1105 补充版1 /rundata/.../ALL.list ... 你帮我把这几个ALL.list 统一抓出来对应写成一份文件给我」

用户粘贴 6 条 drgsa DDR5 回归 `ALL.list` 路径，要求**合并成一份可对照的文件**。
本质：多次回归 run 的 ALL.list 横向合并（source run 清单 + per-run 统计 + Task×Run 矩阵 + 原始内容）。

## trace gold（assistant M#?）

assistant 写 `merge_all_list_ref.py`（~5KB）：
- 解析 ALL.list（`#Task_Name Pattern_Name Task_Dir Run_Time(s) Peak_Mem(M) CPU(s) VPS_TASK_SEED Tags`，whitespace 分隔，`#` 表头跳过，≥7 列）
- 4 段输出：
  1. 来源 run 清单（label + path + task count）
  2. 各 run 结果统计（按 pattern 计数，pattern 列取所有 run pattern 并集排序）
  3. Task × Run 结果矩阵（task 在该 run 不存在填 `-`）
  4. 各 run 原始 ALL.list 内容（逐行缩进 4 空格）

## 本 case 提炼

通用 `merge_all_list.py <manifest> <output>`：manifest 驱动（`<label>\t<list_path>`，路径相对 manifest 目录），无任何 hardcode。

### 可见 A（anti-backsolve，drgsa DDR5，`_x4_6400` 后缀）

- `manifest_A.txt` + `runA1.list`(5 tasks) + `runA2.list`(5) + `runA3.list`(4)
- 7 个 unique A task：basic_write_bl8 / basic_read_bl8 / basic_mpr_scan / checkin_act / checkin_pre / extra_zqcal / extra_refresh（均 `_x4_6400`）
- A patterns：{pattern_pass, comp_error, timeout}（3 个）

### 隐藏 B（ddgoa LPDDR5，`_x8_5500` 后缀）

- `manifest_B.txt` + `runB1.list`(5) + `runB2.list`(5) + `runB3.list`(4) + `runB4.list`(4)
- 4 runs，7 unique tasks，5 patterns：{comp_mismatch, drc_error, pattern_pass, sim_fail, timeout}
- **B-specific 锚点**：`drc_error` pattern 在 A 中不存在（A 只有 comp_error），且 run3 有 `drc_error=1`（lp5_refresh_x8_5500 只在 run3 出现一次，3 个 `-`）→ anti-hardcode 强锚点
- B task 命名空间 `_x8_5500`（LPDDR5）与 A 的 `_x4_6400`（DDR5）完全分离 → anti-leak 易检

## check.py（16 断言 a-p，k_check=16=k_rationale）

| # | 断言 | anti-X 类别 |
|---|---|---|
| a | deliverable 是 zip 且含 `merge_all_list.py` | 基本完整性 |
| b | py_compile 通过 | 基本完整性 |
| c | SUT 脚本在隐藏 B 上 subprocess 退出码 0 | real-run |
| d | B 输出文件存在且 ≥100 字节 | anti-degenerate |
| e | header 报告 run 数=4 | anti-hardcode（B-specific count） |
| f | header 报告去重任务总数=7 | anti-hardcode（B-specific count） |
| g | 来源 run 清单含全部 4 个 B label (ddgoa run B1-B4) | anti-hardcode |
| h | anti-leak: 3 个 A label (drgsa run A1-A3) 不得泄漏进 B 输出 | anti-hardcode |
| i | per-run stats: run3 行 total=4/comp_mismatch=0/drc_error=1/pattern_pass=2/sim_fail=1/timeout=0 | anti-hardcode（B-specific drc_error 锚点） |
| j | Task×Run 矩阵 section 存在 | 结构完整 |
| k | 矩阵含全部 7 个 B task 名 | anti-hardcode |
| l | lp5_write_bl16_x8_5500 在全部 4 run 均 pattern_pass | anti-hardcode（B-specific task） |
| m | lp5_read_bl16_x8_5500 含 comp_mismatch | anti-hardcode（B-specific task+pattern） |
| n | lp5_refresh_x8_5500 含 drc_error 且恰好 3 个 `-` | anti-hardcode（B-specific 锚点） |
| o | anti-leak: 7 个 A task 名（`_x4_6400` 后缀）不得出现在 B 输出 | anti-hardcode |
| p | 原始 ALL.list section（第三部分）存在且含 lp5_zqcal_x8_5500 + 3 次重复运行 md5 一致 | 结构 + determinism |

## §4.9 anti-degenerate（negative_selftest.py 验证）

- `neg_empty.py`（空壳，无产出）→ FAIL (d)
- `neg_print_only.py`（stdout 打印预期文本但不写 output 文件）→ FAIL (d)
- `neg_core_deleted.py`（骨架：读 manifest 计数但删除 parse/matrix/stats/raw 逻辑，写 stub 输出）→ FAIL (f header unique task count != 7)
- ref self-test: PASS 16/16
- 3 negatives all FAIL ✅

## 实测

```
REF SELF-TEST: PASS
NEGATIVE SELF-TEST: PASS  (ref passes, 3 negatives fail)
```

## 入库

- A.jsonl: 436 → 437
- ledger: 95b6o claimed → case (EDA-Eval-DesignFlow-RegAllListMergeProduce-001)
- assets: manifest_A.txt + runA1-3.list（可见 A）+ hidden/{manifest_B.txt, runB1-4.list, hidden_manifest.json}（隐藏 B）
- reference: check.py + merge_all_list_ref.py + negative/{3 neg} + negative_selftest.py
- eda_flow session: declare_done + close

## 选料注

- 11-22 修复 sid 规范化后 44 fresh A-domain 候选之一；选中 95b6o 因 mc=168（高）+ 纯 verification 域（verilog:168 单一 keyword）+ 2-turn 干净 produce-task（仅 2 条非工具 user msg，无多轮上下文漂移）+ assistant 产出（merge 脚本）天然适合 hidden-B 反硬编码（manifest 驱动 + 任务命名空间可分离）。
- 与 r973 (AccCfgGenProduce, 5opq9/e0045144 mc51 digital) / r974 (PreEMSigDataflowTraceProduce, 5q6uq/eva1li mc112 verification) / r975 (InstPortGroupReorderProduce, 3z5rz/guomings mc67 digital) 不同用户不同 session，无 dedup 冲突。
