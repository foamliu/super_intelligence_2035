# 深读笔记 — sid 1789959794365_pet0x (xinqiaoz @ hfeg0pkn004)

- session: `1789959794365_pet0x.messages.json` (639KB, 219 msgs: 114 user / 105 assistant, agent=lead)
- match_count=310；keywords: pdk:808, calibre:182, .gds:66, gdsii:5, skipper:3
- 域判定：**physical_verify**（calibre DRC Pattern QA 系统 `DrcPatternCheck.py` 维护）
- 路径：`/home/xinqiaoz/PDK_QA/pdkQaSystem/DRC/pattern/DrcPatternCheck.py`
- 工具：read_files×21, run_approved_command×41, editor×34, list_allowed_files×2, search_codebase×1, ask_question×1, RAG search×1

## 用户意图轮（12 条 user text）
1. msg0: 从 handoff 文档 `HANDOFF_drc_chdir_revert.md` 恢复上下文继续工作
2. msg23: 诊断「旧 cell（不区分 good/bad）匹配后 report 中 goodExisting=-1 是什么原因？」
3. msg45: 「还是改成 0 吧，无需区分。bad-only 模式没 good cell 是预期，goodExisting 仍然 0 即可。请修改代码，修改之前先备份到 .tmp」← **A 档候选意图轮（纯目标，不给根因）**
4. msg63: 「回到交接文档的回退操作，你的方案是什么？」
5. msg65: 「不用 commit，请执行回退，回退之前在 .tmp 备份代码」
6. msg117: 「drcSelectCheckByCell 是否也应该类似回退？」
7. msg118: 「你刚说 drcSelectCheckByCell 是新方法？和哪个版本对比？git diff 看它之前就有，是否幻觉？」← 用户指出根因/质疑，不作 A 档
8. msg136: 「是的，请回退。」
9. msg165: 「代码第 71 行改过 edaTurbo 数值，calibre 参数 =2 和 =32 有什么区别？」
10. msg171: 「怎么判断运行服务器核数和性能？」
11. msg181: 「好的，我改回去了。」
12. msg185: 「Pattern QA 阶段 1 需求基本完成，剩下在需求文档里。现在请分辨并清理 .tmp 临时文件，全部完成后用 handoff 技能写交接文档。」

## 关键产物与因果链（agent 验证 `[V]`）

### `goodExisting=-1` 根因（msg44 完整因果链）
- `getTargetCellPair` legacy fallback（L413-415）：旧 cell 无 `_F`/`_P`/`BAD_`/`GOOD_` → 返回 `(legacyCell, None)`，goodCell 恒 None
- `checkDrcRule`（L1032）`if goodCell:` 跳过 good 侧 second calibre → `ruleResults[rule]` 无 `"good"` 键
- report 生成段（L1413-1427）`goodExisting = -1`（旧初值），goodSummaryPath 不存在 → 保持 -1
- **修正**（msg53 edit, msg61 验证）：L1415 `goodExisting = -1` → `0`；判断段 L1331 本就已 `0`，行为不变

### `getSecondCalibreSummary`（L1141-1161）
```
ruleResults = {'CHECK1': -1, 'CHECK2': -1, 'CHECK3': -1}
pattern = "^RULECHECK\s+(\S+)\s+\.+\s+TOTAL Result Count = (\d+)\s+\(\d+\)$"
# 命中后遇非匹配行即 break
```
- CHECK1=existing violation 数；CHECK2=waive 原始数；CHECK3=incomplete 原始数

### 判定段（L1348-1356，三态）
```
if badMissing>0 or goodExisting>0 or incomplete>0:    fail
elif goodExistingRaw>0 or incompleteRaw>0:            waive
else:                                                  pass
```
goodExisting=goodSummary.CHECK1, goodExistingRaw=goodSummary.CHECK2,
badMissing=badSummary.CHECK1, incomplete=badSummary.CHECK2, incompleteRaw=badSummary.CHECK3

### 两处回退（msg64-116）
- 回退 #1 `symlinkFileToDir`（L162-178）：恢复 `os.chdir(dirPath)` + 相对 `symlinkName`，删除 `symlinkPath` 绝对路径
- 回退 #2 `drcSelectCheck`（L568-570）：删除 `DRC SUMMARY REPORT` 覆写 elif 块（3 行），走 `else` 原样保留
- diff 827→813 行（-14）

### 幻觉纠正（msg118-135）
- agent 称「drcSelectCheckByCell 是新方法，不在回退范围」→ 用户质疑 → agent 用 `git show HEAD` + OLD 文件验证：方法在 committed 版本已存在（L322）→ **承认幻觉**；但覆写块确实是 diff 新增（git diff `+` 行）→ 仅 drcSelectCheck 的覆写块回退

### edaTurbo（msg165-181）
- L71 `edaTurbo = 2` → `32`：calibre `-drc -turbo {edaTurbo}` 的并发核数
- =2 双核、=32 三十二核；用户问完改回 2（msg181）

## 合成决策
- 取 **B 档 synthesized**，deliverable = `drc_pattern_report.py`（独立 Python，解析 calibre drc.summary 文本 → composite 报告 + 三态判定 + goodExisting 修正）
- L1（离线 Python，但解析真实 calibre second-check 文本格式，subprocess 真跑 SUT 于隐藏 B）
- 14 条断言 a-n，对账 k_check=k_rationale=14
- 隐藏 B 3 个：B1 混合（bad-only+成对+waive+error）/ B2 跨输入守卫（全成对不同名）/ B3 边界（缺 CHECK2/3、good_summary 缺 CHECK1 行→good_existing=-1 区分 bad-only 0）
- 负样本 4 个：empty/print/always_pass/no_default_fix(复现原 bug -1)；§4.9 三假 = empty(a)+print(b)+always_pass(c) 全 FAIL
- 自验：ref PASS 14/14 + negative_selftest 4/5(全FAIL+ref PASS) + 三假全 FAIL；test_md5 == 磁盘 check.py
