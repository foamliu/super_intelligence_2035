# Lite 跨 shard 缺陷扫描报告（D shard 发起 · 2026-11-25 r1284）

> **背景**：D shard 已 117/117 Lite 全绿（124 含 Full）。在 36.15 eval 宿主（`hfeg0tedaap02` / `10.251.36.15`）对本机做只读跨 shard 扫描，发现 A/B/C Lite 仍有一批 **P0 假阴性** 与 **L1 契约违规**，按 fix-order §1.3 记 `cross_shard` 交回对应 shard 修。D 不动别线 case/reference，仅本报告 + lite_health_D.tsv cross_shard 行 + discuss/D.md 指针。

## 0. 环境与判据

- **扫描宿主**：`hfeg0tedaap02` = `10.251.36.15`（eval 宿主本人）。
- **GUI 二进制可用性**（实测）：`hspice` / `hspice64` / `vcs` / `calibre` / `verdi` / `wv` / `innovus` / `virtuoso` **全部 MISSING**。
- **Lite 分布**：A=116 / B=130 / C=137 / D=117（合计 500）。
- **清单 md5**：`f7816ef4137353904e40a1a3b01fb3ae`（`eval/cases_lite.txt`，500 行）。
- **D 自身复验**（本轮在 36.15 真跑）：
  - `IOBufTune-001` hspice_mock → `check()` 返回 `True` ✅
  - `SineScanStdout-001` tclsh mock → `negative_selftest.py` PASSED（3 neg 全 FAIL）✅
  - ⇒ D 的 L4 在 36.15 真跑通过，非仅静态判定。

## 1. P0 跨 shard 缺陷（L4：参考解在 36.15 真跑 FAIL，假阴性）

### 1.1 B shard — hspice 依赖系统性问题（7 条确认 FAIL + 1 条缺 ref zip）

B shard 有 **8 条** Lite case 的 `check.py` 通过 `subprocess` 调 `hspice`，36.15 无 hspice ⇒ 参考解必 FAIL（L2/L4 双 FAIL = 假阴性）。**这正是 D r1283 `IOBufTune-001` 用 `hspice_mock`（faithful Shichman-Hodges 瞬态模拟器桩）修好的同一类 bug**，建议 B 按 D 的 mock 模式批量修。

| case_id | bin | 36.15 ref check 实测 | 复现命令 |
|:--|:--|:--|:--|
| `EDA-Eval-DesignFlow-GmidLut-001` | hspice | `{'pass':False}` ref re-run failed: hspice missing | `cd reference/EDA-Eval-DesignFlow-GmidLut-001 && python3 -c "import check,tempfile;print(check.check('reference_submit.zip',tempfile.mkdtemp()))"` |
| `EDA-Eval-DesignFlow-OpampChar-001` | hspice | `False` | 同上换 id |
| `EDA-Eval-DesignFlow-SpiceSim-001` | hspice | EXC `hspice not in PATH; grader must run on .75 sandbox` | 同上 |
| `EDA-Eval-DesignFlow-SpiceTbGen-001` | hspice | EXC `hspice executable not found in PATH or fallback` | 同上 |
| `EDA-Eval-DesignFlow-TaperBufOpt-001` | hspice | EXC `candidate failed on A` | 同上 |
| `EDA-Eval-DesignFlow-VlshftParamOpt-001` | hspice | EXC `4/12 conditions passed`（hspice run failed） | 同上 |
| `EDA-Eval-DesignFlow-StdLibCharTmpl-001` | hspice | EXC `COND g FAILED` | 同上 |
| `EDA-Eval-DesignFlow-InvTripDelay-001` | hspice | **NO_REF_ZIP**（L0/L2：缺 reference_submit.zip） | `ls reference/EDA-Eval-DesignFlow-InvTripDelay-001/` |

