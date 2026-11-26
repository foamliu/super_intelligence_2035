# Deepread: 1791786838927_a15un — xinqiaoz PDK QA test-suite status analysis

- **user**: xinqiaoz
- **host**: 10.129.2.11 (hfeg0plg76)
- **session_file**: 1791786838927_a15un (dir under `~/.cline/data/sessions/`)
- **match_count**: 521 (drc:4153 / calibre:1809 / pdk:1210 / pex:122 / .gds:102 / lvs:18)
- **domain**: physical_verify (PDK QA DRC/calibre test suite)
- **msgs**: 229 (1 user-text turn at U#0 + 3 mid-session user-text turns at U#13/U#24/U#26/U#65/U#98/U#202; the rest are tool_result user-role messages)
- **real user turns (text)**: 7

## U#0 (verbatim — the original intent, A档 candidate)

> 当前项目的 test case 有哪些，哪些是可以真正跑通的 case？哪些是不能跑通的？原因是什么？

**Classification**: analysis-Q&A / explain / inventory — 用户要枚举项目的 test case，分类哪些 PASS / FAIL / SKIP，并解释原因。**这是真实用户意图**，无任何预设修复方案。符合 11-15 §二 revival（analysis-Q&A/explain/doc-search 全部复活为合法任务）。

**A档选轮规则**: U#0 是「提出需求 / 表达目标」型轮次，用户未给出根因或修复方案 → 符合 A档任务说明选用规则。

## Assistant 工具链 (前 64 msgs，对应 U#0 的回答)

1. `list_allowed_files` / `read_file` 探索 `/home/xinqiaoz/PDK_QA/pdkQaSystem/` 项目结构
2. 读 `run_all_tests.py` 入口 → 识别 17 个 test 目录
3. 本地直接跑 `run_all_tests.py` → 11 PASS / 6 SKIP（Calibre VCO mismatch on RHEL8）
4. U#13 用户建议「ssh 到本地 CentOS 7.8 机器跑（绕过 VCO）」
5. 用户在终端配合 ssh-keygen / ssh-copy-id（U#24/U#26 提供执行结果）
6. Assistant 写 `ssh_test_pdkqa` profile → 通过 ssh 在 `hfeg0pfn108` 跑 17 tests → **14 PASS / 3 FAIL / 0 SKIP**
7. 逐个跑 3 个 FAIL 的 case 拿详细错误堆栈
8. U#64 产出完整分析报告（表格 + 3 FAIL 根因）

## U#64 deliverable（用户接受的最终报告结构，A档金标准）

```
## 完整测试分析报告（基于 SSH 到 hfeg0pfn108 实际运行）
> 17 项测试，结果：14 PASS / 3 FAIL / 0 SKIP

### 全部 Test Case 清单与状态详解
| 测试目录 | 状态 | 依赖 | 说明 |
| `ldr/` | PASS | G5_CIP LDR CSV | 解析 1663 行 LDR 数据 |
| `drcSyntax/` | PASS | Calibre rules_syntax_checker | SVRF 语法检查通过 |
| ... (14 PASS) ...
| `emptyDeriveLayer/` | FAIL | G5_CIP DRC + GDS + Calibre | CWD 导致相对 INCLUDE 路径找不到 |
| `patternLayerVsDesignRuleLayerChange/` | FAIL | G5_CIP GDS + LDF + Truth + calibredrv | TruthTable 构造函数参数签名不匹配 |
| `drcWithPattern/` | FAIL | G5_CIP config.ini + GDS + Calibre + calibredrv | CWD 导致相对 INCLUDE 路径找不到 |

### 3 个 FAIL 的详细根因
1. emptyDeriveLayer/drcWithPattern — 相对 INCLUDE 路径问题
   错误: "problem with access, file type, or file open of this include file: rules/calibre.layer"
   根因: calibreDRC_DDR5.rule 第 47 行 INCLUDE "rules/calibre.layer" (相对路径)，checker 内部 os.chdir(self.workDir) 后 calibre -svrf 在错误 CWD 找不到
2. patternLayerVsDesignRuleLayerChange — 构造函数参数签名不匹配
   错误: "__init__() missing 1 required positional argument: 'pnpAreaConfFile'"
   根因: TruthTable.__init__(truthTableJsonPath, pnpAreaConfFile) 必需两参，但 check() 中只传一个
```

## 后续轮次（**不属于本案任务说明**，分离）

- U#65: "好的，我们先开始尝试修复这 3 个失败的 case" — 新任务（修复）
- U#98: "请回退你的修改...修复 test case 的原则是只能动 tests 目录的代码" — 修复策略约束
- U#202: "/handoff 请交接" — 生成 handoff 文档

本案 **只取 U#0**，U#65 及之后的修复轮次是 trace 里的另一个任务，**不进 prompt**。

## reframe 决策

- **模式**: `mock-behavioral test-suite-status-analysis-Q&A`（**C 域首例 test-suite-status 静态分析 + evidence-only mode**，同 r736 LayoutElementAttribution 的 ③evidence-only P-006 r618 (C)-(A) 分流）
- **理由**: 真实任务是对**固定 PDK QA test suite**（17 tests + 实际运行日志 + 错误堆栈）做枚举 + 状态分类 + 根因解释；SUT 无需重跑测试（也无 PDK 环境），仅需**分析已产出的 result.log + run_test.py 源码**，输出结构化 JSON 报告
- **distinct vs**:
  - r736 LayoutElementAttribution = 枚举 layout instances + 归属 autovia/powerfill（layout 域）
  - r737 ScriptReconAnalysis = AST 静态分析 + 关系图构建（脚本域）
  - **本案 = test-suite 状态枚举 + 根因解释 + evidence 引用（test-runner 域，C 域首例 test-suite-status-analysis）**
- **牙齿来源** (evidence-only mode):
  1. content-correctness（≥18 断言：枚举数 / 每测状态 / 每测根因 / summary 计数）
  2. evidence-verification（每条 FAIL/SKIP 的 evidence 必须引用 B fixture 真实存在的 log 行内容，防 print-gold stub）
  3. B/B2 cross-input guard（不同 fixture 不同 pass/fail/skip 模式 + 不同 FAIL 根因，反硬编码 A）
  4. anti-stub（空壳/print-gold/exit-1 三假提交全 FAIL）

## BUILD a15un → TestSuiteStatusAnalysis-001

- **asset A**: `sample_input/tests/` 12 个 mock PDK QA test 目录（9 PASS + 2 FAIL + 1 SKIP），每目录含 `run_test.py`（带 `# DEPENDS: ...` 头注释）+ `result.log`（含 `STATUS: PASS/FAIL/SKIP` + `ERROR:`/`REASON:` 块）
- **prompt.txt**: U#0 逐字原文
- **task_brief.md**: ≤3 行交付接口（不写"要做什么"）
- **hidden B**: `hidden/b/tests/` 10 个 mock LVS/PEX/DRC test 目录（7 PASS + 2 FAIL + 1 SKIP），不同的失败测试 + 不同的 error tokens，反 A 硬编码
- **hidden B2**: `hidden/b2/tests/` 6 个 mock lib-check test 目录（4 PASS + 1 FAIL + 1 SKIP），最小 cross-input guard，反硬编码 A 或 B
- **hidden_manifest.json**: B/B2 路径 + 设计说明
- **reference/solve.py**: 纯 stdlib (os/json/sys/re)，扫 tests/ → 读 result.log 抽 status/reason/evidence → 读 run_test.py 抽 DEPENDS → 输出 JSON
- **reference/check.py**: ≥18 断言（a-r），subprocess 真跑 B/B2/empty dir，对账人工独立推得的 B/B2 ground truth
- **3 negatives**: solve_empty / solve_print_gold / solve_status_only（只读 status 不抽 evidence/dependencies）
- **negative_selftest.py**: 三 negative 必 FAIL distinct

## 纪律

- SUT 沙箱只含 `sample_input/tests/` + `prompt.txt` + `task_brief.md`；`hidden/` + `reference/` 不进 SUT ✓
- 不脱敏：user=xinqiaoz / host=10.129.2.11 / session_file=1791786838927_a15un 真值 ✓
- 11-15 §二 revival：reclaim from parked（旧 note「test-inventory 元任务(r46)」pre-11-15 误判，analysis-Q&A 复活）
- 只动 C shard 文件 ✓
