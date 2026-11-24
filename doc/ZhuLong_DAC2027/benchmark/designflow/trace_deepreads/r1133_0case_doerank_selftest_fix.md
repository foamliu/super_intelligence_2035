# r1133 (2026-11-24) — 0-case 治理轮 · DOERankBuild-001 §4.9 negative_selftest 补齐 + B §4.9 完整性再审

## 背景
r1132 跨 shard §4.9 审计报告 B=0 gap（仅核 refdir 类），但将 61 个"无 refdir" B case 标为"inline-test 类，另线未深查"。本轮复查该结论并补齐发现的真 gap。

## 前置确认
1. **新 scan 检查**：eda_flow open_session(hfhds201) → `ls /home/t0002965/log/ssh_eda_search_*` → 最新仍 `20261124_023802`（r1131/r1132 同源，mtime 02:45），eda_trace_20261124.log mtime 00:01（无在跑 scan，ps 无 daily_eda_scan/orchestrator 进程）。**无新 scan 到达，fresh B-spice 池耗尽条件延续（第 6 轮 0-case）**。
2. 527j4 专项 build 轮需 2–3 轮 + 80MB DSPF，单轮 40min 预算不可行，本轮不启动。

## 本轮工作

### 1. r1132 "61 无 refdir" 结论再审 — 发现命名匹配 bug
r1132（及我本轮初版脚本）用单一命名约定匹配 reference/ 目录，但实际 reference/ 下**混存两种命名**：
- 2076 个全名目录 `EDA-Eval-DesignFlow-<X>-001`
- 431 个短名目录 `<X>-001`

用 **both-name 匹配**（`cid` 与 `short(cid)=cid.replace("EDA-Eval-DesignFlow-","")` 均查）重审 B 561 case：

| 类别 | 数量 |
|:--|--:|
| 有 refdir + negative_selftest.py ✓ | 560 |
| 有 refdir 但**无** negative_selftest.py（真 §4.9 gap） | **1** |
| 完全无 refdir | 0 |

**结论**：r1132 报的"61 无 refdir inline-test"是**命名匹配 bug 造成的假象**——这 61 个 case 实际都有 refdir（在另一种命名下），且 60 个有 negative_selftest.py。**B 真 §4.9 gap = 1 个：DOERankBuild-001**（有 check.py 10414B + doe_rank_ref.py 参考解 + gen_assets.py，但无 negative/ 目录、无 negative_selftest.py）。

### 2. DOERankBuild-001 §4.9 补齐
**case 摘要**：DOE (Design-of-Experiments) 锥形缓冲器（NAND + 3 级 inverter）设计点 PDP 排序器。SUT 交付 doe_rank.py + doe_rank.csv，check 16 条断言（a-p）：a-d zip/解析/表头/行数，e-g dly/area/dA 公式，h-i 排序+rank 序号，j-k PDP/delay 最优 variant，l-m nand/inv 标签，n 无不合理点（dly≤45），o B1 泛化，p B2 anti-hardcode（scale area 表）。k=16，ref 16/16 PASS 已验证。

**补齐内容**（reference/DOERankBuild-001/negative/）：
- `neg_empty.py` — 空壳，不产出 doe_rank.csv → FAIL 9/16（a/b/c/d... 多条）
- `neg_print_only.py` — 硬编 A 集 25 行 expected CSV（从 A/_expected_doe_rank.csv 抄录），忽略输入参数 → **PASS a-n（14/16）但 FAIL o（B1 泛化）+ p（B2 anti-hardcode）**，干净演示 check 的 anti-hardcode 齿
- `neg_core_removed.py` — 参考解删核心：去掉 DLY_TARGET 过滤（保留不合理点）+ 去掉 dA 排序（保输入序）→ FAIL 10/16（d 行数/h 排序/i rank/j PDP 最优/k delay 最优/n 不合理点）
- `negative_selftest.py` — harness：对每个 fake 打包 submit.zip（fake 改名 doe_rank.py + 跑 A 生成 doe_rank.csv），跑 check.py 断言 exit code；ref 必须 PASS、3 fake 必须 FAIL

**自验结果**：
```
[REF ] exit=0 pass=True  OK
[neg_empty         ] exit=1 pass=False  OK (FAIL as expected)  9/16
[neg_print_only    ] exit=1 pass=False  OK (FAIL as expected)  14/16  (FAIL o,p)
[neg_core_removed  ] exit=1 pass=False  OK (FAIL as expected)  10/16  (FAIL d,h,i,j,k,n)
ALL NEGATIVE SELFTESTS PASS: ref PASS + 3 fakes FAIL.
```
§4.9 (a)(b)(c) 三假齐 FAIL ✓，ref PASS ✓。

## 台账动作
- 0 claim / 0 mark（无新 case、无新 parked）
- 台账 B 维持 1758（case 592 · parked 1166）
- eda_flow session `default_designflow-b_shardB-r1133_0` 已 close

## 指标
- 📊 trace 覆盖率: covered=592/target=4529=13.1%(mc>=10, 不变，无新 case)
- 🎯 通过率: 最近20条 20/20=100%(观察值, 不变)
- 📦 MEMORY_B <32KB ✓
- DEBT: 0

## 结论与下一步
1. **B §4.9 完整性 = 561/561 = 100%**（DOERankBuild-001 补齐后，全部 B case 均有 negative_selftest.py + 三假 FAIL）。r1132 "61 无 refdir" 假象已澄清，B 真 gap = 0。
2. fresh B-spice 池仍耗尽（第 6 轮 0-case），等新 scan。
3. 跨 shard A/C/D 仍 26 个 §4.9 gap（r1132 清单），非 B 职责但已记录供各 shard agent。
4. 527j4 专项 build 轮仍待启动（需 2–3 轮 + 80MB DSPF 上下文重建）。
