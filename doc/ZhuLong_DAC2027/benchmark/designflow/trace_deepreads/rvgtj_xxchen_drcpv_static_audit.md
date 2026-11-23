# Deepread — rvgtj · xxchen@hfeg0plg06 · drcpv 静态审计

- **session**: `1795334271776_rvgtj.messages.json`
- **user/host**: xxchen / hfeg0plg06
- **match_count**: 254 (domain: physical_verify)
- **shard**: C
- **case_id**: `EDA-Eval-DesignFlow-DrcpvStaticAudit-001` (drcpv_static_audit, k=12)
- **claimed**: 2026-11-23 07:33 · **marked case**: 2026-11-23 08:14

## 1. 真实任务

xxchen 维护 DRC pattern 验证 GUI 工具 `drcpv`（部署在
`/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/`，PyQt 包，结构
`app.py` + `model/` + `generate/` + `golden/` + `ui/` + `tests/`）。他做了一次
**drcpv 代码 review**（产出 `tasks/drcpv_review.md`），向 agent 提了三个问题：

1. **冗余 / DRY 审计**：包里哪些 module-level def/class 从未被引用（dead
   symbols），哪些只在 `tests/` 下被引用（test-only symbols），哪些长度≥10
   的字符串字面量在多个生产文件里重复（duplicated literals）。
2. **README 是否够 agent 用**：README 是否覆盖 6 个必需章节（Agent 快速上手 /
   运行 / 测试命令 / 数据流 / 文件职责 / 约定）。
3. **死代码 / 未用导入检测**：每个生产 `.py` 里哪些 import 进来的名字从未在该
   文件里作为 `Name` 使用（unused imports）。

agent 写了两个 helper 脚本：
- `_grep_drcpv_symbols.py`：用 `ast` 收集 module-level def/class，再用
  word-boundary regex 统计引用，分出 dead / test-only。
- `_unused_imports_scan.py`：用 `ast` 收集 `import`/`import from` 绑定名，与
  `ast.Name.id` 集合做差，列出 unused imports。

最终产出 `tasks/drcpv_review.md` 汇总三轴结果。

## 2. Case 复刻设计

把"帮 xxchen 写 drcpv 静态审计工具"复刻成一个可判分的 design_flow case：

- **交付**：纯标准库 `drcpv_audit.py`（`ast`+`re`+`os`+`json`），CLI
  `python3 drcpv_audit.py <pkg_root> <report.json>`，写 7 键 report.json。
- **五轴静态分析**：dead_symbols / test_only_symbols / unused_imports /
  duplicated_literals / readme_coverage。
- **A（给 SUT）**：`sample_a/drcpv_a`，4 dead / 3 test-only / 4-file dup
  (literal=`/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1`) /
  README present={运行,数据流}。
- **B（隐藏判分）**：`hidden/drcpv_b`，5 dead / 4 test-only / 5-file dup
  (literal=`/home/yyzhang/work/drcpv_tool/1.2/cell_rule2`) / README
  present={运行,测试命令,约定} missing={Agent 快速上手,数据流,文件职责} /
  unused 5 文件 9 名。B 比 A 多出 `ldrdeckmap`/`qa_runner`/
  `param_config_dialog`/`group_dialog` 模块。
- **反硬编**：check 回跑 A，A dead==4 / dup_count==4 / A readme missing 匹配 A
  oracle，hardcode_b（永远输出 B 的报告）在 A 上必然 FAIL。
- **确定性**：3 次跑 B 的 report.json md5 一致。
- **12 条独立断言**，test_rationale 用 `12 条断言：①…⑫…` 格式。

## 3. 质量门验证（local negative_selftest.py）

```
golden         PASS
empty_shell    FAIL   (→ ② no report.json)
print_only     FAIL   (→ ② no report.json)
hardcode_b     FAIL   (→ ⑨ A dead==5 != 4)
naive_stub     FAIL   (→ ④ B dead count wrong, classes ignored)
delete_core    FAIL   (→ ④ B dead count==0 != 5)
§4.9 three-fake distinct failure points: 2 (need >=2)
all-negatives distinct failure points: 4
SELFTEST: OK
```

golden PASS + 5 negatives FAIL + §4.9 2-distinct + 全 5-neg 4-distinct。

## 4. 选料理由

2026-11-23 本轮 shard C 硬预算 40min 做 1 条 case。从最新 summary.tsv 取 top C
候选，rvgtj（mc=254, physical_verify）在 4 shard ledger 里全 fresh（未被任何
shard claim 过），且任务是"写静态审计工具"——交付物是纯 Python 脚本、判分可
全自动化、天然适合 design_flow 双参 check(deliverable, workdir) 模式，无需
EDA 解释器。claim 后 deepread 98 条消息确认任务可复刻。

## 5. 落地

- `EDA-Eval-DesignFlow_C.jsonl` 586 → 587
- assets: `assets/EDA-Eval-DesignFlow-DrcpvStaticAudit-001/{sample_a,hidden}`
  （39 文件）
- reference: `reference/EDA-Eval-DesignFlow-DrcpvStaticAudit-001/{check.py,
  solve.py, negative_selftest.py, negative/×5}`（8 文件）
- ledger: `trace_ledger_C.tsv` rvgtj → case
