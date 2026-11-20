# trace deepread — 1791861499459_57s2p (kenwang @ 172.16.8.192, mc=23)

- session_file: `1791861499459_57s2p.messages.json` (516KB / 33 msgs)
- host: 172.16.8.192 (kenwang), 真实身份可 ssh 免密
- domain: **layout_virtuoso** (SKILL `.il` 版图 QA pattern 生成 + dbcreaterect/dbcreatepolygon)
- 关键词: cellview:205? (实际 .il 里 dbCreateRect/dbCreatePolygon/dbCreateProp + dbcreaterect:74 dbcreatepolygon:31 drc:81 ddgetobj:24)

## 用户原话（逐字）

- **U#1**：「访问一下目录文件 /home/kenwang/workplace/AutoPattern/QA_pattern_auto/DRQA_Phase1_Release_v0.3/Library/Candence/space_pattern.md」
- **U#2（核心任务）**：「考虑到之前产生的 M1_S_1.il code 不合格，虽然 Pattern 是 ok 的，但是产生的 code 中存在大量的坐标，这是不符合要求的，我们的要求是在保证原来 Pattern 结构不变的情况下，code 中不可以存在具体的坐标，因为坐标不具有可移植性，当参数改变的时候，坐标也会跟着改变，如果不是用坐标的时候，参数改变只需要少量的数值参数改变即可，所以按照这个目标，尽最大努力的产生出来高质量的 code，且图形结构需要和有坐标的要求一样的」

## 真实 assistant 工具链（33 msgs）

1. `read_files` space_pattern.md
2. `list_allowed_files` + `search_codebase("M1_S_1")` 定位 QA_pattern_sourceCode/M1_S_1/
3. `read_files` M1_S_1.il（坏版，硬编码坐标）+ run_M1_S1.il + fix_m1_s1.py + drqa_topology.il + M1_S_20 样例
4. `run_commands` mkdir QA_pattern/M1_S_1/
5. `editor` 写参数化 M1_S_1.il：`procedure(drqaRotatedRect(cv lp cx cy len wid pid cls tv ev ru ca br))` ——
   坐标由 `(cx, cy, len, wid)` + `c=s=0.70710678`（45°）推导，`dbCreatePolygon` 4 点 round(...)/db 归一化，
   `dbCreateProp` 挂 drqaPatternId/Classification/TestValueUm/ExpectedViolation/RuleUid/CaseUid/BranchUid；
   `procedure(drqaRect/drqaPoly/drqaMark)` 同理；主函数 `drqaRun_M1_S_1()` 用 `for` 循环 + `(x, y, g, L=1.0, T=0.2)` 参数生成
   10 variants × 2 classifications（20 good + 10 bad），gap g 是 BOUNDARY/PASS_HIGH/FAIL_LOW 间唯一变量，**0 硬编码绝对坐标**
6. `ask_question`（mkdir 权限）→ 用户协助
7. 后续 read_files 验证写入

## 真实交付（gold）

参数化 SKILL `.il`：所有 `dbCreateRect`/`dbCreatePolygon` 调用的坐标参数均为变量算术表达式
（`(ox + i*pitch) : oy`、`(cx + hl*c - hw*s)` 等），字面量只出现在头部变量赋值（L/W/g/pitch/ox/oy/n），
图案几何结构与原硬编码版一致。M1 SPACE rule QA pattern。

## reframe（mock-behavioral · 新子型 `skill-pattern-decoordinate-param-infer`）

真实 Virtuoso SKILL + OA 环境 path-dependent，grader 无法真跑 → 纯 stdlib 微型 fixture：
- 输入：硬编码坐标的 `.il`（`dbCreateRect(cv lp list(x1:y1, x2:y2))` 字面量 + `lp=list("LAYER" "PURPOSE")`）
- 候选 `decoordinate_pattern.py`：(1) 解析所有 dbCreateRect 字面坐标 → bbox；(2) 推断参数化结构
  （n variants 沿 X 单行排列，每 variant 2 矩形，L/W/gap/pitch/origin0/layer）；(3) 生成参数化 SKILL 代码，
  **dbCreateRect(...) 调用内不得出现数字字面量**（用户核心要求）；(4) 按参数模拟重生成几何，校验与原始一致
- fixture：A(M1/L1.0/W0.2/gap0.014/n3/pitch5.0/origin[0,0]) / B 反 A(M2/L0.8/W0.15/gap0.020/n4/pitch3.0/origin[2,2]) /
  B2 edge(M3/n1/pitch=null)
- check 26 条件 a-z：参数推断 + 几何一致性 + 去坐标字面量校验 + 反硬编码 + 确定性 + 退化守卫

## 11-15 task初衷 B类复活

U#2 本质是「改写代码使之参数化、去坐标」—— 旧规则可能判为 refactor/explain 类 weak；
按 11-15 新标准 = 真实用户意图，合法造题。本 case 实证复活。

## distinct vs 近期 C case

- r710 DrcRunStatusAnalyze = Calibre DRC 日志解析
- r709 HierPathOccurInfo = hierPath 层次变换累乘 + 阵列偏移 + bbox DBU→UU
- r707 BwzDummyFlowExtract = TVF deck dummy 流水线结构提取
- r706 CadToolCliRefactorAudit = SKILL.md 关联文档 + CLI 改造审计表
- 本例 = **SKILL 图案 .il 去坐标参数化推断 + 几何一致性校验**（distinct ✓）

## case 落库

- case_id: `EDA-Eval-DesignFlow-SkillPatternDecoordinate-001`
- domain: layout_virtuoso, tier L1, 档位 B, k_rationale=k_check=26
- cases/C/EDA-Eval-DesignFlow-SkillPatternDecoordinate-001.json
- assets/.../{prompt.txt, task_brief.md, pattern_bad_A.il, hidden/{pattern_bad_B.il, pattern_bad_B2.il, hidden_manifest.json}}
- reference/.../{check.py, decoordinate_pattern_ref.py, reference_submit.zip, negative/{stub_empty,stub_print_expected,stub_delete_core}.py, negative_selftest.py}
- 自验: reference 26/26 PASS ✓ + 3 negatives 全 FAIL (first_fail json/layer/regen_match distinct) ✓ + 确定性 ✓ + A∩B∩B2 全异 ✓ + jsonl test field round-trip PASS ✓
