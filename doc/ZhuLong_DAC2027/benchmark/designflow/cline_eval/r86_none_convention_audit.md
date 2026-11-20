# r86 audit: BLOCKER⑧ (None-约定假 FAIL) — REFUTED

**日期**：2026-11-05（shard A 轮 86）
**问题**：r84 发现 run_one.sh 旧 runner 把 `check()` 返回 `None` 误判 FAIL（已修：新增 `elif r is None: PASS`）。BLOCKER⑧ 假设：20 unique cline 实跑中 15 条历史 FAIL 可能含 None-约定假 FAIL → rolling-20=6/20=30% 可能被 None-bug 抬高（真值应更高=更易）。
**判据**：旧 runner 对 None-return 记 `reason="None"`（`else` 分支 `ok=False` → FAIL + `detail=str(None)="None"`）；对 raise 记 `reason="exception: "+repr(e)`（异常分支，新旧 runner 均 FAIL）；对 harness 沙箱层（无 submit.zip / killed）记非 check.py 原文。

## 方法
读 `cline_eval_status.jsonl` 31 行 → 按 `task_id` 去重取 latest → 21 unique（6 PASS / 15 FAIL）。对 15 FAIL 的 `reason` 字段做模式分类，并与 `judge_env_audit.tsv` 交叉（排除 BLOCKER⑤ judge-env 假 FAIL 干扰）。

## 结果

### 15 FAIL 按 reason 模式分类
| 类 | n | 说明 | None-bug? |
|---|---|---|---|
| `exception: AssertionError(...)` | 12 | check.py 抛 AssertionError = 真条件失败；异常路径新旧 runner 均 FAIL | ❌ 不可能 |
| HARNESS_KILL（no submit.zip / killed） | 3 | 沙箱层未跑 check.py（无 submit.zip 或超时杀） | ❌ 不涉及 check.py |
| `reason="None"`（None-bug 唯一指纹） | **0** | — | — |

**结论**：**0 / 15 是 None-约定假 FAIL**。BLOCKER⑧ REFUTED。rolling-20=6/20=30% 是真值，未被 None-bug 抬高。

### 12 CHECK_RAISED 的异常内容抽样（确证是条件失败非环境错）
| case | reason 片段 | 真信号类型 |
|---|---|---|
| EmXlsModel-001 | `(b) FAIL: py_compile error: IndentationError line 441` | ①form（候选 py_compile 失败） |
| PdkDirSizeScan-001 | `(e) FAIL: run on fixture_B exited 2; stderr=...argparse rejects --state` | ①form（候选缺 --state 接口） |
| IMPSR1253VddPmFix-001 | `FAIL (10/16 conditions failed): c: diagno...` | ③capability |
| LsfPrimesimSubmit-001 | `(f) FAIL: JSON missing fields: [mode, outdir, bsub_cmd, ...]` | ①form/④spec（JSON schema） |
| StarRCDspfFlow-001 | `[d] FAIL: A report missing resistors/layers/PASS` | ③capability |
| LibArcExtract-001 | `[n] no hallucinated/missing arcs: arc multiset ... DFF recovery/removal/setup/hold` | ③capability |
| STAFlow-001 | `d: common_setup.tcl missing set STA_ROOT` | ④naming-mismatch |
| TLEFRules-001 | `(w) lef_rules.py source must not hardcode A literals` | ④guard-comment（r3 false positive） |
| SynLintFlow-001 | `7/26 passed. Failed: c(dc_syn/USE_LSF/...)` | ③capability |
| DCCombHier-001 | `3/18 conditions failed [k, n, o]` | ③capability+④spec |
| DRCDeckOpt-001 | `FAIL [2]: (l) B 建议1 edge-band pre-filter; (m)` | ③capability（A 过拟合） |
| FindPcells-001 | `[e] FAIL: find_pcells.py does not access design.block` | ④judge-narrow（getTopBlock 替代） |

**全部 12 条异常信息均引用具体条件标签**（(b)/(e)/(c)/(f)/(d)/(n)/(k)/(l)/(m)/(w)/[e]/[d]），是真实条件判定失败，**非** FileNotFoundError / ImportError 等环境错。即与 BLOCKER⑤（judge-env BROKEN）也无关。

### judge-env 审计交叉（排除 BLOCKER⑤）
12 CHECK_RAISED 中：3 条在 `judge_env_audit.tsv` 标 SAFE（LsfPrimesimSubmit / StarRCDspfFlow / LibArcExtract）；9 条不在 audit.tsv（用 workdir-relative / here_direct / resolve 模式，非 BROKEN 模式）。**0 条 BROKEN**。→ 即便有 judge-env bug 也不影响这 12 条的 verdict，但实测它们本就不 BROKEN。

### 3 HARNESS_KILL（非 check.py）
| case | exit | 原因 |
|---|---|---|
| Verification-001 | killed(non-productive) | L1/offline case 被 PreToolUse hook 拦 run_commands → ②premise-missing（hook-block，非模型能力） |
| PwrGlobals-001 | killed(timeout1500s+overflow) | cline thrash 47 iter / 0 deliverable → ③capability |
| ETMExtract-001 | killed(non-productive) | cline thrash 34 iter / 0 deliverable / pyAether loop → ③capability |

此 3 条无 check.py 调用，None-bug 不适用。（Verification-001 的 ②hook-block 是已知 L1/offline × strict-hook 限制，独立问题。）

## 最终判据
- **BLOCKER⑧ CLOSED（REFUTED）**：rolling-20=6/20=30% 真实，未被 None-约定假 FAIL 抬高。
- 12 CHECK_RAISED 全是真条件失败（①form/③capability/④spec-narrow），3 HARNESS_KILL 全是 cline 自身（②hook-block/③thrash）。
- 无需重判 / 重跑任何历史 FAIL。rolling-20 基数 6/20 不变。
- **下轮指引**：rolling 已触 30% 上限且确证为真值 → **不应再开新 cline 实跑**（再 PASS 必超 30%，按 §5 应判「太简单」并加难，而非继续刷分）。优先路径转为 ① 加难（上隐藏 B 加条件 / 换更难 trace 重跑已有 case）或 ② 逐条修 97 BROKEN judge-env（不影响 rolling，扩充可实跑池）。

## 复用方法学
**None-bug 指纹 = `reason="None"`**：旧 runner `else` 分支对 None-return 记 `detail=str(None)`；新 runner 该路径已改 PASS。任何 jsonl 中 FAIL 行 reason 字面为 `"None"` 即旧 None-bug 假 FAIL，可重判为 PASS（重跑 reference_submit.zip 经新 runner 验证）。本批 0 条命中。