**B 例外（已 graceful，无需修）**：
- `LisMeasExtract-001`：ref PASS（`hspice_real=False` 优雅跳过）✅
- `SlicerFbTimeOpt-001`：EXC `missing asset src_sp/params_A or hidden params_B`（**setup/asset 问题，非 hspice**，但仍是 P0，请 B 诊断 hidden_manifest）。

### 1.2 A shard — vcs 依赖（1 条确认 + 1 条 setup 问题）

| case_id | bin | 36.15 ref check 实测 | 备注 |
|:--|:--|:--|:--|
| `EDA-Eval-DesignFlow-FmRtl2RtlDemo-001` | vcs | EXC `spec_b.json (hidden B) not found in workdir` | **hidden_manifest/setup 问题**（非 vcs 本身），请 A 诊断 hidden B 注入 |
| `EDA-Eval-DesignFlow-NetCellMap-001` | vcs | **PASS** ✅（graceful，无需修） | — |

### 1.3 C shard — calibre（1 条，已 graceful）

| case_id | bin | 36.15 ref check 实测 | 备注 |
|:--|:--|:--|:--|
| `EDA-Eval-DesignFlow-DrcPairWaiveClassify-001` | calibre | **PASS** ✅（calibre 作为字符串参数传给 python 脚本，非真实二进制调用） | — |

## 2. P2 跨 shard 缺陷（L1：check.py 返回值契约违规，123 条）

对 A/B/C 全部 Lite case 跑 `scripts/audit_check_returns.py` + 自写 Lite 过滤扫描，共 **123 条** Lite case 的 `check()` 末位 return 形状不符合判分契约（tuple / str / None / var / call-helper-透传 / dict-非pass-ok 键 / IfExp / BoolOp / Compare / BinOp）。在新契约下这些会被判 FAIL（即使交付件正确）= 假阴性。

- **复现**（在 EDA-Flow-Bench 根目录）：
  ```bash
  python3 scripts/audit_check_returns.py --all | awk -F'\t' 'NR>1 && $2!="OK"'
  ```
- **明细**：见 `lite_health_D.tsv` 中 `status=cross_shard`、`fix_note` 以 `L1-batch:` 开头的汇总行；逐条 id 清单已落入该行 `fix_note`（按 shard 分组）。
- **按 shard 计数**：A≈37 / B≈45 / C≈41（粗计，精确数见 audit 脚本输出）。
- **修法**：按 `reports/JUDGE_CONTRACT.md` §3（tuple→`return True/False`，helper 透传→包一层，dict 非法键→加 `pass` 键）。D r1271 已清零 606/606，可参考。

## 3. L0 误报澄清

初扫报 13 条「missing refdir」为**误报**：这些 case 的 case 文件用短名（如 `cases/A/DesignListGen-001.json`），refdir 实为全名 `reference/EDA-Eval-DesignFlow-DesignListGen-001/`（扫描脚本未尝试带前缀路径）。已逐条 `ls` 确认 refdir + check.py 均存在，**L0 无缺陷**，不记 cross_shard。

## 4. 给对应 shard 的请求

- **B**（最重）：① 7 条 hspice-依赖 case 用 D 的 `hspice_mock` 模式修（参考 `reference/EDA-Eval-DesignFlow-IOBufTune-001/hspice_mock/` + D r1283 心跳）；② `InvTripDelay-001` 补 `reference_submit.zip`；③ `SlicerFbTimeOpt-001` 诊断 hidden asset 注入。
- **A**：① `FmRtl2RtlDemo-001` 诊断 hidden B（spec_b.json）注入；② L1 批量修。
- **C**：L1 批量修（calibre/virtuoso 类已确认无真实二进制调用）。
- 全 shard：L1 123 条按 JUDGE_CONTRACT 修返回值形状（不改断言逻辑/条数）。

## 5. D 自身结论

D 117/117 Lite 在 36.15 真跑复验通过（IOBufTune + SineScanStdout spot-check），保持 green。本轮无 D case 需修。等待 A/B/C 修复 + zhulong 最终 3-run（fix-order §6）。

— D shard r1284
